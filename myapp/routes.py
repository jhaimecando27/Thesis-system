from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    session,
)

import os
from .helpers import TabuSearch
import random
from werkzeug.utils import secure_filename
from datetime import datetime

from .forms import UploadForm, SelectionForm
import googlemaps

import pandas as pd

bp = Blueprint("map", __name__)

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise Exception("API_KEY not found in environment variables.")

gmaps = googlemaps.Client(key=API_KEY)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/DataGathering", methods=["GET", "POST"])
def data_gathering():

    form = UploadForm()

    if request.method == "POST":
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            filestream = form.file.data
            df = pd.read_csv(filestream)
            objectId = df[df.columns[0]].tolist()
            coordinates = list(
                zip(df[df.columns[1]].tolist(), df[df.columns[2]].tolist())
            )
            session["data"] = dict(zip(objectId, coordinates))
            return redirect(url_for("data_selection"))

    return render_template("data_gathering.html", form=form)


@bp.route("/DataSelection", methods=["GET", "POST"])
def data_selecton():
    form = SelectionForm()
    form.options.choices = list(session["data"].keys())

    if request.method == "POST":
        if form.validate_on_submit():
            coordinates = [session["data"][objectId] for objectId in form.options.data]
            coordinate_strings = [f"{lat},{lon}" for lon, lat in coordinates]
            return redirect(url_for("output_map", coordinates=coordinate_strings))

    return render_template("data_selection.html", form=form)


@bp.route("/Map")
def output_map():
    locations = request.args.getlist("coordinates")
    print(locations)

    result = gmaps.distance_matrix(
        origins=locations,
        destinations=locations,
        mode="driving",
        departure_time=datetime.now(),
    )

    # Distance matrix
    dm = [
        [element["distance"]["value"] for element in row["elements"]]
        for row in result["rows"]
    ]

    soln_init = [i for i in range(len(locations))]
    random.shuffle(soln_init)

    ts_search = TabuSearch(dm)
    result = ts_search.search(soln_init)

    output_routes = [locations[i] for i in result]

    # Find center of all locations for initial map view
    total_lat = 0
    total_lng = 0
    for loc in output_routes:
        lat, lng = map(float, loc.split(","))
        total_lat += lat
        total_lng += lng

    center_lat = total_lat / len(locations)
    center_lng = total_lng / len(locations)

    objectId = []
    for loc in output_routes:
        for id, xy in session["data"].items():
            lon, lat = xy
            xy_mod = f"{lat},{lon}"
            if loc == xy_mod:
                objectId.append(id)

    return render_template(
        "map.html",
        api_key=API_KEY,
        locations=output_routes,
        objectId=objectId,
        center_lat=center_lat,
        center_lng=center_lng,
    )
