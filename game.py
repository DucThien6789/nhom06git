import tkinter as tk
from tkinter import messagebox
import random

# ===== Cấu hình trò chơi =====
CHOICES = ["Kéo", "Búa", "Bao"]
EMOJI = {"Kéo": "✂️", "Búa": "🪨", "Bao": "📄"}
BEATS = {"Kéo": "Bao", "Búa": "Kéo", "Bao": "Búa"}  # A thắng B nếu BEATS[A] == B

# ===== Ứng dụng =====
class RPSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kéo – Búa – Bao")
        self.geometry("520x430")
        self.resizable(False, False)

        # Trung tâm màn hình
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 3
        self.geometry(f"+{x}+{y}")

        # Điểm số
        self.user_score = 0
        self.cpu_score = 0
        self.round_num = 0

        self.build_ui()

    def build_ui(self):
        # Tiêu đề
        title = tk.Label(self, text="Kéo – Búa – Bao", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(14, 4))

        # Khung điểm
        score_frame = tk.Frame(self)
        score_frame.pack(pady=4)

        self.user_score_lbl = tk.Label(score_frame, text="Bạn: 0", font=("Segoe UI", 12))
        self.user_score_lbl.grid(row=0, column=0, padx=10)

        self.cpu_score_lbl = tk.Label(score_frame, text="Máy: 0", font=("Segoe UI", 12))
        self.cpu_score_lbl.grid(row=0, column=1, padx=10)

        self.round_lbl = tk.Label(score_frame, text="Ván: 0", font=("Segoe UI", 12))
        self.round_lbl.grid(row=0, column=2, padx=10)

        # Khung kết quả
        result_card = tk.Frame(self, bd=0, relief="groove", highlightthickness=1, highlightbackground="#ddd")
        result_card.pack(padx=16, pady=10, fill="x")

        vs = tk.Label(result_card, text="Bạn  vs  Máy", font=("Segoe UI", 12))
        vs.pack(pady=(8, 2))

        self.choices_lbl = tk.Label(result_card, text="—", font=("Segoe UI Emoji", 26))
        self.choices_lbl.pack()

        self.outcome_lbl = tk.Label(result_card, text="Hãy chọn một trong ba nút bên dưới!", font=("Segoe UI", 12))
        self.outcome_lbl.pack(pady=(4, 10))

        # Nút lựa chọn
        buttons = tk.Frame(self)
        buttons.pack(pady=4)
        for i, c in enumerate(CHOICES):
            tk.Button(
                buttons, text=f"{EMOJI[c]}  {c}",
                font=("Segoe UI", 12, "bold"),
                width=10, height=1,
                command=lambda ch=c: self.play(ch)
            ).grid(row=0, column=i, padx=8, pady=4)

        # Lịch sử
        hist_frame = tk.Frame(self)
        hist_frame.pack(padx=16, pady=8, fill="both", expand=True)

        tk.Label(hist_frame, text="Lịch sử (tối đa 12 lượt gần nhất):", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.history = tk.Listbox(hist_frame, height=8, font=("Consolas", 11))
        self.history.pack(fill="both", expand=True, pady=(4, 0))

        # Thanh dưới: nút Reset & Hướng dẫn
        bottom = tk.Frame(self)
        bottom.pack(pady=10)

        tk.Button(bottom, text="🔄 Reset", font=("Segoe UI", 11), width=10, command=self.reset_game)\
            .grid(row=0, column=0, padx=6)

        tk.Button(bottom, text="❓ Luật chơi", font=("Segoe UI", 11), width=10, command=self.show_rules)\
            .grid(row=0, column=1, padx=6)

        tk.Button(bottom, text="🚪 Thoát", font=("Segoe UI", 11), width=10, command=self.quit)\
            .grid(row=0, column=2, padx=6)

    def play(self, user_choice: str):
        cpu_choice = random.choice(CHOICES)
        self.round_num += 1

        # Xác định kết quả
        if user_choice == cpu_choice:
            outcome = "Hòa 🤝"
        elif BEATS[user_choice] == cpu_choice:
            outcome = "Bạn thắng 🎉"
            self.user_score += 1
        else:
            outcome = "Bạn thua 😢"
            self.cpu_score += 1

        # Cập nhật giao diện
        self.choices_lbl.config(
            text=f"{EMOJI[user_choice]}  {user_choice}   —   {EMOJI[cpu_choice]}  {cpu_choice}"
        )
        self.outcome_lbl.config(text=outcome)
        self.user_score_lbl.config(text=f"Bạn: {self.user_score}")
        self.cpu_score_lbl.config(text=f"Máy: {self.cpu_score}")
        self.round_lbl.config(text=f"Ván: {self.round_num}")

        # Ghi lịch sử (giữ 12 mục)
        line = f"Ván {self.round_num:02d}: Bạn {user_choice:<3}  |  Máy {cpu_choice:<3}  -> {outcome}"
        self.history.insert(0, line)
        if self.history.size() > 12:
            self.history.delete(tk.END)

    def reset_game(self):
        self.user_score = 0
        self.cpu_score = 0
        self.round_num = 0
        self.user_score_lbl.config(text="Bạn: 0")
        self.cpu_score_lbl.config(text="Máy: 0")
        self.round_lbl.config(text="Ván: 0")
        self.choices_lbl.config(text="—")
        self.outcome_lbl.config(text="Hãy chọn một trong ba nút bên dưới!")
        self.history.delete(0, tk.END)

    def show_rules(self):
        messagebox.showinfo(
            "Luật chơi",
            "Kéo cắt Bao, Búa đập Kéo, Bao bọc Búa.\n"
            "Chọn một trong ba: Kéo / Búa / Bao. Máy sẽ chọn ngẫu nhiên.\n"
            "Thắng: +1 điểm, Thua: +1 điểm cho máy, Hòa: không ai + điểm."
        )

if __name__ == "__main__":
    app = RPSApp()
    app.mainloop()
