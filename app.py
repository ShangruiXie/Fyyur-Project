#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __init__(self, name, city, state, address, phone, image_link, genres, facebook_link, website, seeking_talent=False, seeking_description=""):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.genres = genres
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    def shortDetail(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def longDetail(self):
        return {
            'id': self.id,
            'name': self.name,
            'city':  self.city,
            'state': self.state
        }

    def allDetail(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': self.genres,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __init__(self, name, city, state, phone, genres, image_link, website, facebook_link, seeking_venue=False, seeking_description=""):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.website = website
        self.facebook_link = facebook_link

    def shortDetail(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def allDetail(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'website': self.website,
            'facebook_link': self.facebook_link
        }


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def allDetail(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artiist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def artisitDetail(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artiist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def venueDetail(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time
        }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    data = []
    city = ""
    state = ""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venue_result = Venue.query.group_by(
        Venue.id, Venue.city, Venue.state).all()

    for venue in venue_result:
        upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > current_time).all()
        upcoming_shows_count = len(upcoming_shows)

        if city == venue.city and state == venue.state:
            data[len(data) - 1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcomping_shows": upcoming_shows_count
            })
        else:
            city = venue.city
            state = venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcomping_shows": upcoming_shows_count
                }]
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venue_result = Venue.query.filter(Venue.name.ilike(
        '%' + request.form['search_term'] + '%')).all()
    venues = []
    for venue in venue_result:
        venues = list(map(Venue.shortDetail, venue_result))
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        venue_detail = Venue.allDetail(venue)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # past shows
        past_shows_result = Show.query.join(Artist).filter(
            Show.venue_id == venue_id).filter(Show.start_time <= current_time)
        past_shows = list(map(Show.artisitDetail, past_shows_result))
        venue_detail["past_shows"] = past_shows
        venue_detail["past_shows_count"] = len(past_shows)
        # upcoming shows
        upcoming_shows_result = Show.query.join(Artist).filter(
            Show.venue_id == venue_id).filter(Show.start_time > current_time)
        upcoming_shows = list(map(Show.artisitDetail, upcoming_shows_result))
        venue_detail["upcoming_shows"] = upcoming_shows
        venue_detail["upcoming_shows_count"] = len(upcoming_shows)

        return render_template('pages/show_venue.html', venue=venue_detail)
    else:
        return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            # seeking_talent=False,
            # seeking_description=""
        )
        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists_result = Artist.query.all()
    data = list(map(Artist.shortDetail, artists_result))
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    artists_result = Artist.query.filter(Artist.name.ilike(
        '%' + request.form['search_term'] + '%')).all()
    data = list(map(Artist.shortDetail, artists_result))
    Response = {
        'count': len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_result = Artist.query.get(artist_id)
    if not artists_result:
        return render_template('errors/404.html')

    artists_detail = Artist.allDetail(artist_result)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # past shows
    past_shows_result = Show.query.join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time <= current_time)
    past_shows = list(map(Show.venueDetail, past_shows_result))
    artists_detail["past_shows"] = past_shows
    artists_detail["past_shows_count"] = len(past_shows)
    # upcoming shows
    upcoming_shows_result = Show.query.join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time > current_time)
    upcoming_shows = list(map(Show.venueDetail, upcoming_shows_result))
    artists_detail["upcoming_shows"] = upcoming_shows
    artists_detail["upcoming_shows_count"] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_result = Artist.query.get(artist_id)
    if not artists_result:
        return render_template('errors/404.html')
    form.name.data = artist_result.name
    form.city.data = artist_result.city
    form.state.data = artist_result.state
    form.phone.data = artist_result.phone
    form.genres.data = artist_result.genres
    form.facebook_link.data = artist_result.facebook_link
    form.image_link.data = artist_result.image_link
    form.website.data = artist_result.website

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    artist_result = Artist.query.get(artist_id)
    try:
        artist_result.name = request.form['name']
        artist_result.city = request.form['city']
        artist_result.state = request.form['state']
        artist_result.phone = request.form['phone']
        artist_result.genres = request.form.getlist('genres')
        artist_result.image_link = request.form['image_link']
        artist_result.facebook_link = request.form['facebook_link']
        artist_result.website = request.form['website']
        # artist_result.seeking_venue
        # artist_result.seeking_description
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Aritist ' +
              request.form['name'] + ' could not be updated.')
    else:
        flash('Aritist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_result = Venue.query.get(venue_id)
    if not venue_result:
        return render_template('errors/404.html')
    form.name.data = venue_result.name
    form.city.data = venue_result.city
    form.state.data = venue_result.state
    form.phone.data = venue_result.phone
    form.address.data = venue_result.address
    form.genres.data = venue_result.genres
    form.facebook_link.data = venue_result.facebook_link
    form.image_link.data = venue_result.image_link
    form.website.data = venue_result.website

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue_result = Venue.query.get(venue_id)
    if not venue_result:
        return render_template('errors/404.html')
    try:
        venue_result.name = request.form['name']
        venue_result.city = request.form['city']
        venue_result.state = request.form['state']
        venue_result.phone = request.form['phone']
        venue_result.address = request.form['address']
        venue_result.genres = request.form.getlist('genres')
        venue_result.facebook_link = request.form['facebook_link']
        venue_result.image_link = request.form['image_link']
        venue_result.website = request.form['website']
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
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
        new_artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            seeking_description=request.form['seeking_description']
        )
        db.session.add(new_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows_result = Show.query.all()
    data = list(map(Show.allDetail, shows_result))
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        new_show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
