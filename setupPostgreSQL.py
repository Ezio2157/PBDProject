
import psycopg2 as PBD

def dbConectar():
    ip = "localhost"
    puerto = 5432
    basedatos = "Empresa"

    usuario = "postgres"
    contrasena = "12345"

    print("---dbConectar---")
    print("---Conectando a Postgresql---")

    try:
        conexion = PBD.connect(user=usuario, password=contrasena, host=ip, port=puerto, database=basedatos)
        print("Conexión realizada a la base de datos",conexion)
        return conexion
    except PBD.DatabaseError as error:
        print("Error en la conexión")
        print(error)
        return None

#-------------------------------------------------------------------

def dbDesconectar():
    print("---dbDesconectar---")
    try:
        #conexion.commit()
        conexion.close()
        print("Desconexión realizada correctamente")
        return True
    except PBD.DatabaseError as error:
        print("Error en la desconexión")
        print(error)
        return False

#-------------------------------------------------------------------

def configuracion_tablas_postgresql(conexion):
    print("---configuracion_tablas_postgresql---")
    try:
        cursor = conexion.cursor()

        # Crear la tabla Usuarios si no existe
        consulta = """
            CREATE TABLE IF NOT EXISTS Usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(50) NOT NULL
            );
        """
        cursor.execute(consulta)

        # Insertar usuarios de ejemplo solo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        count = cursor.fetchone()[0]
        if count == 0:
            usuarios_ejemplo = [
                ("admin", "password123"),
                ("user1", "password1"),
                ("user2", "password2")
            ]
            # Usamos %s para parámetros en PostgreSQL
            cursor.executemany("INSERT INTO Usuarios (username, password) VALUES (%s, %s)", usuarios_ejemplo)
            print("Usuarios de ejemplo insertados correctamente.")
        else:
            print("La tabla Usuarios ya contiene datos.")

        cursor.close()
        print("Tabla 'Usuarios' creada o verificada exitosamente en PostgreSQL")
        return True
    except PBD.DatabaseError as error:
        print("Error al crear la tabla o insertar usuarios en PostgreSQL")
        print(error)
        return False

#-------------------------------------------------------------------

def login_seguro(username, password):
    print("---login---")
    conexion = dbConectar()  # Abre la conexión para autenticación
    if not conexion:
        print("Error: no se pudo conectar para autenticar.")
        return False

    try:
        cursor = conexion.cursor()
        consulta = "SELECT * FROM Usuarios WHERE username = %s AND password = %s"
        cursor.execute(consulta, [username, password])
        usuario = cursor.fetchone()
        cursor.close()
        dbDesconectar(conexion)  # Cierra la conexión después de la autenticación
        if usuario:
            print("Usuario autenticado:", usuario)
            return True
        else:
            print("Usuario o contraseña incorrectos")
            return False
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        dbDesconectar(conexion)
        return False

#-------------------------------------------------------------------

# Función de autenticación insegura simple
def login_inseguro_base(username, password):
    print("---login---")
    conexion = dbConectar()  # Abre la conexión para autenticación
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
            return True
        else:
            print("Usuario o contraseña incorrectos")
            return False
    except PBD.DatabaseError as error:
        print("Error al autenticar usuario")
        print(error)
        dbDesconectar(conexion)
        return False