# Task 1: Setting Up Flask with Flask-SQLAlchemy
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:********@127.0.0.1/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSessionSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    workout_sessions = db.relationship('WorkoutSession', backref='member')

class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    session_date = db.Column(db.Date)
    session_time = db.Column(db.String(50))
    activity = db.Column(db.String(255))

# Task 2: Implementing CRUD Operations for Members Using ORM
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200

# Task 3: Managing Workout Sessions with ORM
@app.route('/workout-sessions', methods=['GET'])
def get_workout_sessions():
    workout_sessions = WorkoutSession.query.all()
    return workout_sessions_schema.jsonify(workout_sessions)

@app.route('/workout-sessions', methods=['POST'])
def add_workout_session():
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_workout_session = WorkoutSession(session_id=workout_session_data['session_id'], member_id=workout_session_data['member_id'], session_date=workout_session_data['session_date'], session_time=workout_session_data['session_time'], activity=workout_session_data['activity'])
    db.session.add(new_workout_session)
    db.session.commit()
    return jsonify({"message": "New workout session added successfully"}), 201

@app.route('/workout-sessions/<int:id>', methods=['PUT'])
def update_workout_session(id):
    workout_session = WorkoutSession.query.get_or_404(id)
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout_session.member_id = workout_session_data['member_id']
    workout_session.session_date = workout_session_data['session_date']
    workout_session.session_time = workout_session_data['session_time']
    workout_session.activity = workout_session_data['activity']
    db.session.commit()
    return jsonify({"message": "Workout session details updated successfully"}), 200

@app.route('/workout-sessions/by-member', methods=['GET'])
def query_workout_sessions_by_member():
    name = request.args.get('name')
    member = Member.query.filter(Member.name == name).first()
    if member:
        return workout_sessions_schema.jsonify(member.workout_sessions)
    else:
        return jsonify({"message": "Member not found"}), 404
    
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)