# Script for initializing the user database

import os
import sys
import transaction
from urllib.parse import urlparse

import pymongo


from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    db_url = urlparse(settings['mongo_uri'])
    conn = pymongo.Connection(host=db_url.hostname,
                              port=db_url.port)
    db = conn[db_url.path[1:]]

    # clear the profile data
    db['profiles'].remove()

if __name__ == '__main__':
    main()
