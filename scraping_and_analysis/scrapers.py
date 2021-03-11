from bs4 import BeautifulSoup
import requests

import pandas as pd

ranking_page = "https://firstcycling.com/ranking.php?k=fc&rank={}&y={}&page={}"


def scrape_top(args):
    year, page, mens = args
    gender = "el" if mens else "wel"
    with requests.get(ranking_page.format(gender, year, page)) as fp:
        soup = BeautifulSoup(fp.text, "html.parser")

    return [int(tr.find("a")["href"].split("=")[1]) for tr in soup.find("tbody").find_all("tr")]


def scrape_rider(rider):
    try:
        with requests.get(f"https://firstcycling.com/rider.php?r={rider}&teams=1") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
        tables = soup.find_all("table", **{"class": "tablesorter"})
        if len(tables) == 1:
            return []
        return [
            (rider, int(a["href"].split("=")[1]))
            for a in tables[1].find_all("a")      
        ]
    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{rider}'").with_traceback(sys.exc_info()[2])


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


def get_pretty_rider(rider):
    with requests.get(f"https://www.procyclingstats.com/{rider}") as fp:
        soup = BeautifulSoup(fp.text, "html.parser")
    return {"name": " ".join(soup.title.text.strip().split()), "url": rider.split("/", 1)[1], "year": 0}


def get_pretty_team(team):
    with requests.get(f"https://www.procyclingstats.com/{team}") as fp:
        soup = BeautifulSoup(fp.text, "html.parser")
    return {
        "name": soup.find("h1").text,
        "url": team.split("/", 1)[1],
        "year": int(soup.find("span", **{"class": ["red"]}).text),
    }
