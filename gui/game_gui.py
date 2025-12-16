import tkinter as tk
from tkinter import ttk, messagebox
import time

from config.settings import DIFFICULTY_LEVELS, ALGORITHMS, GUI_CONFIG
from game.game_controller import GameController
from game.nim_logic import get_game_info, apply_move


# ======================================================
# SETUP WINDOW
# ======================================================
class SetupWindow:
    def __init__(self, on_start_callback):
        self.on_start_callback = on_start_callback
        self.root = tk.Tk()
        self.root.title("NIM Misère - Setup")
        self.root.geometry("400x360")
        self.root.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="NIM Misère", font=("Arial", 16, "bold")).pack(pady=10)

        # Mode
        ttk.Label(frame, text="Game Mode").pack(anchor="w")
        self.mode_var = tk.StringVar(value="Komputer_VS_Komputer")
        ttk.Combobox(
            frame,
            textvariable=self.mode_var,
            values=["Komputer_VS_Komputer", "PLAYER_VS_Komputer"],
            state="readonly"
        ).pack(fill="x", pady=5)

        # Difficulty
        ttk.Label(frame, text="Difficulty").pack(anchor="w")
        self.diff_var = tk.StringVar(value="Easy")
        ttk.Combobox(
            frame,
            textvariable=self.diff_var,
            values=list(DIFFICULTY_LEVELS.keys()),
            state="readonly"
        ).pack(fill="x", pady=5)

        # Player 1
        ttk.Label(frame, text="Player 1").pack(anchor="w")
        self.p1_algo = tk.StringVar(value="Reflex")
        ttk.Combobox(
            frame,
            textvariable=self.p1_algo,
            values=list(ALGORITHMS.keys()),
            state="readonly"
        ).pack(fill="x", pady=5)

        # Player 2
        ttk.Label(frame, text="Player 2").pack(anchor="w")
        self.p2_algo = tk.StringVar(value="Alpha-Beta")
        ttk.Combobox(
            frame,
            textvariable=self.p2_algo,
            values=list(ALGORITHMS.keys()),
            state="readonly"
        ).pack(fill="x", pady=5)

        ttk.Button(frame, text="Start Match", command=self.start).pack(pady=15)

    def start(self):
        settings = {
            "mode": self.mode_var.get(),
            "difficulty": self.diff_var.get(),
            "player1_algo": self.p1_algo.get(),
            "player2_algo": self.p2_algo.get()
        }
        self.root.destroy()
        self.on_start_callback(settings)

    def run(self):
        self.root.mainloop()


