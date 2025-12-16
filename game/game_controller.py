"""
Controller untuk menjalankan pertandingan komputer vs komputer
"""

import time
from game.nim_logic import is_terminal, apply_move
from algorithms.reflex import reflex_move
from algorithms.alpha_beta import alphabeta_move


class GameController:
    """
    Controller untuk mengelola pertandingan NIM antara dua AI.
    """
    
    def __init__(self, initial_state, player1_algo, player2_algo):
        """
        Inisialisasi game controller.
        
        Args:
            initial_state: List berisi jumlah stik di setiap tumpukan
            player1_algo: str, "Reflex" atau "Alpha-Beta" atau "Human"
            player2_algo: str, "Reflex" atau "Alpha-Beta"
        """
        self.initial_state = initial_state.copy()
        self.state = initial_state.copy()
        self.player1_algo = player1_algo
        self.player2_algo = player2_algo
        self.current_player = 1
        self.game_over = False
        self.winner = None
        
        # Statistik
        self.move_history = []
        self.total_moves = 0
        self.match_start_time = None
        self.match_duration = 0
        
        # Algoritma mapping
        self.algo_map = {
            "Reflex": reflex_move,
            "Alpha-Beta": alphabeta_move
        }
    
    def reset(self):
        """Reset game ke kondisi awal."""
        self.state = self.initial_state.copy()
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.total_moves = 0
        self.match_start_time = None
        self.match_duration = 0
    
    def get_current_algo(self):
        """Mendapatkan algoritma untuk pemain saat ini."""
        if self.current_player == 1:
            return self.player1_algo
        else:
            return self.player2_algo
    
    def play_one_move(self):
        """
        Mainkan satu langkah dari pemain saat ini.
        
        Returns:
            dict: Informasi tentang langkah yang dimainkan
        """
        if self.game_over:
            return None
        
        # Mulai timer match pada move pertama
        if self.match_start_time is None:
            self.match_start_time = time.time()
        
        # Dapatkan algoritma untuk pemain saat ini
        algo_name = self.get_current_algo()
        algo_func = self.algo_map[algo_name]
        
        # Eksekusi move
        move, stats = algo_func(self.state)
        
        # Terapkan move
        self.state = apply_move(self.state, move)
        self.total_moves += 1
        
        # Simpan history
        move_info = {
            "move_number": self.total_moves,
            "player": self.current_player,
            "algorithm": algo_name,
            "move": move,
            "state_after": self.state.copy(),
            "stats": stats
        }
        self.move_history.append(move_info)
        
        # Cek apakah game selesai
        if is_terminal(self.state):
            self.game_over = True
            # Pemain yang mengambil stik terakhir = kalah (Misère)
            self.winner = 2 if self.current_player == 1 else 1
            self.match_duration = time.time() - self.match_start_time
            
            move_info["game_over"] = True
            move_info["winner"] = self.winner
            move_info["loser"] = self.current_player
        else:
            move_info["game_over"] = False
            # Ganti pemain
            self.current_player = 2 if self.current_player == 1 else 1
        
        return move_info
    
    def get_match_summary(self):
        """
        Mendapatkan ringkasan pertandingan.
        
        Returns:
            dict: Ringkasan lengkap pertandingan
        """
        # Jika game belum selesai, hitung durasi sementara
        if not self.game_over and self.match_start_time:
            current_duration = time.time() - self.match_start_time
        else:
            current_duration = self.match_duration
        
        # Hitung statistik per pemain
        p1_moves = [m for m in self.move_history if m["player"] == 1]
        p2_moves = [m for m in self.move_history if m["player"] == 2]
        
        p1_total_time = sum(m["stats"]["duration_ms"] for m in p1_moves)
        p2_total_time = sum(m["stats"]["duration_ms"] for m in p2_moves)
        
        p1_total_nodes = sum(m["stats"].get("nodes_explored", 0) for m in p1_moves)
        p2_total_nodes = sum(m["stats"].get("nodes_explored", 0) for m in p2_moves)
        
        summary = {
            "winner": self.winner if self.game_over else None,
            "loser": (2 if self.winner == 1 else 1) if self.game_over else None,
            "total_moves": self.total_moves,
            "match_duration_sec": current_duration,
            "player1": {
                "algorithm": self.player1_algo,
                "moves_count": len(p1_moves),
                "total_time_ms": p1_total_time,
                "avg_time_ms": p1_total_time / len(p1_moves) if p1_moves else 0,
                "total_nodes": p1_total_nodes
            },
            "player2": {
                "algorithm": self.player2_algo,
                "moves_count": len(p2_moves),
                "total_time_ms": p2_total_time,
                "avg_time_ms": p2_total_time / len(p2_moves) if p2_moves else 0,
                "total_nodes": p2_total_nodes
            }
        }
        
        return summary