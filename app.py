from flask import Flask, render_template, request, redirect, url_for, abort
import re
from pathlib import Path
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///leaderboard.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

TRACKS = ["Mushroom Gorge", "Bowser's Castle", "Rainbow Road Wii", "Coconut Mall"]
#leaderboards = {track: [] for track in TRACKS}

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    time_mins = db.Column(db.Integer, nullable=False)
    time_s = db.Column(db.Integer, nullable=False)
    time_ms = db.Column(db.Integer, nullable=False)

#FIXME: verify and remove if removing svg code
def to_slug(name: str) -> str:
    # lowercase, replace non letters/numbers with hyphens, collapse repeats
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    return slug.strip('-')

@app.route("/")
def index():
    return render_template("index.html", maps=TRACKS)

@app.route("/leaderboard/<map_name>")
def leaderboard(map_name):
    if map_name not in TRACKS:
        abort(404)

    times = Leaderboard.query.filter_by(track=map_name).all()
    #sort times, only render top 10 on leaderboard
    times = sorted(times, key=lambda x: x.time_mins + (x.time_s / 60) + (x.time_ms / 60000))[:10]

    #FIXME: remove svg code below potentially    
    svg_filename = f"{to_slug(map_name)}.svg"
    svg_path = Path(app.static_folder) / "img" / "maps" / svg_filename
    has_svg = svg_path.exists()

    return render_template(
            "leaderboard.html",
            map_name=map_name,
            times=times,
            svg_filename=svg_filename,
            has_svg=has_svg,
        )

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    map_name = request.form.get("map_name", "") 
    try:
        time_mins = int(request.form.get("time_mins", ""))
        time_s = int(request.form.get("time_s", ""))
        time_ms = int(request.form.get("time_ms", ""))
    except ValueError:
        return redirect(url_for("leaderboard", map_name=map_name))

    if not name or map_name not in TRACKS or time_mins < 0 or time_s < 0 or time_ms < 0 or time_s >= 60 or time_ms >= 1000 or time_mins >= 60:
        #FIXME: maybe add assertions here?
        return redirect(url_for("leaderboard", map_name=map_name))

    new_entry = Leaderboard(track=map_name, name=name, time_mins=time_mins, time_s=time_s, time_ms=time_ms)
    db.session.add(new_entry)
    db.session.commit()
    
    #leaderboards[map_name].append({"name": name, "time_mins": time_mins, "time_s": time_s, "time_ms": time_ms})
    return redirect(url_for("leaderboard", map_name=map_name)) 

if __name__ == "__main__":
    app.run(debug=True)