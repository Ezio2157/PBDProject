# Flask Dual DB Server

Este proyecto es un servidor web construido con Flask que se conecta a dos tipos de bases de datos: Oracle (utilizando la librería `oracledb`) y PostgreSQL (utilizando la librería `psycopg2`). El servidor incluye una funcionalidad básica de autenticación de usuarios (inicio de sesión) y permite acceder a datos desde ambas bases de datos.

## Requisitos

Asegúrate de tener instalados los siguientes componentes:

- Python 3.8 o superior
- Oracle Database
- PostgreSQL

### Dependencias de Python

Este proyecto utiliza las siguientes librerías de Python. Las versiones están especificadas en el archivo `requirements.txt`:

- Flask 2.3.2
- oracledb 1.1.0
- psycopg2 2.9.7

Para instalar las dependencias, ejecuta el siguiente comando:

```bash
pip install -r requirements.txt