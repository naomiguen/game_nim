# gui/game_gui.py
"""
GUI untuk Game NIM - Komputer vs Komputer
Menggunakan multiple windows untuk setup, game, dan hasil
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from game.game_controller import GameController
from config.settings import DIFFICULTY_LEVELS, ALGORITHMS, ALPHABETA_MAX_STICKS


class SetupWindow:
    """Window untuk setup pertandingan."""

    def __init__(self, on_start_callback):
        self.on_start_callback = on_start_callback
        self.window = tk.Tk()
        self.window.title("Setup Pertandingan - Game NIM Misère")
        self.window.geometry("650x750")
        self.window.resizable(True, True)

        # Jika user klik X, tutup app dengan bersih
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk window setup."""
        # Header
        header_frame = tk.Frame(self.window, bg="#2c3e50", pady=20)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="🎮 Game NIM Misère",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()

        tk.Label(
            header_frame,
            text="AI vs AI Battle Arena",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack()

        # Main content
        content_frame = tk.Frame(self.window, padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Info box
        info_frame = tk.LabelFrame(
            content_frame,
            text="ℹ️ Aturan Permainan",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            info_frame,
            text="• Dalam satu giliran, pemain dapat mengambil berapa saja stik\n"
                 "  dari SATU tumpukan (dari 1 stik sampai semua stik di tumpukan tersebut)\n"
                 "• Pemain yang mengambil stik TERAKHIR adalah KALAH (Misère variant)\n"
                 "• Dua AI akan bertanding untuk menentukan siapa yang lebih unggul",
            font=("Arial", 10),
            justify=tk.LEFT
        ).pack()

        # Difficulty selection
        diff_frame = tk.LabelFrame(
            content_frame,
            text="📊 Pilih Level Kesulitan",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        diff_frame.pack(fill=tk.X, pady=(0, 15))

        self.difficulty_var = tk.StringVar(value="Medium")

        for level_name, level_info in DIFFICULTY_LEVELS.items():
            frame = tk.Frame(diff_frame)
            frame.pack(fill=tk.X, pady=2)

            rb = tk.Radiobutton(
                frame,
                text=f"{level_name}",
                variable=self.difficulty_var,
                value=level_name,
                font=("Arial", 10, "bold")
            )
            rb.pack(side=tk.LEFT)

            tk.Label(
                frame,
                text=f"- {level_info['total_sticks']} stik, {len(level_info['piles'])} tumpukan",
                font=("Arial", 9),
                fg="#7f8c8d"
            ).pack(side=tk.LEFT, padx=(5, 0))

        # Algorithm selection
        algo_frame = tk.LabelFrame(
            content_frame,
            text="🤖 Pilih Algoritma untuk Setiap Player",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        algo_frame.pack(fill=tk.X, pady=(0, 15))

        # Player 1
        p1_frame = tk.Frame(algo_frame)
        p1_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            p1_frame,
            text="Player 1 (🔴 Merah):",
            font=("Arial", 10, "bold"),
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.player1_var = tk.StringVar(value="Reflex")
        for algo_name in ALGORITHMS.keys():
            tk.Radiobutton(
                p1_frame,
                text=algo_name,
                variable=self.player1_var,
                value=algo_name,
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)

        # Player 2
        p2_frame = tk.Frame(algo_frame)
        p2_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            p2_frame,
            text="Player 2 (🔵 Biru):",
            font=("Arial", 10, "bold"),
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.player2_var = tk.StringVar(value="Alpha-Beta")
        for algo_name in ALGORITHMS.keys():
            tk.Radiobutton(
                p2_frame,
                text=algo_name,
                variable=self.player2_var,
                value=algo_name,
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)

        # Auto-play settings
        autoplay_frame = tk.LabelFrame(
            content_frame,
            text="⚙️ Pengaturan Tambahan",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        autoplay_frame.pack(fill=tk.X, pady=(0, 20))

        self.autoplay_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            autoplay_frame,
            text="Auto-play (langkah otomatis tanpa tombol)",
            variable=self.autoplay_var,
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        speed_frame = tk.Frame(autoplay_frame)
        speed_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            speed_frame,
            text="Delay antar langkah:",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)

        self.speed_var = tk.IntVar(value=500)
        speed_scale = tk.Scale(
            speed_frame,
            from_=100,
            to=2000,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=200,
            resolution=100
        )
        speed_scale.pack(side=tk.LEFT, padx=10)

        tk.Label(
            speed_frame,
            text="ms",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)

        # Start button (dibikin nempel bawah biar selalu kelihatan)
        bottom_frame = tk.Frame(self.window, padx=30, pady=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            bottom_frame,
            text="▶️  Mulai Pertandingan",
            command=self.start_match,
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            padx=40,
            pady=15,
            cursor="hand2"
        ).pack(fill=tk.X)

    def start_match(self):
        """Callback ketika tombol start diklik."""
        difficulty_name = self.difficulty_var.get()
        difficulty = DIFFICULTY_LEVELS[difficulty_name]

        total_sticks = difficulty.get("total_sticks")
        if total_sticks is None:
            total_sticks = sum(difficulty.get("piles", []))

        allow_alphabeta = difficulty.get("allow_alphabeta", total_sticks <= ALPHABETA_MAX_STICKS)

        p1 = self.player1_var.get()
        p2 = self.player2_var.get()

        # Enforce: Alpha-Beta hanya aman untuk state kecil
        if ("Alpha-Beta" in (p1, p2)) and (not allow_alphabeta or total_sticks > ALPHABETA_MAX_STICKS):
            messagebox.showwarning(
                "Alpha-Beta dibatasi",
                f"Level {difficulty_name} ({total_sticks} stik) terlalu besar untuk Alpha-Beta.\n"
                "Agar tidak freeze, Alpha-Beta otomatis diganti ke Reflex."
            )
            if p1 == "Alpha-Beta":
                p1 = "Reflex"
            if p2 == "Alpha-Beta":
                p2 = "Reflex"

        settings = {
            "difficulty": difficulty_name,
            "player1_algo": p1,
            "player2_algo": p2,
            "autoplay": self.autoplay_var.get(),
            "speed_ms": self.speed_var.get()
        }

        self.window.destroy()
        self.on_start_callback(settings)


    def run(self):
        """Jalankan window."""
        self.window.mainloop()


class GameWindow:
    """Window untuk menampilkan jalannya pertandingan."""

    def __init__(self, settings, on_finish_callback):
        self.settings = settings
        self.on_finish_callback = on_finish_callback

        self.window = tk.Tk()
        self.window.title("Pertandingan Berlangsung - Game NIM Misère")
        self.window.geometry("900x700")

        # Jika user klik X, perlakukan sebagai stop
        self.window.protocol("WM_DELETE_WINDOW", self.force_finish)

        # Inisialisasi controller
        difficulty = DIFFICULTY_LEVELS[settings["difficulty"]]
        self.controller = GameController(
            difficulty["piles"],
            settings["player1_algo"],
            settings["player2_algo"]
        )

        self.is_running = True

        # Tracking after() supaya bisa dibatalkan saat stop/destroy
        self.autoplay_after_id = None
        self.start_after_id = None

        self.setup_ui()

        # Start match (jadwalkan, simpan ID)
        self.start_after_id = self.window.after(500, self.start_match)

    def setup_ui(self):
        """Setup UI untuk window game."""
        # Header
        header_frame = tk.Frame(self.window, bg="#34495e", pady=15)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="⚔️ Pertandingan Sedang Berlangsung",
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="white"
        ).pack()

        # Info pertandingan
        info_text = (
            f"Level: {self.settings['difficulty']} | "
            f"Player 1: {self.settings['player1_algo']} 🔴 vs "
            f"Player 2: {self.settings['player2_algo']} 🔵"
        )
        tk.Label(
            header_frame,
            text=info_text,
            font=("Arial", 10),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack()

        # Main content
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Game state
        left_frame = tk.LabelFrame(
            main_frame,
            text="📊 Status Tumpukan",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Scrollable canvas untuk tumpukan
        canvas_container = tk.Frame(left_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.state_canvas = tk.Canvas(canvas_container, bg="#ecf0f1")
        scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.state_canvas.yview)

        self.state_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.state_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Current player indicator
        self.current_player_label = tk.Label(
            left_frame,
            text="",
            font=("Arial", 11, "bold"),
            pady=10
        )
        self.current_player_label.pack()

        # Right: Log
        right_frame = tk.LabelFrame(
            main_frame,
            text="📝 Log Pertandingan",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.log_text = scrolledtext.ScrolledText(
            right_frame,
            font=("Courier", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Bottom: Controls
        control_frame = tk.Frame(self.window, pady=10)
        control_frame.pack(fill=tk.X, padx=10)

        if not self.settings["autoplay"]:
            self.next_button = tk.Button(
                control_frame,
                text="⏭️ Langkah Berikutnya",
                command=self.next_step,
                font=("Arial", 11, "bold"),
                bg="#3498db",
                fg="white",
                padx=20,
                pady=10
            )
            self.next_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            control_frame,
            text="⏹️ Hentikan & Lihat Hasil",
            command=self.force_finish,
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def _cancel_after_jobs(self):
        """Batalkan semua after() yang terjadwal untuk mencegah callback menembak window yang sudah ditutup."""
        for job_id_attr in ("autoplay_after_id", "start_after_id"):
            job_id = getattr(self, job_id_attr, None)
            if job_id is not None:
                try:
                    self.window.after_cancel(job_id)
                except Exception:
                    pass
                setattr(self, job_id_attr, None)

    def draw_state(self):
        """Gambar state tumpukan dalam bentuk text/bar chart."""
        self.state_canvas.delete("all")

        state = self.controller.state
        max_pile = max(state) if state else 1
        canvas_width = self.state_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 400

        y_offset = 20
        row_height = 35

        for i, pile in enumerate(state):
            # Label row
            label = f"Row {i}:"
            self.state_canvas.create_text(
                10, y_offset,
                text=label,
                anchor=tk.W,
                font=("Arial", 10, "bold")
            )

            # Bar representing pile
            bar_x_start = 80
            bar_max_width = max(50, canvas_width - 150)  # clamp agar tidak negatif/kecil

            if pile > 0:
                bar_width = (pile / max_pile) * bar_max_width
                self.state_canvas.create_rectangle(
                    bar_x_start, y_offset - 10,
                    bar_x_start + bar_width, y_offset + 10,
                    fill="#3498db",
                    outline="#2980b9",
                    width=2
                )

            # Count label
            count_text = f"{pile} stik"
            self.state_canvas.create_text(
                canvas_width - 60, y_offset,
                text=count_text,
                anchor=tk.W,
                font=("Arial", 9)
            )

            y_offset += row_height

        self.state_canvas.config(scrollregion=self.state_canvas.bbox("all"))

    def log_message(self, message):
        """Tambahkan pesan ke log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_match(self):
        """Mulai pertandingan."""
        # start_after_id sudah “terpakai”
        self.start_after_id = None

        self.log_message("=" * 50)
        self.log_message("🎮 PERTANDINGAN DIMULAI")
        self.log_message(f"Level: {self.settings['difficulty']}")
        self.log_message(f"Player 1 (🔴): {self.settings['player1_algo']}")
        self.log_message(f"Player 2 (🔵): {self.settings['player2_algo']}")
        self.log_message(f"Total Stik: {sum(self.controller.state)}")
        self.log_message("=" * 50)
        self.log_message("")

        self.draw_state()
        self.update_current_player()

        if self.settings["autoplay"]:
            self.autoplay_after_id = self.window.after(self.settings["speed_ms"], self.auto_play)

    def update_current_player(self):
        """Update label pemain saat ini."""
        player = self.controller.current_player
        algo = self.controller.get_current_algo()
        color = "#e74c3c" if player == 1 else "#3498db"
        emoji = "🔴" if player == 1 else "🔵"

        self.current_player_label.config(
            text=f"Giliran: Player {player} {emoji} ({algo})",
            fg=color
        )

    def next_step(self):
        """Jalankan satu langkah."""
        if not self.is_running:
            return

        move_info = self.controller.play_one_move()
        if move_info:
            self.process_move(move_info)

    def auto_play(self):
        """Auto-play untuk pertandingan."""
        self.autoplay_after_id = None  # job sedang dieksekusi sekarang

        if not self.is_running:
            return

        self.next_step()

        if self.is_running and not self.controller.game_over:
            self.autoplay_after_id = self.window.after(self.settings["speed_ms"], self.auto_play)

    def process_move(self, move_info):
        """Process hasil move."""
        player = move_info.get("player")
        player_emoji = "🔴" if player == 1 else "🔵"

        self.log_message(
            f"Move #{move_info.get('move_number')}: Player {player} {player_emoji} "
            f"({move_info.get('algorithm')})"
        )

        move = move_info.get("move")
        if move is None:
            note = move_info.get("note", "Move tidak tersedia.")
            self.log_message(f"  ↳ {note}")
        else:
            self.log_message(f"  ↳ Ambil {move[1]} stik dari Row {move[0]}")

        stats = move_info.get("stats") or {}
        duration = float(stats.get("duration_ms", 0.0))
        stat_text = f"  ↳ Waktu: {duration:.2f} ms"

        nodes = int(stats.get("nodes_explored", 0))
        if nodes > 0:
            stat_text += f", Nodes: {nodes}"

        if stats.get("fallback_used"):
            stat_text += ", Fallback: YA"

        if stats.get("error"):
            stat_text += f", Error: {stats.get('error')}"

        self.log_message(stat_text)
        self.log_message("")

        self.draw_state()

        if move_info.get("game_over"):
            self.finish_match()
        else:
            self.update_current_player()

    def force_finish(self):
        """Paksa selesai dan tampilkan hasil."""
        if not self.is_running:
            return

        self.is_running = False
        self._cancel_after_jobs()

        if self.controller.game_over:
            self.finish_match()
        else:
            self.log_message("\n⚠️ Pertandingan dihentikan paksa!")
            self.window.destroy()
            # Kembali ke setup
            app = SetupWindow(lambda s: GameWindow(s, self.on_finish_callback).run())
            app.run()

    def finish_match(self):
        """Selesaikan pertandingan dan pindah ke result window."""
        if not self.is_running:
            # tetap pastikan after dibatalkan
            self._cancel_after_jobs()

        self.is_running = False
        self._cancel_after_jobs()

        summary = self.controller.get_match_summary()
        self.window.destroy()
        self.on_finish_callback(summary, self.settings)

    def run(self):
        """Jalankan window."""
        self.window.mainloop()


class ResultWindow:
    """Window untuk menampilkan hasil pertandingan."""

    def __init__(self, summary, settings):
        self.summary = summary
        self.settings = settings

        self.window = tk.Tk()
        self.window.title("Hasil Pertandingan - Game NIM Misère")
        self.window.geometry("700x650")
        self.window.resizable(False, False)

        # Jika user klik X, tutup window hasil
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk window hasil."""
        # Header
        winner = self.summary['winner']
        header_bg = "#27ae60" if winner else "#95a5a6"

        header_frame = tk.Frame(self.window, bg=header_bg, pady=20)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="🏆 PERTANDINGAN SELESAI",
            font=("Arial", 22, "bold"),
            bg=header_bg,
            fg="white"
        ).pack()

        if winner:
            winner_algo = self.summary[f'player{winner}']['algorithm']
            winner_emoji = "🔴" if winner == 1 else "🔵"
            tk.Label(
                header_frame,
                text=f"Pemenang: Player {winner} {winner_emoji} ({winner_algo})",
                font=("Arial", 14),
                bg=header_bg,
                fg="white"
            ).pack()

        # Main content
        content_frame = tk.Frame(self.window, padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Match info
        info_frame = tk.LabelFrame(
            content_frame,
            text="📊 Ringkasan Pertandingan",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        info_data = [
            ("Level:", self.settings['difficulty']),
            ("Total Langkah:", str(self.summary['total_moves'])),
            ("Durasi Match:", f"{self.summary['match_duration_sec']:.2f} detik")
        ]

        for label, value in info_data:
            row = tk.Frame(info_frame)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Arial", 10, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 10), anchor=tk.W).pack(side=tk.LEFT)

        # Player statistics
        for player_num in [1, 2]:
            player_data = self.summary[f'player{player_num}']
            is_winner = (player_num == self.summary['winner'])

            emoji = "🔴" if player_num == 1 else "🔵"
            trophy = " 🏆" if is_winner else ""

            player_frame = tk.LabelFrame(
                content_frame,
                text=f"{emoji} Player {player_num} - {player_data['algorithm']}{trophy}",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=10
            )
            player_frame.pack(fill=tk.X, pady=(0, 10))

            stats = [
                ("Jumlah Langkah:", f"{player_data['moves_count']} moves"),
                ("Total Waktu:", f"{player_data['total_time_ms']:.2f} ms"),
                ("Rata-rata Waktu:", f"{player_data['avg_time_ms']:.2f} ms/move"),
                ("Total Nodes Explored:", f"{player_data['total_nodes']:,}")
            ]

            for label, value in stats:
                row = tk.Frame(player_frame)
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text=label, font=("Arial", 9), width=20, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row, text=value, font=("Arial", 9, "bold"), anchor=tk.W).pack(side=tk.LEFT)

        # Conclusion
        if winner:
            loser = self.summary['loser']
            loser_algo = self.summary[f'player{loser}']['algorithm']
            loser_emoji = "🔴" if loser == 1 else "🔵"

            conclusion_frame = tk.Frame(content_frame, bg="#ecf0f1", padx=15, pady=15)
            conclusion_frame.pack(fill=tk.X, pady=(10, 15))

            tk.Label(
                conclusion_frame,
                text=f"💔 Player {loser} {loser_emoji} ({loser_algo}) mengambil stik terakhir dan KALAH",
                font=("Arial", 10),
                bg="#ecf0f1",
                fg="#7f8c8d",
                wraplength=600,
                justify=tk.CENTER
            ).pack()

        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="🔄 Pertandingan Baru",
            command=self.new_match,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="❌ Keluar",
            command=self.window.destroy,  # lebih bersih daripada quit untuk multi-window
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=12
        ).pack(side=tk.LEFT, padx=5)

    def new_match(self):
        """Mulai pertandingan baru."""
        self.window.destroy()
        app = SetupWindow(lambda s: GameWindow(s, lambda summary, settings: ResultWindow(summary, settings).run()).run())
        app.run()

    def run(self):
        """Jalankan window."""
        self.window.mainloop()
