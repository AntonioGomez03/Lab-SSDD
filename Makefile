
run-server:
	@echo "Ejecutando el servidor..."
	@pip install -e . ; \
	clear ; \
	icedrive-authentication --Ice.Config=config/authentication.config

run-client:
	@echo "Ejecutando el cliente..."
	@pip install -e . ; \
	clear ; \
	icedrive-client

delete-users:
	@echo "Eliminando usuario..."
	@echo '{"users": []}' > data/users.json
	@sleep 1 > /dev/null 2>&1 || timeout /nobreak /t 1 > NUL
	clear

