from flask import Flask, request, jsonify, Response, render_template, redirect, url_for
from typing import Tuple
from app import app, db
from app.models import User, Team, Log
import requests
import datetime
from sqlalchemy import asc

def create_response(data: dict=None, status: int=200, message: str='') -> Tuple[Response, int]:
	if type(data) is not dict and data is not None:
		raise TypeError('Data should be a dictionary.')

	response = {
		'code': status,
		'success': 200 <= status < 300,
		'message': message,
		'result': data
	}
	return jsonify(response), status


@app.route('/slack-redirect', methods=['POST'])
def slack_redirect():
	command = request.values.get('text', None)
	response_url = request.values.get('response_url', None)
	user_id = request.values.get('user_id', None)
	response_type = 'ephemeral'
	if not response_url:
		#TODO add proper error handler
		return 'InternalError: no response url detected'
	if command == 'help':
		json = {'text': SUPPORT_MESSAGE}
		requests.post(response_url, json=json)
	elif command == 'game':
		json = get_game_url(user_id)	
		requests.post(response_url, json=json)	
	elif command == 'login':
		json = {'text': 'https://harmonia.space/team-view.html?team_id='+user_id, 'response_type': response_type}
		requests.post(response_url, json=json)
	else:
		json = {'text': INVALID_COMMAND_MESSAGE}
		requests.post(response_url, json=json)
	return "", 200


@app.route('/')
@app.route('/type.html', methods=['GET'])
def index():
        return render_template('type.html')


@app.route('/about.html')
def about():
        return render_template('about.html')


@app.route('/login.html')
@app.route('/login')
def login():
        return render_template('login.html')


@app.route('/team-view.html', methods=['GET'])
def team_view():
	if request:
		team_name = request.values.get('team_id', None)
		team = Team.query.filter_by(name=team_name).all()
		if team == []:
			team = Team.query.get(1)
	else:
		team = Team.query.get(1)
	times = []
	moods = []
	stresses = []
	current = datetime.datetime.now()
	oldest = Log.query.order_by(asc('timestamp')).limit(1).all()[0].timestamp
	while current > oldest:
		current -= datetime.timedelta(days=7)
		mood, stress = team.avg_mood_stress_at(current)
		if mood and stress:
			moods.append(mood)
			stresses.append(stress)
			times.append(current.strftime("%b %d %Y"))
	times.reverse()
	moods.reverse()
	stresses.reverse()
	return render_template('team-view.html', labels=times, mood_values=moods, stress_values=stresses)


# Log results from a game
@app.route('/add_log', methods=['POST'])
def add_log():
	user = User.query.get(request.values.get('user_id', None))
	if user:
		timestamp = request.values.get('timestamp', None)
		mood = request.values.get('mood', None)
		stress = request.values.get('stress', None)
		user.new_log(timestamp=timestamp, mood=mood, stress=stress)
		return create_response({'content': 'log created'})
	else:
		return create_response({'status': 400, 'content': 'invalid user_id'})


@app.route('/game')
def game():
	pass


@app.route('/add_user', methods=['POST'])
def add_user():
	name = request.values.get('name', None)
	db.save(User(name))
	return create_response({'content': 'user created'})


@app.route('/get_users', methods=['GET'])
def get_users():
	users = [str(u) for u in User.query.all()]
	return create_response({'content': users})


def get_game_url(user_id):
	return 'PLACEHOLDER'


def get_login_url(user_id):
	return 'PLACEHOLDER'


SUPPORT_MESSAGE = 'INSERT_SUPPORTIVE_MESSAGE AND FLUFFY UNICORNS HERE'
INVALID_COMMAND_MESSAGE = 'Illegal command!'
