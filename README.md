# Basic user login and registeration Flask app

### Steps to start

- Clone the repo
- Make python virtual environment 
    ```
    python3 -m venv env
    ```
- Install dependencies
    ```
    pip install -r requirements.txt
    ```
- Add following environment variables to ".env" file and place it in same directory as the project.
    ```
    DB_URI=postgresql://user:password@host:port/schema
    REDIS_HOST=localhost
    REDIS_PORT=6379
    JWT_SECRET_KEY=secretkey
    ```
- Start the app with
    ```
    python app.py
    ```