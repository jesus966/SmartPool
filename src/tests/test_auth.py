import unittest
import json

from src.tests.BaseCase import BaseCase


class SignupTest(BaseCase):

    def test_successful_signup(self):
        # First, let's login the user ROOT
        # Given
        user_name = "root"
        password = "toor"
        payload = json.dumps({
            "user_name": user_name,
            "password": password
        })

        # When
        response = self.app.post('/api/auth/login', headers={"Content-Type": "application/json"}, data=payload)

        # Then
        self.assertEqual(str, type(response.json['token']))
        self.assertEqual(200, response.status_code)
        token = response.json['token']  # Save this token, we will need it for latter tests

        # Try to register a new user to the system

        # Given
        payload = json.dumps({
            "user_name": "victor",
            "email": "victor@hotmail.com",
            "password": "victorvictor",
            "is_admin": True
        })

        # When
        response = self.app.post('/api/auth/signup', headers={"Content-Type": "application/json",
                                                              "Authorization": "Bearer " + token}, data=payload)

        # Then
        self.assertEqual(str, type(response.json['id']))
        self.assertEqual(200, response.status_code)

        # Test PUT method, modifiyng data from the newly creater user

        # Given
        payload = json.dumps({
            "modify_user": "victor",
            "modify_data": {
                "user_name": "victor",
                "email": "victor3@hotmail.com",
                "password": "victorvictor2",
                "is_admin": False}
        })

        # When
        response = self.app.put('/api/auth/signup', headers={"Content-Type": "application/json",
                                                              "Authorization": "Bearer " + token}, data=payload)

        # Then
        self.assertEqual(str, type(response.json['id']))
        self.assertEqual(200, response.status_code)

        # Test PATCH method, modifiyng only the user name from the newly creater user

        # Given
        payload = json.dumps({
            "modify_user": "victor",
            "modify_data": {
                "user_name": "victorPalos"
            }
        })

        # When
        response = self.app.patch('/api/auth/signup', headers={"Content-Type": "application/json",
                                                              "Authorization": "Bearer " + token}, data=payload)

        # Then
        self.assertEqual(str, type(response.json['id']))
        self.assertEqual(200, response.status_code)

        # Test that we can delete a user
        # Given
        payload = json.dumps({
            "user_name": "victorPalos",
        })

        # When
        response = self.app.delete('/api/auth/signup', headers={"Content-Type": "application/json",
                                                                "Authorization": "Bearer " + token}, data=payload)

        # Then
        self.assertEqual(200, response.status_code)

        # Now, test what happens when we try to delete a user that doesn't exists
        # Given
        payload = json.dumps({
            "user_name": "victor2",
        })
        # When
        response = self.app.delete('/api/auth/signup', headers={"Content-Type": "application/json",
                                                                "Authorization": "Bearer " + token}, data=payload)

        # Then
        self.assertEqual(400, response.status_code)


if __name__ == '__main__':
    unittest.main()
