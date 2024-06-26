"""Module for servants implementations."""

import threading
import time
import Ice
import os
import IceStorm
from .discovery import Discovery
from .delayed_response import AuthenticationQueryResponse
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
        return now-self.__last_refresh<120 

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""
        if time.time()-self.__last_refresh>120: 
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
    
    


class AuthenticationI(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""
    def __init__(self, authenticationQuery_prx, adapter, authentication):
        self.authentication = authentication
        self.authenticationQuery_prx=authenticationQuery_prx
        self.adapter = adapter
        self.expected_responses = {}

    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:      
        """Authenticate an user by username and password and return its User."""
        try:
            user_prx = self.authentication.login(username,password,current)
            return user_prx
        except IceDrive.Unauthorized:
            response_prx = self.prepare_amd_response_callback(current,exception=IceDrive.Unauthorized())
            self.authenticationQuery_prx.login(username,password,response_prx)
            return self.expected_responses[response_prx.ice_getIdentity()]

    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) ->  IceDrive.UserPrx:
        """Create an user with username and the given password."""
        if self.authentication.userExists(username):
            raise IceDrive.UserAlreadyExists()

        response_prx = self.prepare_amd_response_callback(current,default_action=lambda: self.authentication.createUser(username,password,self.adapter))
        self.authenticationQuery_prx.doesUserExist(username,response_prx)
        return self.expected_responses[response_prx.ice_getIdentity()]

    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""
        try:
            self.authentication.removeUser(username,password,current)
        except IceDrive.Unauthorized:
            response_prx = self.prepare_amd_response_callback(current, exception= IceDrive.Unauthorized())
            self.authenticationQuery_prx.removeUser(username,password,response_prx)
            return self.expected_responses[response_prx.ice_getIdentity()]

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.
        
        Don't check anything related to its authentication state or anything else.
        """
        verified = self.authentication.verifyUser(user,current) # Se comprueba si el usuario pertenece al servicio
        if not verified: # Si no pertenece
            response_prx = self.prepare_amd_response_callback(current,default_result=False)
            self.authenticationQuery_prx.verifyUser(user,response_prx)
            return self.expected_responses[response_prx.ice_getIdentity()] # Se espera a la respuesta
        return verified
    
    def remove_object_if_exists(
        self, adapter: Ice.ObjectAdapter, identity: Ice.Identity, exception=None, default_result=None, default_action=None
    ) -> None:
        """Remove an object from the adapter if it exists."""
        if adapter.find(identity) is not None:
            adapter.remove(identity)
            if exception is not None:
                self.expected_responses[identity].set_exception(exception)
            elif default_result is not None:
                self.expected_responses[identity].set_result(default_result)
            elif default_action is not None:
                user_prx=default_action()
                user_prx = IceDrive.UserPrx.checkedCast(user_prx)
                self.expected_responses[identity].set_result(user_prx)

        del self.expected_responses[identity]

    def prepare_amd_response_callback(self, current, exception=None, default_result=None, default_action=None):
        """Publish the authentication topic."""
        future = Ice.Future()
        response = AuthenticationQueryResponse(future)
        response_prx = self.adapter.addWithUUID(response)
        response_prx = IceDrive.AuthenticationQueryResponsePrx.checkedCast(response_prx)
        self.expected_responses[response_prx.ice_getIdentity()] = future

        args = (current.adapter, response_prx.ice_getIdentity())
        if exception is not None:
            args += (exception,)
        elif default_result is not None:
            args += (None,default_result,)
        elif default_action is not None:
            args += (None, None,default_action,)

        threading.Timer(5.0, self.remove_object_if_exists, args).start()

        return response_prx

        


class Authentication():
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
            newUser_prx = self.createUser(username,password,current.adapter) # Se crea el usuario

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
    
    def userExists(self, username):
        return jm.exist_username(username,users_file)
    
    def createUser(self, username, password, adapter):
        user=User(username,password) 
        jm.add_user(username,password,users_file) # Se añade el usuario al fichero de usuarios
        return self.__getOrAddUserProxy(user,adapter) # Se añade el usuario al adaptador si no está o se devuelve si ya está
