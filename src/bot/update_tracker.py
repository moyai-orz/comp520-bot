import json
from dataclasses import dataclass
from pathlib import Path

from .scoreboard import Scoreboard


@dataclass
class Update:
    alias: str
    new_score: str
    old_score: str | None
    url: str


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
        self.previous_time = self._load_state()
        self.previous_scores: dict[str, str] = {}

    def _load_state(self) -> str | None:
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                return state.get("generated_time")
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading state file: {e}")
            return None

    def _save_state(self) -> None:
        try:
            state = {"generated_time": self.previous_time}

            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(state, f)

            temp_file.replace(self.state_file)
        except OSError as e:
            print(f"Error saving state file: {e}")

    def check_updates(self) -> list[Update]:
        self.scoreboard.refresh()

        if self.scoreboard.generated_time == self.previous_time:
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
                        old_score=self.previous_scores.get(alias),
                        new_score=current_scores[alias],
                        url=f"{self.scoreboard.BASE_URL}{alias}_results.html",
                    )
                )

                self.previous_scores[alias] = current_scores[alias]

        self.previous_time = self.scoreboard.generated_time
        self._save_state()

        return updates
