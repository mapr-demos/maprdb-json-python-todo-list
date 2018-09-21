from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "mapr_python_app"

from app import views
