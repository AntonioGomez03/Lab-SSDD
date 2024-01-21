"""Servant implementation for the delayed response mechanism."""

from .json_manager import JsonManager as jm
import Ice
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive

AUTHENTICATION_TOPIC_NAME="authentication"

class AuthenticationQueryResponse(IceDrive.AuthenticationQueryResponse):

    """Query response receiver."""
    def __init__(self, future: Ice.Future):
        self.future = future

    def loginResponse(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> None:
        """Receive an User when other service instance knows about it and credentials are correct."""
        print(f" Respuesta desde el AuthenticationQueryResponse. ---> {user}")
        self.future.set_result(user)
        current.adapter.remove(current.id)

    def userExists(self, current: Ice.Current = None) -> None:   
        print(" Respuesta desde el AuthenticationQueryResponse. ---> Usuario existe")
        self.future.set_result(True)
        current.adapter.remove(current.id)
        self.future.set_exception(IceDrive.UserAlreadyExistsException())

    def userRemoved(self, current: Ice.Current = None) -> None:
        """Receive an invocation when other service instance knows the user and removed it."""
        print(" Respuesta desde el AuthenticationQueryResponse. ---> Usuario eliminado")
        self.future.set_result(True)
        current.adapter.remove(current.id)

    def verifyUserResponse(self, result: bool, current: Ice.Current = None) -> None:
        """Receive a boolean when other service instance is owner of the `user`."""
        self.future.set_result(result)
        current.adapter.remove(current.id)

class AuthenticationQuery(IceDrive.AuthenticationQuery):
    """Query receiver.""" 
    def __init__(self,authentication):
        self.authentication=authentication

    def login(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user login."""
        print("Recibido un login desde el AuthenticationQuery")
        try:
            user_prx=self.authentication.login(username,password,current)
            response.loginResponse(user_prx)
        except Exception:
            pass

    def doesUserExist(self, username, response):
        print("Recibido un doesUserExist desde el AuthenticationQuery")
        if self.authentication.userExists(username):
            response.userExists()

    def removeUser(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user to be removed."""
        print("Recibido un removeUser desde el AuthenticationQuery")
        try:
            self.authentication.removeUser(username,password,current)
            response.userRemoved()
        except Exception:
            pass
    def verifyUser(self, user: IceDrive.UserPrx, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an `User` to be verified."""
        print("Recibido un verifyUser desde el AuthenticationQuery")
        if(self.authentication.verifyUser(user,current) and user.isAlive()):
            response.verifyUserResponse(True)