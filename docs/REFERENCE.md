# Reference

Precise, complete, and boring on purpose. If a knob, port, schema, or failure
mode exists in this system, it is on this page. For narrative, see
[BONSAI_101.md](../BONSAI_101.md); for mechanics, [UNDER_THE_HOOD.md](UNDER_THE_HOOD.md).

## 1. Processes and ports

| Process | Port | Required | Started by | Health check |
|---|---|---|---|---|
| `llama-server` (writer + judge) | 8080 | yes | you, in a terminal | `curl :8080/health` → `{"status":"ok"}` |
| Bonsai-Image-Demo backend (illustrator) | 8800 | no | `BACKEND_PORT=8800 ./scripts/serve.sh` in their repo | `curl :8800/backends` → `"healthy":true` |
| Night Library server | 8400 | yes | `./scripts/serve.sh` here | `curl :8400/web/` → 200 |

Port conflicts: the image studio defaults to **:8000**, which collides with
common dev servers — always start it with `BACKEND_PORT=8800`. Override the
library's expectations with the environment variables below.

## 2. Configuration

### scripts/serve.py (environment variables)

| Variable | Default | Effect |
|---|---|---|
| `PORT` | `8400` | library's listen port |
| `STUDIO_URL` | `http://127.0.0.1:8800` | where `/illustrate` forwards |

### web/index.html (constants, top of the script block)

| Constant | Default | Effect |
|---|---|---|
| `WRITER` | `http://127.0.0.1:8080` | llama-server base URL (browser-direct; CORS is open on llama-server) |
| `SAMPLING` | `temp .5 · top_k 20 · top_p .85 · repeat_penalty 1.05 (last 64)` | model-card sampling. **Do not raise `repeat_penalty`**: at 1.15 it amputates multi-token proper nouns on second mention ("Hanuman" → "Han") |
| `READ_WPS` | `2.6` | the reading metronome, words/second. The "ahead" meter is `(genWords − litWords) / READ_WPS` |
| beat budget | `max_tokens: 220` | one beat ≈ 90–120 words |
| story length | `6` beats max, or "wind down" | then the closing beat + truth note |

## 3. HTTP surface

### What the page calls

| Call | Where | Contract |
|---|---|---|
| `POST {WRITER}/v1/chat/completions` (stream) | browser → llama-server | OpenAI-compatible SSE; deltas in `choices[0].delta.content` |
| `POST {WRITER}/v1/chat/completions` (json_schema) | browser → llama-server | `response_format: {type:"json_schema", json_schema:{name, schema}}`; llama-server compiles the schema to GBNF and masks the sampler |
| `POST /illustrate` | browser → serve.py | same-origin; body forwarded verbatim to the studio; returns raw `image/png`, or `503` when the studio is down |

### The image studio's `/generate` (verified against its live OpenAPI)

Request (JSON): `prompt` (string, required) · `seed` (int, 42) · `steps`
(int, 4 — the model is designed for exactly 4) · `guidance` (float, 1.0) ·
`width`/`height` (int, 512; multiples of 32) · `backend` (enum, optional).
Response: **raw `image/png` bytes** — not JSON, not base64.

**Why the proxy exists:** the studio's FastAPI sends no
`Access-Control-Allow-Origin` header, so a browser on any other origin fails
CORS preflight. Server-to-server HTTP has no CORS, so `serve.py` forwards.
(Upstream fix: a `CORSMiddleware` PR to Bonsai-Image-Demo would make the proxy
optional; until then it is load-bearing.)

## 4. Schemas (grammar-pinned at decode time)

### Scene — drives both painters

```json
{ "time":  "dusk|night|starlit|moonlit|dawn|golden",
  "mood":  "wonder|courage|calm|triumph|mischief|dream",
  "focus": "string (4–60 chars)",
  "image_prompt": "string (30–220 chars)" }
```

### Branches — the child's two choices

```json
{ "a": "string (8–70 chars)", "b": "string (8–70 chars)" }
```

### Judgment — `studio/judge.py`

Five dimensions (`imagination_spark`, `resilience_modeled`,
`pride_in_humanity`, `wonder_to_sleep_arc`, `truth_anchor`), each `number 0–1`,
plus `strongest_moment` and `revision_note` (strings, 10–200 chars).
Composite = mean; `wonder_to_sleep_arc ≥ 0.6` is an absolute gate.

### Canon seed — `canon/canon.json`

| Field | Type | Notes |
|---|---|---|
| `id` | string | snake_case, stable, used by the judge's `--seed` |
| `title` | string | the bedtime title, not the academic one |
| `civilization`, `era` | string | shown on the card |
| `values` | string[] | 2–3; woven by showing, never preached |
| `hook` | string | one sentence; becomes the first beat's instruction |
| `truth` | string | the honest historical note — cite what's real, name what's myth |
| `cast` | string | **full names with roles.** The system prompt instructs the model to copy these exactly; small models copy from context far more reliably than they recall from weights |

## 5. Sampling notes (hard-won)

| Setting | Value | Why |
|---|---|---|
| `temperature` / `top_k` / `top_p` | 0.5 / 20 / 0.85 | the model card's recommendation; defaults drift |
| `repeat_penalty` | 1.05, window 64 | loop prevention without name amputation (see §2) |
| dialogue | narration preferred, quotes tolerated | the prompt asks for reported speech; the 1.7B partially complies. Well-formed quotes are fine; the historical "broken quotes" artifact was a *renderer* bug (below), not a model fault |

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `CORS policy: No 'Access-Control-Allow-Origin'` calling `:8800` | the image studio sends no CORS headers | use the library's `/illustrate` proxy (default since v0.2); never call `:8800` from the browser |
| Words truncated mid-word, periods missing ("Gilgamesh" → "Gil") | **fixed in v0.2** — the streaming renderer appended only new word indices; tokens that *extended* the last word (and their punctuation) were dropped | update; the renderer now refreshes the last span on every delta |
| Names shortened on *second* mention only | `repeat_penalty` too high penalizes a name's tokens after first use | keep ≤ 1.05 |
| tok/s far below benchmark | llama-server in macOS **background QoS** (launched via nohup/launchd/CI) | launch from a normal terminal; check `ps -o stat -p <pid>` for the `N` flag (footgun #16) |
| Image studio setup fails at "Metal toolchain" | mlx JIT-compiles kernels; needs full Xcode + Metal Toolchain | `xcodebuild -downloadComponent MetalToolchain` |
| First illustration takes 20–30s, then ~6–11s | kernel compilation on first render | expected; the proxy budgets 120s, the page 90s |
| `/illustrate` → 503 | studio not running / wrong port | `BACKEND_PORT=8800 ./scripts/serve.sh` in Bonsai-Image-Demo; or set `STUDIO_URL` |
| Stale app after editing `web/` | browser heuristic-caches the shell | serve.py sends `Cache-Control: no-store` for `/illustrate` only; hard-reload the page (no SW here by design) |
| Story repeats its own first paragraph | `repeat_penalty` removed entirely | restore 1.05/64; the forward-motion prompt rule needs the floor |