# ======================================================
# GAME WINDOW
# ======================================================
class GameWindow:
    def __init__(self, settings, on_finish_callback):
        self.settings = settings
        self.on_finish_callback = on_finish_callback
        self.auto_play = True  # Auto-play aktif by default

        diff = DIFFICULTY_LEVELS[settings["difficulty"]]
        self.controller = GameController(
            diff["piles"],
            settings["player1_algo"],
            settings["player2_algo"]
        )

        self.root = tk.Tk()
        self.root.title("NIM Misère - Game")
        self.root.geometry("900x720")
        self.root.resizable(True, True)

        self._build_ui()
        self._draw_state()
        
        # Bind resize event untuk responsif
        self.root.bind("<Configure>", self._on_resize)
        
        # Start auto-play
        if settings["mode"] == "Komputer_VS_Komputer":
            self.root.after(500, self._auto_step)
        elif settings["mode"] == "PLAYER_VS_Komputer":
            # Langsung cek giliran player di awal
            self.root.after(300, self._check_player_turn)

    # ---------------- UI ----------------
    def _build_ui(self):
        # Frame utama
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas dengan frame untuk responsif
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#0b4f0b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Info text
        self.info = tk.Text(main_frame, height=6, state="disabled", wrap="word")
        self.info.pack(fill="x", pady=5)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=5)

        # Tombol berbeda untuk mode berbeda
        if self.settings["mode"] == "PLAYER_VS_Komputer":
            # Info label untuk player
            ttk.Label(btn_frame, text="🎮 Tunggu giliran Anda - Dialog akan muncul otomatis", foreground="blue", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        else:
            ttk.Button(btn_frame, text="Next Move", command=self.next_move).pack(side="left", padx=5)
            self.auto_btn = ttk.Button(btn_frame, text="⏸ Pause Auto Play", command=self.toggle_auto)
            self.auto_btn.pack(side="left", padx=5)

    def _on_resize(self, event):
        """Handle window resize untuk redraw"""
        if hasattr(self, 'controller'):
            self.root.after(100, self._draw_state)

    # ---------------- GAME LOGIC ----------------
    def _check_player_turn(self):
        """Cek apakah giliran player dan tampilkan dialog otomatis"""
        if self.controller.game_over:
            return
            
        if self.settings["mode"] == "PLAYER_VS_Komputer" and self.controller.current_player == 1:
            # Giliran player - tampilkan dialog otomatis
            self.root.after(200, self._player_move_dialog)
    
    def toggle_auto(self):
        self.auto_play = not self.auto_play
        if self.settings["mode"] == "PLAYER_VS_Komputer":
            if self.auto_play:
                self.auto_btn.config(text="▶ Komputer Auto Play (ON)")
            else:
                self.auto_btn.config(text="⏸ Komputer Auto Play (OFF)")
        else:
            if self.auto_play:
                self.auto_btn.config(text="⏸ Pause Auto Play")
                self._auto_step()
            else:
                self.auto_btn.config(text="▶ Resume Auto Play")

    def _auto_step(self):
        if not self.auto_play or self.controller.game_over:
            return
        
        # Di mode PLAYER_VS_AI, auto play hanya untuk AI (player 2)
        if self.settings["mode"] == "PLAYER_VS_Komputer":
            if self.controller.current_player == 1:
                # Giliran player - tampilkan dialog
                self.root.after(200, self._check_player_turn)
                return
        
        # Execute move
        self.next_move()
        
        # Cek lagi apakah game over setelah move
        if self.controller.game_over:
            summary = self.controller.get_match_summary()
            self.root.after(1000, lambda: self._show_result(summary))
            return
            
        self.root.after(600, self._auto_step)

    def next_move(self):
        if self.controller.game_over:
            return  # Jangan proses lagi jika sudah game over

        # PLAYER VS AI - Giliran Player (tidak perlu manual call dialog)
        if self.settings["mode"] == "PLAYER_VS_Komputer" and self.controller.current_player == 1:
            return  # Dialog akan dipanggil otomatis oleh _check_player_turn

        # AI move
        move_info = self.controller.play_one_move()
        
        if move_info is None:
            return
            
        self._draw_state()
        self._log_move(move_info)
        
        # Cek apakah game sudah selesai dari move_info
        if move_info.get("game_over", False):
            # Game selesai, akan ditangani di _auto_step
            return
        
        # Setelah AI move di PLAYER_VS_AI, cek apakah giliran player
        if self.settings["mode"] == "PLAYER_VS_AI":
            if not self.controller.game_over and self.controller.current_player == 1:
                self.root.after(600, self._check_player_turn)
            elif not self.controller.game_over and self.controller.current_player == 2:
                self.root.after(600, self._auto_step)

    def _player_move_dialog(self):
        # Cek apakah memang giliran player
        if self.controller.current_player != 1:
            return
            
        if self.controller.game_over:
            return
        
        # Cek apakah dialog sudah terbuka
        if hasattr(self, 'player_dialog') and self.player_dialog and self.player_dialog.winfo_exists():
            return  # Dialog sudah terbuka, jangan buka lagi
        
        state = self.controller.state
        dialog = tk.Toplevel(self.root)
        self.player_dialog = dialog  # Simpan referensi
        dialog.title("🎮 Your Turn!")
        dialog.geometry("400x550")
        dialog.resizable(True, True)
        dialog.grab_set()
        
        # Cleanup saat dialog ditutup
        def on_dialog_close():
            self.player_dialog = None
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Main container dengan Canvas untuk scrolling
        main_container = tk.Frame(dialog, bg="white")
        main_container.pack(fill="both", expand=True)
        
        # Canvas + Scrollbar
        canvas = tk.Canvas(main_container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content frame
        frame = tk.Frame(scrollable_frame, bg="white", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # Header
        tk.Label(frame, text="🎮 YOUR TURN!", 
                font=("Arial", 16, "bold"), 
                fg="#2c3e50", bg="white").pack(pady=(0, 5))
        
        tk.Label(frame, text="Pilih pile dan jumlah korek api", 
                font=("Arial", 10), 
                fg="#7f8c8d", bg="white").pack(pady=(0, 15))

        pile_var = tk.IntVar(value=0)
        sticks_var = tk.IntVar(value=1)

        # Input section
        input_frame = tk.LabelFrame(frame, text=" Pilihan Anda ", 
                                   font=("Arial", 10, "bold"),
                                   bg="white", fg="#34495e",
                                   relief="groove", bd=2, padx=15, pady=10)
        input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(input_frame, text="Nomor Pile (P0, P1, P2...):", 
                bg="white", fg="#2c3e50", 
                font=("Arial", 9)).pack(anchor="w", pady=(5,2))
        pile_spin = tk.Spinbox(input_frame, from_=0, to=len(state)-1, 
                              textvariable=pile_var, width=30,
                              font=("Arial", 10))
        pile_spin.pack(pady=(0, 10), fill="x")
        
        tk.Label(input_frame, text="Jumlah korek api:", 
                bg="white", fg="#2c3e50",
                font=("Arial", 9)).pack(anchor="w", pady=(0,2))
        sticks_spin = tk.Spinbox(input_frame, from_=1, to=max(state) if state else 1, 
                                textvariable=sticks_var, width=30,
                                font=("Arial", 10))
        sticks_spin.pack(pady=(0, 5), fill="x")
        
        # Info pile
        info_frame = tk.LabelFrame(frame, text=" Info Pile Saat Ini ", 
                                  font=("Arial", 10, "bold"),
                                  bg="white", fg="#34495e",
                                  relief="groove", bd=2, padx=15, pady=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = "\n".join([f"Pile {i}  →  {s} korek api" for i, s in enumerate(state) if s > 0])
        tk.Label(info_frame, text=info_text, 
                font=("Courier", 9), 
                fg="#27ae60", bg="white",
                justify="left").pack(anchor="w")

        def confirm():
            i = pile_var.get()
            k = sticks_var.get()
            
            if i >= len(state):
                messagebox.showerror("Error", f"Pile {i} tidak ada!\nPile tersedia: 0-{len(state)-1}")
                return
                
            if state[i] < k or k <= 0:
                messagebox.showerror("Error", 
                    f"Move tidak valid!\n\n"
                    f"Pile {i} punya {state[i]} korek api.\n"
                    f"Anda mencoba ambil {k} korek api.\n\n"
                    f"Anda hanya bisa ambil 1-{state[i]} korek api.")
                return

            # Apply move
            self.controller.state = apply_move(self.controller.state, (i, k))
            self.player_dialog = None
            dialog.destroy()
            self._draw_state()
            
            # Tambahkan ke move history untuk player
            self.controller.total_moves += 1
            player_move_info = {
                "move_number": self.controller.total_moves,
                "player": 1,
                "algorithm": "Human",
                "move": (i, k),
                "state_after": self.controller.state.copy(),
                "stats": {"duration_ms": 0, "nodes_explored": 0}
            }
            self.controller.move_history.append(player_move_info)
            
            self._log(f"👤 YOU → Pile {i}, ambil {k} korek api")
            
            # Cek apakah player yang mengambil batang terakhir (player kalah)
            if sum(self.controller.state) == 0:
                # Player mengambil batang terakhir = Player KALAH
                self.controller.game_over = True
                self.controller.winner = 2  # AI menang
                
                # Hitung waktu akhir
                if self.controller.match_start_time:
                    self.controller.match_duration = time.time() - self.controller.match_start_time
                
                player_move_info["game_over"] = True
                player_move_info["winner"] = 2
                player_move_info["loser"] = 1
                
                summary = self.controller.get_match_summary()
                self.root.after(500, lambda: self._show_result(summary))
                return
            
            # Ganti giliran ke AI
            self.controller.current_player = 2
            
            # AI auto play langsung jalan
            self.root.after(800, self._auto_step)

        # Buttons
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(fill="x", pady=(5, 15))
        
        tk.Button(btn_frame, text="✓ KONFIRMASI", 
                 command=confirm,
                 font=("Arial", 11, "bold"),
                 bg="#27ae60", fg="white",
                 activebackground="#229954",
                 activeforeground="white",
                 relief="raised", bd=3,
                 cursor="hand2",
                 padx=20, pady=12).pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        tk.Button(btn_frame, text="✗ BATAL", 
                 command=dialog.destroy,
                 font=("Arial", 11, "bold"),
                 bg="#e74c3c", fg="white",
                 activebackground="#c0392b",
                 activeforeground="white",
                 relief="raised", bd=3,
                 cursor="hand2",
                 padx=20, pady=12).pack(side="left", padx=(5, 0), expand=True, fill="x")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        
        pile_spin.focus()
        pile_spin.selection_range(0, tk.END)

    # ---------------- DRAW ----------------
    def _draw_state(self):
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 900
        if canvas_height <= 1:
            canvas_height = 500

        self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#0b4f0b", outline="")

        state = self.controller.state
        if not state:
            return
            
        total_piles = len(state)
        max_sticks = max(state) if state else 1
        total_sticks = sum(state)

        base_scale = min(canvas_width / 900, canvas_height / 500)
        
        if total_sticks > 50:
            stick_factor = max(0.3, 1.0 - (total_sticks - 50) / 200)
            pile_factor = max(0.4, 1.0 - (max_sticks - 10) / 30)
        elif total_sticks > 30:
            stick_factor = max(0.5, 1.0 - (total_sticks - 30) / 100)
            pile_factor = max(0.6, 1.0 - (max_sticks - 7) / 20)
        else:
            stick_factor = 1.0
            pile_factor = 1.0

        match_height = max(20, int(45 * base_scale * stick_factor))
        match_width = max(3, int(6 * base_scale * stick_factor))
        head_radius = max(2, int(5 * base_scale * stick_factor))
        pile_gap = max(15, int(50 * base_scale * pile_factor))
        row_gap = max(30, int(80 * base_scale * stick_factor))

        center_x = canvas_width // 2
        base_y = canvas_height - 50

        pile_data = [(i, count) for i, count in enumerate(state)]
        pile_data_sorted = sorted(pile_data, key=lambda x: x[1])
        
        for display_level, (original_pile_idx, pile_count) in enumerate(pile_data_sorted):
            if pile_count == 0:
                continue
                
            y = base_y - (len(pile_data_sorted) - 1 - display_level) * row_gap
            start_x = center_x - (pile_count * pile_gap) // 2

            for j in range(pile_count):
                x = start_x + j * pile_gap

                self.canvas.create_rectangle(
                    x - match_width // 2,
                    y - match_height,
                    x + match_width // 2,
                    y,
                    fill="#f5e28b",
                    outline=""
                )

                self.canvas.create_oval(
                    x - head_radius,
                    y - match_height - head_radius * 2,
                    x + head_radius,
                    y - match_height,
                    fill="#e74c3c",
                    outline=""
                )
            
            label_font_size = max(8, int(10 * base_scale))
            self.canvas.create_text(
                start_x - 35, y - match_height // 2,
                text=f"P{original_pile_idx}: {pile_count}",
                fill="white",
                font=("Arial", label_font_size, "bold"),
                anchor="e"
            )
            
            self.canvas.create_text(
                start_x + pile_count * pile_gap + 35, y - match_height // 2,
                text=f"{pile_count}",
                fill="yellow",
                font=("Arial", label_font_size, "bold"),
                anchor="w"
            )

        info = get_game_info(state)
        font_size = max(9, int(12 * base_scale))
        self.canvas.create_text(
            20, 20,
            anchor="nw",
            fill="white",
            font=("Arial", font_size, "bold"),
            text=f"Total sticks: {info['total_sticks']} | Active piles: {info['active_piles']}"
        )
        
        if self.controller.current_player == 1:
            player_color = "#3498db" if self.settings["mode"] == "PLAYER_VS_Komputer" else "yellow"
            player_text = "YOU" if self.settings["mode"] == "PLAYER_VS_Komputer" else "Player 1"
        else:
            player_color = "#e74c3c"
            player_text = "Komputer" if self.settings["mode"] == "PLAYER_VS_Komputer" else "Player 2"
            
        self.canvas.create_text(
            canvas_width - 20, 20,
            anchor="ne",
            fill=player_color,
            font=("Arial", font_size, "bold"),
            text=f"Turn: {player_text}"
        )

    # ---------------- LOG ----------------
    def _show_result(self, summary):
        """Tampilkan result window dan tutup game window"""
        self.root.destroy()
        self.on_finish_callback(summary, self.settings)
    
    def _log_move(self, m):
        self._log(
            f"Move {m['move_number']} | "
            f"P{m['player']} ({m['algorithm']}) "
            f"→ pile {m['move'][0]} take {m['move'][1]}"
        )

    def _log(self, text):
        self.info.config(state="normal")
        self.info.insert("end", text + "\n")
        self.info.see("end")
        self.info.config(state="disabled")

    def run(self):
        self.root.mainloop()


# ======================================================
# RESULT WINDOW
# ======================================================
class ResultWindow:
    def __init__(self, summary, settings):
        self.summary = summary
        self.settings = settings
        self.root = tk.Tk()
        self.root.title("🏆 Match Result")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        self.root.configure(bg="#2c3e50")
        self._build_ui()

    def _build_ui(self):
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        winner_frame = tk.Frame(main_frame, bg="#27ae60", relief="raised", borderwidth=3)
        winner_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            winner_frame,
            text="🏆 WINNER 🏆",
            font=("Arial", 18, "bold"),
            bg="#27ae60",
            fg="white",
            pady=10
        ).pack()
        
        winner_algo = (self.settings["player1_algo"] if self.summary["winner"] == 1 
                      else self.settings["player2_algo"])
        
        tk.Label(
            winner_frame,
            text=f"Player {self.summary['winner']}",
            font=("Arial", 28, "bold"),
            bg="#27ae60",
            fg="white"
        ).pack()
        
        tk.Label(
            winner_frame,
            text=f"({winner_algo})",
            font=("Arial", 14),
            bg="#27ae60",
            fg="white",
            pady=5
        ).pack()

        stats_frame = tk.Frame(main_frame, bg="#34495e", relief="groove", borderwidth=2)
        stats_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        tk.Label(
            stats_frame,
            text="Match Statistics",
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="white",
            pady=10
        ).pack()
        
        stats = [
            ("Total Moves:", self.summary['total_moves']),
            ("Duration:", f"{self.summary['match_duration_sec']:.2f} seconds"),
            ("Difficulty:", self.settings['difficulty']),
            ("Game Mode:", self.settings['mode'])
        ]
        
        for label, value in stats:
            row = tk.Frame(stats_frame, bg="#34495e")
            row.pack(fill="x", padx=20, pady=3)
            
            tk.Label(
                row,
                text=label,
                font=("Arial", 11),
                bg="#34495e",
                fg="#bdc3c7",
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                row,
                text=str(value),
                font=("Arial", 11, "bold"),
                bg="#34495e",
                fg="white",
                anchor="e"
            ).pack(side="right")

        players_frame = tk.Frame(main_frame, bg="#2c3e50")
        players_frame.pack(fill="x", pady=(0, 15))
        
        for i, algo in enumerate([self.settings['player1_algo'], self.settings['player2_algo']], 1):
            color = "#27ae60" if i == self.summary['winner'] else "#95a5a6"
            player_label = tk.Label(
                players_frame,
                text=f"Player {i}: {algo}",
                font=("Arial", 10),
                bg="#2c3e50",
                fg=color
            )
            player_label.pack()

        tk.Button(
            main_frame,
            text="Close",
            command=self.root.destroy,
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="raised",
            borderwidth=2,
            cursor="hand2",
            padx=30,
            pady=10
        ).pack(pady=10)

    def run(self):
        self.root.mainloop()