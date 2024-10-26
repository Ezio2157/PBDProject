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

        # Crear tabla Usuarios si no existe
        consulta = """
            BEGIN
                EXECUTE IMMEDIATE 'CREATE TABLE Usuarios (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    username VARCHAR2(50) NOT NULL UNIQUE,
                    password VARCHAR2(50) NOT NULL
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
                ("admin", "password123"),
                ("user1", "password1"),
                ("user2", "password2")
            ]
            cursor.executemany("INSERT INTO Usuarios (username, password) VALUES (:user, :pass)", usuarios_ejemplo)
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

    try:
        cursor = conexion.cursor()
        sentencia =   "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"
        cursor.execute(sentencia)
        usuario = cursor.fetchone()
        cursor.close()
        #dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        return usuario
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        #dbDesconectar(conexion)
        return False


# Login inseguro para blind por tiempo
def login_inseguro_time_oracle(username, password):
    print("---login---")
    print("login_inseguro_time")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    try:
        cursor = conexion.cursor()
        sentencia =   "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"
        cursor.execute(sentencia)
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


# Login inseguro para errores
def login_inseguro_errors_oracle(username, password):
    print("---login---")
    print ("---login_inseguro_errors---")
    conexion = dbConectarOracle()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    try:
        cursor = conexion.cursor()
        sentencia =   "SELECT * FROM Usuarios WHERE username = '"+username+"' AND password = '"+password+"'"
        cursor.execute(sentencia)
        usuario = cursor.fetchone()

        cursor.close()
        dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        if usuario:
            print("Usuario autenticado:", usuario)
            return usuario
        else:
            print("Usuario o contraseña incorrectos")
            return usuario
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        dbDesconectar(conexion)
        return error
