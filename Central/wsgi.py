from server import app
import time
import sys

if __name__ == "__main__":
    print("Waiting 10 secs for DB to initialize", file=sys.stderr, flush=True)
    time.sleep(10)
    app.run(host="0.0.0.0", port= 8080)

