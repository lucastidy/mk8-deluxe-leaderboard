from flask import Flask, render_template, request, redirect, url_for, abort
import re
from pathlib import Path
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "default=None")  #FIXME: set a real secret key!

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///leaderboard.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

import users

migrate = Migrate(app, db)

TRACKS = [
    # Base Game (48 tracks)
    "Mario Kart Stadium", "Water Park", "Sweet Sweet Canyon", "Thwomp Ruins",
    "Mario Circuit", "Toad Harbor", "Twisted Mansion", "Shy Guy Falls",
    "Sunshine Airport", "Dolphin Shoals", "Electrodrome", "Mount Wario",
    "Cloudtop Cruise", "Bone-Dry Dunes", "Bowser's Castle (MK8)", "Rainbow Road (MK8)",

    "Moo Moo Meadows (Wii)", "Mario Circuit (GBA)", "Cheep Cheep Beach (DS)", "Toad's Turnpike (N64)",
    "Dry Dry Desert (GCN)", "Donut Plains 3 (SNES)", "Royal Raceway (N64)", "DK Jungle (3DS)",
    "Wario Stadium (DS)", "Sherbet Land (GCN)", "Music Park (3DS)", "Yoshi Valley (N64)",
    "Tick-Tock Clock (DS)", "Piranha Plant Slide (3DS)", "Grumble Volcano (Wii)", "Rainbow Road (N64)",

    "Yoshi Circuit (GCN)", "Excitebike Arena", "Dragon Driftway", "Mute City (F-Zero)",
    "Baby Park (GCN)", "Cheese Land (GBA)", "Wild Woods", "Animal Crossing",
    "Neo Bowser City (3DS)", "Ribbon Road (GBA)", "Super Bell Subway", "Big Blue (F-Zero)",

    # Booster Course Pass (48 tracks)
    # Wave 1
    "Paris Promenade (Tour)", "Toad Circuit (3DS)", "Choco Mountain (N64)", "Coconut Mall (Wii)",
    "Tokyo Blur (Tour)", "Shroom Ridge (DS)", "Sky Garden (GBA)", "Ninja Hideaway (Tour)",

    # Wave 2
    "New York Minute (Tour)", "Mario Circuit 3 (SNES)", "Kalimari Desert (N64)", "Waluigi Pinball (DS)",
    "Sydney Sprint (Tour)", "Snow Land (GBA)", "Mushroom Gorge (Wii)", "Sky-High Sundae",

    # Wave 3
    "London Loop (Tour)", "Boo Lake (GBA)", "Rock Rock Mountain (3DS)", "Maple Treeway (Wii)",
    "Berlin Byways (Tour)", "Peach Gardens (DS)", "Merry Mountain (Tour)", "Rainbow Road (3DS)",

    # Wave 4
    "Amsterdam Drift (Tour)", "Riverside Park (GBA)", "DK Summit (Wii)", "Yoshi's Island",
    "Bangkok Rush (Tour)", "Mario Circuit (DS)", "Waluigi Stadium (GCN)", "Singapore Speedway (Tour)",

    # Wave 5
    "Athens Dash (Tour)", "Daisy Cruiser (GCN)", "Moonview Highway (Wii)", "Squeaky Clean Sprint",
    "Los Angeles Laps (Tour)", "Sunset Wilds (GBA)", "Koopa Cape (Wii)", "Vancouver Velocity (Tour)",

    # Wave 6
    "Rome Avanti (Tour)", "DK Mountain (GCN)", "Daisy Circuit (Wii)", "Piranha Plant Cove",
    "Madrid Drive (Tour)", "Rosalina's Ice World (3DS)", "Bowser Castle 3 (SNES)", "Rainbow Road (Wii)"
]

#leaderboards = {track: [] for track in TRACKS}

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(100), nullable=False)
    time_mins = db.Column(db.Integer, nullable=False)
    time_s = db.Column(db.Integer, nullable=False)
    time_ms = db.Column(db.Integer, nullable=False)


    #link to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="scores")

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
@login_required
def submit():
    map_name = request.form.get("map_name", "") 
    try:
        time_mins = int(request.form.get("time_mins", ""))
        time_s = int(request.form.get("time_s", ""))
        time_ms = int(request.form.get("time_ms", ""))
    except ValueError:
        return redirect(url_for("leaderboard", map_name=map_name))

    if map_name not in TRACKS or time_mins < 0 or time_s < 0 or time_ms < 0 or time_s >= 60 or time_ms >= 1000 or time_mins >= 60:
        #FIXME: maybe add assertions here?
        return redirect(url_for("leaderboard", map_name=map_name))

    new_entry = Leaderboard(
        track=map_name, 
        time_mins=time_mins, 
        time_s=time_s, 
        time_ms=time_ms, 
        user_id=current_user.id)  # attaches to current_user

    db.session.add(new_entry)
    db.session.commit()
    
    #leaderboards[map_name].append({"name": name, "time_mins": time_mins, "time_s": time_s, "time_ms": time_ms})
    return redirect(url_for("leaderboard", map_name=map_name)) 


if __name__ == "__main__":
    app.run(debug=True)