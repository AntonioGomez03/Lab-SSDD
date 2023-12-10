"""Module for servants implementations."""

import time
import Ice
from .json_manager import JsonManager as jm
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive # noqa


users_file="users.json"

class User(IceDrive.User):
    """Implementation of an IceDrive.User interface."""
    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.__last_refresh=time.time()

    def getUsername(self, current: Ice.Current = None) -> str:
        """Return the username for the User object."""
        return self.__username

    def isAlive(self, current: Ice.Current = None) -> bool:
        """Check if the authentication is still valid or not."""
        now=time.time()
        return now-self.__last_refresh<2 #En realidad debería ser 120 (se ha puesto 2 segundos para las pruebas)

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""
        if(not jm.exist_user(self.__username,self.__password,users_file)):
            raise IceDrive.UserNotExist() 
        self.__last_refresh=time.time()
    
    def getPassword(self):
        return self.__password
    
    def getLastRefresh(self):
        return self.__last_refresh
    
    def __str__(self):
        return f"Usuario: {self.__username}, Password: {self.__password}, Ultimo refresh: {self.__last_refresh}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eval__(self):
        return self.__str__()
    
    


class Authentication(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""
    def __init__(self):
        self.users = []
        self.users_prx = []

    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Authenticate an user by username and password and return its User."""
        if jm.exist_user(username,password,users_file): # Si el usuario existe
            # FIXME Se debe comprobar si en la lista de usuarios hay alguno con el mismo nombre y contraseña, no si el objeto está en la lista
            user=User(username,password)
            if user not in self.users:
                self.users.append(user) # Se añade el usuario a la lista de usuarios
                newUser_prx=current.adapter.addWithUUID(user) # Se añade el usuario al adaptador
                self.users_prx.append(newUser_prx) # Se añade el usuario a la lista de usuarios del adaptador
            else:
                newUser_prx=self.users_prx[self.users.index(user)]
        else:
            raise IceDrive.Unauthorized() # Se lanza una excepción
        return IceDrive.UserPrx.uncheckedCast(newUser_prx) # Se devuelve el usuario

    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) ->  IceDrive.UserPrx:
        """Create an user with username and the given password."""

        if jm.exist_user(username,password,users_file): # Se comprueba si el usuario ya existe
                raise IceDrive.UserAlreadyExists()
        else:
            user=User(username,password) 
            self.users.append(user) # Se añade el usuario a la lista de usuarios
            newUser_prx=current.adapter.addWithUUID(user) # Se añade el usuario al adaptador
            self.users_prx.append(newUser_prx) # Se añade el usuario a la lista de usuarios del adaptador
            jm.add_user(username,password,users_file) # Se añade el usuario al fichero de usuarios

        return IceDrive.UserPrx.uncheckedCast(newUser_prx) # Se devuelve el usuario

    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""
        if jm.exist_user(username,password,users_file):
            for user,user_prx in zip(self.users,self.users_prx):
                if user.getUsername()==username and user.getPassword()==password:
                    user_id=user_prx.ice_getIdentity()
                    current.adapter.remove(user_id)
                    jm.remove_user(username,password,users_file)
        else:
            raise IceDrive.Unauthorized()

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.
        
        Don't check anything related to its authentication state or anything else.
        """
        return user in self.users_prx