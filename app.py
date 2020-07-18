import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Refelct exisitng database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def home():
    return(
        "Welcome to the Hawaii Climate API<br><br>"
        "Available Routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/<start>yyyy-mm-dd<br>"
        "/api/v1.0/<start>yyyy-mm-dd/yyyy-mm-dd<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results= session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= previous_year).all()
    # Close the session
    session.close()
    # Convert list of tuples into normal list
    hawaii_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        hawaii_prcp.append(prcp_dict)

    return jsonify(hawaii_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create session link
    session = Session(engine)
    # Return a JSON list of stations
    results = session.query(Station.station).all()
    # close the session
    session.close()
    # convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session link
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the last year of data.
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= previous_year).\
    filter(Measurement.station == 'USC00519281').all()
    # Close session
    session.close()
    # convert list of tuples into normal list
    temp_list = list(np.ravel(results))
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create session link
    session = Session(engine)
    # Query Min, Max, and avg for all dates greater than or equal to given start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    # End session
    session.close()
    # convert list of tuples into normal list
    start_date = list(results)
    return jsonify(start_date)
    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create session link
    session = Session(engine)
    # Query Min, Max, and avg for all dates greater than or equal to given start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    # End session
    session.close()
    # convert list of tuples into normal list
    chosen_dates = list(results)
    return jsonify(chosen_dates)


if __name__ == "__main__":
    app.run(debug=True)