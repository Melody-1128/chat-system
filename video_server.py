import json
import socket
import threading

VIDEO_IP = '0.0.0.0'
VIDEO_PORT = 1113
SIZE_SPEC = 10


def recvn(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def send_bytes(sock, data):
    length = f"{len(data):010d}".encode('utf-8')
    sock.sendall(length + data)


def recv_bytes(sock):
    length_bytes = recvn(sock, SIZE_SPEC)
    if not length_bytes:
        return None
    size = int(length_bytes.decode('utf-8'))
    return recvn(sock, size)


def send_json(sock, obj):
    payload = json.dumps(obj).encode('utf-8')
    send_bytes(sock, payload)


def recv_json(sock):
    raw = recv_bytes(sock)
    if raw is None:
        return None
    return json.loads(raw.decode('utf-8'))


def send_frame_packet(sock, metadata, frame_bytes):
    send_json(sock, metadata)
    send_bytes(sock, frame_bytes or b'')


def recv_frame_packet(sock):
    metadata = recv_json(sock)
    if metadata is None:
        return None, None
    frame_bytes = recv_bytes(sock)
    if frame_bytes is None:
        return None, None
    return metadata, frame_bytes


class VideoServer:
    def __init__(self, host=VIDEO_IP, port=VIDEO_PORT):
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(8)
        print(f"[VIDEO SERVER] Listening on {self.host}:{self.port}")

    def start(self):
        try:
            while True:
                client_sock, addr = self.server.accept()
                print(f"[VIDEO SERVER] Connection from {addr}")
                thread = threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("[VIDEO SERVER] Shutting down.")
        finally:
            self.server.close()

    def handle_client(self, sock):
        username = None
        try:
            handshake = recv_json(sock)
            if not handshake:
                return
            username = handshake.get('username')
            target = handshake.get('target')
            if not username:
                return

            with self.lock:
                self.clients[username] = sock
            print(f"[VIDEO SERVER] Registered video client: {username}, target={target}")

            while True:
                metadata, frame_bytes = recv_frame_packet(sock)
                if metadata is None:
                    break
                packet_type = metadata.get('type')
                if packet_type == 'frame':
                    self.forward_frame(metadata, frame_bytes)
                elif packet_type == 'end':
                    self.forward_frame(metadata, b'')
        except Exception as exc:
            print(f"[VIDEO SERVER] Client error ({username}): {exc}")
        finally:
            with self.lock:
                if username in self.clients and self.clients[username] is sock:
                    del self.clients[username]
            try:
                sock.close()
            except Exception:
                pass
            print(f"[VIDEO SERVER] Disconnected: {username}")

    def forward_frame(self, metadata, frame_bytes):
        target = metadata.get('target')
        if not target:
            return
        with self.lock:
            target_sock = self.clients.get(target)
        if target_sock:
            try:
                send_frame_packet(target_sock, metadata, frame_bytes)
            except Exception as exc:
                print(f"[VIDEO SERVER] Failed to forward frame to {target}: {exc}")


if __name__ == '__main__':
    server = VideoServer()
    server.start()
