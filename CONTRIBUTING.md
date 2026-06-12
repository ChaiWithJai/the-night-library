# Contributing

This library accepts two kinds of gifts: **stories** and **repairs**. Both are
judged by artifacts, not status — the same standard the whole Bonsai field
study runs on: *fluent intel is not verified intel.*

## Contributing a story (the initiation)

Your first contribution here should be a seed — a story your civilization
tells its children. That's deliberate: it's the contribution that makes the
library more itself.

**Standards a seed must meet:**

1. **Complete schema** — every field in
   [docs/REFERENCE.md §4](docs/REFERENCE.md#4-schemas-grammar-pinned-at-decode-time),
   especially `cast` (full names with roles — this is load-bearing, see the
   reference) and `truth`.
2. **An honest truth note.** Cite what is historical; name what is myth.
   Myths are canon — Anansi sits beside Apollo 13 as an equal — but lying
   about which is which fails review. If your note can't survive a skeptical
   adult asking *"really?"*, sharpen it.
3. **Respect for the source.** Stories belong to the civilizations that first
   told them. Use the tradition's own names (the `cast` field enforces this
   mechanically), don't flatten heroes into generic superheroes, and if the
   story is living and sacred to a people, represent it the way they tell it.
4. **The judge's verdict, in the PR.** Generate a story from your seed in the
   app, save the text, run
   `python3 studio/judge.py story.txt --seed your_id`, and paste the JSON
   into the PR description. **Composite ≥ 0.7, sleep gate PASS.** The rubric,
   not a maintainer's taste, is the gatekeeper — that's what keeps the canon
   honest as it grows.

## Contributing a repair

- **Bugs:** file with a reproduction — the artifact that proves it. The
  best bug reports in this project's history were screenshots with one
  sentence ("note how the periods don't show" found a renderer bug that had
  been silently amputating every word-final token).
- **Footguns:** verified adoption traps (yours or upstream's) are
  first-class contributions. Reproduce, document the artifact, file. The
  ledger lives at
  [the-little-tree-thinks](https://github.com/ChaiWithJai/the-little-tree-thinks).
- **Code:** one file, no build step, stdlib only is the covenant — for the
  web app *and* the server. A dependency needs to pay rent a paragraph of
  justification can cover. View-source is a feature; keep the whole system
  readable in one sitting.

## Workflow

Branch → PR → merge. No direct pushes to `main`. PR descriptions state what
was verified and how — "it works" is a claim; a command, an output, or a
screenshot is evidence. Conventional-commit style titles
(`feat:`, `fix:`, `docs:`).

## Tone

Write docs the way the existing ones are written: precise about numbers,
honest about limitations (the 1.7B's wobbles are documented, not hidden),
and warm without being cute. If a sentence wouldn't survive being read aloud
at bedtime or in a code review, revise until it would survive both.
