#   Routes
#
#       * `/api/v1.0/precipitation`
#           * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
#       * `/api/v1.0/stations`
#           * Return a json list of stations from the dataset.
#       * `/api/v1.0/tobs`
#           * Return a json list of Temperature Observations (tobs) for the previous year
#       * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#           * Return a json list of the minimum temperature, the average temperature, and
#               the max temperature for a given start or start-end range.
#           * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates
#               greater than and equal to the start date.
#           * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX`
#               for dates between the start and end date inclusive.

# dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# set up
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect database
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# Table References
Station = Base.classes.station
Measurement = Base.classes.measurement

# creates session link from python to database
session = Session(engine)

# set up Flask
app = Flask(__name__)

# flask Routes
@app.route("/")
def landing():
    return(
    f"<a href='/api/v1.0/precipitation'>Precipitation</a><br/>"
    f"<a href='/api/v1.0/stations'>Stations</a><br/>"
    f"<a href='/api/v1.0/tobs'>Temps from All Stations</a><br/>"
    f"<a href='/api/v1.0/precipitation'>Precipitation</a><br/>"
    f"/api/v1.0/-ymd-start_date<br/>"
    f"api/v1.0/-ymd-start/-ymd-end<br/>")

# precipitation

@app.route("/api/v1.0/precipitation")
def precipitation():
    #return precipitation for prior year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 9) - dt.timedelta(days=365)
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    #return a json of the totals
    rain_total = []
    for rain in precip:
        row = {}
        row['date'] = precip[0]
        row['prcp'] = precip[1]
        rain_total.append(row)

    return jsonify(rain_total)

# stations
@app.route('/api/v1.0/stations')
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

# tobs
@app.route("/api/v1.0/tobs")
def tobs():
    #return temp list for prior year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 9) - dt.timedelta(days=365)
    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    temp_total = []
    for temp in temps:
        row = {}
        row['date'] = temps[0]
        row['prcp'] = temps[1]
        temp_total.append(row)

    return jsonify(temp_total)


# start
@app.route('/api/v1.0/<start>')
def trip1(start):

    # go back one year from start date and go to end of data for min/avg/max temp
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = dt.date(2017, 8, 1)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

# start and end
@app.route('/api/v1.0/<start>/<end>')
def trip2(start, end):

    # go back one year from start and date and go to end of data for min/avg/max temp
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


if __name__ == "__main__":
    app.run(debug=True)
