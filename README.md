# IceDrive Authentication service template

This repository contains the project template for the Authentication service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Ejecución

El objetivo principal de este repositorio es la creación de un servicio de autenticación. Sin embargo, también se ha creado un cliente de prueba.

### Ejecución del servidor

```
make run-server
```

### Ejecución del cliente

```
make run-client
```

### Otras ejecuciones

Con el objetivo de facilitar la eliminación de los usuarios de la persistencia de forma rápida, se puede usar el siguiente comando:

```
make delete-users
```

## Workflows

Además del workflow de Ruff, se ha decidido crear otro que realize las pruebas unitarias de la clase User con el objetivo de automatizar la fase de testing.
