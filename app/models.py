from app import db

user_tag_association_table = db.Table(
    'user_tag_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.PrimaryKeyConstraint('user_id', 'tag_id')
)

request_tag_association_table = db.Table(
    'request_tag_association',
    db.Column('request_id', db.Integer, db.ForeignKey('request.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.PrimaryKeyConstraint('request_id', 'tag_id')
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    phone_number = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    radius = db.Column(db.Float)
    device_id = db.Column(db.String(256), unique=True)
    account_id = db.Column(db.String(256), unique=True)
    
    requests = db.relationship('Request', backref='user', lazy='dynamic')
    tags = db.relationship('Tag', secondary=user_tag_association_table, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    image_url = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    claimed = db.Column(db.Integer, default=-1)
    price = db.Column(db.Float)
    breaker_name = db.Column(db.String(64), nullable=True)
    fixer_name = db.Column(db.String(64), nullable=True)

    tags = db.relationship('Tag', secondary=request_tag_association_table, backref=db.backref('requests', lazy='dynamic'), lazy='dynamic')    

    def __repr__(self):
        return '<Request %r>' % (self.title[:10])
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(64), unique=True)
