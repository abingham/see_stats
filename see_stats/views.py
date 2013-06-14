import io
import os
import pstats
import tempfile

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import (authenticated_userid,
                              remember,
                              forget)
from pyramid.view import view_config


def common_response(request, rsp):
    rslt = dict(rsp)
    rslt.update(
        dict(
            favicon = request.static_url('see_stats:static/favicon.ico'),
            stylesheet = request.static_url('see_stats:static/pylons.css'),
            small_logo = request.static_url('see_stats:static/pyramid-small.png'),
            userid = authenticated_userid(request),
        ))
    return rslt


class StatsFacade:
    """This exists to fool the pstats.Stats.load_stats() function into
    getting it's data from something other than a file or a Profile
    object.
    """

    def __init__(self, raw):
        import marshal
        self.stats = marshal.loads(raw)

    def create_stats(self):
        pass


@view_config(route_name='upload', renderer='templates/upload.mustache')
def upload(request):
    return common_response(
        request,
        {
            'userid': authenticated_userid(request),
        })

@view_config(route_name='profiles', renderer='templates/profiles.mustache')
def profiles(request):
    userid = authenticated_userid(request)
    visible = lambda p: p['public'] or (p['userid'] == userid)

    return common_response(
        request,
        {
            'entries': list(filter(visible, request.db.profiles())),
            'userid': userid,
        })

@view_config(route_name='profile', renderer='templates/profile.mustache')
def profile(request):
    profile_id = request.matchdict['profile_id']

    entry = request.db.profile(profile_id)
    sio = io.StringIO()
    sf = StatsFacade(entry['data'])
    pstats.Stats(sf, stream=sio).print_stats()
    sio.seek(0)
    return common_response(
        request,
        {
            'stats': sio.read(),
            'userid': authenticated_userid(request),
        })

@view_config(route_name='process_upload')
def process_upload(request):
    description = request.POST['description']
    input_file = request.POST['stats_file'].file

    try:
        public = (request.POST['public'] == 'on')
    except KeyError:
        public = False

    # TODO: What else to store? We have an issue with versions, which
    # is that the pstats an cprofile must match. There is no
    # compatibility guarantee between versions.
    # Perhaps we need to abstract it somehow...use our own format. But how?
    profile_id = request.db.insert(
        description=description,
        data=input_file.read(),
        public=public,
        userid=authenticated_userid(request))

    return HTTPFound('/profile/{}'.format(profile_id))

@view_config(route_name='login', renderer='templates/login.mustache')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/profiles'
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    # password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        # password = request.params['password']
        #if USERS.get(login) == password:
        headers = remember(request, login)
        return HTTPFound(location=came_from,
                         headers=headers)
        # message = 'Failed login'

    return common_response(
        request,
        dict(
            message = message,
            url = request.application_url + '/login',
            came_from = came_from,
            login = login,
        ))

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location='/profiles',
        headers=headers)
