
"""
Konfigurasi level kesulitan untuk Game Nim
"""

DIFFICULTY_LEVELS = {
    "Easy": {
        "description": "Permainan ringan untuk testing cepat",
        "piles": [1, 3, 5, 7],
        "total_sticks": 16
    },
    "Medium": {
        "description": "Tantangan sedang dengan lebih banyak tumpukan",
        "piles": [1, 3, 5, 7, 9, 11, 13, 15],
        "total_sticks": 64
    },
    "Hard": {
        "description": "Tantangan berat dengan 500 stik",
        "piles": [10, 20, 30, 40, 50, 60, 70, 80, 90, 50],
        "total_sticks": 500
    },
    "Extreme": {
        "description": "Tantangan ekstrem dengan 2000 stik",
        "piles": [100, 150, 200, 250, 300, 350, 250, 200, 150, 50],
        "total_sticks": 2000
    }
}

# Algoritma yang tersedia
ALGORITHMS = {
    "Reflex": "Agen berbasis aturan (NIM-SUM)",
    "Alpha-Beta": "Minimax dengan Alpha-Beta Pruning"
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