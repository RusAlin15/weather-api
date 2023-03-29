from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)

stations = pd.read_csv('resources/stations.txt', skiprows=17)
stations = stations[["STAID", "STANAME                                 ", 'CN']]
stations.rename(columns={"STANAME                                 ": "Station Name",
                         "STAID": "Station ID", 'CN': 'Country Code'}, inplace=True)
stations.replace('^\s+', '', regex=True, inplace=True)
stations.replace('\s+$', '', regex=True, inplace=True)


@app.route('/')
def home():
    return render_template("home.html", data=stations.to_html(index=False))


@app.route('/country/<country>')
def country(country):
    country = country.upper()
    st = stations.loc[stations['Country Code'] == country]
    if st.empty:
        return f"For inserted country: {country} wasn't found any station!"
    result = st.to_dict(orient="records")
    return result


@app.route('/spec-temp/<sta_id>/<date>')
def spec_temp(sta_id, date):
    st = read_file(sta_id)
    pr = st.loc[st['Date'] == date]

    if pr.empty:
        return f"For inserted date, there wasn't found any entry!"
    result = pr.to_dict(orient="records")
    return result


@app.route('/station-name/<sta_id>')
def get_station_name(sta_id):
    print(sta_id)
    result = {}
    result["Station Name"] = str(stations.loc[stations['Station ID'] == int(sta_id)]['Station '
                                                                                     'Name'].squeeze())
    if result is "":
        return f"For inserted country: {country} wasn't found any station!"
    return result


@app.route('/station-id/<station_name>')
def get_station_id(station_name):
    station_name = station_name.upper()
    result = {}
    result["Station ID"] = str(stations.loc[stations['Station Name'] == station_name]['Station ' \
                                                                                      'ID'].squeeze())
    if result is "":
        return f"For inserted country: {country} wasn't found any station!"
    return str(result)


@app.route('/station/<sta_id>')
def all_from_station(sta_id):
    st = read_file(sta_id)
    if st.empty:
        return f"For inserted country: {country} wasn't found any station!"
    result = st.to_dict(orient="records")
    return result


@app.route('/yearly/<sta_id>/<date>')
def all_from_years(sta_id, date):
    date = date.split('-')
    st = read_file(sta_id)
    result = []
    for index, row in st.iterrows():
        if str(row['Date']).split('-')[1] == date[0] and str(row['Date']).split('-')[2][:2] == date[
            1]:
            result.append({
                "Date": row['Date'],
                "Quality Code": row['Quality Code'],
                "Station ID": row['Station ID'],
                "Temperature": row['Temperature']
            })
    if st.empty:
        return f"For inserted country: {country} wasn't found any station!"
    return result


def read_file(sta_id):
    file_name = "resources/" + "TG_STAID" + str(sta_id).zfill(6) + ".txt"
    st = pd.read_csv(file_name, skiprows=20, parse_dates=["    DATE"])
    st.replace('^\s+', '', regex=True, inplace=True)
    st.replace('\s+$', '', regex=True, inplace=True)
    st['TG0'] = st['   TG'].mask(st['   TG'] == -9999, np.nan)
    st['TG'] = st['TG0'] / 10
    st.rename(columns={"    DATE": "Date", " Q_TG": "Quality Code",
                       "STAID": "Station ID", 'TG': 'Temperature'}, inplace=True)
    st = st[['Station ID', 'Date', 'Quality Code', 'Temperature']]
    return st


@app.route("/examples")
def examples():
    return render_template("examples.html")


@app.route("/test")
def test_yourself():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(debug=True)
