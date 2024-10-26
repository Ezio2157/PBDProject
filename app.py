from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from flask.scaffold import setupmethod

from setupOracle import *
from setupPostgreSQL import *
import os
import webbrowser
import dynamic_html

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para sesiones seguras


# Diccionario de inyecciones SQL
sql_injections = {
    "database_error": {
        "title": "Inyección SQL Basada en Errores de la BD",
        "description": """
            <p>Utiliza los mensajes de error devueltos por la base de datos para extraer información confidencial.
            Este tipo de inyección se aprovecha de mensajes de error explícitos en las consultas SQL.</p>
        """,
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
        "route_oracle": "login_oracle_time_based",
        "route_postgres": "login_postgres_time_based",
        "function_oracle": login_inseguro_time_oracle,
        "function_postgres": login_inseguro_time_postgresql
    }
}

# Ruta para la página de índice del laboratorio
@app.route('/index')
def index():
    return render_template('index.html', sql_injections=sql_injections)

# Rutas dinámicas para inicio de sesión de SQL Injection en Oracle y PostgreSQL
@app.route('/login/oracle/<tipo_sqli>', methods=['GET', 'POST'])
def login_oracle(tipo_sqli):
    return login_sqli(tipo_sqli, database="Oracle")

@app.route('/login/postgres/<tipo_sqli>', methods=['GET', 'POST'])
def login_postgres(tipo_sqli):
    return login_sqli(tipo_sqli, database="Postgres")

# Función de inicio de sesión común para manejar explicaciones dinámicas y autenticación
def login_sqli(tipo_sqli, database):
    sqli_info = sql_injections.get(tipo_sqli)
    if not sqli_info:
        return "Tipo de SQL Injection no encontrado.", 404

    # Selecciona la función de autenticación insegura según el tipo de SQL Injection y la base de datos
    auth_function = sqli_info["function_oracle"] if database == "Oracle" else sqli_info["function_postgres"]

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Llama a la función de autenticación insegura
        resultado_sentencia = auth_function(username, password)
        if resultado_sentencia:
            session['user'] = username
            flash(str(resultado_sentencia),category='Correcto')
            #return resultado_sentencia
        else:
            flash(str(resultado_sentencia), "error")
            return redirect(url_for(f'login_{database.lower()}', tipo_sqli=tipo_sqli))

    # Renderiza login.html con el contenido dinámico del SQL Injection
    return render_template('login.html', title=sqli_info["title"], description=sqli_info["description"], database=database)

# Ruta protegida de ejemplo
@app.route('/home')
def home():
    if 'user' in session:
        return jsonify({"message": f"Bienvenido, {session['user']}"})
    return redirect(url_for('login_oracle', tipo_sqli="database_error"))

# Inicialización de la conexión a Oracle y configuración de tablas
def initialize_databaseOracle():
    print("Inicializando base de datos Oracle...")
    conexionOracle = dbConectarOracle()
    if conexionOracle:
        configuracionTablas_oracle(conexionOracle)
        dbDesconectar(conexionOracle)
    else:
        print("Error al conectar con la base de datos Oracle")

# Inicialización de la conexión a PostgreSQL y configuración de tablas
def initialize_databasePostgreSQL():
    conexionPostgreSQL = dbConectarPostgreSQL()
    if conexionPostgreSQL:
        configuracion_tablas_postgresql(conexionPostgreSQL)
        dbDesconectar(conexionPostgreSQL)
    else:
        print("Error al conectar con la base de datos PostgreSQL")

if __name__ == '__main__':
    # Inicializa las bases de datos
    initialize_databaseOracle()
    initialize_databasePostgreSQL()
    # Abre la página de inicio automáticamente en el navegador
    webbrowser.open("http://127.0.0.1:5000/index")
    app.run()