# server.py
import socket
import threading
import datetime

HOST = "0.0.0.0"   # lắng nghe mọi địa chỉ
PORT = 5050        # có thể đổi nếu trùng

def handle_client(conn, addr):
    try:
        conn.settimeout(10)
        with conn:
            # Đọc 1 dòng lệnh từ client (ví dụ: "TIME\n")
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(1024)
                if not chunk:
                    return
                data += chunk
            cmd = data.decode("utf-8", errors="ignore").strip().upper()
            if cmd == "TIME":
                # ISO 8601 + múi giờ UTC
                now = datetime.datetime.now(datetime.timezone.utc).astimezone()
                msg = now.isoformat(timespec="seconds")
                conn.sendall((msg + "\n").encode("utf-8"))
            else:
                conn.sendall(b"ERR Unknown command\n")
    except socket.timeout:
        pass
    except Exception as e:
        # In ra log nhẹ nhàng, không làm vỡ server
        print(f"[ERROR] {addr}: {e}")

def start_server(host=HOST, port=PORT):
    print(f"[SERVER] Listening on {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    start_server()
