from flask import Flask
from threading import Thread
app = Flask('')
@app.route('/')
def main():
    return 'JDJG Bot is up and running!!'

def run():
    app.run(host='0.0.0.0', port=8080)

def b():
    server = Thread(target=run)
    server.start()