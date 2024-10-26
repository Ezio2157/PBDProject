from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from setupOracle import dbConectar, dbDesconectar, configuracionTablas, login
import os
import webbrowser  # Para abrir la página automáticamente

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para sesiones seguras

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if login(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401
    return render_template("login.html")

# Ruta protegida de ejemplo
@app.route('/home')
def home():
    if 'user' in session:
        return jsonify({"message": f"Bienvenido, {session['user']}"})
    return redirect(url_for('login_route'))

# Inicialización de la conexión a la BD y configuración de tablas
@app.before_first_request
def initialize_database():
    conexion = dbConectar()
    if conexion:
        configuracionTablas(conexion)
        dbDesconectar(conexion)
    else:
        print("Error al conectar con la base de datos")

if __name__ == '__main__':
    # Abre la página de inicio automáticamente en el navegador
    webbrowser.open("http://127.0.0.1:5000/home")
    app.run()
