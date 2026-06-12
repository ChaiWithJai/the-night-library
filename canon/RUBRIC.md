# The Bedtime Benchmark — what "the best bedtime story in civilization" means

Most story benchmarks measure fluency. Bedtime has a different job description:
the listener should fall asleep braver, kinder, and prouder of being human than
they woke up. Five dimensions, scored 0–1:

| Dimension | The question it asks |
|---|---|
| **Imagination spark** | Did it open a door the child will keep walking through after the lights are out — an image, a "what if" they'll retell tomorrow? |
| **Resilience modeled** | Does someone in the story meet difficulty and *do something about it* — visibly, repeatably, without magic doing all the work? |
| **Pride in humanity** | Does the child inherit something true about what people have done — a civilization, an inventor, a kindness — that makes "we" feel bigger? |
| **Wonder-to-sleep arc** | Does the energy curve *descend*? Excitement early, warmth late, a last line you can whisper. A great story that ends loud is a failed bedtime story. |
| **Truth anchor** | Does it honor its source? The canon note ("tell them it's true") must survive the retelling — no flattening Hanuman into a generic superhero. |

**Composite = mean of the five.** A story below 0.6 on *wonder-to-sleep* fails
regardless of composite — that gate is absolute, because the job is sleep.

## How scoring runs

`studio/judge.py` asks Bonsai itself to score each story — with the judgment
schema **grammar-pinned at decode time**, the same trick this stack uses
everywhere: the model is not asked to be reliable, it is *constrained* to be.

```bash
python3 studio/judge.py story.txt --seed gilgamesh_enkidu
```

This is deliberately lightweight. The rubric's real job isn't leaderboards —
it's keeping the canon honest as it grows: every new seed and every prompt
change answers to the same five questions.
