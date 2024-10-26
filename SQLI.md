# Tipos de Inyección SQL

## 1. SQL Injection Clásico
- **Inyección SQL Basada en Errores de la BD (Database-Error-Based SQL Injection):** Utiliza los mensajes de error devueltos por la base de datos para llevar a cabo la inyección de manera muy sencilla.
- **Inyección SQL Basada en Errores del servidor (Server-Error-Based SQL Injection):** Utiliza los mensajes de error devueltos por el servidor para obtener información sobre la base de datos y realizar inyecciones.
- **Inyección SQL Basada en Unión (Union-Based SQL Injection):** Combina dos o más consultas usando la palabra clave `UNION` para obtener resultados adicionales de la base de datos.
- **Inyección SQL Basada en Booleanos (Boolean-Based SQL Injection):** Emplea consultas booleanas para determinar si ciertas condiciones son verdaderas o falsas, sin necesidad de mensajes de error.

## 2. Inyección SQL a Ciegas (Blind SQL Injection)
- **Inyección Basada en Verdadero/Falso (Blind Boolean-Based SQL Injection):** Evalúa los resultados en función de respuestas booleanas sin revelar datos directamente, útil cuando los mensajes de error están deshabilitados.
- **Inyección Basada en Tiempo (Time-Based Blind SQL Injection):** Evalúa el tiempo de respuesta del servidor para inferir si la inyección es exitosa o no. Esta técnica es útil en aplicaciones que no revelan errores ni permiten consultas booleanas.
