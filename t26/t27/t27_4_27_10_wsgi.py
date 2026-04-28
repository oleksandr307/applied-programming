import uuid
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Лабораторна робота №4</title>
</head>
<body>
{}
</body>
</html>"""

USERS = {"admin": "1234", "user": "1111"}

AUTH_FORM = """
<h2>Автентифікація</h2>
<form method="post" action="/">
Логін: <input type="text" name="login"/><br/>
Пароль: <input type="password" name="password"/><br/>
<input type="submit" value="Увійти"/>
</form>
<p>{}</p>
"""

MENU_PAGE = """
<h2>Оберіть задачу</h2>
<p><a href="/task1">Задача 27.4</a> — Визначити кількість змін знаку в послідовності цілих чисел.</p>
<p><a href="/task2">Задача 27.10</a> — Ввести дві матриці та обчислити їх добуток.</p>
<p><a href="/logout">Вийти</a></p>
"""

sessions = {}


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    session_id = environ.get("HTTP_COOKIE", "")

    if "session=" in session_id:
        session_id = session_id.split("session=")[1].split(";")[0].strip()

    user = sessions.get(session_id)

    status = "200 OK"
    headers = [("Content-type", "text/html; charset=utf-8")]

    if path == "/logout":
        if session_id in sessions:
            del sessions[session_id]
        headers.append(("Set-Cookie", "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT"))
        start_response("302 Found", [("Location", "/")] + headers[1:])
        return [b""]

    if user is None and path != "/":
        start_response("302 Found", [("Location", "/")])
        return [b""]

    if path == "/":
        if method == "POST":
            try:
                request_body_size = int(environ.get("CONTENT_LENGTH", 0))
            except ValueError:
                request_body_size = 0
            request_body = environ["wsgi.input"].read(request_body_size)
            params = parse_qs(request_body.decode())
            login = params.get("login", [""])[0]
            password = params.get("password", [""])[0]

            if login in USERS and USERS[login] == password:
                new_session = str(uuid.uuid4())
                sessions[new_session] = login
                headers.append(("Set-Cookie", f"session={new_session}; Path=/"))
                start_response("302 Found", [("Location", "/menu")] + headers[1:])
                return [b""]
            else:
                start_response(status, headers)
                return [HTML_PAGE.format(AUTH_FORM.format("Невірний логін або пароль")).encode()]
        else:
            start_response(status, headers)
            return [HTML_PAGE.format(AUTH_FORM.format("")).encode()]

    elif path == "/menu":
        start_response(status, headers)
        return [HTML_PAGE.format(MENU_PAGE).encode()]

    elif path == "/task1":
        from t27_4_task1 import handle_task1
        return handle_task1(environ, start_response)

    elif path == "/task2":
        from t27_10_task2 import handle_task2
        return handle_task2(environ, start_response)

    else:
        start_response("404 Not Found", headers)
        return [HTML_PAGE.format("<h2>Сторінку не знайдено</h2>").encode()]


if __name__ == "__main__":
    httpd = make_server("localhost", 8000, application)
    print("Сервер запущено на http://localhost:8000")
    httpd.serve_forever()
