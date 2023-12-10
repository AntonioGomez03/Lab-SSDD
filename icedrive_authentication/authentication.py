"""Module for servants implementations."""

import time
import Ice
import os
from .json_manager import JsonManager as jm
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive # noqa


users_file=os.path.join('data','users.json')

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
        print(f"Last refresh: {self.__last_refresh}, Now: {now}")
        return now-self.__last_refresh<2 #En realidad debería ser 120 (se ha puesto 2 segundos para las pruebas)

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""
        if time.time()-self.__last_refresh>2: # Si han pasado más de 2 minutos desde el último refresh
            raise IceDrive.Unauthorized()

        if not jm.exist_username(self.__username,users_file): # No hay nigun usuario con ese username
            raise IceDrive.UserNotExist()
        elif not jm.exist_user(self.__username,self.__password,users_file): # Hay algun usuario con ese username pero con otra contraseña
            raise IceDrive.Unauthorized() 
        
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
            user=User(username,password)
            newUser_prx=self.__getOrAddUserProxy(user,current.adapter) # Se añade el usuario al adaptador si no está o se devuelve si ya está
        else:
            raise IceDrive.Unauthorized() # Se lanza una excepción
        return IceDrive.UserPrx.uncheckedCast(newUser_prx) # Se devuelve el usuario

    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) ->  IceDrive.UserPrx:
        """Create an user with username and the given password."""

        if jm.exist_username(username,users_file): # Se comprueba si el username ya existe
                raise IceDrive.UserAlreadyExists()
        else:
            user=User(username,password) 
            jm.add_user(username,password,users_file) # Se añade el usuario al fichero de usuarios
            newUser_prx=self.__getOrAddUserProxy(user,current.adapter) # Se añade el usuario al adaptador si no está o se devuelve si ya está

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
                    self.users.remove(user)
                    self.users_prx.remove(user_prx)
                    jm.remove_user(username,password,users_file)
        else:
            raise IceDrive.Unauthorized()

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.
        
        Don't check anything related to its authentication state or anything else.
        """
        return user in self.users_prx
    
    def __userInUsersList(self,user)->bool:
        existe=False
        for u in self.users:
            if u.getUsername()==user.getUsername() and u.getPassword()==user.getPassword():
                existe=True
        return existe
    
    def __getOrAddUserProxy(self,user, adapter) :
        newUser_prx=None
        if not self.__userInUsersList(user):
            self.users.append(user) # Se añade el usuario a la lista de usuarios
            newUser_prx=adapter.addWithUUID(user) # Se añade el usuario al adaptador
            self.users_prx.append(newUser_prx) # Se añade el usuario a la lista de usuarios del adaptador
        else:
            index = next(i for i, u in enumerate(self.users) if u.getUsername() == user.getUsername() and u.getPassword() == user.getPassword())
            newUser_prx=self.users_prx[index]
            self.users[index].refresh() # Se actualiza el último refresh del usuario 
        return newUser_prx