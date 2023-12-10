from icedrive_authentication.authentication import User
import unittest
import time

class TestUser(unittest.TestCase):

    def test_user_creation(self):
        user = User("username", "password")
        self.assertIsNotNone(user)

    def test_user_creation_with_empty_username(self):
        user= User("", "password")
        self.assertIsNone(user)

    def test_user_is_alive_ok(self):
        user = User("username", "password")
        self.assertTrue(user.isAlive())

    def test_user_is_alive_nok(self):
        user = User("username", "password")
        time.sleep(3)
        self.assertFalse(user.isAlive())
    

if __name__ == "__main__":
    try:
        unittest.main()
    except:
        pass
'''

pytest  

'''