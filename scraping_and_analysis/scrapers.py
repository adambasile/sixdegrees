from bs4 import BeautifulSoup
import requests

import pandas as pd

ranking_page = "https://www.procyclingstats.com/rankings.php?date={}-12-31&nation=&age=&zage=&page=smallerorequal&team=&offset={}&filter=Filter&p={}e&s=season-individual"


def scrape_top(args):
    year, offset, mens = args
    gender = "m" if mens else "w"
    with requests.get(ranking_page.format(year, offset, gender)) as fp:
        soup = BeautifulSoup(fp.text, "html.parser")
    top_riders = [a["href"] for a in soup.find("table", **{"class": "basic"}).find_all("a")[::3]]
    return top_riders


def scrape_rider(rider):
    try:
        with requests.get(f"https://www.procyclingstats.com/{rider}") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")

        with requests.get(f"https://www.procyclingstats.com/{rider}/statistics/season-statistics") as fp:
            pointsoup = BeautifulSoup(fp.text, "html.parser")

        teams = pd.Series(
            {
                int(teamyear.find("div", **{"class": "season"}).text): teamyear.find("a")["href"]
                for teamyear in soup.find("ul", **{"class": "rdr-teams"}).find_all("li")
                if teamyear.find("div", **{"class": "season"}).text
            }
        )
        teams = teams[teams.index < 2022]

        points = pd.read_html(str(pointsoup.find("table")))[0].dropna().astype(int).set_index("Season")[["Points"]]

        out = points.reindex(teams.index).fillna(0)
        out["Teams"] = teams
        out["Rider"] = rider
        return list(out[["Rider", "Teams", "Points"]].itertuples(index=False, name=None))

    except Exception as e:
        import sys

        raise type(e)(f"Problem with '{rider}'").with_traceback(sys.exc_info()[2])


def scrape_team(team):
    try:
        with requests.get(f"https://www.procyclingstats.com/{team}") as fp:
            soup = BeautifulSoup(fp.text, "html.parser")
        return [a["href"] for a in soup.find("ul", style=" ", **{"class": ("list", "pad2")}).find_all("a")]
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