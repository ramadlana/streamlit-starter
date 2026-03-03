import os

from flask import Blueprint, current_app, render_template
from flask_login import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def index():
    streamlit_port = os.environ.get("STREAMLIT_PORT", "8501")
    streamlit_url = f"http://localhost:{streamlit_port}"
    if not current_app.debug:
        streamlit_url = "/dashboard-app/"
    return render_template("index.html", streamlit_url=streamlit_url)
