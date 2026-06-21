import datetime
import json
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup

# =====================================================================
# CONFIGURATION: Paste your browser cookie strings here
# =====================================================================
USER_COOKIES = {
    "orac": "YOUR_ORAC_SESSIONID_HERE"  # Paste your ORAC 'sessionid' cookie here
}

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def get_codeforces_solves(handle):
    if not handle: return pd.DataFrame(columns=["Date", "CF_Count"])
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            dates = []
            unique = set()
            for sub in data["result"]:
                if sub.get("verdict") == "OK" and "problem" in sub:
                    p_id = f"{sub['problem'].get('contestId')}{sub['problem'].get('index')}"
                    dt = datetime.datetime.fromtimestamp(sub["creationTimeSeconds"])
                    if p_id not in unique:
                        unique.add(p_id)
                        dates.append(dt.strftime("%Y-%m-%d"))
            if dates:
                return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="CF_Count")
    except Exception:
        pass
    return pd.DataFrame(columns=["Date", "CF_Count"])


def get_atcoder_solves(handle):
    if not handle: return pd.DataFrame(columns=["Date", "AC_Count"])
    url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={handle}&from_second=0"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            dates = []
            unique = set()
            for sub in response.json():
                if sub.get("result") == "AC":
                    p_id = sub.get("problem_id")
                    dt = datetime.datetime.fromtimestamp(sub["epoch_second"])
                    if p_id not in unique:
                        unique.add(p_id)
                        dates.append(dt.strftime("%Y-%m-%d"))
            if dates:
                return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="AC_Count")
    except Exception:
        pass
    return pd.DataFrame(columns=["Date", "AC_Count"])


def get_dmoj_solves(handle):
    if not handle: return pd.DataFrame(columns=["Date", "DMOJ_Count"])
    url = f"https://dmoj.ca/api/v2/submissions?user={handle}"
    dates = []
    unique_problems = set()
    page = 1
    try:
        while True:
            response = requests.get(f"{url}&page={page}", timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
            results = data.get("data", {}).get("objects", [])
            if not results:
                break
            for sub in results:
                if sub.get("result") == "AC":
                    prob_id = sub.get("problem")
                    time_str = sub.get("date")
                    if prob_id and time_str and prob_id not in unique_problems:
                        unique_problems.add(prob_id)
                        dates.append(time_str[:10])
            if not data.get("data", {}).get("has_next", False):
                break
            page += 1
    except Exception:
        pass
    if dates:
        return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="DMOJ_Count")
    return pd.DataFrame(columns=["Date", "DMOJ_Count"])


def get_ojuz_solves(handle):
    if not handle: return pd.DataFrame(columns=["Date", "OJUZ_Count"])
    url = f"https://oj.uz/submissions?username={handle}"
    dates = []
    unique = set()
    try:
        res = requests.get(url, headers=BASE_HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 6:
                result_text = cols[5].get_text(strip=True)
                if "100" in result_text or "Accepted" in result_text:
                    p_id = cols[2].get_text(strip=True)
                    time_str = cols[1].get_text(strip=True)[:10]
                    if p_id not in unique:
                        unique.add(p_id)
                        dates.append(time_str)
    except Exception:
        pass
    if dates:
        return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="OJUZ_Count")
    return pd.DataFrame(columns=["Date", "OJUZ_Count"])


def get_leetcode_solves(handle):
    if not handle: return pd.DataFrame(columns=["Date", "LC_Count"])
    url = "https://leetcode.com/graphql"
    query = """
    query userProfileCalendar($username: String!, $year: Int) {
        matchedUser(username: $username) {
            userCalendar(year: $year) {
                submissionCalendar
            }
        }
    }
    """
    try:
        variables = {"username": handle}
        resp = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
        data = resp.json()
        cal_str = data["data"]["matchedUser"]["userCalendar"]["submissionCalendar"]
        cal_dict = json.loads(cal_str)
        dates = []
        for ts, count in cal_dict.items():
            dt = datetime.datetime.fromtimestamp(int(ts))
            for _ in range(count): dates.append(dt.strftime("%Y-%m-%d"))
        if dates:
            return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="LC_Count")
    except Exception:
        pass
    return pd.DataFrame(columns=["Date", "LC_Count"])


