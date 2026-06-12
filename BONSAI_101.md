# Bonsai 101 — Intelligence Density, Explained With a Bedtime Story

*The big idea behind PrismML's models, why latency is the lock on a whole class of
products, and what becomes possible on the devices already in your house.*

## The one-sentence idea

**Intelligence density = how much capability fits in a byte.** PrismML trains and
compresses models to 1-bit and ternary weights — not as a lossy afterthought, but as
the design target — so that real models fit where models never fit before.

## The verified numbers (no marketing, we ran or sourced every one)

| Model | Size | Speed | Where measured |
|---|---|---|---|
| Ternary-Bonsai-1.7B (F16) | 3.2GB | **125.8 tok/s** | M4 Pro, stock llama.cpp + Metal — [our run](https://github.com/ChaiWithJai/the-little-tree-thinks) |
| Ternary-Bonsai-1.7B (TQ2_0) | **590MB** | 111 tok/s (CPU) | M4 Pro, mainline `llama-quantize` — our run |
| Bonsai Image 4B (ternary, MLX 2-bit) | **1.21–1.43GB** | 512² in **5.78s**, 1024² in 24.3s (4 steps) | M4 Pro — [model card](https://huggingface.co/prism-ml/bonsai-image-ternary-4B-mlx-2bit) |
| Bonsai Image 4B (1-bit) | **0.93GB** | — | first sub-1GB diffusion model that runs on iPhone |
| Bonsai Image 4B on **iPhone 17 Pro Max** | — | 512² in **9.4s** (MLX Swift) | model card |

The whole bedtime studio in this repo — a writer *and* an illustrator — is **under 2GB**.
A single photo from a modern phone camera is ~12MB; this is ~150 photos' worth of disk
that tells your child a new story every night, forever, for free.

## Compare/contrast with today's SOTA

| | Frontier cloud (GPT-class, FLUX.2 Pro-class) | Bonsai (this repo, tonight) |
|---|---|---|
| Peak quality | **Higher — this is real and we say so** | Good; tuned for its job |
| Time to first word | 300–900ms network + queue, *every turn* | **~100ms, no network exists** |
| Words per second vs. reading aloud | varies with load and connection | **125 tok/s ≈ 30× faster than a parent reads** |
| Cost per story | API metered, forever | **$0 marginal, Apache 2.0** |
| Offline (airplane, cabin, blackout) | no | **yes** |
| Where the child's voice and choices go | a datacenter | **nowhere — they never leave the device** |
| Fits on an iPhone | no (you ship a thin client) | **yes — the model itself** |

The honest framing: cloud frontier models win benchmarks. Density models win
**situations** — and most of family life is a situation, not a benchmark.

## Why latency is the unlock (the thesis of this demo)

A use case is "real-time" when **generation outruns consumption**:

- A parent reads aloud at ~2.6 words/sec. Bonsai writes at ~80–90 words/sec.
  The story is finished being written ~30× faster than it can be spoken —
  so the child can *change the story mid-telling* and the next page already exists.
- A child's attention forgives about 3 seconds. Cloud round-trips spend most of
  that budget on the network before the model even starts. On-device spends none.
- An illustration every story beat (~25s of telling) needs <25s generation.
  Bonsai Image does 512² in 5.78s on a Mac, 9.4s on an iPhone. **Real-time
  illustrated storytelling cleared the bar in May 2026** — that's what changed.

Latency isn't a nicer version of the same product. Below the attention threshold,
*new products exist*: the story that branches when the child interrupts; the
illustration that appears while the page is still being read; the bedside device
that needs no account, no wifi, no subscription.

## The device math

| Device | RAM | Writer (590MB) + Illustrator (1.2GB) | What it means |
|---|---|---|---|
| iPhone 17 | 8–12GB | fits with the OS to spare | the bedtime studio in a pocket |
| iPad / Mac | 8–64GB | trivial; Metal/MLX accelerated | this demo, today |
| A bedside speaker-class device | 4GB | the 1-bit line (0.93GB image, smaller text) | a storyteller with no cloud and no microphone leaving the room |

## Try it tonight

```bash
# the writer (terminal 1) — stock Homebrew llama.cpp
llama-server -m Ternary-Bonsai-1.7B-F16.gguf --port 8080 -ngl 99

# the illustrator (terminal 2, optional) — PrismML's image studio
# https://github.com/PrismML-Eng/Bonsai-Image-Demo  → BACKEND_PORT=8800 ./scripts/serve.sh

# the library (terminal 3)
./scripts/serve.sh   # then open http://127.0.0.1:8400/web/
```

*Every claim above has a source: our measured runs are chronicled in
[the-little-tree-thinks](https://github.com/ChaiWithJai/the-little-tree-thinks);
the image numbers are from PrismML's own model card. Fluent intel is not verified
intel — go check.*
