# Under the Hood — the Night Library, line by line

*For the hard-parts people. No frameworks, no magic — one HTML file, a model
server, and the browser's actual machinery. We're going to trace a story from
the model's first byte to the moonlight on the canvas, and at every interesting
junction you get a question before you get the answer. Predict first. That's
the deal.*

**What you'll walk away able to do:** explain precisely — not vibes-precisely,
*interview*-precisely — how real-time token streaming, decode-time grammar
constraints, and a two-clock UI work, and rebuild any of them from scratch.

---

## 0. The mental model: two clocks

Everything in this app is two clocks disagreeing in your favor:

- **The writer's clock**: Bonsai emits ~60–125 tokens/second.
- **The reader's clock**: a parent reads aloud at ~2.6 words/second.

One ratio — roughly **30×** — is the entire product. Every section below is
just bookkeeping for that disagreement.

**Pause. Predict:** if generation is 30× faster than reading, what should the
*page* do with words that exist but haven't been "read" yet? Show them?
Hide them? Something else? …Hold that thought for §3.

## 1. The stream: bytes → lines → deltas

There's no SDK here. `streamBeat()` in `web/index.html` does a raw `fetch` to
llama-server's OpenAI-compatible endpoint with `stream: true`, then reads the
body itself:

```js
const reader = r.body.getReader();
const dec = new TextDecoder();
let buf = "";
while (true) {
  const { done, value } = await reader.read();   // a chunk of raw bytes
  if (done) break;
  buf += dec.decode(value, { stream: true });    // bytes → text (stateful!)
  const lines = buf.split("\n"); buf = lines.pop();  // keep the partial line
  for (const ln of lines) {
    if (!ln.startsWith("data: ") || ln.includes("[DONE]")) continue;
    const delta = JSON.parse(ln.slice(6)).choices?.[0]?.delta?.content || "";
    ...
```

Three things people get wrong in interviews, all visible right here:

1. **Chunks are not messages.** The network hands you arbitrary byte windows.
   One chunk might contain two and a half SSE events. That's why `buf` exists
   and why we `lines.pop()` the partial line back into it.
2. **`{ stream: true }` on the TextDecoder.** A UTF-8 character can be *split
   across chunks*. A stateless decode would corrupt it. The decoder keeps the
   half-character and waits.
3. **There is no `await` between deltas** — the loop is pulled by the network.
   The writer's clock lives in this loop; nothing in our code paces it.

**Pause. Predict:** the server is killed mid-beat. What does this loop do —
throw, hang, or end quietly? …`reader.read()` resolves `{done: true}` when the
connection drops, so the loop exits as if the story beat simply ended. The app
degrades to a shorter beat. (Try it. Kill the server mid-sentence.)

## 2. Time-to-first-token is a different number than tok/s

`S.ttft` is stamped once, on the first delta — that's **prompt processing**
(the model reading the conversation so far). The tok/s meter deliberately
starts its stopwatch *at the first token*, not at the request:

```js
const gen_s = (performance.now() - S.tFirstTok) / 1000;
el("#m-tps").textContent = (S.tokensSinceFirst / gen_s).toFixed(0);
```

If you divide by total elapsed time instead, prompt processing pollutes the
rate and your meter lies politely downward. We shipped that bug for about an
hour; the fix is the two-stopwatch split you see above.

## 3. The ghost page (answer to §0's question)

Words stream in ~30× faster than they're read. The page **shows them
immediately — at 13% opacity**:

```css
#page .w { opacity: .13; transition: opacity .45s ease; }
#page .w.lit { opacity: 1; }
```

Each delta becomes `<span class="w">` nodes the moment it arrives, so the
words *occupy their final layout slots* instantly — faint ink. Then a metronome
lights them at the reader's clock:

```js
setInterval(() => {
  const unlit = document.querySelector("#page .w:not(.lit)");
  if (unlit) { unlit.classList.add("lit"); S.litWords++;
               unlit.scrollIntoView({ block: "nearest" }); }
}, 1000 / READ_WPS);   // READ_WPS = 2.6
```

**Why this is the smooth version:** the jank in naive streaming UIs is
*layout shift* — text appears, paragraphs grow, buttons jump. Here, layout
cost is paid once per word at insertion (while it's nearly invisible), and the
visible animation is pure opacity — compositor work, no reflow. The page
follows the *reader's* cursor (`scrollIntoView`, nearest), never the writer's,
so the view is as calm as the voice.

And the faint ink is not just engineering: it's the thesis on the page. You
can *see* how far ahead the model is — that shimmer of unread words is
intelligence density, literally visible.

**Pause. Predict:** set `READ_WPS = 5`. What happens to the "ahead" number in
the meter? Work it out from `(genWords - litWords) / READ_WPS` before you run it.

## 4. Grammar-as-contract: the part that makes a 1.7B dependable

Three calls in this app need *structure*, not prose: scene JSON, branch
choices, judge scores. We never parse-and-pray. The request carries a schema:

```js
body: JSON.stringify({
  messages: [...],
  response_format: { type: "json_schema",
                     json_schema: { name: "out", schema } },
  ...
})
```

Under the hood, llama-server compiles that JSON Schema into a **GBNF grammar**
and applies it *inside the sampler*: at every step, tokens that would violate
the grammar are masked out before sampling. The model doesn't "try" to emit
valid JSON — invalid JSON is **unrepresentable** in its output space. Enums
pin vocabularies (`"mood": enum[...]`), `minLength` forbids the lazy empty
string, `additionalProperties: false` forbids invention.

This is the deepest idea in the repo: **move the contract from hope (prompt)
to physics (decode mask)**. A 590MB model with a grammar beats a model 100×
its size with a "please respond in JSON" prayer — for *this* class of job.

**Pause. Predict:** what's the failure mode that grammar *can't* fix?
…Semantics. The JSON will parse; the `mood` may still be wrong for the scene.
Grammar buys you structure; the rubric and judge exist for meaning.

## 5. The illustrator: upgrade, never depend

```js
drawDreamscape(scene);          // instant, from the same scene JSON
try {  ...fetch(ILLUSTRATOR + "/generate"...)  // 45s budget
  // success → swap the <canvas> for the <img>, chip says "Bonsai Image 4B"
} catch {
  // chip says "dream canvas" and tells you how to start the studio
}
```

The dream canvas is painted *synchronously* from scene JSON (gradient by
`time`, stars, moon, ridgeline, the `focus` line in gold) — so the frame is
never empty, never a spinner. The real diffusion render is an *upgrade* that
arrives in ~6s when the studio is up. Two painters, one contract: scene JSON.

## 6. Experiments (do these, in order)

1. **Kill the writer mid-beat.** Watch §1's prediction come true. Restart it;
   the next beat works — no state on the server side except the KV cache.
2. **`READ_WPS = 5`** — check your §3 prediction against the meter.
3. **Delete `repeat_penalty` from `SAMPLING`.** Generate three beats of the
   same story. Watch a 1.7B model fall in love with its own first paragraph.
   Put it back.
4. **Break the contract on purpose:** in `SCENE_SCHEMA`, remove
   `additionalProperties: false`, ask for a scene, and log what extra keys a
   small model invents when the fence comes down.
5. **Open DevTools → Performance, record a beat.** Find the long tasks. There
   shouldn't be any over ~50ms; if you find one, you've found our next PR.

---

*If you read this far you can rebuild the whole thing from memory, which is
the point. The library has no secrets — it's one file, two clocks, and a
grammar. Goodnight.*
