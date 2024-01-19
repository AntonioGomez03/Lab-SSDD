"""Servant implementations for service discovery."""

import Ice
Ice.loadSlice("icedrive_authentication/icedrive.ice")
import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self, auth_prx):
        self.authentications={auth_prx}
        self.directories={}
        self.blobs={}
        self.auth_prx=auth_prx

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        if prx not in self.authentications:
            self.authentications.add(prx)
            print(f"Authentication service detected: {prx}")

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        if prx not in self.directories:
            self.directories.add(prx)
            print(f"Directory service detected: {prx}")

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        if prx not in self.blobs:
            self.blobs.add(prx)
            print(f"Blob service detected: {prx}")

    def list_authentication_services(self):
        """Return a list of all the authentication services."""
        print("\n------------------------------------------------\n")
        for authentication in self.authentications:
            print(f"Authentication service: {authentication}")
        print("\n------------------------------------------------\n")