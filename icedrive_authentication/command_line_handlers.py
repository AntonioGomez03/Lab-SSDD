import sys

from .app import ClientApp, AuthenticationApp


def client() -> int:
    app = ClientApp()
    return app.main(sys.argv)


def server() -> int:
    app = AuthenticationApp()
    return app.main(sys.argv)

if __name__ == "__main__":
    if "client" in sys.argv:
        client()
    elif "server" in sys.argv:
        server()

