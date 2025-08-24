# client_gui.py
import socket
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5050

class TimeClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tra cứu thời gian qua Socket (TCP)")
        self.geometry("480x280")
        self.resizable(False, False)

        # --- UI ---
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        # Host/Port
        row = 0
        ttk.Label(frm, text="Server IP/Host:").grid(column=0, row=row, sticky="w")
        self.ent_host = ttk.Entry(frm)
        self.ent_host.insert(0, DEFAULT_HOST)
        self.ent_host.grid(column=1, row=row, sticky="ew")
        frm.columnconfigure(1, weight=1)

        row += 1
        ttk.Label(frm, text="Port:").grid(column=0, row=row, sticky="w")
        self.ent_port = ttk.Entry(frm, width=10)
        self.ent_port.insert(0, str(DEFAULT_PORT))
        self.ent_port.grid(column=1, row=row, sticky="w")

        # Buttons
        row += 1
        btns = ttk.Frame(frm)
        btns.grid(column=0, row=row, columnspan=2, pady=(8, 0), sticky="w")
        self.btn_once = ttk.Button(btns, text="Lấy thời gian", command=self.get_time_once)
        self.btn_once.pack(side=tk.LEFT, padx=(0, 8))
        self.auto_var = tk.BooleanVar(value=False)
        self.chk_auto = ttk.Checkbutton(btns, text="Tự động cập nhật", variable=self.auto_var, command=self.toggle_auto)
        self.chk_auto.pack(side=tk.LEFT)

        ttk.Label(btns, text="Chu kỳ (ms):").pack(side=tk.LEFT, padx=(12, 4))
        self.ent_interval = ttk.Entry(btns, width=8)
        self.ent_interval.insert(0, "1000")
        self.ent_interval.pack(side=tk.LEFT)

        # Kết quả
        row += 1
        ttk.Label(frm, text="Kết quả:").grid(column=0, row=row, sticky="w", pady=(12, 0))
        self.lbl_time = ttk.Label(frm, text="(chưa có dữ liệu)", font=("Segoe UI", 12, "bold"))
        self.lbl_time.grid(column=0, row=row+1, columnspan=2, sticky="w")

        # Latency
        row += 2
        self.lbl_latency = ttk.Label(frm, text="Độ trễ: - ms")
        self.lbl_latency.grid(column=0, row=row, columnspan=2, sticky="w", pady=(8, 0))

        # Status
        row += 1
        self.status = ttk.Label(frm, text="Trạng thái: sẵn sàng", foreground="gray")
        self.status.grid(column=0, row=row, columnspan=2, sticky="w", pady=(8, 0))

        self._auto_job = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Networking ---
    def request_time(self, host, port, timeout=3.0):
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(b"TIME\n")
            s.settimeout(timeout)
            data = b""
            while not data.endswith(b"\n"):
                chunk = s.recv(1024)
                if not chunk:
                    break
                data += chunk
        return data.decode("utf-8", errors="ignore").strip()

    def get_time_once(self):
        host = self.ent_host.get().strip()
        try:
            port = int(self.ent_port.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi", "Port không hợp lệ.")
            return

        def work():
            self.set_status("Đang yêu cầu thời gian...")
            t0 = time.perf_counter()
            try:
                resp = self.request_time(host, port, timeout=3.0)
                latency_ms = int((time.perf_counter() - t0) * 1000)
                if resp.startswith("ERR"):
                    self.update_ui(error=resp)
                else:
                    self.update_ui(time_str=resp, latency=latency_ms)
            except Exception as e:
                self.update_ui(error=str(e))

        threading.Thread(target=work, daemon=True).start()

    def update_ui(self, time_str=None, latency=None, error=None):
        def _apply():
            if error:
                self.lbl_time.config(text=f"Lỗi: {error}")
                self.lbl_latency.config(text="Độ trễ: - ms")
                self.set_status("Thất bại")
            else:
                self.lbl_time.config(text=time_str)
                self.lbl_latency.config(text=f"Độ trễ: {latency} ms")
                self.set_status("Thành công")
        self.after(0, _apply)

    def set_status(self, text):
        self.status.config(text=f"Trạng thái: {text}")

    # --- Auto refresh ---
    def toggle_auto(self):
        if self.auto_var.get():
            self.schedule_auto()
        else:
            self.cancel_auto()

    def schedule_auto(self):
        try:
            interval = int(self.ent_interval.get().strip())
            interval = max(200, interval)  # tránh quá nhanh
        except ValueError:
            interval = 1000
        self.get_time_once()
        self._auto_job = self.after(interval, self.schedule_auto)

    def cancel_auto(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
            self._auto_job = None

    def on_close(self):
        self.cancel_auto()
        self.destroy()

if __name__ == "__main__":
    app = TimeClientApp()
    app.mainloop()
