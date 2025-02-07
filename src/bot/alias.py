import typing as t
from dataclasses import dataclass


@dataclass
class Alias:
    name: str
    link: t.Optional[str]
    passed_tests: str

    def get_results_url(self, base_url: str) -> str:
        return f"{base_url}{self.name}_results.html"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alias):
            return NotImplemented
        return self.name == other.name and self.passed_tests == other.passed_tests
