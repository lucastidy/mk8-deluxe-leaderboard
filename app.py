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
    times = sorted(leaderboard[map_name], key=lambda x: x["time"], reverse=True)[:10]
    return render_template("leaderboard.html", map_name=map_name, times=times)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    map_name = request.form.get("map_name", "") 
    try:
        time_val = float(request.form.get("time", ""))
    except ValueError:
        return redirect(url_for("leaderboard", map_name=map_name))

    if not name or map_name not in leaderboards or time_val <= 0:
        return redirect(url_for("leaderboard", map_name=map_name))

    leaderboards[map_name].append({"name": name, "time": time_val})
    return redirect(url_for("leaderboard", map_name=map_name)) 

if __name__ == "main":
    app.run(debug=True)