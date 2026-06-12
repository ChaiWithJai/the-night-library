# Extending the Library

Task-oriented recipes. Each one is complete — copy, follow, done. Schema
details live in [REFERENCE.md](REFERENCE.md); the *why* lives in
[UNDER_THE_HOOD.md](UNDER_THE_HOOD.md).

## Add a story to the canon

The canonical first contribution. Full ritual and standards:
[CONTRIBUTING.md](../CONTRIBUTING.md). The short version:

1. Add a seed object to `canon/canon.json` — every field in
   [REFERENCE.md §4](REFERENCE.md#4-schemas-grammar-pinned-at-decode-time),
   including **`cast` with full names**: the prompt makes the model copy
   names from context instead of recalling them, which is the difference
   between "Gilgamesh" and a 1.7B improvising "Gil".
2. Reload the page — the card appears; generate a story.
3. Judge it: `python3 studio/judge.py story.txt --seed your_id`
   (needs composite ≥ 0.7 and sleep gate PASS).

## Change the reading pace

`READ_WPS` in `web/index.html` (default 2.6 words/s — a calm adult read-aloud).
Lower for younger listeners; the "ahead" meter scales automatically
(`ahead = (genWords − litWords) / READ_WPS`). For silent-reading mode,
set 4.5–5.5.

## Point at a different writer

`WRITER` in `web/index.html`. Any OpenAI-compatible `/v1/chat/completions`
with SSE streaming works — another machine on your LAN
(`http://192.168.x.x:8080`), a bigger Bonsai, anything llama-server serves.
Two requirements: CORS open (llama-server default) and `json_schema` response
format support for the grammar-pinned calls. If you must use a server without
CORS, route it through `scripts/serve.py` the way `/illustrate` already does —
the pattern is ~25 lines.

## Swap or relocate the illustrator

`STUDIO_URL` env var on `scripts/serve.py`
(default `http://127.0.0.1:8800`):

```bash
STUDIO_URL=http://192.168.1.20:8800 ./scripts/serve.sh
```

Any backend satisfying the contract works: `POST /generate` with
`{prompt, seed, steps, width, height}` returning raw `image/png`. To adapt a
backend with a different shape, translate inside `serve.py`'s `do_POST` —
keep the page's contract stable and put adapters at the edge.

## Tune the illustration style

The style suffix is appended to every scene's `image_prompt` in
`illustrate()` (`web/index.html`): `"children's storybook illustration, soft
warm light, gentle, painterly"`. Change it once, every frame follows. Bonsai
Image 4B is designed for exactly 4 denoising steps — more steps don't help
(model card); spend your budget on resolution (`768×768` ≈ 2× the time of 512²).

## Add a dimension to the rubric

1. Define it in `canon/RUBRIC.md` — one row: the dimension and the question
   it asks.
2. Add the key to `DIMENSIONS` in `studio/judge.py`; the schema builds from
   that list, so the grammar updates itself.
3. Decide whether it gates (like `wonder_to_sleep_arc`) or merely averages —
   gates are for dimensions where failure invalidates the artifact's *job*,
   not just its quality.

## Reuse the two core patterns elsewhere

**Grammar-as-contract** (make a small model dependable): copy `askJSON()`
from `web/index.html` or `judge()` from `studio/judge.py`. The whole trick is
`response_format: {type: "json_schema", json_schema: {name, schema}}` on
llama-server — schema → GBNF → sampler mask. Enums for vocabularies,
`minLength` against lazy outputs, `additionalProperties: false` against
invention.

**Always-works degradation** (demos that can't die): render the cheap honest
version synchronously from the same data that feeds the expensive version,
then upgrade in place when the expensive one arrives — and label which one
the viewer is seeing (`#ill-chip`). The fallback must be *good enough to
ship*, or it's not a fallback, it's an apology.
