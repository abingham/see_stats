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
               data,
               userid,
               public=True):
        return self.db['profiles'].insert(
            {
                'data': data,
                'public': public,
                'userid': userid,
            })
