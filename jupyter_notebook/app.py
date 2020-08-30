# Ignore SQLITE warnings related to Decimal numbers in the database might not need
import warnings
warnings.filterwarnings('ignore')

#Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

##################
# Database Setup #
##################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

#reflect into new model
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

#save references
measurement = Base.classes.measurement
station = Base.classes.station

###############
# Flask Setup #
###############
app = Flask(__name__)

#set up routes for what is needed
@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>Stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>Temp Observations</a><br/>"
        f"<a href='/api/v1.0/start'>Start Date for trip: Enter YYYY-MM-DD in URL</a><br/>"
        f"<a href='/api/v1.0/start/end'>Temp Averages on trip: Enter YYYY-MM-DD/YYYY-MM-DD in URL</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create link
    session = Session(engine)
    #query last 12 months of precopitation
    scores = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').all()
    
    
    session.close()

    #dictionary for the row data and append to a list using date as the key and prcp as the value
    precipitation_list = []
    for date, prcp in scores:
        precp_dict = {}
        precp_dict["date"] = date
        precp_dict["prcp"] = prcp
        precipitation_list.append(precp_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    #query all stations from the station dataset
    stations = session.query(station.station, station.name).all()
    #stations are going to be in toupels so we need to unpack them
    all_results = list(np.ravel(stations))
    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def tobs():
    #create link
    session = Session(engine)
    #query the dates and temperature observations of the most active station for the last year of data
   
    results = session.query(measurement.station, measurement.tobs).filter(measurement.station == "USC00519281").\
        filter(func.strftime('%Y-%m-%d', measurement.date) >= dt.date(2016, 8, 23)).all()
    
    session.close()

    tobs_results = list(np.ravel(results))
    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
def one_day(start = 'start_date'):
    #create link
    session = Session(engine)
    #set up for user to enter a date in Y-m-d format
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()

    #query the min, avg, and max temps for a given start date
    stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    session.close()

    #create list for query
    returns_list = []
    date_dict = {'Trip Start Date': start}
    returns_list.append(date_dict)
    returns_list.append({'Observation': 'Tmin', 'Temperature': stats[0][0]})
    returns_list.append({'Observation': 'Tavg', 'Temperature': stats[0][1]})
    returns_list.append({'Observation': 'Tmax', 'Temperature': stats[0][2]})

    # summ_stats = list(np.ravel(returns_list))
    return jsonify(returns_list)
   
@app.route('/api/v1.0/<start>/<end>')
def start_end(start = 'start_date', end = 'end_date'):
    #create link
    session = Session(engine)
    #set up user to enter a date in Y-m-d format
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()

    #query the min, avg, and max temps for a given start date and end date
    stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date, measurement.date <= end_date).all()
    session.close()

    summ_stats = list(np.ravel(stats))
    return jsonify(f"Average of Low, Overall Average, and High Tempatures during trip: {summ_stats}")

if __name__ == '__main__':
    app.run(debug=True)