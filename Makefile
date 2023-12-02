
run-server:
	@echo "Ejecutando el servidor..."
	@pip install . &> /dev/null && \
	clear && \
	icedrive-authentication --Ice.Config=config/authentication.config