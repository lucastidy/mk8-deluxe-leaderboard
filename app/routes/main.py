from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import boto3

s3 = boto3.client("s3")

from .. import db
from ..models import Leaderboard

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

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html", maps=TRACKS, CUPS=CUPS)

@main.route("/leaderboard/<map_name>")
def leaderboard(map_name):
    if map_name not in TRACKS:
        abort(404)

    times = Leaderboard.query.filter_by(track=map_name, verified=True).all()
    # sort times, only render top 10 on leaderboard
    full_times = sorted(
        times, key=lambda x: x.time_mins + (x.time_s / 60) + (x.time_ms / 60000)
    )

    times = full_times[:10]

    user_index = None

    if(
        current_user.is_authenticated 
        and current_user.scores.filter_by(track=map_name, verified=True).first() is not None
    ):
        if current_user.scores.filter_by(track=map_name, verified=True).first() not in times:
            times.append(current_user.scores.filter_by(track=map_name, verified=True).first())
            user_index = full_times.index(current_user.scores.filter_by(track=map_name, verified=True).first())

    return render_template(
        "leaderboard.html",
        map_name=map_name,
        times=times,
        user_index=user_index
    )

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/submit", methods=["POST"])
@login_required
def submit():
    map_name = request.form.get("map_name", "")
    try:
        time_mins = int(request.form.get("time_mins", ""))
        time_s = int(request.form.get("time_s", ""))
        time_ms = int(request.form.get("time_ms", ""))
    except ValueError:
        return redirect(url_for("main.leaderboard", map_name=map_name))

    if not validate_time(map_name, time_mins, time_s, time_ms, TRACKS):
        flash("Invalid Time", "invalid_time")
        return redirect(url_for("main.leaderboard", map_name=map_name))

    screenshot = request.files.get("screenshot")

    if not screenshot:
        flash("Missing screenshot file.", "missing_screenshot")
        return redirect(url_for("main.leaderboard", map_name=map_name))

    filename = secure_filename(screenshot.filename)

    if not allowed_file(filename):
        flash("Invalid screenshot file type. Please upload a PNG or JPG file"
        , "invalid_screenshot")
        return redirect(url_for("main.leaderboard", map_name=map_name))
    
    unique_name = f"{uuid.uuid4().hex}_{filename}"

    if current_app.config["USE_S3"]:
        # upload to s3 !!
        s3.upload_fileobj(
            screenshot,
            current_app.config["S3_BUCKET_NAME"],
            unique_name,  # folder inside the bucket
            ExtraArgs={"ContentType": screenshot.content_type},
        )
        file_url = f"https://{current_app.config['S3_BUCKET_NAME']}.s3.us-west-2.amazonaws.com/{unique_name}"
    else:
        # save locally
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        screenshot.save(file_path)
        file_url = f"/static/uploads/{unique_name}"

    existing_entry = Leaderboard.query.filter_by(
        track=map_name, user_id=current_user.id
    ).first()

    if existing_entry:
        # update existing entry
        existing_entry.time_mins = time_mins
        existing_entry.time_s = time_s
        existing_entry.time_ms = time_ms
        existing_entry.screenshot_path = file_url
        existing_entry.verified = False
        flash("Entry updated! Awaiting verification...", "pending")
    else:
        # new entry if not found
        new_entry = Leaderboard(
            track=map_name,
            time_mins=time_mins,
            time_s=time_s,
            time_ms=time_ms,
            user_id=current_user.id,
            screenshot_path=file_url,
            verified=False,
        )
        flash("New entry created! Awaiting verification...", "pending")
        db.session.add(new_entry)

    db.session.commit()

    return redirect(url_for("main.leaderboard", map_name=map_name))

def validate_time(map_name: str, time_mins: int, time_s: int,
    time_ms: int, tracks: list[str]) -> bool:
    if map_name not in tracks:
        return False
    if time_mins < 0 or time_mins >= 60:
        return False
    if time_s < 0 or time_s >= 60:
        return False
    if time_ms < 0 or time_ms >= 1000:
        return False
    return True
