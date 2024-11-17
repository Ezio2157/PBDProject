import oracledb as PBD

# Función para conectar a la base de datos
def dbConectarOracle():
    ip = "localhost"
    puerto = 1521
    s_id = "xe"
    usuario = "system"
    contrasena = "12345"

    print("---dbConectarOracle---")
    print("---Conectando a Oracle---")

    try:
        conexion = PBD.connect(user=usuario, password=contrasena, host=ip, port=puerto, sid=s_id)
        print("Conexión realizada a la base de datos", conexion)
        return conexion
    except PBD.DatabaseError as error:
        print("Error en la conexión")
        print(error)
        return None

# Función para desconectar de la base de datos
def dbDesconectar(conexion):
    print("---dbDesconectar---")
    try:
        if conexion:  # Verifica que la conexión no sea None
            conexion.commit()  # Confirma los cambios

            conexion.close()
            print("Desconexión realizada correctamente")
            return True
        else:
            print("No hay conexión para cerrar.")
            return False
    except PBD.DatabaseError as error:
        print("Error en la desconexión")
        print(error)
        return False

# Función para la configuración de tablas
def configuracionTablas_oracle(conexion):
    print("---configuracionTablas---")
    try:
        cursor = conexion.cursor()

        # Crear tabla Usuarios si no existe con columna session_cookie
        consulta = """
            BEGIN
                EXECUTE IMMEDIATE 'CREATE TABLE Usuarios (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    username VARCHAR2(50) NOT NULL UNIQUE,
                    password VARCHAR2(50) NOT NULL,
                    session_cookie VARCHAR2(255)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE = -955 THEN
                        NULL;  -- Ignora si la tabla ya existe
                    ELSE
                        RAISE;
                    END IF;
            END;
        """
        cursor.execute(consulta)

        # Insertar usuarios de ejemplo solo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        count = cursor.fetchone()[0]
        print("Usuarios en la tabla:", count)
        if count == 0:
            usuarios_ejemplo = [
                ("admin", "password123", "t4SpnpWyg76A3K2BqcFh2vODq0fqJGvs38ydh9"),
                ("user1", "password1", "d382yd8n21df4314fn817yf6834188ls023d8d"),
                ("user2", "password2", "u73dv226d726gh23fnjncuyg0q9udfjf47eueu")
            ]
            cursor.executemany(
                "INSERT INTO Usuarios (username, password, session_cookie) VALUES (:username, :password, :session_cookie)",
                usuarios_ejemplo
            )
            print("Usuarios de ejemplo insertados correctamente.")
        else:
            print("La tabla Usuarios ya contiene datos.")

        cursor.close()
        print("Tabla 'Usuarios' creada o verificada exitosamente")
        return True
    except PBD.DatabaseError as error:
        print("Error al crear la tabla o insertar usuarios")
        print(error)
        return False


# Función de autenticación
def login_seguro_oracle(username, password):
    print("---login---")
    print("login_seguro")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = :user AND password = :pass", (username, password))
        usuario = cursor.fetchone()
        cursor.close()
        #dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        if usuario:
            print("Usuario autenticado:", usuario)
            return True
        else:
            print("Usuario o contraseña incorrectos")
            return False
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        #dbDesconectar(conexion)
        return False


# Función de autenticación insegura
def login_inseguro_base_oracle(username, password):
    print("---login---")
    print("login_inseguro_base")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False
    sentencia =   "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"

    try:
        cursor = conexion.cursor()
        cursor.execute(sentencia)
        usuario = cursor.fetchall()
        cursor.close()
        #dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        obj_resultado = {"resultado":usuario, "sentencia":sentencia}
        return obj_resultado
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        #dbDesconectar(conexion)
        return {"resultado":error, "sentencia":sentencia}


# Login inseguro para blind con username y password
def login_inseguro_blind_no_cookie_oracle(username, password):
    print("---login---")
    print("login_inseguro_blind sin cookie")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    sentencia =   "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"
    try:
        cursor = conexion.cursor()
        cursor.execute(sentencia)
        usuario = cursor.fetchone()
        cursor.close()
        #dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        if usuario:
            print("Usuario autenticado:", usuario)
            return {"resultado":usuario,"sentencia":sentencia, "auth":"true"}
        else:
            print("Usuario o contraseña incorrectos")
            return {"sentencia":sentencia}
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        #dbDesconectar(conexion)
        return {"sentencia":sentencia}


# Login inseguro para errores
def login_inseguro_errors_oracle(username, password):
    print("---login---")
    print ("---login_inseguro_errors---")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    sentencia = "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"
    try:
        cursor = conexion.cursor()
        cursor.execute(sentencia)
        usuario = cursor.fetchone()

        cursor.close()
        dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        if usuario:
            if isinstance(usuario, tuple) and len(usuario) == 3:
                return {"resultado": usuario, "sentencia": sentencia, "auth":"true"}
            else:
                print("Usuario autenticado:", usuario)
                return {"resultado":usuario,"sentencia":sentencia}
        else:
            print("Usuario o contraseña incorrectos")
            return {"sentencia":sentencia}
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        dbDesconectar(conexion)
        return {"resultado":error, "sentencia":sentencia}

# Función de autenticación insegura para blind injections via cookie
def login_inseguro_blind_oracle(cookie_value):
    print("---login_inseguro_blind_oracle---")
    conexion = dbConectarOracle()
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    # Simular inyección SQL blind via cookie
    sentencia = "SELECT * FROM Usuarios WHERE session_cookie = '" + cookie_value + "'"
    try:
        cursor = conexion.cursor()
        """
        # Simular retraso si se detecta una función de tiempo en la inyección
        if "sleep(" in cookie_value.lower() or "benchmark(" in cookie_value.lower():
            print("Simulando retraso en la consulta por inyección de tiempo")
            time.sleep(5)  # Retraso de 5 segundos para simular una inyección de tiempo
        """
        cursor.execute(sentencia)
        usuario = cursor.fetchone()
        cursor.close()
        if usuario:
            print("Usuario autenticado:", usuario)
            return {"resultado": usuario, "sentencia": sentencia, "auth": "true"}
        else:
            print("Usuario o cookie incorrectos")
            return {"sentencia": sentencia}
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario con cookie")
        print(error)
        return {"resultado": error, "sentencia": sentencia}
