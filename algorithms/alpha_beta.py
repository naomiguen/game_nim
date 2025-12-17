"""
Algoritma Alpha-Beta Pruning untuk NIM Misere
Optimasi: Memoization + Depth Limit + Heuristic Evaluation + Recursion Limit Fix
"""

import time
import sys
from functools import reduce
from operator import ixor
from game.nim_logic import is_terminal, get_moves, apply_move

# 1. FIX RECURSION ERROR: Naikkan batas rekursi Python
sys.setrecursionlimit(5000)

class AlphaBetaAgent:
    def __init__(self, max_depth=200):
        self.nodes_explored = 0
        self.pruning_count = 0
        self.memo = {}
        # Batasi kedalaman agar tidak crash pada game dengan ribuan stik
        self.max_depth = max_depth 

    def reset_counters(self):
        self.nodes_explored = 0
        self.pruning_count = 0
        self.memo = {}

    def get_nim_sum(self, state):
        """Hitung XOR sum (untuk heuristic)."""
        return reduce(ixor, state, 0)

    def heuristic_value(self, state, is_max_turn):
        """
        Menilai kondisi papan menggunakan rumus matematika (Reflex) 
        jika kedalaman pencarian sudah mentok.
        """
        ones = sum(1 for p in state if p == 1)
        bigs = sum(1 for p in state if p > 1)
        nim_s = self.get_nim_sum(state)

        # Logika Misere (Sama seperti Reflex Agent)
        is_winning = False
        if bigs == 0:
            # End Game: Menang jika jumlah tumpukan GENAP (karena kita ingin sisakan ganjil buat lawan)
            # Tapi tunggu, di sini giliran KITA. Jika sisa GENAP, kita ambil 1, sisa GANJIL buat lawan.
            # Lawan ambil terakhir -> Lawan kalah -> Kita Menang.
            is_winning = (ones % 2 == 0)
        else:
            # Normal Game: Menang jika NIM-SUM != 0
            is_winning = (nim_s != 0)

        # Jika menurut rumus kita menang:
        # Jika giliran MAX (AI), return 1. Jika giliran MIN (Lawan), return -1.
        if is_winning:
            return 1 if is_max_turn else -1
        else:
            return -1 if is_max_turn else 1

    def alphabeta(self, state, is_max_turn, alpha, beta, depth):
        self.nodes_explored += 1
        
        state_key = (tuple(state), is_max_turn)

        if state_key in self.memo:
            return self.memo[state_key]

        if is_terminal(state):
            return 1 if is_max_turn else -1
        
        # 2. DEPTH LIMIT CHECK
        # Jika sudah berpikir terlalu dalam (melebihi batas), stop berpikir
        # dan gunakan insting matematika (heuristic)
        if depth <= 0:
            return self.heuristic_value(state, is_max_turn)

        moves = get_moves(state)
        
        # Urutkan moves: ambil stik terbanyak dulu (optimasi pruning)
        # Tapi jika depth tinggal sedikit, random aja biar cepat
        if depth > 2:
            moves.sort(key=lambda x: x[1], reverse=True)

        if is_max_turn:
            value = float('-inf')
            for move in moves:
                next_state = apply_move(state, move)
                # Kurangi depth setiap rekursi
                val = self.alphabeta(next_state, False, alpha, beta, depth - 1)
                value = max(value, val)
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.pruning_count += 1
                    break
        else:
            value = float('inf')
            for move in moves:
                next_state = apply_move(state, move)
                val = self.alphabeta(next_state, True, alpha, beta, depth - 1)
                value = min(value, val)
                beta = min(beta, value)
                if beta <= alpha:
                    self.pruning_count += 1
                    break
        
        self.memo[state_key] = value
        return value

    def get_best_move(self, state):
        start_time = time.time()
        self.reset_counters()
        
        best_value = float('-inf')
        best_move = None
        
        moves = get_moves(state)
        # Sorting moves di level teratas sangat penting
        moves.sort(key=lambda x: x[1], reverse=True)

        alpha = float('-inf')
        beta = float('inf')

        # Tentukan kedalaman dinamis berdasarkan kompleksitas
        # Jika stik sedikit, depth dalam. Jika stik ribuan, depth dangkal.
        total_sticks = sum(state)
        current_depth_limit = self.max_depth
        if total_sticks > 500:
            current_depth_limit = 100  # Kurangi depth jika stik sangat banyak

        for move in moves:
            next_state = apply_move(state, move)
            value = self.alphabeta(next_state, False, alpha, beta, current_depth_limit)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)
        
        duration_ms = (time.time() - start_time) * 1000.0
        
        stats = {
            "algorithm": "Alpha-Beta (Robust)",
            "duration_ms": duration_ms,
            "nodes_explored": self.nodes_explored,
            "pruning_count": self.pruning_count,
            "best_value": best_value,
            "total_possible_moves": len(moves),
            "depth_limit": current_depth_limit
        }
        
        return best_move, stats

def alphabeta_move(state):
    agent = AlphaBetaAgent()
    return agent.get_best_move(state)