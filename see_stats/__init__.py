from urllib.parse import urlparse

from gridfs import GridFS
import pymongo
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from .profile_db import ProfileDB


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # TODO: Update to use beaker
    session_factory = UnencryptedCookieSessionFactoryConfig('secret')

    # TODO: Something secure.
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret',
        # callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        session_factory=session_factory)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

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
        event.request.db = ProfileDB(db)
        # event.request.trail_fs = GridFS(db)

    config.add_subscriber(add_mongo_db, NewRequest)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('upload', '/upload')
    config.add_route('profiles', '/profiles')
    config.add_route('profile', '/profile/{profile_id}')
    config.add_route('process_upload', '/process_upload')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
