# Import the dependencies
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

# Global Variables
# Calculate the date one year from the last date in the dataset
end_date = datetime.strptime("2017-08-23", "%Y-%m-%d").date()
start_date = end_date - timedelta(days=365)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save reference to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session (link) from Python to the DB
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
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation analysis"""
    # Query precipitation and date
    precipitation_query = session.query(Measurement.prcp, Measurement.date).filter(
        Measurement.date.between(start_date, end_date)
    ).all()

    # Convert to dictionary
    precipitation_dict = {d: p for p, d in precipitation_query}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List data of all stations"""      
    # Query the station names
    stations_query = session.query(Station.name).all()
    stations_list = list(np.ravel(stations_query))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query most active station from the past year"""
    tobs_query = session.query(Measurement.tobs, Measurement.date).filter(
        Measurement.station == "USC00519281",
        Measurement.date.between(start_date, end_date)
    ).all()

    tobs_list = [{"date": d, "TOBS": t} for t, d in tobs_query]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return min, max, and avg temperature from specified start date"""
    start_only_query = session.query(func.min(Measurement.tobs), 
                                      func.avg(Measurement.tobs), 
                                      func.max(Measurement.tobs)).filter(
        Measurement.date >= start
    ).all()
    
    temps = [{'Minimum Temperature': min, 
              'Average Temperature': avg, 
              'Maximum Temperature': max} for min, avg, max in start_only_query]

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end="2017-08-23"):
    """Return min, max, and avg temperature from specified start and end date"""
    start_end_query = session.query(func.min(Measurement.tobs), 
                                     func.avg(Measurement.tobs), 
                                     func.max(Measurement.tobs)).filter(
        Measurement.date.between(start, end)
    ).all()
    
    temps = [{'Minimum Temperature': min, 
              'Average Temperature': avg, 
              'Maximum Temperature': max} for min, avg, max in start_end_query]

    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)