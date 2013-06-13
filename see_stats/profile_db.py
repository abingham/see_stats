import datetime

from bson.objectid import ObjectId


class ProfileDB:
    def __init__(self, db):
        self.db = db

    def profiles(self):
        return self.db['profiles'].find()

    def profile(self, id):
        return self.db['profiles'].find_one(
            {'_id': ObjectId(id)})

    def insert(self,
               description,
               data,
               userid,
               public=True):
        return self.db['profiles'].insert(
            {
                'description': description,
                'data': data,
                'public': public,
                'userid': userid,
                'timestamp': datetime.datetime.now().isoformat(),
            })
