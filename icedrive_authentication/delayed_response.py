"""Servant implementation for the delayed response mechanism."""

from .json_manager import JsonManager as jm
import Ice
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive

AUTHENTICATION_TOPIC_NAME="authentication"

class AuthenticationQueryResponse(IceDrive.AuthenticationQueryResponse):

    """Query response receiver."""
    def __init__(self, future: Ice.Future, auth):
        self.future = future
        self.auth=auth

    def loginResponse(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> None:
        """Receive an User when other service instance knows about it and credentials are correct."""
        if user in self.auth.users_prx:
            self.future.set_result(user)
            print(f"Usuario {user.getUsername()} logeado correctamente")
        else: 
            pass

    def userRemoved(self, current: Ice.Current = None) -> None:
        """Receive an invocation when other service instance knows the user and removed it."""

    def verifyUserResponse(self, result: bool, current: Ice.Current = None) -> None:
        """Receive a boolean when other service instance is owner of the `user`."""


class AuthenticationQuery(IceDrive.AuthenticationQuery):
    """Query receiver.""" 
    def __init__(self):
        pass

    def login(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user login."""
        from .authentication import User
        user = User(username, password)
        user_prx = current.adapter.addWithUUID(user)
        user_prx = IceDrive.UserPrx.uncheckedCast(user_prx)
        response.loginResponse(user_prx)

    def removeUser(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user to be removed."""

    def verifyUser(self, user: IceDrive.UserPrx, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an `User` to be verified."""