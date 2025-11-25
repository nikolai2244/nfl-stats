import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, make_response, render_template

app = Flask(__name__)

# Mapping for NFL.com stats
STAT_CATEGORIES = {
    "passing_yards": {
        "url": "https://www.nfl.com/stats/player-stats/category/passing/2025/REG/all/passingyards/desc",
        "column": "YDS"
    },
    "passing_tds": {
        "url": "https://www.nfl.com/stats/player-stats/category/passing/2025/REG/all/passingtouchdowns/desc",
        "column": "TD"
    },
    "rushing_yards": {
        "url": "https://www.nfl.com/stats/player-stats/category/rushing/2025/REG/all/rushingyards/desc",
        "column": "YDS"
    },
    "receiving_yards": {
        "url": "https://www.nfl.com/stats/player-stats/category/receiving/2025/REG/all/receivingyards/desc",
        "column": "YDS"
    },
    "receptions": {
        "url": "https://www.nfl.com/stats/player-stats/category/receiving/2025/REG/all/receptions/desc",
        "column": "REC"
    },
    "field_goals_made": {
        "url": "https://www.nfl.com/stats/player-stats/category/field-goals-made/2025/REG/all/fieldgoalsmade/desc",
        "column": "FGM"
    }
}

def scrape_nfl_stats(url, stat_col_name, max_results=20):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")
    players = []
    if not table:
        print(f"No table found at {url}")
        return []
    try:
        header = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        stat_idx = header.index(stat_col_name)
    except ValueError:
        print(f"Stat column '{stat_col_name}' not found, using fallback index 4")
        stat_idx = 4
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        if len(cols) > stat_idx:
            name = cols[1].get_text(strip=True) if len(cols) > 1 else None
            team = cols[2].get_text(strip=True) if len(cols) > 2 else None
            stat = cols[stat_idx].get_text(strip=True)
            try:
                stat_val = float(stat.replace(",", ""))
            except Exception:
                stat_val = 0.0
            if name and team:
                players.append({
                    "name": name,
                    "team": team,
                    "stat": stat_val
                })
    ranked = sorted(players, key=lambda x: x['stat'], reverse=True)[:max_results]
    return ranked

@app.route('/api/<stat_type>')
def api_stat(stat_type):
    n = request.args.get("n", 20, type=int)
    stat_info = STAT_CATEGORIES.get(stat_type)
    if not stat_info:
        return make_response(jsonify({
            "status": "error",
            "message": f"Stat type '{stat_type}' not found."
        }), 404)
    data = scrape_nfl_stats(stat_info["url"], stat_info["column"], max_results=n)
    status = "ok" if data else "no_data"
    response = make_response(jsonify({
        "status": status,
        "stat_type": stat_type,
        "results": len(data),
        "players": data
    }), 200)
    response.headers["Cache-Control"] = "public, max-age=300" # Cache for 5 minutes
    return response

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "NFL.com Stats API Backend",
        "available_stats": list(STAT_CATEGORIES.keys()),
        "usage": "/api/<stat_type>?n=20"
    })

# ------- NEW DASHBOARD FRONTEND ROUTE --------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
