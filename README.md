# ARC-AGI-3 Adaptive Agent

A reproducible, CPU-first baseline for Kaggle's **ARC Prize 2026 — ARC-AGI-3** code competition. It is built on the official ARC Prize Kaggle Starter and keeps the local agent, generated notebook, and Kaggle runtime in lock-step.

## Competition analysis

ARC-AGI-3 is an interactive reasoning benchmark. The agent must explore novel environments, infer useful state, set goals, plan actions, and adapt over multiple turns. It is not a static prediction task: Kaggle runs the notebook in competition mode and automatically generates the submission artifact from gameplay.

The metric is Relative Human Action Efficiency (RHAE). A completed level receives `(human_actions / agent_actions)^2`, capped at 1.15. Game scores are weighted by level number, and the final score averages game scores. Therefore, completing later levels and avoiding unnecessary actions are both important.

The competition requires notebook submissions, disables internet access during evaluation, and caps notebook runtime at 9 hours. The official starter recommends Python 3.12 and the `arc-agi` toolkit. This project uses CPU-only execution because the baseline has no model inference or GPU dependency; switching to T4 or RTX 6000 is a deliberate future optimization, not a requirement.

## Strategy

The baseline is intentionally conservative:

1. **Legal-action filtering.** Use the current frame's available actions whenever exposed, with a safe enum fallback.
2. **Action coverage.** Try each newly available simple action once before randomizing among familiar actions. This gives information about the interaction vocabulary without assuming that ACTION1 always means the same thing.
3. **Coordinate probing.** If ACTION6 is available, probe a deterministic sequence over the documented 64×64 board only periodically, so coordinate actions do not consume the full budget.
4. **State compression.** Hash stable public frame fields to track whether actions produce new state or stagnation.
5. **Reproducibility.** Seed exploration from the game ID and cap each game at 240 actions.
6. **Competition safety.** No internet, external model calls, filesystem dependencies, or hidden data are used in the decision loop.

This is a platform-valid baseline, not a claim of strong leaderboard performance. The next performance layer should add game-family policies and visual state parsers behind the same `Agent` interface. Those additions should be benchmarked locally before spending a Kaggle submission run.

## Local workflow

The official starter requires Python 3.12. With the starter dependencies and framework installed:

```bash
make setup
make list-games
make verify-local
make play-local GAME=ls20 STEPS=240
make notebook
```

The generated notebook is `notebooks/submission.ipynb`. It installs the offline competition wheel, writes the agent to a temporary path, waits for Kaggle's gateway sidecar during competition rerun, and runs the official framework to produce `submission.parquet`.

## Submission status

As of October 30, 2026, Kaggle shows **“New entrants are currently not allowed”** for this account because the entry deadline was October 26, 2026. The final submission deadline is November 2, 2026, but the account cannot join the competition after the entry cutoff. The notebook is nevertheless complete and ready for a participant who joined before the cutoff or for local evaluation and open-source collaboration.

## Sources

- [Kaggle competition page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)
- [ARC-AGI-3 overview](https://arcprize.org/arc-agi/3)
- [ARC Prize 2026 competition page](https://arcprize.org/competitions/2026/arc-agi-3)
- [Official toolkit overview](https://docs.arcprize.org/toolkit/overview)
- [Competition mode](https://docs.arcprize.org/toolkit/competition_mode)
- [Scoring methodology](https://docs.arcprize.org/methodology.md)
- [Official Kaggle Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter)
