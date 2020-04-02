# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import logging
import sys
from datetime import date, datetime
from logging import FileHandler, Formatter

import babel as babel
import dateutil
import dateutil.parser
from flask import Flask, flash, render_template, request, abort, jsonify, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment
from dataclasses import dataclass
from typing import List

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from sqlalchemy import ARRAY, func
from sqlalchemy.sql import expression

from forms import ShowForm, ArtistForm, VenueForm

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

@dataclass
class Venue(db.Model):
    __tablename__ = 'Venue'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    city: str = db.Column(db.String(120), nullable=False)
    state: str = db.Column(db.String(120), nullable=False)
    address: str = db.Column(db.String(120), nullable=False)
    phone: str = db.Column(db.String(120), nullable=True)
    image_link: str = db.Column(db.String(500), nullable=True)
    facebook_link: str = db.Column(db.String(120), nullable=True)
    genres: List = db.Column(ARRAY(db.String(120)), nullable=True)
    seeking_talent: bool = db.Column(db.Boolean, server_default=expression.true(), nullable=False)
    seeking_description: str = db.Column(db.String(120), nullable=True)

    def asdict(self):
        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state, 'address': self.address,
                'phone': self.phone, 'genres': self.genres, 'image_link': self.image_link,
                'facebook_link': self.facebook_link, 'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description}


@dataclass
class Artist(db.Model):
    __tablename__ = 'Artist'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    city: str = db.Column(db.String(120), nullable=False)
    state: str = db.Column(db.String(120), nullable=False)
    phone: str = db.Column(db.String(120), nullable=True)
    image_link: str = db.Column(db.String(500), nullable=True)
    facebook_link: str = db.Column(db.String(120), nullable=True)
    genres: List = db.Column(ARRAY(db.String(120)), nullable=True)
    seeking_venue: bool = db.Column(db.Boolean, server_default=expression.true(), nullable=False)
    seeking_description: str = db.Column(db.String(120), nullable=True)

    def asdict(self):
        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state, 'phone': self.phone,
                'genres': self.genres, 'image_link': self.image_link, 'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description}

@dataclass
class Show(db.Model):
    __tablename__ = 'Show'
    venue_id: int = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False, primary_key=True)
    artist_id: int = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False,  primary_key=True)
    start_time: datetime = db.Column(db.DateTime, nullable=False,  primary_key=True)
    venue = db.relationship('Venue', backref=db.backref('artist_association'))
    artist = db.relationship('Artist', backref=db.backref('venue_association'))

    def asdict(self):
        return {'id': self.id, 'venue_id': self.venue_id, 'artist_id': self.artist_id, 'start_time': self.start_time}


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


