from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	phone_number = db.Column(db.Integer)
	geo = db.Column(db.String(64))
	radius = db.Column(db.Float)
	requests = db.relationship('Request', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.name)

class Request(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	image_encoded = db.Column(db.String(256))
	geo = db.Column(db.String(64))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Request %r>' % (self.title[:10])