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
        f"<a herf='/api/v1.0/precipitation'>Precipitation</a><br/>"
        f"<a herf='/api/v1.0/stations'>Stations</a><br/>"
        f"<a herf='/api/v1.0/tobs'>Temp Observations</a><br/>"
        f"<a herf='/api/v1.0/<start>'></a><br/>"
        f"<a herf='/api/v1.0/<start>/<end>'></a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create link
    session = Session(engine)

    #query last 12 months of precopitation
    scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= '2016-08-23', measurement.date <= '2017-08-23').\
    order_by(measurement.date).all()

    #dictionary for the row data and append to a list using date as the key and prcp as the value
    precipitation_list = []
    for score in scores:
        row = {"date": "prcp"}
        row["date"] = score[0]
        row["prcp"]= float(score[1])
        precipitation_list.append(row)
    
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def station():
    #create link
    session = Session(engine)

    #query all stations from the station dataset
    stations = session.query(station.station, station.name).group_by(station.station).all()

    #stations are going to be in toupels so we need to unpack them
    all_results = list(np.ravel(stations))

    return jsonify(all_results)


@app.route("/api/v1.0/tobs")
def tobs():
    #create link
    session = Session(engine)

    #query the dates and temperature observations of the most active station for the last year of data
    temp_list = []
    results = session.query(measurement.station, measurement.tobs).filter(measurement.station == "USC00519281").\
        filter(func.strftime('%Y-%m-%d', measurement.date) >= dt.date(2016, 8, 23)).all()
    temp_list.append(results)

    

if __name__ == '__main__':
    app.run(debug=True)