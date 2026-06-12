# Field Guide to the Night Library

*Ethnographic notes for new members of the tribe — the PrismML team, the Bonsai
community, and anyone who intends to live here rather than visit.*

**Who this is for:** you already know what a GGUF is and roughly why 1.58 bits
matter. **What you'll walk away able to do:** add a story to the canon, swap an
illustrator backend, and reuse this repo's two core patterns in your own Bonsai
projects.

---

## 1. The vocabulary (learn these eight words and you speak the language)

| Term | Meaning |
|---|---|
| **the writer** | Ternary-Bonsai-1.7B on stock llama-server, port 8080. Never a fork. |
| **the illustrator** | Bonsai Image 4B behind `POST /generate`, port 8800 — or its understudy: |
| **dream canvas** | the procedural nightscape painted from scene JSON when no image studio is running. The demo never has a broken pane. |
| **the canon** | `canon/canon.json` — twelve civilizational seeds. Each carries a **truth note**: the real history, ready for "did that really happen?" |
| **density meter** | the two-cursor bar: Bonsai writing vs. a parent reading aloud. The gap between cursors is the product thesis, rendered. |
| **grammar-as-contract** | JSON schemas enforced at *decode time* (llama-server `json_schema` → GBNF). The model isn't asked to be reliable; it's constrained to be. |
| **sleep gate** | the rubric dimension that's absolute: a story that ends loud fails regardless of composite. The job is sleep. |
| **footgun** | a verified adoption trap, filed with a reproduction. The ledger lives in [the-little-tree-thinks](https://github.com/ChaiWithJai/the-little-tree-thinks). |

## 2. The site map (ports and processes)

```
:8080  llama-server, Ternary-Bonsai-1.7B   (required — the writer & the judge)
:8800  Bonsai-Image-Demo FastAPI backend   (optional — the illustrator)
:8400  python http.server, this repo       (the library itself)
```

The page calls the writer **directly from the browser** — llama-server's CORS is
open by default, so there is no proxy, no backend of our own, no place for a
secret to hide. View source; that's the whole system.

## 3. The two patterns worth stealing

**Grammar-as-contract.** Every structured ask in this repo — scene JSON, branch
choices, judge scores — ships a JSON schema in the request and lets llama-server
compile it to a grammar the sampler cannot escape (`web/index.html`, search
`askJSON`; `studio/judge.py`, search `SCHEMA`). This is what makes a 1.7B model
*dependable* enough to drive UI. If you take one thing home, take this.

**Always-works degradation.** The illustrator is a privilege, not a dependency:
`illustrate()` paints the dream canvas instantly from the same scene JSON, then
*upgrades* to a real Bonsai Image render if `:8800` answers. The chip on the
frame tells the truth about which painter worked. Demos with a single point of
failure die on stage; this one degrades into something still beautiful.

## 4. Rituals

**Adding a seed to the canon (the initiation).** A first contribution here is a
story, which is the correct first contribution for a library:

1. Pick a story your civilization tells its children — one that sparks
   imagination, models resilience, or carries pride in what humans have done.
2. Add a seed object to `canon/canon.json`: `id`, `title`, `civilization`,
   `era`, `values[]`, a one-sentence `hook`, and an honest `truth` note
   (cite what's historical, name what's myth — myths are canon too; lying
   about which is which is not).
3. Generate a story from your seed in the app, save the text, and face the judge:
   `python3 studio/judge.py story.txt --seed your_seed_id`
4. Composite ≥ 0.7 and sleep gate PASS → open the PR with the judge output
   pasted in. The rubric, not a maintainer's taste, is the gatekeeper.

**Filing a footgun (the status ritual).** Hit a trap — a silent failure, a
contradictory doc, a cache that lied? Reproduce it, write down the artifact
that proves it, and file it. On this ship, finding a footgun is rank.

## 5. For the PrismML team specifically

- **The integration surface you own:** `POST /generate` on the image studio.
  This repo's client normalizes b64 / url / blob response shapes
  (`web/index.html`, search `normalize`) — if you stabilize the shape, say so
  in your README and we'll pin it.
- **What your models are doing here:** the 1.7B is the writer *and* the judge
  *and* the art director (scene JSON) — three roles, one 590MB file, because
  grammar pinning makes each role contract-bound.
- **What we'd upstream if you asked:** the QoS footgun note for your docs
  (llama-server in background QoS halves throughput — `ps -o stat`, look for
  `N`), and the bedtime rubric as a worked example of LLM-as-judge on a 1.7B.

## 6. Performance truth table (measured, not vibed)

| Thing | Number | Conditions |
|---|---|---|
| Time to first word | 0.16–0.21s | M4 Pro, F16 + Metal, warm server |
| Generation | 62 tok/s busy box · 125.8 quiet box | same hardware, honest range |
| Branch continuation | ~0.2s | child taps a choice → next page streams |
| Illustration 512² | 5.78s | Bonsai Image 4B ternary, M4 Pro, per PrismML's card |
| Whole studio on disk | < 2GB writer+illustrator (transformer); ~4.5GB with full image payload | |

## 7. Prove you live here

Run the initiation ritual end-to-end: one new seed, one generated story, one
judge verdict ≥ 0.7 with the sleep gate passing. When your seed's `truth` note
survives a skeptical adult asking "really?" — you're a member.
