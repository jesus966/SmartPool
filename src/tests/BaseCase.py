import logging
import unittest

from src import app
from src.database.db import db
from src.database.models import User


class BaseCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.db = db.get_db()

        # Create a user named 'root' with admin privileges
        user = User()
        user.user_name = 'root'
        user.email = 'root@root.es'
        user.password = 'toor'
        user.is_admin = True
        user.hash_password()
        user.save()

        logging.basicConfig(filename="test.log",
                            level=logging.DEBUG, format='%(asctime)s %(message)s')

    def tearDown(self):
        # Delete Database collections after the test is complete
        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)
