from app import create_app, db
from app.models import User, Leaderboard
import random

app = create_app()

with app.app_context():

    print("creating fake users...")
    users = []
    for _ in range(12): 
        user = User(username=("fakeUser" + str(random.randint(1,888))))
        user.set_password("test123")
        users.append(user)
        db.session.add(user)
    db.session.commit()

    print("creating leaderboard entries...")
    tracks = ["Sunshine Airport", "Dolphin Shoals", "Electrodrome", "Mount Wario"]
    screenshot_path = "static/uploads/acorn-cup.png"

    for u in users:
        for track in tracks:
            entry = Leaderboard(
                track=track,
                time_mins=random.randint(1, 2),
                time_s=random.randint(0, 59),
                time_ms=random.randint(0, 999),
                user_id=u.id,
                verified=True,
                screenshot_path=screenshot_path,
            )
            db.session.add(entry)

    db.session.commit()
    print("success seeding data")