# Addressing a weird serialization error
def fix_json_array(obj, attr):
    arr = getattr(obj, attr)
    if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
        print("Incorrect format")
        print(arr)
        arr = arr[1:-1]
        arr = ''.join(arr).split(",")
        setattr(obj, attr, arr)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Group location by city and state.
    # Query each venue based on such condition
    # Calculate upcoming show
    # Build result dictionary
    locations = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    response = []
    for location in locations:
        venue_arr = []
        venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == location.city)\
            .filter(Venue.state == location.state).all()
        for venue in venues:
            # Is this even required by the View
            upcoming_num = Show.query. \
                filter(Show.start_time >= date.today()). \
                filter(Show.venue.has(id=venue.id)). \
                count()
            venue_dict = {"id": venue.id, "name": venue.name, "num_upcoming_shows": upcoming_num}
            venue_arr.append(venue_dict)
        response_item = {"city": location.city, "state": location.state, "venues": venue_arr}
        response.append(response_item)
    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    #venues = Venue.query.filter(Venue.name.contains(request.form.get('search_term', ''))).all() Case sensitive
    venues = Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term', '')}%")).all() # Case insensitive
    print(venues)
    count = 0
    data = []
    for venue in venues:
        count += 1
        upcoming_num = Show.query. \
            filter(Show.start_time >= date.today()). \
            filter(Show.venue.has(id=venue.id)). \
            count()
        body = {"id": venue.id, "name": venue.name, "num_upcoming_shows": upcoming_num}
        data.append(body)


    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    # I am new to Python, SQL+ORM so here is my attempt
    # Get Venue based on ID
    # Each Venue make another query to return list of upcoming and past shows
    # Use the information to create a custom dictionary for view

    row = Venue.query.get(venue_id)
    # Query upcoming show based on venue ID
    upcoming = db.session.query(Show, Artist).\
        filter(Show.start_time >= date.today()).\
        filter(Show.venue.has(id=row.id)). \
        filter(Show.artist_id == Artist.id). \
        all()
    # Query past show based on venue ID
    past = db.session.query(Show, Artist).\
        filter(Show.start_time < date.today()).\
        filter(Show.venue.has(id=row.id)). \
        filter(Show.artist_id == Artist.id). \
        all()
    upcoming_resp = []
    upcoming_count = 0
    for i in upcoming:
        body = {"artist_id": i.Show.artist_id, "artist_name": i.Artist.name, "artist_image_link": i.Artist.image_link,
                "start_time": i.Show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}
        upcoming_resp.append(body)
        upcoming_count += 1
    past_resp = []
    past_count = 0
    for i in past:
        body = {"artist_id": i.Show.artist_id, "artist_name": i.Artist.name, "artist_image_link": i.Artist.image_link,
            "start_time": i.Show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}
        past_resp.append(body)
        past_count += 1
    row = row.asdict()
    row["past_shows"] = past_resp
    row["past_shows_count"] = past_count
    row["upcoming_shows"] = upcoming_resp
    row["upcoming_shows_count"] = upcoming_count

    return render_template('pages/show_venue.html', venue=row)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    # called upon submitting the new artist listing form

    try:
        # Future reference: Maybe the data should probably be sanitized before comitting to DB?
        venue = Venue(**request.form)  # Deserialize into artist object
        if venue.seeking_talent == 'y':
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.genres = request.form.getlist('genres')
        error = False
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form["name"] + ' could not be listed.')
    else:
        flash('Venue ' + request.form["name"] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        error = False
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred while deleting Venue ' + venue_id )
    else:
        flash('Venue ' + venue_id + ' was deleted successfully')
    return render_template('pages/home.html')

    return None

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Dataclass decorator will take care of serialization to dictionary / JSON
    query = Artist.query.all()
    for item in query:
        fix_json_array(item, "genres")
    return render_template('pages/artists.html', artists=query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists = Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%")).all()
    count = 0
    data = []
    for artist in artists:
        count += 1
        upcoming_num = Show.query. \
            filter(Show.start_time >= date.today()). \
            filter(Show.artist.has(id=artist.id)). \
            count()
        body = {"id": artist.id, "name": artist.name, "num_upcoming_shows": upcoming_num}
        data.append(body)

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id

    artist = Artist.query.get(artist_id)
    fix_json_array(artist, "genres")
    # Query upcoming show based on venue ID
    upcoming = db.session.query(Show, Venue). \
        filter(Show.artist.has(id=artist_id)). \
        filter(Show.start_time >= date.today()). \
        filter(Show.venue_id == Venue.id). \
        all()
    # Query past show based on venue ID
    past = db.session.query(Show, Venue). \
        filter(Show.artist.has(id=artist_id)). \
        filter(Show.start_time < date.today()). \
        filter(Show.venue_id == Venue.id). \
        all()
    upcoming_resp = []
    upcoming_count = 0
    for i in upcoming:
        body = {"venue_id": i.Show.venue_id, "venue_name": i.Venue.name, "venue_image_link": i.Venue.image_link,
                "start_time": i.Show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}
        upcoming_resp.append(body)
        upcoming_count += 1
    past_resp = []
    past_count = 0
    for i in past:
        body = {"venue_id": i.Show.venue_id, "venue_name": i.Venue.name, "venue_image_link": i.Venue.image_link,
                "start_time": i.Show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}
        past_resp.append(body)
        past_count += 1
    artist = artist.asdict()
    artist["past_shows"] = past_resp
    artist["past_shows_count"] = past_count
    artist["upcoming_shows"] = upcoming_resp
    artist["upcoming_shows_count"] = upcoming_count
    print(upcoming)
    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        fix_json_array(artist, "genres")
        form = ArtistForm(**artist.asdict())
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    except:
        abort(500)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    try:
        # Deserialize form into Artist object
        genres = request.form.getlist('genres')
        data = Artist(**request.form)
        if data.seeking_venue == 'y':
            data.seeking_venue = True
        else:
            data.seeking_venue = False
        # Fill out the missing info from the form with ones from the database
        data.id = artist_id
        data.genres = genres
        # Making the updates
        error = False
        artist = Artist.query.filter_by(id=artist_id).update(data.asdict())
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form["name"] + ' could not be updated.')
    else:
        flash('Artist ' + request.form["name"] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        fix_json_array(venue, "genres")
        form = VenueForm(**venue.asdict())
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except:
        abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    try:
        # Deserialize form into Artist object
        genres = request.form.getlist('genres')
        data = Venue(**request.form)
        # Fill out Venue missing info from the form with ones from the database
        data.id = venue_id
        data.genres = genres
        if data.seeking_talent == 'y':
            data.seeking_talent = True
        else:
            data.seeking_talent = False
        # Making the updates
        error = False
        Venue.query.filter_by(id=venue_id).update(data.asdict())
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form["name"] + ' could not be updated.')
    else:
        flash('Venue ' + request.form["name"] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist = Artist(**request.form)
        artist.genres = request.form.getlist('genres')
        if artist.seeking_venue == 'y':
            artist.seeking_venue = True
        else:
            artist.seeking_venue = False
        error = False
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')
    else:
        flash('Artist ' + request.form["name"] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Only show upcoming shows.
    q = db.session.query(Show, Venue, Artist).join(Artist).join(Venue).filter(Show.start_time >= date.today()).all()
    response = []
    for row in q:
        item = {"venue_id": row.Venue.id, "venue_name": row.Venue.name, "artist_id": row.Artist.id,
                "artist_name": row.Artist.name, "artist_image_link": row.Artist.image_link,
                "start_time": row.Show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}
        response.append(item)

    return render_template('pages/shows.html', shows=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(**request.form)
        error = False
        print(show)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. The show could not be listed.')
    else:
        flash('A show was successfully listed!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
