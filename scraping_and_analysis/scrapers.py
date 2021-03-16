from bs4 import BeautifulSoup
import requests
from retrying import retry
import pandas as pd
import re

ranking_page = "https://firstcycling.com/ranking.php?k=fc&rank={}&y={}&page={}"


def scrape_top(args):
    year, page, mens = args
    gender = "el" if mens else "wel"
    with requests.get(ranking_page.format(gender, year, page)) as fp:
        soup = BeautifulSoup(fp.text, "html.parser")

    return [int(tr.find("a")["href"].split("=")[1]) for tr in soup.find("tbody").find_all("tr")]


@retry(stop_max_attempt_number=3)
def scrape_rider(rider):
    try:
        with requests.get(f"https://firstcycling.com/rider.php?r={rider}&teams=1") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
        tables = soup.find_all("table", **{"class": "tablesorter"})
        if len(tables) == 1:
            return []
        return [(rider, int(a["href"].split("=")[1])) for a in tables[1].find_all("a")]
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{rider}'").with_traceback(sys.exc_info()[2])


@retry(stop_max_attempt_number=3)
def scrape_team(team):
    try:
        with requests.get(f"https://firstcycling.com/team.php?l={team}&riders=2") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
        return [
            int(a["href"].split("=")[1])
            for a in soup.find_all("table", **{"class": "tablesorter"})[0].find_all("a")[::2]
        ]
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{team}'").with_traceback(sys.exc_info()[2])


@retry(stop_max_attempt_number=3)
def get_pretty_rider(rider):
    try:
        with requests.get(f"https://firstcycling.com/rider.php?r={rider}") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
        return {"name": soup.find("h1").text, "url": rider, "year": 0}
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{rider}'").with_traceback(sys.exc_info()[2])

        
year_pat = re.compile(r"r=\d+&y=(\d\d\d\d)")


@retry(stop_max_attempt_number=3)
def get_pretty_team(team):
    try:
        with requests.get(f"https://firstcycling.com/team.php?l={team}") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
         
        year_match = re.search(year_pat, fp.text)
        if year_match:
            year = int(year_match.group(1))
        else:
            try:
                year = int(soup.find("option", selected=True).text.split()[0])
            except:
                year = 1
        return {
            "name": soup.find("h1").text,
            "url": -team,
            "year": year,
        }
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{team}'").with_traceback(sys.exc_info()[2])
        
        
@retry(stop_max_attempt_number=3)
def team_year_from_rider(args):
    rider, team = args
    try:
        with requests.get(f"https://firstcycling.com/rider.php?r={rider}&teams=1") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")

        team_row, = [tr for tr in soup.find("div", **{"id":"wrapper"}).find_all("tr") if f"team.php?l={team}" in str(tr)]
        return {team: int(team_row.find("td").text)}
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{rider}', '{team}'").with_traceback(sys.exc_info()[2])
       
