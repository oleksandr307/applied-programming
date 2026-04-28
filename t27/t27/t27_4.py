from urllib.parse import parse_qs

TASK1_PAGE = """
<h2>Задача 27.4</h2>
<p>Вводьте ненульові цілі числа. Для завершення введіть 0.</p>
<p>{}</p>
<form method="post" action="/task1">
Число: <input type="text" name="number"/>
<input type="submit" name="action" value="Обробити"/>
<input type="submit" name="action" value="Завершити"/>
</form>
<p><a href="/menu">Повернутися в меню</a></p>
"""


def count_sign_changes(numbers):
    if len(numbers) < 2:
        return 0
    count = 0
    for i in range(1, len(numbers)):
        if numbers[i - 1] * numbers[i] < 0:
            count += 1
    return count


def handle_task1(environ, start_response):
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

    sequence_key = f"seq_{session_id}"
    if sequence_key not in sessions:
        sessions[sequence_key] = []

    sequence = sessions[sequence_key]
    message = ""
    result = ""

    if environ.get("REQUEST_METHOD") == "POST":
        try:
            request_body_size = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            request_body_size = 0
        request_body = environ["wsgi.input"].read(request_body_size)
        params = parse_qs(request_body.decode())
        action = params.get("action", [""])[0]
        number_str = params.get("number", [""])[0]

        if action == "Обробити":
            if number_str:
                try:
                    num = int(number_str)
                    if num == 0:
                        if sequence:
                            result = f"Кількість змін знаку: {count_sign_changes(sequence)}"
                        else:
                            result = "Послідовність порожня."
                        sessions[sequence_key] = []
                    else:
                        sequence.append(num)
                except ValueError:
                    message = "Будь ласка, введіть ціле число."

            if sequence:
                message = f"Поточна послідовність: {', '.join(map(str, sequence))}"

        elif action == "Завершити":
            if sequence:
                result = f"Послідовність: {', '.join(map(str, sequence))}<br/>Кількість змін знаку: {count_sign_changes(sequence)}"
            else:
                result = "Послідовність порожня."
            sessions[sequence_key] = []

    if result:
        message = result

    content = TASK1_PAGE.format(message)
    start_response(status, headers)
    return [HTML_PAGE.format(content).encode()]
