from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	phone_number = db.Column(db.Integer)
	requests = db.relationship('Request', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.name)

class Request(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	image_url = db.Column(db.String(256))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))