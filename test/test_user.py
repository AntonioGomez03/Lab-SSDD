from icedrive_authentication.authentication import User
import unittest
import time

class TestUser(unittest.TestCase):

    def test_user_creation(self):
        user = User("username", "password")
        self.assertIsNotNone(user)

    def test_get_username(self):
        user=User("username","password")
        self.assertEqual(user.getUsername(),"username")

    def test_get_password(self):
        user=User("username","password")
        self.assertEqual(user.getPassword(),"password")

    def test_get_last_refresh(self):
        user=User("username","password")
        self.assertIsInstance(user.getLastRefresh(),float)

    def test_user_is_alive_ok(self):
        user = User("username", "password")
        self.assertTrue(user.isAlive())

    def test_user_is_alive_nok(self):
        user = User("username", "password")
        time.sleep(121) # El refresh solo dura 120 segundos
        self.assertFalse(user.isAlive())
    

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception:
        print("Error en los test de la clase User")
