import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from .scoreboard import Scoreboard


@dataclass
class Update:
    alias: str
    new_score: str
    old_score: Optional[str]
    url: str


@dataclass
class State:
    generated_time: Optional[datetime]
    scores: Dict[str, str]

    @classmethod
    def from_dict(cls, data: dict, time_format: str) -> "State":
        time_str = data.get("generated_time")
        generated_time = datetime.strptime(time_str, time_format) if time_str else None
        return cls(generated_time=generated_time, scores=data.get("scores", {}))

    def to_dict(self, time_format: str) -> dict:
        return {
            "generated_time": (
                self.generated_time.strftime(time_format)
                if self.generated_time
                else None
            ),
            "scores": self.scores,
        }


class UpdateTracker:
    def __init__(
        self,
        scoreboard: Scoreboard,
        tracked_aliases: set[str],
        state_file: str | Path = ".scoreboard_state.json",
    ):
        self.scoreboard = scoreboard
        self.tracked_aliases = tracked_aliases
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> State:
        if not self.state_file.exists():
            return State(generated_time=None, scores={})

        try:
            with open(self.state_file) as f:
                data = json.load(f)
            return State.from_dict(data, self.scoreboard.TIME_FORMAT)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Failed to load state file: {e}")
            return State(generated_time=None, scores={})

    def _save_state(self) -> None:
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            temp_file = self.state_file.with_suffix(".tmp")
            state_dict = self.state.to_dict(self.scoreboard.TIME_FORMAT)

            with open(temp_file, "w") as f:
                json.dump(state_dict, f, indent=2)

            temp_file.replace(self.state_file)
        except OSError as e:
            print(f"Failed to save state file: {e}")

    def check_updates(self) -> list[Update]:
        self.scoreboard.refresh()

        current_time = self.scoreboard.generated_time

        if (
            self.state.generated_time is not None
            and current_time <= self.state.generated_time
        ):
            return []

        current_scores = {
            alias.name: alias.passed_tests for alias in self.scoreboard.aliases
        }

        updates: list[Update] = []

        for alias in self.tracked_aliases:
            if alias in current_scores:
                updates.append(
                    Update(
                        alias=alias,
                        old_score=self.state.scores.get(alias),
                        new_score=current_scores[alias],
                        url=f"{self.scoreboard.BASE_URL}{alias}_results.html",
                    )
                )

                self.state.scores[alias] = current_scores[alias]

        self.state.generated_time = current_time
        self._save_state()

        return updates
