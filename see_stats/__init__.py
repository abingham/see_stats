from urllib.parse import urlparse

from gridfs import GridFS
import pymongo
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # TODO: Update to use beaker
    session_factory = UnencryptedCookieSessionFactoryConfig('secret')

    config = Configurator(
        settings=settings,
        session_factory=session_factory)

    config.add_renderer(
        name='.mustache',
        factory='see_stats.mustache_renderer.MustacheRendererFactory')

    db_url = urlparse(settings['mongo_uri'])
    conn = pymongo.Connection(host=db_url.hostname,
                              port=db_url.port)
    config.registry.settings['db_conn'] = conn

    def add_mongo_db(event):
        settings = event.request.registry.settings
        db = settings['db_conn'][db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        event.request.db = db
        # event.request.trail_fs = GridFS(db)

    config.add_subscriber(add_mongo_db, NewRequest)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('profiles', '/profiles')
    config.add_route('process_upload', '/process_upload')
    config.scan()
    return config.make_wsgi_app()
