import typing as t
from datetime import datetime
from functools import cached_property

import requests
from bs4 import BeautifulSoup, Tag

from .alias import Alias
from .error import FetchError, ParseError


class Scoreboard:
    BASE_URL: str = "https://www.cs.mcgill.ca/~cs520/scoreboard/"
    TIME_FORMAT: str = "%d/%m/%Y %H:%M:%S"

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

        self._soup = self._fetch()

    def _fetch(self) -> BeautifulSoup:
        try:
            res = self.session.get(self.BASE_URL)
            res.raise_for_status()
        except requests.RequestException as e:
            raise FetchError(f"Failed to fetch scoreboard: {e}")
        return BeautifulSoup(res.text, "html.parser")

    @cached_property
    def generated_time(self) -> datetime:
        try:
            header = self._soup.find("h2", class_="page-header")

            if not header:
                raise ParseError("Could not find page header")

            next_sibling = header.find_next_sibling(string=True)

            if not next_sibling:
                raise ParseError("Could not find generation time")

            return datetime.strptime(
                str(next_sibling)
                .strip("() ")
                .lstrip("generated ")
                .rstrip()
                .rstrip(")"),
                self.TIME_FORMAT,
            )
        except Exception as e:
            raise ParseError(f"Failed to parse generation time: {e}")

    @cached_property
    def aliases(self) -> list[Alias]:
        try:
            result_table = self._soup.find("table", {"id": "resultTable"})

            if not result_table:
                raise ParseError("Could not find result table")

            result_table = t.cast(Tag, result_table)
            rows = result_table.find_all("tr")[1:]
            aliases: list[Alias] = []

            for row in rows:
                if isinstance(row, Tag):
                    cols = row.find_all("td")
                    if len(cols) == 2:
                        name = cols[0].get_text(strip=True)
                        link = cols[0].find("a")
                        href: t.Optional[str] = link["href"] if link else None
                        if href:
                            href = self.BASE_URL + href
                        passed_tests = cols[1].get_text(strip=True)
                        aliases.append(Alias(name, href, passed_tests))

            return aliases
        except Exception as e:
            raise ParseError(f"Failed to parse aliases: {e}")

    def refresh(self) -> None:
        properties = ["generated_time", "aliases"]

        for property in properties:
            del self.__dict__[property]

        self._soup = self._fetch()
