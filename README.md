# Mario Kart 8 Deluxe Leaderboard
Live [Here](https://mk8dxleaderboard.com)!

A full-stack web application that tracks and displays Mario Kart 8 Deluxe player stats and race results.  
Built for friends and local tournaments to easily log races, compare times, and view per-track rankings.

## Features
-  **User Accounts:** Register and login.  
- **Per-track leaderboards.** All MK8DX cups and tracks are listed; each track has its own board displaying `# / Player / Time`.  
- **Auth-gated submissions.** Users must **register / log in** to submit a time (submission UI appears on the track page when logged in).
- **Verified Submissions Only.** Users must upload a screenshot or image showing proof that the time they are uploading is real and is their own. 
-  **Cloud Deployment:** Hosted on AWS Elastic Beanstalk with PostgreSQL RDS and S3 storage  
-  **CI/CD:** GitHub Actions for automated testing and deployment  

## Tech Stack
- **Language:** Python, HTML/CSS, SQL
- **Frameworks:** Flask, Jinja2
- **Tools:** Docker, AWS

### Option A — Docker
```bash
# from repo root
docker build -t mk8dxleaderboard .
docker run -p 5000:5000 mk8dxleaderboard
# visit http://localhost:5000
```

### Option B — Python (local)
```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # starts the dev server
```

#### Notes:
- The repo includes a Dockerfile for container runs.
- If you deploy to AWS Elastic Beanstalk, the .platform/nginx/conf.d/ folder and .ebignore are already present to help with environment setup. 

### Usage 
1. Open the site and choose a Cup -> Track.
2. View the leaderboard for that track.
3. Register / Log in to submit your own time

## License
This project is licensed under the [MIT License](LICENSE).  
© Nintendo for all Mario Kart names, logos, and related assets.

Built by: Lucas Tidy
