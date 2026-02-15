from enum import StrEnum
from fastapi import Depends
from models.race import PcsRace, RaceCategory
from models.result import PcsResult
from repositories.base_repository import BaseRepository, get_base_repository
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from bs4 import BeautifulSoup
import re


class RaceClass(StrEnum):
    WORLD_TOUR = "1.UWT"
    PRO_SERIES = "1.Pro"


class RaceCircuit(StrEnum):
    WORLD_TOUR = "1"
    PRO_SERIES = "26"


class PcsService:
    def __init__(self, repository: BaseRepository = Depends(get_base_repository)):
        self.repository = repository

    async def fetch_startlist(self, pcs_path: str, year: int) -> list[str]:
        url = f"https://www.procyclingstats.com/race/{pcs_path}/{year}/startlist"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        rider_names = []
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                # The startlist is usually in a UL with class 'startlist_v4'
                startlist_ul = soup.find("ul", class_="startlist_v4")
                if not startlist_ul:
                    print("No startlist found (ul.startlist_v4 missing).")
                    return []

                # Each team is an LI in the top UL.
                # Inside each team LI, there is a UL of riders.
                # Riders are LIs inside that nested UL.
                # Structure: ul.startlist_v4 > li > div.ridersCont > ul > li > a (name)

                riders_conts = startlist_ul.find_all("div", class_="ridersCont")
                for cont in riders_conts:
                    rider_ul = cont.find("ul")
                    if not rider_ul:
                        continue

                    for rider_li in rider_ul.find_all("li"):
                        # Name is usually in an anchor tag
                        a_tag = rider_li.find("a")
                        if a_tag:
                            rider_names.append(a_tag.text.strip())

                return rider_names

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e.response.status_code}")
                return []
            except Exception as e:
                print(f"An error occurred: {e}")
                return []

    async def fetch_race_results(self, pcs_path: str, year: int) -> list[PcsResult]:
        base_url = "https://www.procyclingstats.com/race"
        url = f"{base_url}/{pcs_path}/{year}/result"
        print(url)
        result: list[PcsResult] = []

        # PCS often blocks scripts without a User-Agent, so we mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                # Await the response
                response = await client.get(url)
                response.raise_for_status()  # Raises an error for 4xx/5xx codes

                # Parsing is CPU-bound (sync), but fast enough here to keep in the loop
                soup = BeautifulSoup(response.content, "html.parser")

                # Find the results table (usually the first table on the page)
                table = soup.find("table")

                if not table:
                    print("No table found.")
                    return

                # Extract rows
                rows = table.find_all("tr")

                # Print Header
                print(f"{'Pos':<5} {'Rider':<30} {'Team':<25}")
                print("-" * 60)

                for row in rows:
                    cols = row.find_all("td")

                    # Ensure it's a data row (rank is usually the first column)
                    if len(cols) > 2:
                        position = cols[0].text.strip()

                        # Rider Name (usually col 5 in the HTML structure of PCS)
                        # We look for the anchor tag <a> inside to get the clean name
                        rider_cell = cols[5]  # Adjust index if PCS changes layout
                        rider_name = (
                            rider_cell.find("a").text.strip()
                            if rider_cell.find("a")
                            else rider_cell.text.strip()
                        )

                        # Team Name (usually col 6)
                        team_cell = cols[6]
                        team_name = (
                            team_cell.find("a").text.strip()
                            if team_cell.find("a")
                            else team_cell.text.strip()
                        )

                        pos = int(position) if position.isdigit() else None
                        info = str(position) if not position.isdigit() else None
                        result.append(
                            PcsResult(
                                position=pos,
                                cyclist_name=rider_name,
                                team_name=team_name,
                                info=info,
                            )
                        )

                return result

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e.response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")

    async def fetch_races_list(
        self, year: int, circuit: int, cls: str
    ) -> list[PcsRace]:
        url = f"https://www.procyclingstats.com/races.php?s=&year={year}&circuit={circuit}&class={cls}&filter=Filter"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        races = []
        async with httpx.AsyncClient(
            headers=headers, follow_redirects=True, timeout=30.0
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            # Iterate over table rows; fallback to any <a> that looks like a race link
            for tr in soup.select("table tr"):
                a = tr.find("a", href=True)
                if not a:
                    continue
                href = a["href"]

                # normalize relative hrefs to start with '/'
                if not href.startswith("http"):
                    if not href.startswith("/"):
                        href = "/" + href

                # Only accept canonical race links whose path starts with /race or /races/<slug>
                m_path = re.search(r"^/(?:race|races)/([A-Za-z0-9\-_%]+)", href, re.I)
                if not m_path:
                    # skip non-race links (e.g. /calendar/races-database)
                    continue

                name = a.get_text(strip=True)
                abs_url = (
                    href
                    if href.startswith("http")
                    else f"https://www.procyclingstats.com{href}"
                )

                # extract PCS path/slug from the href, e.g. 'liege-bastogne-liege'
                pcs_path = m_path.group(1).rstrip("/") if m_path else None

                # Prefer explicit td with class 'cu500' which contains the date on PCS
                date = None
                date_td = tr.find("td", class_="cu500")
                if date_td and date_td.text:
                    date = date_td.get_text(" ", strip=True)

                # fallback: look for <time> or nearby td text (older layouts)
                if not date:
                    time_tag = tr.find("time")
                    if time_tag and time_tag.text:
                        date = time_tag.text.strip()

                parent_td = a.find_parent("td")
                if not date and parent_td:
                    # check the next sibling td (often date/class)
                    next_td = parent_td.find_next_sibling("td")
                    if next_td and next_td.text:
                        date_txt = next_td.get_text(" ", strip=True)
                        if date_txt:
                            date = date_txt

                # final fallback: regex on row text
                if not date:
                    row_text = tr.get_text(" ", strip=True)
                    m = re.search(
                        r"\b(\d{1,2}\s+[A-Za-zéûôç'-]{3,}\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b",
                        row_text,
                        re.I,
                    )
                    date = m.group(1) if m else None

                # if date is in DD.MM format (e.g. '31.08'), convert to datetime with given year and 09:00
                if date:
                    ddmm = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\s*$", date)
                    if ddmm:
                        try:
                            d = int(ddmm.group(1))
                            mo = int(ddmm.group(2))
                            date = datetime(
                                year, mo, d, 9, 0, tzinfo=ZoneInfo("Europe/Brussels")
                            )
                        except Exception:
                            # leave raw string if conversion fails
                            pass

                # try to extract race class/category from adjacent cells or row text
                race_class = None
                if parent_td:
                    sibling = parent_td.find_next_sibling("td")
                    for _ in range(2):
                        if not sibling:
                            break
                        stext = sibling.get_text(" ", strip=True)
                        cm = re.search(
                            r"\b(1\.UWT|1\.Pro|1\.HC|1\.1|1\.2|2\.1|2\.2|HC|UWT|Pro)\b",
                            stext,
                            re.I,
                        )
                        if cm:
                            race_class = cm.group(1)
                            break
                        sibling = sibling.find_next_sibling("td")
                if not race_class:
                    row_text = tr.get_text(" ", strip=True)
                    cm = re.search(
                        r"\b(1\.UWT|1\.Pro|1\.HC|1\.1|1\.2|2\.1|2\.2|HC|UWT|Pro)\b",
                        row_text,
                        re.I,
                    )
                    race_class = cm.group(1) if cm else None

                cat = (
                    RaceCategory.WORLD_TOUR
                    if race_class == RaceCircuit.WORLD_TOUR
                    else RaceCategory.OTHER
                )

                race = PcsRace(
                    name=name,
                    start_timestamp=date,
                    year=year,
                    category=cat,
                    pcs_path=pcs_path,
                )

                races.append(race)

            # fallback: if table parsing returned nothing, scan all links on the page
            if not races:
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if not href.startswith("http") and not href.startswith("/"):
                        href = "/" + href

                    m_path = re.search(
                        r"^/(?:race|races)/([A-Za-z0-9\-_%]+)", href, re.I
                    )
                    if not m_path:
                        continue

                    name = a.get_text(strip=True)
                    abs_url = (
                        href
                        if href.startswith("http")
                        else f"https://www.procyclingstats.com{href}"
                    )
                    pcs_path = m_path.group(1).rstrip("/") if m_path else None

                    # attempt to find a raw date string and race class nearby for fallback links
                    date = None
                    parent_td = a.find_parent("td")
                    if parent_td:
                        txt = parent_td.get_text(" ", strip=True)
                        m = re.search(
                            r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b",
                            txt,
                            re.I,
                        )
                        if m:
                            date = m.group(1)

                    # if this is DD.MM in fallback, convert to timezone-aware datetime
                    if date:
                        ddmm = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\s*$", date)
                        if ddmm:
                            try:
                                d = int(ddmm.group(1))
                                mo = int(ddmm.group(2))
                                date = datetime(
                                    year,
                                    mo,
                                    d,
                                    9,
                                    0,
                                    tzinfo=ZoneInfo("Europe/Brussels"),
                                )
                            except Exception:
                                pass

                    race_class = None
                    if parent_td:
                        sibling = parent_td.find_next_sibling("td")
                        for _ in range(2):
                            if not sibling:
                                break
                            stext = sibling.get_text(" ", strip=True)
                            cm = re.search(
                                r"\b(1\.UWT|1\.Pro|1\.HC|1\.1|1\.2|2\.1|2\.2|HC|UWT|Pro)\b",
                                stext,
                                re.I,
                            )
                            if cm:
                                race_class = cm.group(1)
                                break
                            sibling = sibling.find_next_sibling("td")
                    if not race_class:
                        parent_tr = a.find_parent("tr")
                        row_text = (
                            parent_tr.get_text(" ", strip=True) if parent_tr else ""
                        )
                        cm = re.search(
                            r"\b(1\.UWT|1\.Pro|1\.HC|1\.1|1\.2|2\.1|2\.2|HC|UWT|Pro)\b",
                            row_text,
                            re.I,
                        )
                        race_class = cm.group(1) if cm else None

                    cat = (
                        RaceCategory.WORLD_TOUR
                        if race_class == RaceCircuit.WORLD_TOUR
                        else RaceCategory.OTHER
                    )

                    race = PcsRace(
                        name=name,
                        start_timestamp=date,
                        year=year,
                        category=cat,
                        pcs_path=pcs_path,
                    )

                    races.append(race)

        return races


def get_pcs_service(
    repository: BaseRepository = Depends(get_base_repository),
) -> PcsService:
    return PcsService(repository)
