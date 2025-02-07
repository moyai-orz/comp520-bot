from typing import List, Optional, Tuple, TypeAlias, cast

import requests
from bs4 import BeautifulSoup, Tag
from requests.models import HTTPError

SCOREBOARD_URL = "https://www.cs.mcgill.ca/~cs520/scoreboard/"

Total: TypeAlias = int
Passed: TypeAlias = int
Alias: TypeAlias = str
AliasLink: TypeAlias = Optional[str]
PassedTests: TypeAlias = str
GenerationTime: TypeAlias = str

Scoreboard: TypeAlias = Tuple[
    GenerationTime, List[Tuple[Alias, AliasLink, PassedTests]]
]


def get_scoreboard() -> Tuple[Optional[HTTPError], Optional[Scoreboard]]:
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    scoreboard_res = requests.get(SCOREBOARD_URL, headers=headers)

    if scoreboard_res.status_code != 200:
        return HTTPError(scoreboard_res.text), None

    soup = BeautifulSoup(scoreboard_res.text, "html.parser")
    header = soup.find("h2", class_="page-header")

    if not header:
        return HTTPError("Could not find page header"), None

    next_sibling = header.find_next_sibling(string=True)

    if not next_sibling:
        return HTTPError("Could not find generation time"), None

    generated_time = (
        str(next_sibling).strip("() ").lstrip("generated ").rstrip().rstrip(")")
    )

    result_table = soup.find("table", {"id": "resultTable"})

    if not result_table:
        return HTTPError("Could not find result table"), None

    result_table = cast(Tag, result_table)
    rows = result_table.find_all("tr")[1:]
    results: List[Tuple[Alias, AliasLink, PassedTests]] = []

    for row in rows:
        if isinstance(row, Tag):
            cols = row.find_all("td")
            if len(cols) == 2:
                alias = cols[0].get_text(strip=True)
                link = cols[0].find("a")
                href: Optional[str] = link["href"] if link else None
                if href:
                    href = SCOREBOARD_URL + href
                passed_tests = cols[1].get_text(strip=True)
                results.append((alias, href, passed_tests))

    return None, (generated_time, results)
