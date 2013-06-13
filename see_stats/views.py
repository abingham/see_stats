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


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'see_stats'}

@view_config(route_name='upload', renderer='templates/upload.mustache')
def upload(request):
    return {}

@view_config(route_name='profiles', renderer='templates/profiles.mustache')
def profiles(request):
    return {
        'lengths': [{'l': len(p['data']) } for p in request.db.profiles()],
        'logged_in': authenticated_userid(request),
    }

@view_config(route_name='profile', renderer='templates/profile.mustache')
def profile(request):
    profile_id = request.matchdict['profile_id']
    # TODO: Instead of the db, we should be passing around an
    # abstraction over it. Something simple...a model layer.
    entry = request.db.profile(profile_id)
    with tempfile.TemporaryDirectory() as tdir:
        fname = os.path.join(tdir, 'profile')
        with open(fname, 'w+b') as tfile:
            tfile.write(entry['data'])
        sio = io.StringIO()
        pstats.Stats(fname, stream=sio).print_stats()

    sio.seek(0)
    return {
        'stats': sio.read()
    }

@view_config(route_name='process_upload')
def process_upload(request):
    input_file = request.POST['stats_file'].file

    # TODO: What else to store? We have an issue with versions, which
    # is that the pstats an cprofile must match. There is no
    # compatibility guarantee between versions.
    # Perhaps we need to abstract it somehow...use our own format. But how?
    profile_id = request.db.insert(
        data=input_file.read(),
        public=True,
        userid='dummy')

    return HTTPFound('/profile/{}'.format(profile_id))

    # with tempfile.TemporaryDirectory() as tempdir:
    #     fname = os.path.join(tempdir.name, 'profiledata')
    #     with open(fname, 'w') as tempf:
    #         tempf.write(input_file.read())



    # filename = request.POST['stats_file'].filename

    # # ``input_file`` contains the actual file data which needs to be
    # # stored somewhere.



    # # Note that we are generating our own filename instead of trusting
    # # the incoming filename since that might result in insecure paths.
    # # Please note that in a real application you would not use /tmp,
    # # and if you write to an untrusted location you will need to do
    # # some extra work to prevent symlink attacks.

    # file_path = os.path.join('/tmp', '%s.mp3' % uuid.uuid4())

    # # We first write to a temporary file to prevent incomplete files from
    # # being used.

    # temp_file_path = file_path + '~'
    # output_file = open(temp_file_path, 'wb')

    # # Finally write the data to a temporary file
    # input_file.seek(0)
    # while True:
    #     data = input_file.read(2<<16)
    #     if not data:
    #         break
    #     output_file.write(data)

    # # If your data is really critical you may want to force it to disk first
    # # using output_file.flush(); os.fsync(output_file.fileno())

    # output_file.close()

    # # Now that we know the file has been fully saved to disk move it into place.

    # os.rename(temp_file_path, file_path)

    # return Response('OK')

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

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        # password = password,

        # common stuff. TODO: Refactor?
        favicon = request.static_url('see_stats:static/favicon.ico'),
        stylesheet = request.static_url('see_stats:static/pylons.css'),
        small_logo = request.static_url('see_stats:static/pyramid-small.png')
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location='/profiles',
        headers=headers)
