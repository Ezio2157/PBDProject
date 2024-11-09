# Tipos de Inyección SQL

## 1. SQL Injection Clásico
- **Inyección SQL Basada en Errores de la BD (Database-Error-Based SQL Injection):** Utiliza los mensajes de error devueltos por la base de datos para llevar a cabo la inyección de manera muy sencilla.
- **Inyección SQL Basada en Errores del servidor (Server-Error-Based SQL Injection):** Utiliza los mensajes de error devueltos por el servidor para obtener información sobre la base de datos y realizar inyecciones.
- **Inyección SQL Basada en Unión (Union-Based SQL Injection):** Combina dos o más consultas usando la palabra clave `UNION` para obtener resultados adicionales de la base de datos.
- **Inyección SQL Basada en Booleanos (Boolean-Based SQL Injection):** Emplea consultas booleanas para determinar si ciertas condiciones son verdaderas o falsas, sin necesidad de mensajes de error.

Ejemplos más complejos de Inyección SQL Basada en Booleanos
1. Verificación de la existencia de un usuario
En un escenario típico, una consulta SQL podría buscar un nombre de usuario y contraseña para autenticar a un usuario. Una inyección basada en booleanos podría intentar determinar si un usuario específico existe:

Consulta original:

sql
Copiar código
SELECT * FROM Usuarios WHERE username = 'input_user' AND password = 'input_password';
Inyección:

Supongamos que un atacante quiere saber si el usuario admin existe:
sql
Copiar código
' OR username = 'admin' -- 
Esto cambiaría la consulta a:
sql
Copiar código
SELECT * FROM Usuarios WHERE username = '' OR username = 'admin' -- ' AND password = 'input_password';
Si la condición devuelve una respuesta (es decir, si el usuario admin existe), la respuesta del sistema cambia, permitiendo al atacante inferir que el usuario admin está presente.
2. Extracción de longitud del nombre de usuario
Un atacante podría determinar la longitud de un nombre de usuario con múltiples consultas booleanas.

Consulta original:

sql
Copiar código
SELECT * FROM Usuarios WHERE username = 'input_user' AND password = 'input_password';
Inyección (para verificar si el nombre de usuario tiene una longitud específica):

Supongamos que el atacante quiere verificar si el nombre de usuario tiene 5 caracteres:
sql
Copiar código
' OR LENGTH(username) = 5 -- 
Si la condición se evalúa como verdadera, el atacante sabe que hay un usuario con una longitud de nombre de 5 caracteres.
3. Extracción de caracteres uno por uno
El atacante puede determinar los caracteres en el nombre de usuario verificando cada posición de forma iterativa.

Consulta original:

sql
Copiar código
SELECT * FROM Usuarios WHERE username = 'input_user' AND password = 'input_password';
Inyección (para verificar si el primer carácter es 'a'):

sql
Copiar código
' OR SUBSTRING(username, 1, 1) = 'a' -- 
Si el resultado es verdadero, el atacante sabe que el primer carácter del nombre de usuario es 'a'.
Esto puede repetirse para cada carácter en la cadena.




## 2. Inyección SQL a Ciegas (Blind SQL Injection)
- **Inyección Basada en Verdadero/Falso (Blind Boolean-Based SQL Injection):** Evalúa los resultados en función de respuestas booleanas sin revelar datos directamente, útil cuando los mensajes de error están deshabilitados.
- **Inyección Basada en Tiempo (Time-Based Blind SQL Injection):** Evalúa el tiempo de respuesta del servidor para inferir si la inyección es exitosa o no. Esta técnica es útil en aplicaciones que no revelan errores ni permiten consultas booleanas.
