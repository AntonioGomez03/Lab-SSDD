"""Authentication service application."""

import threading
import time
import os
from typing import List
from .authentication import AuthenticationI, Authentication
from .delayed_response import AuthenticationQuery
from .discovery import Discovery

import Ice
import IceStorm
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive # noqa

class AuthenticationApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""
    
    def enviar_anuncio_discovery(self, publisher, auth_prx):
        while True:
            publisher.announceAuthentication(auth_prx)
            time.sleep(5)

    def get_topic(self, property):
        """Suscribe to the discovery topic."""
        topic_name = self.communicator().getProperties().getProperty(property)
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy"))
        try:
            topic = topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name)
        return topic

    def suscribe_discovery_topic(self, adapter, auth_prx):
        """Suscribe to the discovery topic."""
        discovery_subscriber = Discovery(auth_prx)
        discovery_prx_subscriber = adapter.addWithUUID(discovery_subscriber)
        topic_discovery = self.get_topic("DiscoveryTopic")
        topic_discovery.subscribeAndGetPublisher({}, discovery_prx_subscriber)

    def suscribe_authenticationQuery_topic(self, adapter,servant):
        """Suscribe to the discovery topic."""
        authenticationQuery_subscriber = AuthenticationQuery(servant.authentication)
        authenticationQuery_prx_subscriber = adapter.addWithUUID(authenticationQuery_subscriber)
        topic_discovery = self.get_topic("AuthenticationQueryTopic")
        topic_discovery.subscribeAndGetPublisher({}, authenticationQuery_prx_subscriber)

    def publish_discovery_topic(self, auth_prx):
        """Publish the discovery topic."""
        topic_discovery = self.get_topic("DiscoveryTopic")
        discovery_publisher = IceDrive.DiscoveryPrx.uncheckedCast(topic_discovery.getPublisher())
        thread = threading.Thread(target=self.enviar_anuncio_discovery, args=(discovery_publisher, auth_prx))
        thread.start()

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""

        adapter=self.communicator().createObjectAdapter("AuthenticationAdapter")
        adapter.activate()

        topic_authenticationQuery = self.get_topic("AuthenticationQueryTopic")
        authenticationQuery_publisher = IceDrive.AuthenticationQueryPrx.uncheckedCast(topic_authenticationQuery.getPublisher())


        servant=AuthenticationI(authenticationQuery_publisher, adapter,Authentication())
        servant_prx=adapter.addWithUUID(servant)
        servant_prx = IceDrive.AuthenticationPrx.uncheckedCast(servant_prx)

        print("Running Authentication service")
        print(f"Proxy: {servant_prx}")
        with open(os.path.join('config','client.txt'), 'w') as f:
            f.write(str(servant_prx))
        
        # Suscribe to the discovery topic
        self.suscribe_discovery_topic(adapter, servant_prx)
        # Publish the discovery topic
        self.publish_discovery_topic(servant_prx)
        # Suscribe to the authenticationQuery topic
        self.suscribe_authenticationQuery_topic(adapter,servant)

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
        
        print(auth_prx.removeUser("user3","pass3"))
        print(auth_prx.removeUser("user10","user10"))

        # Requisito 1 (Un cliente puede hacer "login" con credenciales válidas y un UserPrx es devuelto)
        print("Requisito 1\n Creando el usuario con username: user3 y password: pass3")
        user3 = auth_prx.newUser("user3","pass3")
        user3_login=auth_prx.login("user3","pass3")
        print(f"Comprobación de que los proxies de creación y de login son iguales: {user3==user3_login}\n") # Además, el proxy devuelto es el mismo que el del usuario creado anteriormente

        
        # Requisito 2 (Un cliente con credenciales inválidas al hacer "login" es rechazado)
        try:
            print("Requisito 2\n Intentando hacer login con credenciales inválidas")
            auth_prx.login("user3","abcd")
        except IceDrive.Unauthorized:
            print("Req 2 --> Error. Las credenciales no son correctas\n")

        # Requisito 3 (Un cliente puede registrarse con "newUser" y un UserPrx es devuelto)
        print("Requisito 3\n Creando el usuario con username: user1 y password: pass1")
        user1=auth_prx.newUser("user1","pass1")
        print(f"Proxy devuelto: {user1}\n")

        # Requisito 4 (Un cliente no puede registrarse si el nombre de usuario ya existe)
        try:
            print("Requisito 4\n Intentando crear un usuario con un username ya existente")
            auth_prx.newUser("user1","pass2")
        except IceDrive.UserAlreadyExists:
            print("Req 4 --> Error. El usuario ya existe\n")

        # Requisito 6 (Un cliente no puede borrar un usuario sin aportar las credenciales correctas)
        try:
            print("Requisito 6\n Intentando borrar un usuario sin aportar las credenciales correctas")
            auth_prx.removeUser("user1","pass2") 
        except IceDrive.Unauthorized:
            print("Req 6 --> Error. No se puede borrar el usuario porque las credenciales no son correctas\n")
        
        # Requisito 5 (Un cliente puede eliminar su usuario con "removeUser")
        print("Requisito 5\n Eliminando el usuario con username y password correctos\n")
        auth_prx.removeUser("user1","pass1") 
        
        # Requisito 7 (El método "verifyUser" devuelve verdadero para un UserPrx creado a través de "login" o "newUser")
        print(f"Requisito 7\n Verificando usuario creado por Authenticator: {auth_prx.verifyUser(user3)}\n") 

        # Requisito 8 (El método "verifyUser") devuelve falso para cualquier UserPrx, accesible o no, que no pertenezca a éste servicio)
        print("Requisito 8\n Verificando usuario eliminado y no accesible")
        user4=auth_prx.newUser("user4","pass4")
        auth_prx.removeUser("user4","pass4")
        print(f"Comprobación de la verificación: {auth_prx.verifyUser(user4)}\n") # Se comprueba que el usuario ya no existe

        # Requisito 9 (El método "getUsername" de UserPrx devuelve el nombre del usuario esperado)
        print("Requisito 9\n Creando el usuario con username: user5 y password: pass5")
        user5=auth_prx.newUser("user5","pass5")
        print(f"Username: {user5.getUsername()}\n")

        # Requisito 10 (El método "isAlive" de UserPrx devuelve verdadero si han pasado menos de 2 minutos de su creación o del último "refresh")
        print("Requisito 10\n Comprobando que el usuario está vivo")
        print(f"Esta vivo: {user5.isAlive()}\n")

        # Requisito 11 (El método "isAlive" de UserPrx devuelve falso si han pasado más de 2 minutos de su creación o del último "refresh")
        print("Requisito 11\n Comprobando que el usuario no está vivo")
        print("Esperando 120 segundos")
        time.sleep(120)
        print(f"Esta vivo: {user5.isAlive()}\n")

        # Requisito 12 (El método "isAlive" de UserPrx devuelve falso si el usuario ha sido eliminado)
        print("Requisito 12\n Creando el usuario con username: user6 y password: pass6")
        user6=auth_prx.newUser("user6","pass6")
        print("Eliminando el usuario")
        auth_prx.removeUser("user6","pass6")
        try:
            print(f"Esta vivo: {user6.isAlive()}")
        except Ice.ObjectNotExistException:
            print("Req 12 --> Error. El usuario ya no existe, por lo que no puede llamar ningún método\n")

        # Requisito 13 y 15 (El método "refresh" extiende la duración de las credenciales en 2 minutos) y (El método "refresh" falla con Unauhorized si han pasado más de 2 minutos)
        print("Requisito 13 y 15\n Creando el usuario con username: user7 y password: pass7")
        user7=auth_prx.newUser("user7","pass7")
        print("Refrescando el usuario")
        user7.refresh()
        print(f"Esta vivo: {user7.isAlive()}")
        print("Esperando 120 segundos")
        time.sleep(120)
        print(f"Esta vivo: {user7.isAlive()}")
        try:
            print("Refrescando el usuario")
            user7.refresh()
        except IceDrive.Unauthorized:
            print("Req 15 --> Error. Han pasado más de 2 minutos desde el último refresh")

        # Requisito 14
        print("Requisito 14\n Eliminando el usuario")
        auth_prx.removeUser("user7","pass7")
        try:
            print(f"Esta vivo: {user7.isAlive()}")
        except Ice.ObjectNotExistException:
            print("Req 14 --> Error. El usuario ya no existe, por lo que no puede llamar ningún método")

        
        return 0
    
