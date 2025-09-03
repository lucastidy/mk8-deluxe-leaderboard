from flask import Flask, render_template, request, redirect, url_for, abort
import re
from pathlib import Path
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    login_required,
    current_user,
    login_user,
    logout_user,
    LoginManager,
    UserMixin,
)
from utils import validate_time
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY", "default=None"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///leaderboard.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


CUPS = {
    # base game
    "Mushroom Cup": [
        "Mario Kart Stadium",
        "Water Park",
        "Sweet Sweet Canyon",
        "Thwomp Ruins",
    ],
    "Flower Cup": [
        "Mario Circuit (MK8)",
        "Toad Harbor",
        "Twisted Mansion",
        "Shy Guy Falls",
    ],
    "Star Cup": [
        "Sunshine Airport",
        "Dolphin Shoals",
        "Electrodrome",
        "Mount Wario",
    ],
    "Special Cup": [
        "Cloudtop Cruise",
        "Bone-Dry Dunes",
        "Bowser's Castle (MK8)",
        "Rainbow Road (MK8)",
    ],
    "Shell Cup": [
        "Moo Moo Meadows (Wii)",
        "Mario Circuit (GBA)",
        "Cheep Cheep Beach (DS)",
        "Toad's Turnpike (N64)",
    ],
    "Banana Cup": [
        "Dry Dry Desert (GCN)",
        "Donut Plains 3 (SNES)",
        "Royal Raceway (N64)",
        "DK Jungle (3DS)",
    ],
    "Leaf Cup": [
        "Wario Stadium (DS)",
        "Sherbet Land (GCN)",
        "Music Park (3DS)",
        "Yoshi Valley (N64)",
    ],
    "Lightning Cup": [
        "Tick-Tock Clock (DS)",
        "Piranha Plant Slide (3DS)",
        "Grumble Volcano (Wii)",
        "Rainbow Road (N64)",
    ],
    "Egg Cup": [
        "Yoshi Circuit (GCN)",
        "Excitebike Arena",
        "Dragon Driftway",
        "Mute City (F-Zero)",
    ],
    "Triforce Cup": [
        "Wario's Gold Mine (Wii)",
        "Rainbow Road (SNES)",
        "Ice Ice Outpost",
        "Hyrule Circuit",
    ],
    "Crossing Cup": [
        "Baby Park (GCN)",
        "Cheese Land (GBA)",
        "Wild Woods",
        "Animal Crossing",
    ],
    "Bell Cup": [
        "Neo Bowser City (3DS)",
        "Ribbon Road (GBA)",
        "Super Bell Subway",
        "Big Blue (F-Zero)",
    ],
    # DLC
    "Golden Dash Cup": [
        "Paris Promenade (Tour)",
        "Toad Circuit (3DS)",
        "Choco Mountain (N64)",
        "Coconut Mall (Wii)",
    ],
    "Lucky Cat Cup": [
        "Tokyo Blur (Tour)",
        "Shroom Ridge (DS)",
        "Sky Garden (GBA)",
        "Ninja Hideaway (Tour)",
    ],
    "Turnip Cup": [
        "New York Minute (Tour)",
        "Mario Circuit 3 (SNES)",
        "Kalimari Desert (N64)",
        "Waluigi Pinball (DS)",
    ],
    "Propeller Cup": [
        "Sydney Sprint (Tour)",
        "Snow Land (GBA)",
        "Mushroom Gorge (Wii)",
        "Sky-High Sundae",
    ],
    "Rock Cup": [
        "London Loop (Tour)",
        "Boo Lake (GBA)",
        "Rock Rock Mountain (3DS)",
        "Maple Treeway (Wii)",
    ],
    "Moon Cup": [
        "Berlin Byways (Tour)",
        "Peach Gardens (DS)",
        "Merry Mountain (Tour)",
        "Rainbow Road (3DS)",
    ],
    "Fruit Cup": [
        "Amsterdam Drift (Tour)",
        "Riverside Park (GBA)",
        "DK Summit (Wii)",
        "Yoshi's Island",
    ],
    "Boomerang Cup": [
        "Bangkok Rush (Tour)",
        "Mario Circuit (DS)",
        "Waluigi Stadium (GCN)",
        "Singapore Speedway (Tour)",
    ],
    "Feather Cup": [
        "Athens Dash (Tour)",
        "Daisy Cruiser (GCN)",
        "Moonview Highway (Wii)",
        "Squeaky Clean Sprint",
    ],
    "Cherry Cup": [
        "Los Angeles Laps (Tour)",
        "Sunset Wilds (GBA)",
        "Koopa Cape (Wii)",
        "Vancouver Velocity (Tour)",
    ],
    "Acorn Cup": [
        "Rome Avanti (Tour)",
        "DK Mountain (GCN)",
        "Daisy Circuit (Wii)",
        "Piranha Plant Cove",
    ],
    "Spiny Cup": [
        "Madrid Drive (Tour)",
        "Rosalina's Ice World (3DS)",
        "Bowser Castle 3 (SNES)",
        "Rainbow Road (Wii)",
    ],
}

TRACKS = [track for tracks in CUPS.values() for track in tracks]

# leaderboards = {track: [] for track in TRACKS}


class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(100), nullable=False)
    time_mins = db.Column(db.Integer, nullable=False)
    time_s = db.Column(db.Integer, nullable=False)
    time_ms = db.Column(db.Integer, nullable=False)

    # link to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="scores")


# FIXME: verify and remove if removing svg code
def to_slug(name: str) -> str:
    # lowercase, replace non letters/numbers with hyphens, collapse repeats
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower())
    return slug.strip("-")


@app.route("/")
def index():
    return render_template("index.html", maps=TRACKS, CUPS=CUPS)


@app.route("/leaderboard/<map_name>")
def leaderboard(map_name):
    if map_name not in TRACKS:
        abort(404)

    times = Leaderboard.query.filter_by(track=map_name).all()
    # sort times, only render top 10 on leaderboard
    times = sorted(
        times, key=lambda x: x.time_mins + (x.time_s / 60) + (x.time_ms / 60000)
    )[:10]

    # FIXME: remove svg code below potentially
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

    if not validate_time(map_name, time_mins, time_s, time_ms, TRACKS):
        return redirect(url_for("leaderboard", map_name=map_name))

    new_entry = Leaderboard(
        track=map_name,
        time_mins=time_mins,
        time_s=time_s,
        time_ms=time_ms,
        user_id=current_user.id,
    )  # attaches to current_user

    db.session.add(new_entry)
    db.session.commit()

    return redirect(url_for("leaderboard", map_name=map_name))


# user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            return "Username taken, please choose another.", 400

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
