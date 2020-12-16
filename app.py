import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home(): 
    """Listing all available api routes."""
    return ( 
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br/>"
        f"Replace 'start_date' and 'end_date' using the YYYY-MM-DD format."
    )
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returning list of precipitation data"""
    # Querying all dates and precipitation values
    query1 = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_list = []

    for date, prcp in query1: 
        dict1 = {}
        dict1["date"] = date
        dict1["prcp"] = prcp
        prcp_list.append(dict1)

    return jsonify(prcp_list)
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returning list of stations"""
    # Query all stations
    query2 = session.query(Station.station, Station.name).all()

    session.close()

    station_list = []

    for station, name in query2: 
        dict2 = {}
        dict2["station"] = station
        dict2["name"] = name
        station_list.append(dict2)

    return jsonify(station_list)
#################################################
@app.route("/api/v1.0/tobs")
def tobs(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returning list of temperature data for most active station"""
    # Querying  most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Station.name).\
        filter(Measurement.station == Station.station).\
        order_by(func.count(Measurement.prcp).desc()).first()[0]

    # --- Calculating last date in the DB
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # --- Transforming query to a time object
    last_date_converted = (dt.datetime.strptime(last_date, "%Y-%m-%d")).date()
    # --- Calculating last date in the DB - 1 year ago
    year_ago = last_date_converted - dt.timedelta(days = 365)

    # Querying date and temperature data 
    date_temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.date <= last_date).all()

    session.close()

    tobs_list = []

    for date, tobs in date_temperature: 
        dict3 = {}
        dict3["date"] = date
        dict3["tobs"] = tobs
        tobs_list.append(dict3)

    return jsonify(tobs_list)
#################################################
@app.route("/api/v1.0/<start>")
def start_only(start):
    """Returning list of tmin, tavg and tmmax"""

    start_date = start.split("-")
    canonicalized = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))   

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Querying data
    query3 = session.query(
        Measurement.date, 
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= canonicalized).\
        group_by(Measurement.date).all()

    session.close()

    normals = []

    for date, tmin, tavg, tmax in query3: 
        dict4 = {}
        dict4["date"] = date
        dict4["min"] = tmin
        dict4["avg"] = tavg
        dict4["max"] = tmax
        normals.append(dict4)

    return jsonify(normals)
#################################################
@app.route("/api/v1.0/<start>/<end>")
def end_start(start, end): 

    start_date = start.split("-")
    canonicalized_start = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))

    end_date = end.split("-")
    canonicalized_end = dt.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))   

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Querying data
    query4 = session.query(
        Measurement.date, 
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= canonicalized_start).\
        filter(Measurement.date <= canonicalized_end).\
        group_by(Measurement.date).all()
    
    session.close()

    normals2 = []

    for date, tmin, tavg, tmax in query4: 
        dict5 = {}
        dict5["date"] = date
        dict5["min"] = tmin
        dict5["avg"] = tavg
        dict5["max"] = tmax
        normals2.append(dict5)

    return jsonify(normals2)  
#################################################
if __name__ == '__main__':
    app.run(debug=True)