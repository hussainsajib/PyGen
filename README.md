# PyGen - Python-based Islamic Video generating application


# Running the project in Docker
- Build image: `docker build -t pygen .`
- Run container interactively: `docker run -it -p 8000:8000 --mount type=bind,src=c:\Users\user\Documents\pygen\recitation_data,dst=/assets/recitation_data --env-file ./.env pygen /bin/bash`