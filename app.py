from flask import Flask
from routes.analyze import analyze_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(analyze_bp)

if __name__ == "__main__":
    app.run(debug=True)
