# gui/game_gui.py
"""
GUI untuk Game NIM - Dengan 2 Mode: Pemain vs Komputer & Komputer vs Komputer
Design modern dan user-friendly
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from game.game_controller import GameController
from game.nim_logic import apply_move, is_terminal
from algorithms.reflex import reflex_move
from algorithms.alpha_beta import alphabeta_move
from config.settings import DIFFICULTY_LEVELS, ALGORITHMS


class SetupWindow:
    """Window untuk setup pertandingan dengan design modern."""
    
    def __init__(self, on_start_callback):
        self.on_start_callback = on_start_callback
        self.window = tk.Tk()
        self.window.title("Game NIM Misère - Setup")
        self.window.geometry("750x820")
        self.window.configure(bg="#FFF8E7")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI untuk window setup."""
        # Main container dengan scroll
        canvas = tk.Canvas(self.window, bg="#FFF8E7", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF8E7")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_container = scrollable_frame
        main_container.config(bg="#FFF8E7")
        
        # Padding
        padding = tk.Frame(main_container, bg="#FFF8E7", height=20)
        padding.pack()
        
        # Header - JUDUL
        tk.Label(
            main_container,
            text="Game Nim",
            font=("Arial", 28, "bold"),
            bg="#FFF8E7",
            fg="#FF8C00"
        ).pack(pady=(0, 20))
        
        # Mode Selection dengan layout baru
        mode_label = tk.Label(
            main_container,
            text="Pilih Mode Permainan",
            font=("Arial", 13, "bold"),
            bg="#FFF8E7",
            fg="#8B4513",
            anchor=tk.W
        )
        mode_label.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        self.mode_var = tk.StringVar(value="player_vs_ai")
        
        mode_frame = tk.Frame(main_container, bg="#FFF8E7")
        mode_frame.pack(fill=tk.X, pady=(0, 25), padx=30)
        
        # Mode buttons dengan card style
        self.mode_buttons = {}
        
        modes = [
            ("player_vs_ai", "🎮", "Pemain vs Komputer"),
            ("ai_vs_ai", "⚙️", "Komputer vs Komputer")
        ]
        
        for idx, (value, icon, text) in enumerate(modes):
            is_selected = value == "player_vs_ai"
            
            # Outer card frame
            card_frame = tk.Frame(mode_frame, bg="#FFF8E7")
            card_frame.pack(side=tk.LEFT, padx=7, expand=True, fill=tk.BOTH)
            
            # Inner button frame dengan border
            btn_frame = tk.Frame(
                card_frame,
                bg="#FF8C00" if is_selected else "white",
                relief=tk.SOLID,
                bd=3 if is_selected else 1,
                highlightcolor="#FF8C00",
                highlightthickness=0
            )
            btn_frame.pack(fill=tk.BOTH, expand=True, ipady=30)
            
            # Rb untuk mode selection
            rb_var = tk.IntVar(value=1 if is_selected else 0)
            
            def create_mode_click(val):
                def on_click():
                    self.mode_var.set(val)
                    self.update_mode_buttons()
                    self.on_mode_change()
                return on_click
            
            rb = tk.Radiobutton(
                btn_frame,
                text=f"{icon}\n{text}",
                variable=self.mode_var,
                value=value,
                font=("Arial", 12, "bold"),
                bg="#FF8C00" if is_selected else "white",
                fg="white" if is_selected else "#999",
                selectcolor="#FF8C00",
                activebackground="#FF8C00" if is_selected else "white",
                activeforeground="white" if is_selected else "#999",
                indicatoron=False,
                padx=20,
                pady=30,
                command=create_mode_click(value),
                justify=tk.CENTER
            )
            rb.pack(fill=tk.BOTH, expand=True)
            
            self.mode_buttons[value] = (btn_frame, rb)
        
        # Difficulty Level
        diff_label = tk.Label(
            main_container,
            text="Level Kesulitan",
            font=("Arial", 13, "bold"),
            bg="#FFF8E7",
            fg="#8B4513",
            anchor=tk.W
        )
        diff_label.pack(fill=tk.X, pady=(0, 10), padx=30)
        
        self.difficulty_var = tk.StringVar(value="Easy")
        self.difficulty_buttons = {}
        
        diff_frame = tk.Frame(main_container, bg="#FFF8E7")
        diff_frame.pack(fill=tk.X, pady=(0, 25), padx=30)
        
        for level_name in DIFFICULTY_LEVELS.keys():
            level_info = DIFFICULTY_LEVELS[level_name]
            
            is_selected = level_name == "Easy"
            
            btn = tk.Radiobutton(
                diff_frame,
                text=level_name,
                variable=self.difficulty_var,
                value=level_name,
                font=("Arial", 11, "bold"),
                bg="#FF8C00" if is_selected else "#F5F5F5",
                fg="white" if is_selected else "#999",
                selectcolor="#FF8C00",
                activebackground="#FF8C00",
                activeforeground="white",
                indicatoron=False,
                width=12,
                padx=15,
                pady=10,
                command=self.on_difficulty_change
            )
            btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
            self.difficulty_buttons[level_name] = btn
        
        # Algorithm Selection
        algo_label = tk.Label(
            main_container,
            text="Pilih Algoritma",
            font=("Arial", 13, "bold"),
            bg="#FFF8E7",
            fg="#8B4513",
            anchor=tk.W
        )
        algo_label.pack(fill=tk.X, pady=(0, 10), padx=30)
        
        self.algo_frame_container = tk.Frame(main_container, bg="#FFF8E7")
        self.algo_frame_container.pack(fill=tk.X, pady=(0, 25), padx=30)
        
        self.player1_var = tk.StringVar(value="Reflex")
        self.player2_var = tk.StringVar(value="Alpha-Beta")
        
        self.update_algorithm_section()
        
        # Auto-play option
        autoplay_label = tk.Label(
            main_container,
            text="Main Otomatis",
            font=("Arial", 13, "bold"),
            bg="#FFF8E7",
            fg="#8B4513",
            anchor=tk.W
        )
        autoplay_label.pack(fill=tk.X, pady=(0, 10), padx=30)
        
        self.autoplay_frame = tk.Frame(main_container, bg="#FFF8E7")
        self.autoplay_frame.pack(fill=tk.X, pady=(0, 25), padx=30)
        
        self.autoplay_var = tk.BooleanVar(value=False)
        
        # Custom toggle switch
        toggle_frame = tk.Frame(self.autoplay_frame, bg="#FFF8E7")
        toggle_frame.pack(side=tk.LEFT)
        
        self.toggle_canvas = tk.Canvas(
            toggle_frame,
            width=60,
            height=30,
            bg="#FFF8E7",
            highlightthickness=0,
            cursor="hand2"
        )
        self.toggle_canvas.pack()
        self.toggle_canvas.bind("<Button-1>", self.toggle_autoplay)
        
        # Draw initial toggle state
        self.draw_toggle()
        
        # Start button
        start_btn = tk.Button(
            main_container,
            text="Mulai Permainan",
            command=self.start_match,
            font=("Arial", 15, "bold"),
            bg="#FF8C00",
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            activebackground="#FF7700"
        )
        start_btn.pack(pady=(20, 40), fill=tk.X, padx=30)
        
        # Bottom padding
        padding = tk.Frame(main_container, bg="#FFF8E7", height=30)
        padding.pack()
    
    def on_difficulty_change(self):
        """Update ketika difficulty berubah."""
        # Update button styling
        selected = self.difficulty_var.get()
        for level_name, btn in self.difficulty_buttons.items():
            if level_name == selected:
                btn.config(bg="#FF8C00", fg="white")
            else:
                btn.config(bg="#F5F5F5", fg="#666")
    
    def update_mode_buttons(self):
        """Update warna button mode saat diklik."""
        selected = self.mode_var.get()
        for mode, (btn_frame, rb) in self.mode_buttons.items():
            is_selected = mode == selected
            btn_frame.config(
                bg="#FF8C00" if is_selected else "white",
                bd=3 if is_selected else 1
            )
            rb.config(
                bg="#FF8C00" if is_selected else "white",
                fg="white" if is_selected else "#999",
                activebackground="#FF8C00" if is_selected else "white",
                activeforeground="white" if is_selected else "#999"
            )
    
    def draw_toggle(self):
        """Gambar toggle switch."""
        self.toggle_canvas.delete("all")
        
        is_on = self.autoplay_var.get()
        bg_color = "#4CAF50" if is_on else "#CCCCCC"
        circle_x = 40 if is_on else 15
        
        # Background rounded rectangle
        self.toggle_canvas.create_oval(5, 5, 25, 25, fill=bg_color, outline=bg_color)
        self.toggle_canvas.create_rectangle(15, 5, 45, 25, fill=bg_color, outline=bg_color)
        self.toggle_canvas.create_oval(35, 5, 55, 25, fill=bg_color, outline=bg_color)
        
        # Circle
        self.toggle_canvas.create_oval(
            circle_x - 10, 7, circle_x + 10, 23,
            fill="white",
            outline="white"
        )
    
    def toggle_autoplay(self, event=None):
        """Toggle autoplay state."""
        current = self.autoplay_var.get()
        self.autoplay_var.set(not current)
        self.draw_toggle()
    
    def on_mode_change(self):
        """Update UI ketika mode berubah."""
        self.update_algorithm_section()
        
        # Show/hide autoplay untuk AI vs AI saja
        mode = self.mode_var.get()
        if mode == "ai_vs_ai":
            self.autoplay_frame.pack(fill=tk.X, pady=(0, 25), padx=30)
        else:
            self.autoplay_frame.pack_forget()
    
    def update_algorithm_section(self):
        """Update bagian algoritma berdasarkan mode."""
        # Clear existing widgets
        for widget in self.algo_frame_container.winfo_children():
            widget.destroy()
        
        mode = self.mode_var.get()
        
        if mode == "ai_vs_ai":
            # Show both players untuk AI vs AI
            algo_container = tk.Frame(self.algo_frame_container, bg="#FFF8E7")
            algo_container.pack(fill=tk.X)
            
            for algo in ALGORITHMS.keys():
                is_selected = algo == "Reflex"
                
                btn = tk.Radiobutton(
                    algo_container,
                    text=algo,
                    variable=self.player1_var,
                    value=algo,
                    font=("Arial", 11, "bold"),
                    bg="#FF8C00" if is_selected else "#F0F0F0",
                    fg="white" if is_selected else "#666",
                    selectcolor="#FF8C00",
                    activebackground="#FF8C00",
                    activeforeground="white",
                    indicatoron=False,
                    padx=15,
                    pady=12,
                    width=30,
                    justify=tk.LEFT
                )
                btn.pack(fill=tk.X, pady=5)
        
        else:
            # Show only computer algorithm untuk Player vs AI
            algo_container = tk.Frame(self.algo_frame_container, bg="#FFF8E7")
            algo_container.pack(fill=tk.X)
            
            for algo in ALGORITHMS.keys():
                is_selected = algo == "Reflex"
                
                btn = tk.Radiobutton(
                    algo_container,
                    text=algo,
                    variable=self.player1_var,
                    value=algo,
                    font=("Arial", 11, "bold"),
                    bg="#FF8C00" if is_selected else "#F0F0F0",
                    fg="white" if is_selected else "#666",
                    selectcolor="#FF8C00",
                    activebackground="#FF8C00",
                    activeforeground="white",
                    indicatoron=False,
                    padx=15,
                    pady=12,
                    width=30,
                    justify=tk.LEFT
                )
                btn.pack(fill=tk.X, pady=5)
    
    def start_match(self):
        """Callback ketika tombol start diklik."""
        settings = {
            "mode": self.mode_var.get(),
            "difficulty": self.difficulty_var.get(),
            "player1_algo": self.player1_var.get(),
            "player2_algo": self.player2_var.get() if self.mode_var.get() == "ai_vs_ai" else self.player1_var.get(),
            "autoplay": self.autoplay_var.get() if self.mode_var.get() == "ai_vs_ai" else False,
            "speed_ms": 500
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
        self.window.title("Game NIM Misère - Pertandingan")
        self.window.geometry("1000x750")
        self.window.configure(bg="#FFF8E7")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Game state
        difficulty = DIFFICULTY_LEVELS[settings["difficulty"]]
        self.state = difficulty["piles"].copy()
        self.initial_state = difficulty["piles"].copy()
        
        self.is_player_vs_ai = (settings["mode"] == "player_vs_ai")
        self.is_player_turn = True  # Player mulai duluan di mode player vs AI
        self.game_over = False
        self.winner = None
        
        # For AI vs AI mode
        if not self.is_player_vs_ai:
            self.controller = GameController(
                difficulty["piles"],
                settings["player1_algo"],
                settings["player2_algo"]
            )
            self.is_running = True
        else:
            self.controller = None
            self.computer_algo = settings["player1_algo"]
            self.algo_map = {
                "Reflex": reflex_move,
                "Alpha-Beta": alphabeta_move
            }
        
        self.move_count = 0
        
        self.setup_ui()
        
        # Start match
        if not self.is_player_vs_ai:
            self.window.after(500, self.start_ai_match)
        else:
            self.window.after(500, self.start_player_match)
    
    def setup_ui(self):
        """Setup UI untuk window game."""
        # Header
        header_frame = tk.Frame(self.window, bg="#FF8C00", pady=15)
        header_frame.pack(fill=tk.X)
        
        # Timer di kiri (untuk AI vs AI)
        if not self.is_player_vs_ai:
            self.timer_label = tk.Label(
                header_frame,
                text="⏱️ 0:00",
                font=("Arial", 14, "bold"),
                bg="#FF8C00",
                fg="white"
            )
            self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # Title di tengah - GEDEIN
        title_container = tk.Frame(header_frame, bg="#FF8C00")
        title_container.pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            title_container,
            text="Game NIM Misère",
            font=("Arial", 24, "bold"),
            bg="#FF8C00",
            fg="white"
        ).pack()
        
        mode_text = "AI vs AI" if not self.is_player_vs_ai else "Pemain vs AI"
        tk.Label(
            title_container,
            text=f"Mode: {mode_text} | Level: {self.settings['difficulty']}",
            font=("Arial", 11),
            bg="#FF8C00",
            fg="#FFE8CC"
        ).pack()
        
        # Player indicator di kanan
        self.player_label = tk.Label(
            header_frame,
            text="🎮 Pemain" if self.is_player_vs_ai else "🔴 Player 1",
            font=("Arial", 12, "bold"),
            bg="#FFE8CC",
            fg="#FF8C00",
            padx=20,
            pady=8,
            relief=tk.FLAT
        )
        self.player_label.pack(side=tk.RIGHT, padx=20)
        
        # Main content
        main_frame = tk.Frame(self.window, bg="#FFF8E7")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left: Game board (LEBIH BESAR DAN CANTIK)
        left_frame = tk.Frame(main_frame, bg="#FFF8E7")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Info box
        info_box = tk.Frame(left_frame, bg="#FFE8CC", relief=tk.FLAT, padx=15, pady=10)
        info_box.pack(fill=tk.X, pady=(0, 15))
        
        if self.is_player_vs_ai:
            tk.Label(
                info_box,
                text="Algoritma Komputer: " + self.settings['player1_algo'],
                font=("Arial", 10),
                bg="#FFE8CC",
                fg="#8B4513"
            ).pack(side=tk.LEFT)
        else:
            info_text = f"🔴 {self.settings['player1_algo']} vs 🔵 {self.settings['player2_algo']}"
            tk.Label(
                info_box,
                text=info_text,
                font=("Arial", 10),
                bg="#FFE8CC",
                fg="#8B4513"
            ).pack()
        
        # Canvas untuk stik (DIPERBESAR)
        canvas_container = tk.Frame(left_frame, bg="white", relief=tk.FLAT)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.state_canvas = tk.Canvas(canvas_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.state_canvas.yview)
        
        self.state_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.state_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind click untuk player vs AI
        if self.is_player_vs_ai:
            self.state_canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Instruction untuk player
        if self.is_player_vs_ai:
            instruction = tk.Label(
                left_frame,
                text="💡 Klik pada stik untuk mengambil semua stik dari posisi tersebut hingga akhir baris",
                font=("Arial", 9),
                bg="#FFE8CC",
                fg="#8B4513",
                wraplength=500,
                justify=tk.CENTER,
                padx=10,
                pady=10
            )
            instruction.pack(fill=tk.X, pady=(10, 0))
        
        # Right: Log
        right_frame = tk.Frame(main_frame, bg="#FFF8E7")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="📝 Log Pertandingan",
            font=("Arial", 13, "bold"),
            bg="#FFF8E7",
            fg="#8B4513"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        log_container = tk.Frame(right_frame, bg="white", relief=tk.FLAT)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            font=("Courier", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="white",
            relief=tk.FLAT
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Bottom: Controls (hanya untuk AI vs AI dengan manual mode)
        if not self.is_player_vs_ai and not self.settings["autoplay"]:
            control_frame = tk.Frame(self.window, bg="#FFF8E7", pady=15)
            control_frame.pack(fill=tk.X, padx=20)
            
            self.next_button = tk.Button(
                control_frame,
                text="⏭️ Langkah Berikutnya",
                command=self.next_step,
                font=("Arial", 12, "bold"),
                bg="#FF8C00",
                fg="white",
                relief=tk.FLAT,
                padx=30,
                pady=12,
                cursor="hand2"
            )
            self.next_button.pack(side=tk.LEFT, padx=5)
    
    def draw_state(self):
        """Gambar stik dengan design yang lebih cantik."""
        self.state_canvas.delete("all")
        
        canvas_width = self.state_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 600
        
        y_offset = 30
        row_height = 60
        
        max_sticks_display = 50  # Maksimal stik yang ditampilkan per baris
        
        for i, pile in enumerate(self.state):
            # Label baris
            label_text = f"Baris {i + 1}"
            self.state_canvas.create_text(
                20, y_offset + 15,
                text=label_text,
                anchor=tk.W,
                font=("Arial", 11, "bold"),
                fill="#8B4513"
            )
            
            if pile == 0:
                # Baris kosong
                self.state_canvas.create_text(
                    canvas_width // 2, y_offset + 15,
                    text="Baris kosong",
                    font=("Arial", 10, "italic"),
                    fill="#CCC"
                )
            else:
                # Gambar stik
                display_count = min(pile, max_sticks_display)
                stick_width = 12
                stick_height = 35
                stick_gap = 8
                
                start_x = 120
                
                for j in range(display_count):
                    x1 = start_x + j * (stick_width + stick_gap)
                    x2 = x1 + stick_width
                    y1 = y_offset
                    y2 = y_offset + stick_height
                    
                    # Shadow
                    self.state_canvas.create_oval(
                        x1, y2, x2, y2 + 8,
                        fill="#DDD",
                        outline=""
                    )
                    
                    # Stick (buat clickable untuk player mode)
                    stick_id = self.state_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#FF8C00",
                        outline="#FF7700",
                        width=2,
                        tags=f"stick_{i}_{j}"
                    )
                    
                    # Simpan info untuk click detection
                    if self.is_player_vs_ai:
                        self.state_canvas.tag_bind(stick_id, "<Enter>", 
                            lambda e, row=i, pos=j: self.on_stick_hover(row, pos))
                        self.state_canvas.tag_bind(stick_id, "<Leave>", 
                            lambda e: self.on_stick_leave())
                
                # Count label
                count_text = f"{pile} stik"
                if pile > max_sticks_display:
                    count_text += f" (menampilkan {max_sticks_display})"
                
                self.state_canvas.create_text(
                    canvas_width - 80, y_offset + 15,
                    text=count_text,
                    anchor=tk.E,
                    font=("Arial", 10),
                    fill="#666"
                )
            
            y_offset += row_height
        
        self.state_canvas.config(scrollregion=self.state_canvas.bbox("all"))
    
    def on_stick_hover(self, row, pos):
        """Highlight saat hover di player mode."""
        if not self.is_player_turn or self.game_over:
            return
        
        # Highlight semua stik dari posisi ini sampai akhir
        for j in range(pos, self.state[row]):
            self.state_canvas.itemconfig(f"stick_{row}_{j}", fill="#FFD700")
    
    def on_stick_leave(self):
        """Unhighlight saat leave."""
        # Reset semua stik ke warna normal
        for item in self.state_canvas.find_all():
            if "stick_" in str(self.state_canvas.gettags(item)):
                self.state_canvas.itemconfig(item, fill="#FF8C00")
    
    def on_canvas_click(self, event):
        """Handle click pada canvas untuk player move."""
        if not self.is_player_turn or self.game_over:
            return
        
        # Cari item yang diklik
        item = self.state_canvas.find_closest(event.x, event.y)[0]
        tags = self.state_canvas.gettags(item)
        
        for tag in tags:
            if tag.startswith("stick_"):
                parts = tag.split("_")
                row = int(parts[1])
                pos = int(parts[2])
                
                # Ambil semua stik dari posisi ini sampai akhir
                take_count = self.state[row] - pos
                
                self.player_move(row, take_count)
                break
    
    def player_move(self, row, count):
        """Proses move dari player."""
        self.move_count += 1
        
        # Apply move
        self.state = apply_move(self.state, (row, count))
        self.draw_state()
        
        self.log_message(f"Move #{self.move_count}: 🎮 Pemain")
        self.log_message(f"  ↳ Ambil {count} stik dari Baris {row + 1}")
        self.log_message("")
        
        # Check terminal
        if is_terminal(self.state):
            self.game_over = True
            self.winner = "computer"
            self.show_result()
            return
        
        # Ganti ke giliran komputer
        self.is_player_turn = False
        self.player_label.config(text="🤖 Komputer", bg="#E3F2FD", fg="#2196F3")
        
        # Komputer main otomatis setelah delay
        self.window.after(800, self.computer_move)
    
    def computer_move(self):
        """Komputer main."""
        algo_func = self.algo_map[self.computer_algo]
        move, stats = algo_func(self.state)
        
        self.move_count += 1
        
        # Apply move
        self.state = apply_move(self.state, move)
        self.draw_state()
        
        self.log_message(f"Move #{self.move_count}: 🤖 Komputer ({self.computer_algo})")
        self.log_message(f"  ↳ Ambil {move[1]} stik dari Baris {move[0] + 1}")
        self.log_message(f"  ↳ Waktu: {stats['duration_ms']:.2f} ms")
        self.log_message("")
        
        # Check terminal
        if is_terminal(self.state):
            self.game_over = True
            self.winner = "player"
            self.show_result()
            return
        
        # Ganti ke giliran player
        self.is_player_turn = True
        self.player_label.config(text="🎮 Pemain", bg="#FFE8CC", fg="#FF8C00")
    
    def show_result(self):
        """Tampilkan hasil untuk player vs AI."""
        if self.winner == "player":
            title = "🎉 Selamat!"
            message = "Anda MENANG!\nKomputer mengambil stik terakhir."
        else:
            title = "😢 Sayang Sekali"
            message = "Anda KALAH.\nAnda mengambil stik terakhir."
        
        messagebox.showinfo(title, message)
        
        # Kembali ke setup
        self.window.destroy()
        app = SetupWindow(lambda s: GameWindow(s, self.on_finish_callback).run())
        app.run()
    
    # === AI vs AI Methods ===
    
    def start_ai_match(self):
        """Mulai AI vs AI match."""
        self.log_message("=" * 50)
        self.log_message("🎮 PERTANDINGAN AI vs AI DIMULAI")
        self.log_message(f"🔴 Player 1: {self.settings['player1_algo']}")
        self.log_message(f"🔵 Player 2: {self.settings['player2_algo']}")
        self.log_message(f"📊 Total Stik: {sum(self.state)}")
        self.log_message("=" * 50)
        self.log_message("")
        
        self.draw_state()
        
        if self.settings["autoplay"]:
            self.window.after(self.settings["speed_ms"], self.auto_play)
    
    def start_player_match(self):
        """Mulai player vs AI match."""
        self.log_message("=" * 50)
        self.log_message("🎮 PERTANDINGAN DIMULAI")
        self.log_message(f"🤖 Komputer: {self.computer_algo}")
        self.log_message(f"📊 Total Stik: {sum(self.state)}")
        self.log_message("=" * 50)
        self.log_message("")
        
        self.draw_state()
    
    def next_step(self):
        """Untuk AI vs AI manual mode."""
        if not self.is_running:
            return
        
        move_info = self.controller.play_one_move()
        if move_info:
            self.process_ai_move(move_info)
    
    def auto_play(self):
        """Auto-play untuk AI vs AI."""
        if not self.is_running:
            return
        
        self.next_step()
        
        if self.is_running and not self.controller.game_over:
            self.window.after(self.settings["speed_ms"], self.auto_play)
    
    def process_ai_move(self, move_info):
        """Process move dari AI vs AI."""
        self.state = move_info['state_after']
        
        player_emoji = "🔴" if move_info['player'] == 1 else "🔵"
        
        self.log_message(
            f"Move #{move_info['move_number']}: Player {move_info['player']} {player_emoji} "
            f"({move_info['algorithm']})"
        )
        self.log_message(
            f"  ↳ Ambil {move_info['move'][1]} stik dari Baris {move_info['move'][0] + 1}"
        )
        
        stats = move_info['stats']
        stat_text = f"  ↳ Waktu: {stats['duration_ms']:.2f} ms"
        if stats.get('nodes_explored', 0) > 0:
            stat_text += f", Nodes: {stats['nodes_explored']}"
        self.log_message(stat_text)
        self.log_message("")
        
        self.draw_state()
        
        # Update player indicator
        if not move_info['game_over']:
            next_player = self.controller.current_player
            next_algo = self.controller.get_current_algo()
            emoji = "🔴" if next_player == 1 else "🔵"
            self.player_label.config(text=f"{emoji} Player {next_player}")
        
        if move_info['game_over']:
            self.finish_ai_match()
    
    def finish_ai_match(self):
        """Selesai AI vs AI."""
        self.is_running = False
        summary = self.controller.get_match_summary()
        
        self.window.destroy()
        self.on_finish_callback(summary, self.settings)
    
    def log_message(self, message):
        """Tambahkan pesan ke log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def run(self):
        """Jalankan window."""
        self.window.mainloop()


class ResultWindow:
    """Window untuk menampilkan hasil pertandingan AI vs AI."""
    
    def __init__(self, summary, settings):
        self.summary = summary
        self.settings = settings
        
        self.window = tk.Tk()
        self.window.title("Game NIM Misère - Hasil")
        self.window.geometry("700x700")
        self.window.configure(bg="#FFF8E7")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk window hasil."""
        # Main container
        main_container = tk.Frame(self.window, bg="#FFF8E7")
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Trophy icon
        tk.Label(
            main_container,
            text="🏆",
            font=("Arial", 60),
            bg="#FFF8E7"
        ).pack(pady=(0, 10))
        
        # Title - GEDEIN
        tk.Label(
            main_container,
            text="Permainan Selesai!",
            font=("Arial", 28, "bold"),
            bg="#FFF8E7",
            fg="#FF8C00"
        ).pack(pady=(0, 10))
        
        # Winner announcement
        winner = self.summary['winner']
        winner_algo = self.summary[f'player{winner}']['algorithm']
        winner_emoji = "🔴" if winner == 1 else "🔵"
        
        winner_frame = tk.Frame(main_container, bg="#FFE8CC", relief=tk.FLAT, padx=30, pady=20)
        winner_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            winner_frame,
            text="Pemenang",
            font=("Arial", 14),
            bg="#FFE8CC",
            fg="#8B4513"
        ).pack()
        
        tk.Label(
            winner_frame,
            text=f"{winner_emoji} Player {winner}",
            font=("Arial", 24, "bold"),
            bg="#FFE8CC",
            fg="#FF8C00"
        ).pack()
        
        tk.Label(
            winner_frame,
            text=winner_algo,
            font=("Arial", 16),
            bg="#FFE8CC",
            fg="#8B4513"
        ).pack()
        
        # Match info
        info_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, padx=20, pady=15)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            info_frame,
            text=f"⏱️ Waktu Bermain\n{self.summary['match_duration_sec']:.2f} detik",
            font=("Arial", 12),
            bg="white",
            fg="#666",
            justify=tk.CENTER
        ).pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            info_frame,
            text=f"🎯 Total Langkah\n{self.summary['total_moves']} moves",
            font=("Arial", 12),
            bg="white",
            fg="#666",
            justify=tk.CENTER
        ).pack(side=tk.LEFT, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_container, bg="#FFF8E7")
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="🔄 Main Lagi",
            command=self.new_match,
            font=("Arial", 14, "bold"),
            bg="#FF8C00",
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2"
        ).pack(pady=5, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="❌ Keluar",
            command=self.window.quit,
            font=("Arial", 12),
            bg="#999",
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2"
        ).pack(pady=5, fill=tk.X)
    
    def new_match(self):
        """Mulai pertandingan baru."""
        self.window.destroy()
        app = SetupWindow(lambda s: GameWindow(s, lambda summary, settings: ResultWindow(summary, settings).run()).run())
        app.run()
    
    def run(self):
        """Jalankan window."""
        self.window.mainloop()