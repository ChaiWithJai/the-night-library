# Demo Runbook

How to demo the Night Library to a room, a founder, or a stranger — with the
exact choreography, the talking points that land, and the recovery moves for
everything that can go wrong on stage.

**Time budget:** 4 minutes for the short form, 8 for the full arc.

## Pre-flight (do this before anyone is watching)

```bash
# 1. Writer — from a NORMAL terminal (not nohup/launchd: background QoS
#    halves throughput — footgun #16)
llama-server -m Ternary-Bonsai-1.7B-F16.gguf --port 8080 -ngl 99

# 2. Illustrator (optional but worth it)
cd Bonsai-Image-Demo && BACKEND_PORT=8800 ./scripts/serve.sh

# 3. Library
cd the-night-library && ./scripts/serve.sh
```

Checklist — all three must pass or fix before you start:

- [ ] `curl -s :8080/health` → `ok`
- [ ] `curl -s :8800/backends` → `"healthy":true` (skip if no illustrator)
- [ ] **Warm the illustrator** — first render compiles kernels (20–30s); fire
  one throwaway: `curl -s -X POST :8400/illustrate -H 'Content-Type: application/json' -d '{"prompt":"warmup","steps":4}' -o /dev/null`
- [ ] Open `http://127.0.0.1:8400/web/`, full screen, phone-ish window width
- [ ] Wi-Fi OFF if you want the kill shot (everything keeps working)

## The choreography (beat by beat)

**1. The shelf (15s).** Library screen up. Say: *"Twelve stories from twelve
civilizations — Gilgamesh to Apollo 13. Every one carries a truth note for
when the kid asks 'did that really happen?'"*

**2. Pick one and shut up (20s).** Tap a card. Let them watch the page fill
with faint ink while the first words light up. This sells itself; resist
narrating over it.

**3. The meter (30s).** Point at the top bar: *"Blue is the model writing —
sixty to a hundred-plus tokens a second. Gold is a parent reading aloud.
The story is finished about thirty seconds before your voice gets there.
That faint text? Already written. You're watching intelligence density."*

**4. The interrupt (30s).** When the choices appear, hand over the input:
*"You pick."* When the next page starts streaming in ~0.2s: *"That's the
whole thesis. A child's attention forgives three seconds. The cloud spends
that on the network before any model runs. This never leaves the machine —
there is no network."*

**5. The painter (45s).** When the illustration swaps in, tap the chip:
*"Bonsai Image 4B — a 1.2-gigabyte diffusion model, running on this Mac,
about six seconds a frame warm. The same model runs on an iPhone in nine."*

**6. The kill shot (20s, optional, rehearse it once).** Toggle Wi-Fi off
mid-story. Keep going. *"Writer, illustrator, judge — under two gigabytes,
zero cloud. Bedtime doesn't need the internet."*

**7. Land it (15s).** Wind the story down; let the goodnight line and the
truth note appear. *"And it ends true: the Epic of Gilgamesh really is the
oldest story we have. The kid inherits that."*

## Recovery moves

| On-stage failure | Move |
|---|---|
| Illustration pane shows "dream canvas" | Say: *"that's the fallback painter — the diffusion model is optional"* and keep going. It's a feature; treat it as one. Check `:8800` after. |
| Story stalls mid-beat | Writer died or port clash. The beat ends quietly by design. Restart llama-server; tap a choice — context rebuilds from the page. |
| tok/s reads low | You launched the writer via nohup/automation. Confess footgun #16 — *"macOS quietly throttles background processes; even the loading dock gets inspected on this project"* — it's a better story than the benchmark. |
| Browser shows a stale layout | Hard reload. No service worker exists here, so one reload always wins. |

## Reset between demos

```bash
# fresh meter + fresh story state: just reload the page.
# fresh illustrations (new compositions): the seed is per-page-load already.
```

Nothing persists server-side. The library forgets every visitor — that's the
privacy story, demonstrated by the reset being a reload.
