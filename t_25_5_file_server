import socket
import os

HOST = ''
PORT = 20004
SAVE_DIR = 'received'

os.makedirs(SAVE_DIR, exist_ok=True)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print('Файловий сервер очікує...')
conn, addr = s.accept()
print('Клієнт під’єднано:', addr)

while True:
    name_len_data = conn.recv(4)
    if not name_len_data:
        break
    name_len = int.from_bytes(name_len_data, 'big')
    file_name = conn.recv(name_len).decode('utf-8')
    size_data = conn.recv(8)
    if not size_data:
        break
    file_size = int.from_bytes(size_data, 'big')
    file_path = os.path.join(SAVE_DIR, file_name)
    with open(file_path, 'wb') as f:
        received = 0
        while received < file_size:
            chunk = conn.recv(min(4096, file_size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    print(f'Отримано файл: {file_name} ({file_size} байт)')
    conn.sendall(b'OK\n')
conn.close()
