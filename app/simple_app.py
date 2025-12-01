from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>AI Code Review Pipeline</h1><p>This app deploys automatically!</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
