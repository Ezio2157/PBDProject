from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from setupOracle import *
from setupPostgreSQL import *
import os
import webbrowser
import dynamic_html
import diccionarioInyecciones

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para sesiones seguras

# Ruta para la página de índice del laboratorio
@app.route('/index')
def index():
    return render_template('index.html', sql_injections=diccionarioInyecciones.sql_injections)

# Rutas dinámicas para inicio de sesión de SQL Injection en Oracle y PostgreSQL
@app.route('/login/oracle/<tipo_sqli>', methods=['GET', 'POST'])
def login_oracle(tipo_sqli):
    return login_sqli(tipo_sqli, database="Oracle")

@app.route('/login/postgres/<tipo_sqli>', methods=['GET', 'POST'])
def login_postgres(tipo_sqli):
    print("LLEGÓ")
    return login_sqli(tipo_sqli, database="Postgres")

@app.route('/cookie', methods=['POST'])
def cookie_login():
    # tipo_sqli = request.args.get('tipo_sqli')  # Asegúrate de pasar 'tipo_sqli' como parámetro si es necesario
    # database = request.args.get('database')  # Similar para 'database'

    # Obtener el tipo de inyección y la base de datos desde la URL o la sesión
    # Asegúrate de que estos valores estén disponibles según tu lógica de navegación

    # Alternativamente, puedes pasarlos como campos ocultos en el formulario de cookies
    # Ejemplo:
    # <input type="hidden" name="tipo_sqli" value="{{ tipo_sqli }}">
    # <input type="hidden" name="database" value="{{ database }}">

    # Por simplicidad, asumiremos que 'tipo_sqli' y 'database' están disponibles en la sesión
    tipo_sqli = session.get('tipo_sqli')
    database = session.get('database')

    if not tipo_sqli or not database:
        flash("Información de inyección SQL no disponible.", "error")
        return redirect(url_for(f"login_{database.lower()}", tipo_sqli=tipo_sqli, database=database))

    cookie_value = request.form.get('cookie_value')
    print(f"Valor de cookie_value recibido: {cookie_value}")  # Añadir esta línea para depuración


    if not cookie_value:
        flash("No se proporcionó ninguna cookie.", "error")
        return redirect(url_for('login_sqli', tipo_sqli=tipo_sqli, database=database))

    # Obtener la información de la inyección desde el diccionario
    sqli_info = diccionarioInyecciones.sql_injections.get(tipo_sqli)
    if not sqli_info:
        flash("Tipo de SQL Injection no encontrado.", "error")
        return redirect(url_for('login_sqli', tipo_sqli=tipo_sqli, database=database))

    # Seleccionar la función de autenticación basada en el tipo de inyección y la base de datos
    if sqli_info.get("function_oracle") and database == "Oracle":
        auth_function = sqli_info.get("function_oracle")
    elif sqli_info.get("function_postgres") and database == "Postgres":
        auth_function = sqli_info.get("function_postgres")
    else:
        auth_function = None

    if not auth_function:
        flash("Función de autenticación no encontrada.", "error")
        return redirect(url_for('login_sqli', tipo_sqli=tipo_sqli, database=database))

    # Llamar a la función de autenticación correspondiente
    if tipo_sqli in ['blind_boolean', 'time_based']:
        # Autenticación basada en cookie
        result = auth_function(cookie_value)
    else:
        # Otras autenticaciones si es necesario
        result = None

    if result and result.get('auth') == "true":
        # Obtener el nombre de usuario desde el resultado
        usuario = result['resultado'][1] if isinstance(result['resultado'], tuple) and len(result['resultado']) > 1 else "Usuario"

        # Guardar el usuario en la sesión
        session['username'] = usuario

        # Redirigir a la pantalla de bienvenida
        return redirect(url_for('welcome'))
    else:
        # No mostrar ningún mensaje, simplemente redirigir al formulario de cookies nuevamente
        return redirect(url_for(f'login_{database.lower()}', tipo_sqli=tipo_sqli, database=database))


@app.route('/welcome')
def welcome():
    username = session.get('username')
    if not username:
        flash("Debes iniciar sesión primero.", "error")
        return redirect(url_for('login_sqli', tipo_sqli=session.get('tipo_sqli'), database=session.get('database')))
    return render_template('welcome.html', username=username)

# Función de inicio de sesión común para manejar explicaciones dinámicas y autenticación
def login_sqli(tipo_sqli, database):
    sqli_info = diccionarioInyecciones.sql_injections.get(tipo_sqli)
    if not sqli_info:
        return "Tipo de SQL Injection no encontrado.", 404

    # Determinar si es una inyección blind
    blind_types = ['time_based', 'blind_boolean']
    is_blind = tipo_sqli in blind_types

    # Seleccionar la función de autenticación basada en el tipo de inyección y la base de datos
    if database == "Oracle":
        auth_function_blind = sqli_info.get("function_oracle")
        auth_function = login_inseguro_blind_no_cookie_oracle
    elif database == "Postgres":
        auth_function_blind = sqli_info.get("function_postgres")
        auth_function = login_inseguro_blind_no_cookie_postgresql
    else:
        auth_function_blind = None
        auth_function = None

    if request.method == 'POST':
        cookie_value = request.form.get('cookie_value')
        if is_blind and cookie_value:
            # Llamar a la función de inyección blind correspondiente con cookie_value
            result = auth_function_blind(cookie_value)
            # Manejar el resultado en la ruta '/cookie'
            if result and result.get('auth') == "true":
                # Obtener el nombre de usuario desde el resultado
                usuario = result['resultado'][1] if isinstance(result['resultado'], tuple) and len(result['resultado']) > 1 else "Usuario"
                # Guardar el usuario en la sesión
                session['username'] = usuario
                # Redirigir a la pantalla de bienvenida
                return redirect(url_for('welcome'))
            else:
                # No mostrar ningún mensaje, simplemente redirigir al formulario de cookies nuevamente
                return redirect(url_for('login_sqli', tipo_sqli=tipo_sqli, database=database))
        else:
            # Si la cookie es nula, usar autenticación con username y password
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            result = auth_function(username, password)

        # Manejar el resultado de la autenticación
        if result:
            # Crear tarjeta para mostrar la sentencia SQL
            cardSentencia = dynamic_html.generarTarjetaInformacion("Sentencia SQL", result['sentencia'])
            flash(cardSentencia, category='Sentencia')

            # Manejar los resultados
            if 'resultado' in result:
                if 'auth' in result:
                    flash("Bienvenido, sesión iniciada con éxito", category='welcome')
                flash(str(result['resultado']), category='Resultado')
            else:
                flash("Usuario o contraseña incorrectos", category='error')
                flash("Operación realizada con éxito", "success")
        else:
            flash("Error en la operación", "error")
            return redirect(url_for(f'login_{database.lower()}', tipo_sqli=tipo_sqli))

    # Antes de renderizar la plantilla
    session['tipo_sqli'] = tipo_sqli
    session['database'] = database

    # Renderizar login.templates con el contenido dinámico del SQL Injection
    return render_template(
        'login.html',
        title=sqli_info["title"],
        description=sqli_info["description"],
        database=database,
        tipo_sqli=tipo_sqli,
        credenciales=sqli_info["credenciales"],
        is_blind=is_blind  # Pasar la variable para renderizar el formulario adecuado
    )


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
    app.run(debug=True)
