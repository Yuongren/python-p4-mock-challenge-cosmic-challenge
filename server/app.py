#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_migrate import Migrate
from flask import Flask, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def home():
    return ''


# ---------- SCIENTISTS ----------

@app.get('/scientists')
def get_scientists():
    scientists = Scientist.query.all()
    return jsonify([
        s.to_dict(only=('id', 'name', 'field_of_study'))
        for s in scientists
    ]), 200


@app.get('/scientists/<int:id>')
def get_scientist_by_id(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    return jsonify(scientist.to_dict()), 200


@app.post('/scientists')
def create_scientist():
    try:
        scientist = Scientist(
            name=request.json.get('name'),
            field_of_study=request.json.get('field_of_study')
        )
        db.session.add(scientist)
        db.session.commit()
        return jsonify(scientist.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


@app.patch('/scientists/<int:id>')
def update_scientist(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    try:
        for attr in ['name', 'field_of_study']:
            if attr in request.json:
                setattr(scientist, attr, request.json[attr])

        db.session.commit()
        return jsonify(scientist.to_dict()), 202
    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


@app.delete('/scientists/<int:id>')
def delete_scientist(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    db.session.delete(scientist)
    db.session.commit()
    return jsonify({}), 204


# ---------- PLANETS ----------

@app.get('/planets')
def get_planets():
    planets = Planet.query.all()
    return jsonify([
        p.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star'))
        for p in planets
    ]), 200


# ---------- MISSIONS ----------

@app.post('/missions')
def create_mission():
    try:
        mission = Mission(
            name=request.json.get('name'),
            scientist_id=request.json.get('scientist_id'),
            planet_id=request.json.get('planet_id')
        )
        db.session.add(mission)
        db.session.commit()
        return jsonify(mission.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
