import requests
from bs4 import BeautifulSoup
from requests.models import HTTPError

SCOREBOARD_URL = "https://www.cs.mcgill.ca/~cs520/scoreboard/"


Total, Passed = int, int
Alias, AliasLink = str, str
PassedTests = str
GenerationTime = str
Scoreboard = tuple[GenerationTime, list[tuple[Alias, AliasLink, PassedTests]]]


def get_scoreboard() -> Scoreboard:
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    scoreboard_res = requests.get(SCOREBOARD_URL, headers=headers)
    if scoreboard_res.status_code != 200:
        return HTTPError(scoreboard_res.text), None

    soup = BeautifulSoup(scoreboard_res.text)

    generated_time = (
        soup.find("h2", class_="page-header")
        .find_next_sibling(string=True)
        .strip("() ")
        .lstrip("generated ")
        .rstrip()
        .rstrip(")")
    )
    result_table = soup.find("table", {"id": "resultTable"})

    # Extract table rows
    rows = result_table.find_all("tr")[1:]  # Skipping header row

    results = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            alias = cols[0].get_text(strip=True)
            link = cols[0].find("a")
            href = link["href"] if link else None
            if href:
                href = SCOREBOARD_URL + href
            passed_tests = cols[1].get_text(strip=True)

            results.append((alias, href, passed_tests))

    return None, (generated_time, results)
