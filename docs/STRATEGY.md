# ARC-AGI-3 Strategy Memo

## Objective

Maximize the average game score under ARC-AGI-3's RHAE metric while respecting competition mode: one notebook, no internet during evaluation, one environment interaction per game, and a 9-hour notebook limit.

## What the metric rewards

RHAE scores completed levels by squared action efficiency relative to the upper-median human baseline. Later levels receive larger weights in the per-game average, and incomplete games have a hard ceiling based on the fraction of weighted levels completed. The strategic consequence is clear: a short, reliable path to later levels is worth more than spending a large budget over-exploring early levels.

## Recommended architecture

### 1. Perception and state memory

Store a compact history of frame metadata, available actions, level progress, and a hash of the public frame payload. Do not retain unbounded raw frames. A bounded history makes the agent stable under long games and keeps memory predictable.

### 2. Hypothesis manager

Maintain a small set of hypotheses about the game family: navigation, selection, toggle/puzzle, placement, and timing/action-sequence games. Update hypothesis confidence from state transitions rather than from a fixed game-name lookup. A hypothesis should predict which action is likely to produce progress and how much information it provides.

### 3. Information-efficient exploration

At the beginning of a level, test legal simple actions once. Prefer actions that have not been tested in the current state signature. Use ACTION6 only when it is available and the state suggests a clickable interaction. For coordinate actions, coarse-to-fine probing is preferable to independent random points.

### 4. Goal and progress detection

Use changes in `levels_completed`, state transitions, frame signatures, and action-space changes as progress signals. A successful policy should immediately switch from exploration to exploitation after a progress event.

### 5. Recovery

When a level reaches `GAME_OVER`, issue `RESET` as required by the API. Do not issue ordinary actions in the game-over state. Keep reset attempts bounded; repeated resets with no novel state should trigger a conservative stop rather than consuming the full action budget.

## Runtime plan

The baseline uses CPU because it performs no neural inference. The notebook installs only the offline competition wheel and `python-dotenv`, writes the agent into `/tmp`, and executes the official framework. This keeps the save-and-run-all path lightweight and avoids accidentally exposing implementation files as candidate output artifacts.

For a model-based agent, use a T4 first and profile wall-clock time. Reserve RTX 6000 for a measured workload that genuinely needs it. Always keep an action budget per game and a global wall-clock watchdog below nine hours.

## Iteration roadmap

1. Establish a non-zero, reproducible baseline on local games.
2. Add frame render parsing for one game family at a time.
3. Add deterministic policies for the highest-leverage families.
4. Measure completion and actions separately; optimize later-level completion before micro-optimizing easy levels.
5. Run one Kaggle phase-A validation notebook.
6. Submit to competition only after the phase-A notebook is complete and output contains the expected automatically generated artifact.

## Current blocker

The authenticated Kaggle account is not eligible to join this competition because the page reports that new entrants are not allowed after the October 26 entry deadline. This prevents an official competition submission from this account even though the final deadline is November 2. The local notebook and repository are prepared for an eligible account.

## References

- [1]: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3 "ARC Prize 2026 — ARC-AGI-3 Kaggle competition"
- [2]: https://arcprize.org/arc-agi/3 "ARC-AGI-3 benchmark overview"
- [3]: https://docs.arcprize.org/methodology.md "ARC-AGI-3 Scoring Methodology"
- [4]: https://docs.arcprize.org/toolkit/competition_mode "ARC-AGI-3 Competition Mode"
- [5]: https://docs.arcprize.org/actions.md "ARC-AGI-3 Actions"
- [6]: https://docs.arcprize.org/arc-prize-2026.md "ARC Prize 2026 local development starter"
- [7]: https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter "Official ARC-AGI-3 Kaggle Starter"
