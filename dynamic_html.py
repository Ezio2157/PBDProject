import re




# Lista de palabras clave de SQL
SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'JOIN',
    'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'AS', 'GROUP',
    'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
    'DISTINCT', 'CREATE', 'TABLE', 'ALTER', 'DROP', 'TRUNCATE',
    'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'DECLARE', 'SET',
    'VALUES', 'INTO', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
    'NOT', 'AND', 'OR', 'IN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
]

# Compilar una expresión regular para detectar las palabras clave, ignorando mayúsculas/minúsculas
pattern = re.compile(r'\b(' + '|'.join(SQL_KEYWORDS) + r')\b', re.IGNORECASE)




def generarTarjetaInformacion(title, description, code):
    """
    Genera el código HTML de una tarjeta con un título, descripción y bloque de código SQL con resaltado de sintaxis.

    :param title: Título de la tarjeta.
    :param description: Descripción o contenido explicativo.
    :param code: Bloque de código SQL como string.
    :return: String con el código HTML de la tarjeta.
    """

    # Lista de palabras clave de SQL
    SQL_KEYWORDS = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'JOIN',
        'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'AS', 'GROUP',
        'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
        'DISTINCT', 'CREATE', 'TABLE', 'ALTER', 'DROP', 'TRUNCATE',
        'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'DECLARE', 'SET',
        'VALUES', 'INTO', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
        'NOT', 'AND', 'OR', 'IN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'DESC'
    ]

    # Compilar expresiones regulares para comentarios, palabras clave y números
    comment_pattern = re.compile(r'(--.*)', re.MULTILINE)
    keyword_pattern = re.compile(r'\b(' + '|'.join(SQL_KEYWORDS) + r')\b', re.IGNORECASE)
    number_pattern = re.compile(r'\b(\d+)\b')

    # Función para reemplazar comentarios
    def replace_comments(match):
        return f'<span class="comment">{match.group(1)}</span>'

    # Función para reemplazar palabras clave
    def replace_keywords(match):
        return f'<span class="keyword">{match.group(1).upper()}</span>'

    # Función para reemplazar números
    def replace_numbers(match):
        return f'<span class="number">{match.group(1)}</span>'

    # Aplicar las sustituciones en el orden adecuado
    code = comment_pattern.sub(replace_comments, code)
    code = keyword_pattern.sub(replace_keywords, code)
    code = number_pattern.sub(replace_numbers, code)

    # Escapar caracteres especiales de HTML para evitar conflictos
    def escape_html(text):
        """
        Escapa caracteres especiales de HTML en el texto, excepto los ya formateados con spans.
        """
        # Primero, protegemos los spans existentes para que no sean escapados
        span_pattern = re.compile(r'(<span class="(?:keyword|comment|number)">.*?</span>)', re.DOTALL)
        parts = span_pattern.split(text)
        escaped_parts = []
        for part in parts:
            if span_pattern.match(part):
                escaped_parts.append(part)  # No escapamos los spans
            else:
                escaped_parts.append(
                    part.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                        .replace("'", "&#39;")
                )
        return ''.join(escaped_parts)

    # Aplicar el escape a todo el código
    code = escape_html(code)

    # Finalmente, insertar el código resaltado en la estructura HTML de la tarjeta
    html = f'''
<article class="card">
    <header class="card-header">
        <h2>{title}</h2>
    </header>
    <div class="card-body">
        <p>
            {description}
        </p>
        <div class="code-block">
            <pre><code>{code}</code></pre>
        </div>
    </div>
</article>
'''
    return html.strip()


if __name__ == "__main__":
    titulo = "Consulta SQL Básica"
    descripcion = """
    A continuación se muestra un ejemplo de una consulta SQL básica que selecciona todos los usuarios de una tabla y los ordena por edad de forma descendente:
    """
    codigo_sql = """-- Seleccionar todos los usuarios y ordenarlos por edad
    SELECT id, nombre, apellido, edad
    FROM usuarios
    WHERE edad >= 18
    ORDER BY edad DESC
    LIMIT 10;"""

    tarjeta_html = generarTarjetaInformacion(titulo, descripcion, codigo_sql)
    print(tarjeta_html)