def get_orac_solves(enabled):
    if not enabled or USER_COOKIES["orac"] == "YOUR_ORAC_SESSIONID_HERE":
        return pd.DataFrame(columns=["Date", "ORAC_Count"])

    headers = BASE_HEADERS.copy()
    headers["Cookie"] = f"sessionid={USER_COOKIES['orac']}"
    dates = []
    unique = set()
    page = 1

    try:
        while True:
            url = f"https://orac2.info/hub/allsubs/{page}"
            res = requests.get(url, headers=headers, timeout=10)

            if "login" in res.url or "Log in" in res.text:
                print("[-] ORAC authentication session dropped.")
                break

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            if not table:
                break

            rows = table.find_all("tr")[1:]
            if not rows:
                break

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    score = cols[3].get_text(strip=True)
                    status = cols[2].get_text(strip=True)

                    if "100" in score or "Correct" in status:
                        p_id = cols[1].get_text(strip=True)
                        time_raw = cols[0].get_text(strip=True)
                        time_str = time_raw[:10]

                        if p_id not in unique:
                            unique.add(p_id)
                            dates.append(time_str)

            # Target page list containers or "Next" links directly to see if a next page is viable
            pagination_nav = soup.find("ul", class_="pagination")
            if pagination_nav:
                # If there's an explicit navigation bar, look for the next numerical step link
                next_page_exists = pagination_nav.find("a", string=str(page + 1))
                if not next_page_exists or page >= 50:  # Guard cap at 50 pages total
                    break
            else:
                # If no formal bar, stop when a page yields 0 actual data fields
                if len(rows) == 0:
                    break

            page += 1

    except Exception:
        pass

    if dates:
        return pd.DataFrame(dates, columns=["Date"]).groupby("Date").size().reset_index(name="ORAC_Count")
    return pd.DataFrame(columns=["Date", "ORAC_Count"])


def generate_mega_heatmap(handles):
    dfs = {
        "CF_Count": get_codeforces_solves(handles.get("cf")),
        "AC_Count": get_atcoder_solves(handles.get("atcoder")),
        "DMOJ_Count": get_dmoj_solves(handles.get("dmoj")),
        "OJUZ_Count": get_ojuz_solves(handles.get("ojuz")),
        "LC_Count": get_leetcode_solves(handles.get("leetcode")),
        "ORAC_Count": get_orac_solves(handles.get("orac"))
    }

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=364)
    start_date -= datetime.timedelta(days=(start_date.weekday() + 1) % 7)

    grid_df = pd.DataFrame({"Date": pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d")})

    for key, df in dfs.items():
        print(f"-> Found {df[key].sum() if not df.empty else 0} matches via source tag {key}")
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
            grid_df = pd.merge(grid_df, df, on="Date", how="left")
        else:
            grid_df[key] = 0

    grid_df = grid_df.fillna(0)
    count_cols = [k for k in dfs.keys() if k in grid_df.columns]
    grid_df["Count"] = grid_df[count_cols].sum(axis=1)

    grid_df["Date"] = pd.to_datetime(grid_df["Date"])
    grid_df["Weekday"] = (grid_df["Date"].dt.weekday + 1) % 7

    base_date = grid_df["Date"].min()
    grid_df["WeekNum"] = (grid_df["Date"] - base_date).dt.days // 7

    heatmap_data = grid_df.pivot(index="Weekday", columns="WeekNum", values="Count")

    plt.figure(figsize=(16, 3.8))
    colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
    cmap = mcolors.LinearSegmentedColormap.from_list("github_green", colors)

    ax = sns.heatmap(heatmap_data, cmap=cmap, linewidths=2, linecolor="white", cbar=False, square=True, vmax=6)

    ax.set_title("Unified CP Activity Matrix (All Platforms Combined)", fontsize=14, pad=15, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_yticks([0.5, 2.5, 4.5, 6.5])
    ax.set_yticklabels(["Sun", "Tue", "Thu", "Sat"], rotation=0, fontsize=10)

    month_labels, month_positions = [], []
    unique_dates = grid_df.drop_duplicates(subset=["WeekNum"]).copy()
    for _, row in unique_dates.iterrows():
        week_date = row["Date"]
        if week_date.day <= 7:
            month_labels.append(week_date.strftime("%b"))
            month_positions.append(row["WeekNum"] + 0.5)

    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_labels, fontsize=10)

    plt.tight_layout()
    plt.savefig("mega_solves_grid.png", dpi=300)
    print("\nSuccess! Generated unified image file as 'mega_solves_grid.png'")
    plt.show()


if __name__ == "__main__":
    USER_HANDLES = {
        "cf": "quollcucumber1",
        "atcoder": "quollcucumber",
        "dmoj": "quollcucumber",
        "ojuz": "quollcucumber",
        "leetcode": "quollcucumber",
        "orac": True
    }

    generate_mega_heatmap(USER_HANDLES)
