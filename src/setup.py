from src.database.db import db
import getpass

# Only execute if this is main
from src.database.models import User

if __name__ == '__main__':
    response = input("You are about to destroy ALL data contained in the pool database. Are you sure (y/n)?")

    if response == 'y':
        # Delete ALL database
        for collection in db.get_db().list_collection_names():
            db.get_db().get_collection(collection).drop()

        # Create new root user
        email = input("Enter the root user email: ")
        root_passwd = getpass.getpass(prompt='Enter the password of the new root account: ', stream=None)

        user = User()
        user.user_name = "root"
        user.email = email
        user.password = root_passwd
        user.is_admin = True
        user.hash_password()
        user.save()


