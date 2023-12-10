"""Authentication service application."""

import time
import os
from typing import List
from .authentication import Authentication

import Ice
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive # noqa

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
        with open(os.path.join('config','client.txt'), 'w') as f:
            f.write(str(servant_prx))

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

class ClientApp(Ice.Application):
    def run(self,argv:List[str])-> int:
        with open(os.path.join('config','client.txt'), 'r') as f:
            prx = f.read()

        proxy=self.communicator().stringToProxy(prx)
        auth_prx=IceDrive.AuthenticationPrx.checkedCast(proxy)
        if not auth_prx:
            print(f"Proxy {prx} is invalid")
            return 2
        

        # Requisito 1 (Un cliente puede hacer "login" con credenciales válidas y un UserPrx es devuelto)
        user3=auth_prx.newUser("user3","pass3")
        user3_login=auth_prx.login("user3","pass3")
        print(user3==user3_login) # Además, el proxy devuelto es el mismo que el del usuario creado anteriormente

        # Requisito 2 (Un cliente con credenciales inválidas al hacer "login" es rechazado)
        try:
            auth_prx.login("user3","abcd")
        except IceDrive.Unauthorized:
            print("Req 2 --> Error. Las credenciales no son correctas")

        # Requisito 3 (Un cliente puede registrarse con "newUser" y un UserPrx es devuelto)
        user1=auth_prx.newUser("user1","pass1")
        print(user1)

        # Requisito 4 (Un cliente no puede registrarse si el nombre de usuario ya existe)
        try:
            auth_prx.newUser("user1","pass2")
        except IceDrive.UserAlreadyExists:
            print("Req 4 --> Error. El usuario ya existe")

        # Requisito 6 (Un cliente no puede borrar un usuario sin aportar las credenciales correctas)
        try:
            auth_prx.removeUser("user1","pass2") 
        except IceDrive.Unauthorized:
            print("Req 6 --> Error. No se puede borrar el usuario porque las credenciales no son correctas")

        # Requisito 5 (Un cliente puede eliminar su usuario con "removeUser")
        auth_prx.removeUser("user1","pass1") 

        # Requisito 7 (El método "verifyUser" devuelve verdadero para un UserPrx creado a través de "login" o "newUser")
        print(auth_prx.verifyUser(user3)) 

        # Requisito 8 (El método "verifyUser") devuelve falso para cualquier UserPrx, accesible o no, que no pertenezca a éste servicio)
        user4=auth_prx.newUser("user4","pass4")
        auth_prx.removeUser("user4","pass4")
        print(auth_prx.verifyUser(user4)) # Se comprueba que el usuario ya no existe

        # Requisito 9 (El método "getUsername" de UserPrx devuelve el nombre del usuario esperado)
        user5=auth_prx.newUser("user5","pass5")
        print(user5.getUsername())

        # Requisito 10 (El método "isAlive" de UserPrx devuelve verdadero si han pasado menos de 2 minutos de su creación o del último "refresh")
        print(user5.isAlive())

        # Requisito 11 (El método "isAlive" de UserPrx devuelve falso si han pasado más de 2 minutos de su creación o del último "refresh")
        time.sleep(3)
        print(user5.isAlive())

        # Requisito 12 (El método "isAlive" de UserPrx devuelve falso si el usuario ha sido eliminado)
        user6=auth_prx.newUser("user6","pass6")
        auth_prx.removeUser("user6","pass6")
        try:
            print(user6.isAlive())
        except Ice.ObjectNotExistException:
            print("Req 12 --> Error. El usuario ya no existe, por lo que no puede llamar ningún método")

        # Requisito 13 y 15 (El método "refresh" extiende la duración de las credenciales en 2 minutos) y (El método "refresh" falla con Unauhorized si han pasado más de 2 minutos)
        user7=auth_prx.newUser("user7","pass7")
        user7.refresh()
        print(user7.isAlive())
        print("Esperando 3 segundos")
        time.sleep(3)
        print(user7.isAlive())
        try:
            user5.refresh()
        except IceDrive.Unauthorized:
            print("Req 15 --> Error. Han pasado más de 2 minutos desde el último refresh")

        # Requisito 14
        auth_prx.removeUser("user7","pass7")
        try:
            print(user7.isAlive())
        except Ice.ObjectNotExistException:
            print("Req 14 --> Error. El usuario ya no existe, por lo que no puede llamar ningún método")


        return 0
    
