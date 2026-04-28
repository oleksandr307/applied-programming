from urllib.parse import parse_qs

TASK2_SIZE_PAGE = """
<h2>Задача 27.10</h2>
<p>Введіть розміри матриць.</p>
<p>{}</p>
<form method="post" action="/task2">
Рядків (n): <input type="text" name="n"/><br/>
Стовпців (m): <input type="text" name="m"/><br/>
<input type="submit" name="action" value="Далі"/>
</form>
<p><a href="/menu">Повернутися в меню</a></p>
"""

TASK2_MATRIX_PAGE = """
<h2>Задача 27.10 — Введення матриці {}</h2>
<p>Розмір: {}x{}</p>
<p>{}</p>
<form method="post" action="/task2">
{}
<input type="submit" value="Далі"/>
</form>
"""

TASK2_RESULT_PAGE = """
<h2>Задача 27.10 — Результат</h2>
<p><b>Матриця A:</b></p>
<pre>{}</pre>
<p><b>Матриця B:</b></p>
<pre>{}</pre>
<h3>Добуток A * B:</h3>
<pre>{}</pre>
<p>{}</p>
<p><a href="/task2">Обчислити ще раз</a></p>
<p><a href="/menu">Повернутися в меню</a></p>
"""


def parse_matrix(text, n, m):
    rows = text.strip().split("\n")
    matrix = []
    for row in rows:
        values = row.strip().split()
        if len(values) != m:
            return None
        try:
            matrix.append([float(v) for v in values])
        except ValueError:
            return None
    if len(matrix) != n:
        return None
    return matrix


def format_matrix(matrix):
    lines = []
    for row in matrix:
        lines.append("\t".join(str(v) for v in row))
    return "\n".join(lines)


def multiply_matrices(a, b):
    n = len(a)
    m = len(a[0])
    k = len(b[0])
    result = [[0 for _ in range(k)] for _ in range(n)]
    for i in range(n):
        for j in range(k):
            for t in range(m):
                result[i][j] += a[i][t] * b[t][j]
    return result


def handle_task2(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "text/html; charset=utf-8")]

    session_id = environ.get("HTTP_COOKIE", "")
    if "session=" in session_id:
        session_id = session_id.split("session=")[1].split(";")[0].strip()

    from t27_4_27_10_wsgi import sessions, HTML_PAGE

    user = sessions.get(session_id)
    if user is None:
        start_response("302 Found", [("Location", "/")])
        return [b""]

    state_key = f"task2_{session_id}"
    if state_key not in sessions:
        sessions[state_key] = {"step": "size", "n": 0, "m": 0, "a": None, "b": None}

    state = sessions[state_key]
    message = ""

    if environ.get("REQUEST_METHOD") == "POST":
        try:
            request_body_size = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            request_body_size = 0
        request_body = environ["wsgi.input"].read(request_body_size)
        params = parse_qs(request_body.decode())

        if state["step"] == "size":
            action = params.get("action", [""])[0]
            if action == "Далі":
                n_str = params.get("n", [""])[0]
                m_str = params.get("m", [""])[0]
                try:
                    n = int(n_str)
                    m = int(m_str)
                    if n > 0 and m > 0:
                        state["n"] = n
                        state["m"] = m
                        state["step"] = "matrix_a"
                    else:
                        message = "Розміри мають бути додатними."
                except ValueError:
                    message = "Введіть цілі числа."

        elif state["step"] == "matrix_a":
            matrix_text = params.get("matrix_text", [""])[0]
            if matrix_text:
                matrix = parse_matrix(matrix_text, state["n"], state["m"])
                if matrix:
                    state["a"] = matrix
                    state["step"] = "matrix_b"
                else:
                    message = f"Помилка. Введіть матрицю {state['n']}x{state['m']}. Перевірте кількість рядків і стовпців."

        elif state["step"] == "matrix_b":
            matrix_text = params.get("matrix_text", [""])[0]
            if matrix_text:
                matrix = parse_matrix(matrix_text, state["n"], state["m"])
                if matrix:
                    state["b"] = matrix
                    state["step"] = "result"
                else:
                    message = f"Помилка. Введіть матрицю {state['n']}x{state['m']}. Перевірте кількість рядків і стовпців."

    if state["step"] == "size":
        content = TASK2_SIZE_PAGE.format(message)

    elif state["step"] == "matrix_a":
        rows_input = "\n".join(
            ["<input type=\"text\" name=\"matrix_text\" size=\"50\"/><br/>" for _ in range(state["n"])]
        )
        content = TASK2_MATRIX_PAGE.format("A", state["n"], state["m"], message, rows_input)

    elif state["step"] == "matrix_b":
        rows_input = "\n".join(
            ["<input type=\"text\" name=\"matrix_text\" size=\"50\"/><br/>" for _ in range(state["n"])]
        )
        content = TASK2_MATRIX_PAGE.format("B", state["n"], state["m"], message, rows_input)

    elif state["step"] == "result":
        try:
            result = multiply_matrices(state["a"], state["b"])
            content = TASK2_RESULT_PAGE.format(
                format_matrix(state["a"]),
                format_matrix(state["b"]),
                format_matrix(result),
                ""
            )
        except Exception as e:
            content = TASK2_RESULT_PAGE.format(
                format_matrix(state["a"]),
                format_matrix(state["b"]),
                "",
                f"Помилка: {e}"
            )
        sessions[state_key] = {"step": "size", "n": 0, "m": 0, "a": None, "b": None}

    start_response(status, headers)
    return [HTML_PAGE.format(content).encode()]
