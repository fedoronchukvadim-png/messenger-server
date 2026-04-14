import socket
import threading
import json
from datetime import datetime
import os

class ChatServer:
    def __init__(self, host='0.0.0.0', port=None):
        # Render сам выдаст порт через переменную PORT
        self.port = port or int(os.environ.get('PORT', 8888))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, self.port))
        self.server.listen(100)
        self.clients = {}
        self.nicknames = {}
        print(f"🚀 Сервер запущен на {host}:{self.port}")
        print(f"📡 Ожидание подключений...")

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(json.dumps(message).encode('utf-8'))
                except:
                    self.remove_client(client)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            nickname = self.nicknames[client_socket]
            del self.clients[client_socket]
            del self.nicknames[client_socket]
            self.broadcast({
                'type': 'system',
                'message': f"{nickname} покинул чат 👋"
            })
            print(f"📤 {nickname} отключился")

    def handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(1024).decode('utf-8')
            nickname = json.loads(data)['nickname']
            
            self.clients[client_socket] = address
            self.nicknames[client_socket] = nickname
            
            self.broadcast({
                'type': 'system',
                'message': f"{nickname} присоединился к чату 🎉"
            })
            
            print(f"✅ {nickname} подключился ({address[0]}:{address[1]})")
            
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                    
                data = json.loads(message)
                if data['type'] == 'message':
                    print(f"💬 {nickname}: {data['message']}")
                    self.broadcast({
                        'type': 'message',
                        'nickname': nickname,
                        'message': data['message']
                    }, client_socket)
                    
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
        finally:
            self.remove_client(client_socket)
            client_socket.close()

    def start(self):
        while True:
            try:
                client_socket, address = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except KeyboardInterrupt:
                print("\n🛑 Сервер остановлен")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("   🤖 MODERN MESSENGER SERVER 🤖")
    print("=" * 50)
    server = ChatServer()
    server.start()