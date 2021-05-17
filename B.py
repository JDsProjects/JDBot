from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def main():
    return "JDBot is up and running!!"


def run():
    app.run(host="0.0.0.0", port=3000)


def b():
    server = Thread(target=run)
    server.start()
