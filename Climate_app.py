import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite",
    connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start><end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert query results to Dictionary using date as key and prcp as value. Return JSON representation of your dictionary."""
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23')
    prcp_values = []
    for p in results:
        prcp_dict = {}
        prcp_dict["date"] = p.date
        prcp_dict["prcp"] = p.prcp
        prcp_values.append(prcp_dict)
    return jsonify(prcp_values)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from dataset."""
    results = session.query(Station.station, Station.name).all()
    allstations = list(np.ravel(results))
    return jsonify(allstations)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    tobs = list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return JSON list of min temp, avg temp, and max temp for given start or start-end range."""
    """When given start only, calc TMIN, TAVG, and TMAX for all dates greater than equal to start date."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    tempstart = list(np.ravel(results))
    return jsonify(tempstart)
    
@app.route("/api/v1.0/<start><end>")
def temp_start_end(start, end):
    """When given start and end date, calc TMIN, TAVG, and TMAX for dates between start and end date inclusive."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    tempstartend = list(np.ravel(results))
    return jsonify(tempstartend)

if __name__ == '__main__':
    app.run(debug=True)
