"""
Konfigurasi level kesulitan untuk Game Nim
"""

# Batas aman untuk Alpha-Beta (tanpa depth limit).
# Di atas ini, Alpha-Beta cenderung freeze karena state space meledak.
ALPHABETA_MAX_STICKS = 20

DIFFICULTY_LEVELS = {
    "Easy": {
        "description": "Permainan ringan untuk testing cepat (AMAN untuk Alpha-Beta)",
        "piles": [1, 3, 5, 7],
        "total_sticks": 16,
        "allow_alphabeta": True
    },
    "Medium": {
        "description": "Tantangan sedang (disarankan Reflex; Alpha-Beta akan sangat lambat)",
        "piles": [1, 3, 5, 7, 9, 11, 13, 15],
        "total_sticks": 64,
        "allow_alphabeta": False
    },
    "Hard": {
        "description": "Tantangan berat (Reflex saja; Alpha-Beta tidak realistis)",
        "piles": [10, 20, 30, 40, 50, 60, 70, 80, 90, 50],
        "total_sticks": 500,
        "allow_alphabeta": False
    },
    "Extreme": {
        "description": "Tantangan ekstrem (Reflex saja; Alpha-Beta tidak realistis)",
        "piles": [100, 150, 200, 250, 300, 350, 250, 200, 150, 50],
        "total_sticks": 2000,
        "allow_alphabeta": False
    }
}

# Algoritma yang tersedia
ALGORITHMS = {
    "Reflex": "Agen berbasis aturan (Misère NIM-SUM + kasus khusus)",
    "Alpha-Beta": "Minimax dengan Alpha-Beta Pruning (hanya disarankan untuk state kecil)"
}

# Pengaturan GUI
GUI_CONFIG = {
    "window_width": 900,
    "window_height": 700,
    "canvas_width": 600,
    "match_width": 8,
    "match_height": 40,
    "match_gap": 6,
    "row_spacing": 60
}
