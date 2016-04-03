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

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}
		
class Request(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	image_encoded = db.Column(db.Text)
	description = db.Column(db.String(1000))
	geo = db.Column(db.String(64))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Request %r>' % (self.title[:10])
	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}
