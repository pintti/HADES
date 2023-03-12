from app import app
import requests

own_port = 5000
main_server_url = "http://localhost:8080"

if __name__ == "__main__":
    requests.post(main_server_url+"/connect", json={"port": str(own_port)})

    app.run(host="0.0.0.0", port=own_port)
