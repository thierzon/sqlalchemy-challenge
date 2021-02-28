#################################################
# Dependencies 
#################################################
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date --> date format: YYYY-MM-DD<br/>"
        f"/api/v1.0/start_date/end_date --> date format: YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = "2016-08-23"

    # Query the measurement database
    results = session.query(Measurement.date, Measurement.prcp).filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date)\
    .order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the measurement database
    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()

    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = "2016-08-23"

    # Query the measurement database
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date)\
    .order_by(Measurement.date).all()

    session.close()
  
    # Create a dictionary from the row data and append to a list of precipitation data
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the measurement database
    temp_results = session.query(Measurement.tobs).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()
    temp_results = np.ravel(temp_results)

    temp_dates = session.query(Measurement.date).group_by(Measurement.date).all()
    temp_dates = np.ravel(temp_dates)

    session.close()

    # Create a dictionary and add to list if start date is listed in the meusurement database
    for date in temp_dates:

        if date == start:
            temp_list = []
            temp_dict = {}
            temp_dict["TAVG"] = (sum(temp_results) / len(temp_results))
            temp_dict["TMIN"] = min(temp_results)
            temp_dict["TMAX"] = max(temp_results)
            temp_list.append(temp_dict)
            return jsonify(temp_list)

    return jsonify({"error": "Date not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the measurement database
    temp_results = session.query(Measurement.tobs).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)\
    .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).all()
    temp_results = np.ravel(temp_results)

    temp_dates = session.query(Measurement.date).group_by(Measurement.date).all()
    temp_dates = np.ravel(temp_dates)

    session.close()

    # Create a dictionary and add to list if start and end dates are listed in the meusurement database
    for date in temp_dates:

        if date == start:

            for date in temp_dates:

                if date == end:
                    temp_list = []
                    temp_dict = {}
                    temp_dict["TAVG"] = (sum(temp_results) / len(temp_results))
                    temp_dict["TMIN"] = min(temp_results)
                    temp_dict["TMAX"] = max(temp_results)
                    temp_list.append(temp_dict)
                    return jsonify(temp_list)

    return jsonify({"error": "Date not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)