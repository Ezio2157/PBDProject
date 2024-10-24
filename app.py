from flask import Flask
from setupOracle import *

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/test')
def hello_world():  # put application's code here
    return 'Hello World 2!'


if __name__ == '__main__':
    app.run()

    #Conexion con la BD de Oracle
    conexion = dbConectar()

    if conexion:
        #Creación de tablas iniciales
        configuracionTablas(conexion)
        #Desconexion con la BD de Oracle
        dbDesconectar()