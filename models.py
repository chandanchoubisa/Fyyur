from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres= db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(100))
    shows = db.relationship('Show',cascade='all,delete',backref='Venue',lazy=True)

    def __repr__(self):
      return 'Venue {}'.format(self.name)
    


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres= db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(100))
    seeking_venue=db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show',backref='Artist',lazy=True)
    

    def __repr__(self):
      return 'Artist {}'.format(self.name)


class Show(db.Model):
  __tablename__='Show'

  id=db.Column(db.Integer,primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  show_time = db.Column(db.DateTime,nullable=False)

  def __repr__(self):
      return 'Show {} {}'.format(self.venue_id,self.artist_id)



