#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate 
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import config
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Connect to a local postgresql database

db = SQLAlchemy(app)
migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  group_venues = Venue.query.with_entities(func.count(Venue.id),Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  data = []
  for area in group_venues:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
      venue_data.append({
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.show_time > datetime.now()).all())
      })
    data.append({
      "city":area.city,
      "state":area.state,
      "venues":venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  search_response = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in search_response:
    data.append({
      "id":result.id,
      "name":result.name,
      "num_upcoming_shows":len(db.session.query(Show).filter(Show.venue_id==result.id).filter(Show.show_time > datetime.now()).all()),
    })
  response= {
    "count":len(search_response),
    "data":data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
    return render_template('errors/404.html')
  
  upcoming_show_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.show_time > datetime.now()).all()
  upcoming_shows = []

  past_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.show_time< datetime.now()).all()
  past_shows = []

  for show in upcoming_show_data:
    upcoming_shows.append({
      "artist_id":show.artist_id,
      "artist_name":show.Artist.name,
      "artist_image_link":show.Artist.image_link,
      "show_time":show.show_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  for show in past_shows_data:
    past_shows.append({
      "artist_id":show.artist_id,
      "artist_name":show.Artist.name,
      "artist_image_link":show.Artist.image_link,
      "show_time":show.show_time.strftime("%Y-%m-%d %H:%M:%S")
    })
    #print(len(past_shows))
  data = {
    "id":venue.id,
    "name":venue.genres,
    "address":venue.address,
    "city":venue.city,
    "state":venue.state,
    "phone":venue.phone,
    "image_link":venue.image_link,
    "website":venue.website,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "upcoming_shows":upcoming_shows,
    "past_shows":past_shows,
    "upcoming_shows_count":len(upcoming_shows),
    "past_shows_count":len(past_shows),
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    print("First")
    name = request.form['name']
    
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']

    genres = request.form.getlist('genres')
    #print()
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    
    seeking_talent = True if 'seeking_talent' in request.form else False 
    seeking_description = request.form['seeking_description']
    website = request.form['website']
    print("Second")
    

    venue = Venue(
      name=name,city=city,state=state,address=address,phone=phone,genres=genres,
      image_link=image_link,facebook_link=facebook_link,seeking_talent=seeking_talent,
      seeking_description=seeking_description,website=website)

    db.session.add(venue)
    db.session.commit()
  except:
    error=True 
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occured while Posting Venue'+request.form['name'])
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Endpoint for taking a venue_id, and using
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occured. Venue {venue_id} could not be deleted.')
  else:
    flash(f'Venue {venue_id} got deleted successfully.')
  return redirect(url_for("index"))
  # return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Implemented search on artists with partial string search(case-insensitive).
  search_term = request.form.get('search_term','')
  search_response = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in  search_response:
    data.append({
      "id":result.id,
      "name":result.name,
      "num_upcoming_shows":len(db.session.query(Show).filter(Show.artist_id==result.id).filter(Show.show_time > datetime.now()).all()),
    })
  
  response = {
    "count": len(search_response),
    "data":data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  artist_data = db.session.query(Artist).get(artist_id)

  if not artist_data:
    return render_template('errors/404.html')
  
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.show_time > datetime.now()).all()
  upcoming_shows = []

  past_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.show_time < datetime.now()).all()
  past_shows = []

  for show in upcoming_shows_data:
    upcoming_shows.append({
      "venue_id":show.venue_id,
      "venue_name":show.Venue.name,
      "venue_image_link":show.Venue.image_link,
      "start_time":show.show_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in past_shows_data:
    past_shows.append({
      "venue_id":show.venue_id,
      "venue_name":show.Venue.name,
      "venue_image_link":show.Venue.image_link,
      "start_time":show.show_time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
  data = {
    "id":artist_data.id,
    "name":artist_data.name,
    "genres":artist_data.genres,
    "city":artist_data.city,
    "state":artist_data.state,
    "phone":artist_data.phone,
    "website":artist_data.website,
    "image_link":artist_data.image_link,
    "facebook_link":artist_data.facebook_link,
    "seeking_venue":artist_data.seeking_venue,
    "seeking_description":artist_data.seeking_description,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
  }


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
    form.name.data = artist.name 
    form.city.data = artist.city,
    form.state.data = artist.state,
    form.phone.data = artist.phone,
    form.genres.data = artist.genres,
    form.facebook_link.data = artist.facebook_link,
    form.image_link.data = artist.image_link,
    form.website.data = artist.website,
    form.seeking_venue.data = artist.seeking_venue,
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE : take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False 
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

    db.session.commit() 

  except:
    error =True 
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured Whilte Updating Artist')
  else:
    flash('Details of Artist got updated successfuly')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name 
    form.city.data = venue.city,
    form.state.data = venue.state,
    form.phone.data = venue.phone,
    form.address.data = venue.address,
    form.genres.data = venue.genres,
    form.facebook_link.data = venue.facebook_link,
    form.image_link.data = venue.image_link,
    form.website.data = venue.website,
    form.seeking_talent.data = venue.seeking_talent,
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE : take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False 
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address'] 
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_venue = True if 'seeking_venue' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit() 

  except:
    error =True 
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured Whilte Updating Venue')
  else:
    flash('Details of Venue got updated successfuly')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    print("First")
    name = request.form['name']
    
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    
    genres = request.form.getlist('genres')
    
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    
    seeking_venue = True if 'seeking_venue' in request.form else False 
    seeking_description = request.form['seeking_description']
    website = request.form['website']
  

    artist = Artist(
      name=name,city=city,state=state,phone=phone,genres=genres,
      image_link=image_link,facebook_link=facebook_link,seeking_venue=seeking_venue,
      seeking_description=seeking_description,website=website)

    db.session.add(artist)
    db.session.commit()
  except:
    error=True 
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occured while Posting Artist'+request.form['name'])
  else:
    flash('Artist ' + request.form['name'] + ' is successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Displays list of shows at /shows
  shows_data = db.session.query(Show).join(Artist).join(Venue).all()
  print(shows_data)
  data = []

  for show in shows_data:
    data.append({
      "venue_id":show.venue_id,
      "venue_name":show.Venue.name,
      "artist_id":show.artist_id,
      "artist_name":show.Artist.name,
      "artist_image_link":show.Artist.image_link,
      "start_time":show.show_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False
  try:
    print("Hello")
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    print("Check")
    show_time = request.form['show_time']
    print("1")
    show = Show(artist_id=artist_id,venue_id=venue_id,show_time=show_time)
    print("2")
    db.session.add(show)
    print("3")
    db.session.commit()
    print('4')
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:
    flash('Show posted successfully')
  else:
    flash('An error occured while posting Show')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
