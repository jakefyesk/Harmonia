from app import db
from datetime import datetime
from sqlalchemy import desc

class Team(db.Model):
	__tablename__ = 'teams'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	manager = db.Column(db.String, nullable=False)
	team_mood = db.Column(db.Integer)
	team_stress = db.Column(db.Integer)
	users = db.relationship('User', backref='team', lazy='dynamic')

	# TODO get high_risk users
	@property
	def high_risk_users(self):
		return self.users.filter_by(User.high_risk).all()

	def update(self):
		self.mood, self.stress = self.avg_mood_stress_at(datetime.now())

	def avg_mood_stress_at(self, time, n=10):
		mood = 0
		stress = 0
		for user in self.users.all():
			mood_delta, stress_delta = user.avg_mood_stress_at(time)
			mood = mood + mood_delta if mood_delta else mood
			stress = stress + stress_delta if stress_delta else stress
		if mood > 0:
			mood /= self.users.count()
		else:
			mood = None
		if stress > 0:
			stress /= self.users.count() 
		else:
			stress = None
		return mood, stress

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=True)
	position = db.Column(db.String)
	age = db.Column(db.Integer)
	mood = db.Column(db.Float)
	stress = db.Column(db.Float)
	high_risk = db.Column(db.Boolean, default=False)
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	logs = db.relationship('Log', backref='user', lazy='dynamic')
	
	def __repr__(self):
		if self.name:
			return '<User {}>'.format(self.name)
		else:
			return '<Anonymous user>'
	
	def new_log(self, mood, stress, timestamp=datetime.now()):
		db.save(Log(timestamp=timestamp, mood=mood, stress=stress, user=self))
		self.update()
	
	def update(self):
		mood, stress = self.avg_mood_stress_at(datetime.now())
		self.check_risk()
		team = Team.query.get(self.team_id)
		if team:
			team.update()

	def avg_mood_stress_at(self, time, n=10):
		sample_logs = self.logs.filter(Log.timestamp<time).order_by(desc('timestamp')).limit(n)
		mood = 0
		stress = 0
		for log in sample_logs.all():
			mood += log.mood
			stress += log.stress
		if mood > 0:
			mood /= sample_logs.count()
		else:
			mood = None
		if stress > 0:
			stress /= sample_logs.count()
		else:
			stress = None
		return mood, stress
	
	def check_risk(self, n=10):
		#TODO
		pass 


class Log(db.Model):
	__tablename__ = 'logs'

	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime)
	accuracy = db.Column(db.Float)
	speed_s = db.Column(db.Float)
	mood = db.Column(db.Integer)
	stress = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
