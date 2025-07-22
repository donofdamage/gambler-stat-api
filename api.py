from flask import Flask, request, jsonify
from pybaseball import playerid_lookup, season_game_logs
import datetime

app = Flask(__name__)

@app.route('/api/player-stats', methods=['GET'])
def player_stats():
    player = request.args.get('player')
    league = request.args.get('league')
    stat = request.args.get('stat')
    games = int(request.args.get('games', 10))

    if not all([player, league, stat]):
        return jsonify({"error":"Missing required parameters"}), 400
    if league.lower() != 'mlb':
        return jsonify({"error":"Only MLB supported"}), 400

    try:
        first, last = player.split(" ", 1)
        pid_df = playerid_lookup(last, first)
        if pid_df.empty:
            return jsonify({"error":"Player not found"}), 404
        pid = pid_df.iloc[0]['key_mlbam']

        year = datetime.datetime.now().year
        df = season_game_logs(pid, year, split_season=False).dropna(subset=[stat])
        df = df[['Date','Opp',stat]].head(games)

        stats = [{"date":r['Date'], "opponent":r['Opp'], stat: int(r[stat])} for _,r in df.iterrows()]
        total = sum(r[stat] for r in stats)
        avg = round(total/len(stats),2) if stats else 0

        return jsonify({"player":player,"league":league,"stat":stat,"games":stats,"total":total,"average":avg})
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

