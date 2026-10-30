"""Adaptive, deterministic baseline agent for ARC-AGI-3.

Design goals:
- legal-action aware: never emit an action outside the current action space;
- information efficient: probe simple controls before spending coordinate actions;
- reproducible: stable per-game RNG and bounded action budget;
- competition safe: no filesystem/network/model dependencies at decision time.

This is a baseline, not a claim of human-level generalization. The intended
next step is to add game-family-specific policies behind the same interface.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


class MyAgent(Agent):
    """Budgeted adaptive exploration with deterministic replay behavior."""

    MAX_ACTIONS = 240
    PROBE_PERIOD = 6

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        digest = hashlib.sha256(self.game_id.encode("utf-8")).digest()
        self._rng = random.Random(int.from_bytes(digest[:8], "big"))
        self._turn = 0
        self._seen_action_names: set[str] = set()
        self._frame_signatures: set[str] = set()
        self._stagnant_steps = 0
        self._last_signature = ""

    @property
    def name(self) -> str:
        return f"{super().name}.adaptive240"

    @staticmethod
    def _signature(frame: FrameData) -> str:
        """Use stable public frame fields without assuming a game-specific schema."""
        parts: list[str] = []
        for attr in ("state", "levels_completed", "available_actions", "frame_data"):
            value = getattr(frame, attr, None)
            parts.append(repr(value))
        return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()

    @staticmethod
    def _legal_actions(latest_frame: FrameData) -> list[GameAction]:
        raw = getattr(latest_frame, "available_actions", None)
        if raw:
            legal = [a for a in raw if isinstance(a, GameAction)]
            if legal:
                return legal
        return [a for a in GameAction if a is not GameAction.RESET]

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET

        signature = self._signature(latest_frame)
        if signature == self._last_signature:
            self._stagnant_steps += 1
        else:
            self._stagnant_steps = 0
        self._last_signature = signature
        self._frame_signatures.add(signature)

        legal = self._legal_actions(latest_frame)
        legal = [a for a in legal if a is not GameAction.RESET] or [GameAction.ACTION1]

        # Cover each currently legal simple action once. This is more
        # informative than random sampling and works across unknown games.
        unseen = [
            a for a in legal
            if not a.is_complex() and a.name not in self._seen_action_names
        ]
        if unseen:
            action = unseen[0]
        else:
            simple = [a for a in legal if not a.is_complex()]
            complex_actions = [a for a in legal if a.is_complex()]
            # Coordinate actions discover clickable targets, but do not
            # dominate the budget when no visual parser is available.
            if complex_actions and self._turn % self.PROBE_PERIOD == self.PROBE_PERIOD - 1:
                action = complex_actions[0]
            elif simple:
                action = self._rng.choice(simple)
            else:
                action = self._rng.choice(legal)

        self._turn += 1
        self._seen_action_names.add(action.name)
        if action.is_complex():
            # Deterministic board probes over the documented 64x64 range.
            k = self._turn
            x = (17 * k + 11 * (k // 4)) % 64
            y = (29 * k + 7 * (k // 3)) % 64
            action.set_data({"x": int(x), "y": int(y)})
            action.reasoning = {
                "policy": "systematic_coordinate_probe",
                "x": int(x),
                "y": int(y),
            }
        else:
            action.reasoning = {
                "policy": "legal_action_coverage",
                "turn": self._turn,
                "stagnant_steps": self._stagnant_steps,
            }
        return action
