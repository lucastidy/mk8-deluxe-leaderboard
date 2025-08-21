from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

TRACKS = ["Mushroom Gorge"]
leaderboards = {track: [] for track in TRACKS}

@app.route("/")
def index():
    return render_template("index.html", maps=TRACKS)

@app.route("/leaderboard/<map_name>")
def leaderboard(map_name):
    if map_name not in leaderboards:
        abort(404)
    times = sorted(leaderboards[map_name], key=lambda x: x["time_mins"] + (x["time_s"] / 60) + (x["time_ms"] / 60000), reverse=True)[:10]
    return render_template("leaderboard.html", map_name=map_name, times=times)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    map_name = request.form.get("map_name", "") 
    try:
        time_mins = float(request.form.get("time_mins", ""))
        time_s = float(request.form.get("time_s", ""))
        time_ms = float(request.form.get("time_ms", ""))
    except ValueError:
        return redirect(url_for("leaderboard", map_name=map_name))

    if not name or map_name not in leaderboards or time_mins < 0 or time_s < 0 or time_ms < 0 or time_s >= 60 or time_ms >= 1000 or time_mins >= 60:
        return redirect(url_for("leaderboard", map_name=map_name))

    leaderboards[map_name].append({"name": name, "time_mins": time_mins, "time_s": time_s, "time_ms": time_ms})
    return redirect(url_for("leaderboard", map_name=map_name)) 

if __name__ == "__main__":
    app.run(debug=True)