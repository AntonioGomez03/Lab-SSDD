"""Authentication service application."""

import time
from typing import List
from .authentication import Authentication

import Ice
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive

class AuthenticationApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        adapter=self.communicator().createObjectAdapter("AuthenticationAdapter")
        adapter.activate()

        servant=Authentication()
        servant_prx=adapter.addWithUUID(servant)
        print("Running Authentication service")
        print(f"Proxy: {servant_prx}")

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

class ClientApp(Ice.Application):
    def run(self,argv:List[str])-> int:
        if len(argv)!=2:
            print("Error: a proxy is required")

        proxy=self.communicator().stringToProxy(argv[1])
        auth_prx=IceDrive.AuthenticationPrx.checkedCast(proxy)
        if not auth_prx:
            print(f"Proxy {argv[1]} is invalid")
            return 2
        
        newUser=auth_prx.newUser("pepe","1234")
        newUser2=auth_prx.newUser("ana","5678")
        user1=auth_prx.login("pepe","1234")
        print(user1.getUsername()+" is alive: "+str(user1.isAlive()))
        time.sleep(3)
        print("Esperando 3 segundos")
        print(user1.getUsername()+" is alive: "+str(user1.isAlive()))
        print(newUser.getUsername()+" is alive: "+str(newUser.isAlive()))
        print("Usuario valido: "+ str(auth_prx.verifyUser(user1)))
        user1.refresh()
        print(user1.getUsername()+" is alive: "+str(user1.isAlive()))      
        return 0
    
