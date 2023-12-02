import sys

from .app import ClientApp, AuthenticationApp


def client() -> int:
    """Handler for 'ice-calculator-client'."""
    app = ClientApp()
    return app.main(sys.argv)


def server() -> int:
    """Handler for 'ice-calculator-server'."""
    app = AuthenticationApp()
    return app.main(sys.argv)

if __name__ == "__main__":
    if "client" in sys.argv:
        client()
    elif "server" in sys.argv:
        server()
    else:
        print("Usage: python ice_calculator.py client|server")
