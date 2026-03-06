import os

from flask import Blueprint, current_app, render_template
from flask_login import login_required

bp = Blueprint("iframe_app_streamlit", __name__)


@bp.route("/iframe-app-streamlit")
@login_required
def iframe_app_streamlit():
    streamlit_port = os.environ.get("STREAMLIT_PORT", "8501")
    streamlit_url = f"http://localhost:{streamlit_port}"
    if not current_app.debug:
        streamlit_url = "/dashboard-app/"
    return render_template("iframe_app_streamlit.html", streamlit_url=streamlit_url)
