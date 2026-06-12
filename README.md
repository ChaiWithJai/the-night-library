# The Night Library

*There is a library that only opens after dark. It has no shelves and no cloud.
It lives inside the machine on your desk — a writer the size of a photo album and a
painter the size of a home movie — and every night it writes your child a story that
has never existed before, faster than you can read it aloud.*

**A real-time, fully-local bedtime storyteller built on PrismML's Bonsai models** —
the 590MB Ternary-Bonsai-1.7B writes; the 1.2GB Bonsai Image 4B illustrates; nothing
your child says, chooses, or hears ever leaves the room.

<p>
  <img src="screenshots/night-03-library.png" width="270" alt="The canon — twelve stories from twelve civilizations"/>
  <img src="screenshots/night-01-story.png" width="270" alt="A story streaming under a procedural moonlit dreamscape, with the density meter live"/>
</p>

## Why this exists (the trailer for a bigger idea)

This demo is **Bonsai 101** — one cute application that makes *intelligence density*
legible:

- The meter at the top of the page shows two cursors: Bonsai writing (~63–125 tok/s)
  and a parent reading aloud (~2.6 words/s). The story is finished being written
  **~30× faster than it can be spoken** — so when your child grabs your arm and says
  *"no, she finds a TREASURE"*, the branch they chose starts streaming in **0.2 seconds**.
- That 0.2s is the whole thesis. A child's attention forgives about 3 seconds; a cloud
  round-trip spends most of that on the network before any model runs. Below the
  attention threshold, **new products exist** — and they fit on an iPhone.

The numbers, the SOTA compare/contrast, and the device math:
**[BONSAI_101.md](BONSAI_101.md)**.

## The canon

Twelve seeds in [`canon/canon.json`](canon/canon.json), one per civilization-sized
idea: Gilgamesh's friendship, Hanuman's leap, Anansi's pot, Māui's rope, Sequoyah's
letters, twelve seconds at Kitty Hawk, Ada's imagined engine, Apollo 13's arithmetic,
Ibn Battuta's curiosity, Wangari's thirty million trees, Hypatia's questions. Each
seed carries a **truth note** — so when your child asks *"did that really happen?"*,
the answer is ready, and it's *yes*.

What makes a bedtime story *the best in civilization* is a measurable claim here:
[`canon/RUBRIC.md`](canon/RUBRIC.md) defines five dimensions (imagination spark,
resilience modeled, pride in humanity, wonder-to-sleep arc, truth anchor) and
[`studio/judge.py`](studio/judge.py) scores any story against them — with the
judgment schema **grammar-pinned at decode time**, so even a 1.7B judge cannot
return malformed scores. The model isn't asked to be reliable; it is *constrained*
to be. (Sample run: composite 0.82, sleep gate PASS.)

## Run it tonight

```bash
# 1. The writer — stock Homebrew llama.cpp, no forks
brew install llama.cpp
llama-server -m Ternary-Bonsai-1.7B-F16.gguf --port 8080 -ngl 99
#   (model: huggingface.co/prism-ml/Ternary-Bonsai-1.7B-gguf)

# 2. The illustrator (optional) — PrismML's Bonsai Image studio
#    github.com/PrismML-Eng/Bonsai-Image-Demo
BACKEND_PORT=8800 ./scripts/serve.sh
#   Without it, the library paints a procedural "dream canvas" from Bonsai's
#   scene JSON — the page works either way, offline, forever.

# 3. The library
./scripts/serve.sh        # → http://127.0.0.1:8400/web/
```

Verified on an M4 Pro: **0.16s to first word**, 62–125 tok/s generation (machine-state
dependent), branch continuation in ~0.2s, illustrations at 512² in ~5.8s when the
image studio runs. A 1.7B writer has small-model wobbles — a dropped word here, a
bent quote mark there — and the README says so, because *fluent intel is not verified
intel*, including ours.

## One footgun, filed as always

Launching `llama-server` from a background/automation context (nohup, launchd, CI)
lands it in **macOS background QoS** — we measured prompt processing at 29 tok/s that
recovered to 128 tok/s at normal priority. If your tokens are slow, check
`ps -o stat -p <pid>` for the `N` flag before blaming the model.

---

*Part of the Bonsai field-study world — the footgun ledger, the chronicle, and the
case study live at
[the-little-tree-thinks](https://github.com/ChaiWithJai/the-little-tree-thinks).
Stories belong to the civilizations that first told them; this library just keeps
the night shift.*
