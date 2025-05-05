import socket
import time

def auto_add_books(host='127.0.0.1', port=9946, count=1000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.settimeout(10)  # Увеличиваем таймаут
        
        # Получаем приветственное сообщение
        print(sock.recv(4096).decode())
        
        for i in range(1, count + 1):
            # Отправляем выбор меню
            sock.sendall(b"1\n")  # Выбираем "Добавить книгу"
            time.sleep(0.2)
            
            # Получаем подменю добавления
            menu = sock.recv(4096).decode()
            
            # Выбираем генерацию книги
            sock.sendall(b"1.1\n")
            time.sleep(0.2)
            
            # Получаем сгенерированную книгу
            book_info = sock.recv(4096).decode()
            
            # Подтверждаем добавление
            sock.sendall(b"y\n")
            time.sleep(0.2)
            
            # Получаем ответ о добавлении
            response = sock.recv(4096).decode().strip()
            print(f"Книга {i}/{count}: {response}")
            
            # Возвращаемся в главное меню
            if i < count:
                sock.sendall(b"\n")
                time.sleep(0.2)
                
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        sock.close()
        print("Соединение закрыто")

if __name__ == "__main__":
    auto_add_books(count=1000)