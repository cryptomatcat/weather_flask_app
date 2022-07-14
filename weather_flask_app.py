from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import sys
import json
import os

APIkey = "873eca48628b8f3a65180c195f7356ad"
url = "https://api.openweathermap.org/data/2.5/weather"
app = Flask(__name__)

app.config.update(SECRET_KEY=os.urandom(9876))

# file_path = os.path.dirname(sys.argv[0])  # path to directory app.py is in
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///weather.db"

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    degree = db.Column(db.Integer, unique=False, nullable=False)
    state = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return "<city name %r>" % self.name


db.create_all()


@app.route("/")
def index():
    cards = City.query.all()
    return render_template("index.html", cards=cards)


@app.route("/add", methods=["POST"])
def add_city():
    cities_list = []
    for row in City.query.all():
        cities_list.append(row.name)

    city_name = request.form.get("city_name")
    dict_param = {"q": city_name, "appid": APIkey}
    r = requests.get(url, params=dict_param)

    if r.status_code != 404 and r.status_code != 400:
        dict_with_weather_info = json.loads(r.text)
        new_city = City(
            name=city_name,
            degree=dict_with_weather_info["main"]["temp"],
            state=dict_with_weather_info["weather"][0]["main"],
        )
        if city_name in cities_list:
            flash("The city has already been added to the list!")
        else:
            db.session.add(new_city)
            db.session.commit()
    elif (r.status_code == 404) or (r.status_code == 400):
        flash("The city doesn't exist!")
    return redirect(url_for("index"))


@app.route("/delete/<city_id>", methods=["GET", "POST"])
def delete(city_id):
    try:
        city = City.query.filter_by(id=city_id).first()
        db.session.delete(city)
        db.session.commit()
        flash("The city has been deleted!")
    except:
        pass
    return redirect(url_for("index"))


# don't change the following way to run flask:
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(":")
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
