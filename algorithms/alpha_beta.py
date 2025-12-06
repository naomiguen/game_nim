
"""
Algoritma Alpha-Beta Pruning untuk NIM Misere
Minimax dengan optimasi pruning untuk mengurangi node yang dieksplorasi
"""

import time
from game.nim_logic import is_terminal, get_moves, apply_move


class AlphaBetaAgent:
    """
    Agent yang menggunakan algoritma Alpha-Beta Pruning.
    """
    
    def __init__(self):
        self.nodes_explored = 0
        self.pruning_count = 0
    
    def reset_counters(self):
        """Reset counter untuk statistik."""
        self.nodes_explored = 0
        self.pruning_count = 0
    
    def alphabeta(self, state, is_max_turn, alpha, beta):
        """
        Implementasi Alpha-Beta Pruning untuk NIM Misere.
        
        Args:
            state: List berisi jumlah stik di setiap tumpukan
            is_max_turn: bool, True jika giliran MAX (komputer pertama)
            alpha: float, nilai alpha untuk pruning
            beta: float, nilai beta untuk pruning
            
        Returns:
            int: Nilai evaluasi (+1 untuk menang, -1 untuk kalah)
        """
        self.nodes_explored += 1
        
        # Base case: terminal state
        if is_terminal(state):
            # Dalam Misere NIM, pemain yang AKAN jalan pada state terminal
            # adalah pemenang (pemain sebelumnya ambil stik terakhir = kalah)
            return 1 if is_max_turn else -1
        
        moves = get_moves(state)
        
        if is_max_turn:
            # MAX player (mencari nilai maksimum)
            value = float('-inf')
            for move in moves:
                next_state = apply_move(state, move)
                value = max(value, self.alphabeta(next_state, False, alpha, beta))
                alpha = max(alpha, value)
                
                # Alpha-Beta Pruning
                if alpha >= beta:
                    self.pruning_count += 1
                    break
                    
            return value
        else:
            # MIN player (mencari nilai minimum)
            value = float('inf')
            for move in moves:
                next_state = apply_move(state, move)
                value = min(value, self.alphabeta(next_state, True, alpha, beta))
                beta = min(beta, value)
                
                # Alpha-Beta Pruning
                if beta <= alpha:
                    self.pruning_count += 1
                    break
                    
            return value
    
    def get_best_move(self, state):
        """
        Mencari langkah terbaik menggunakan Alpha-Beta Pruning.
        
        Args:
            state: List berisi jumlah stik di setiap tumpukan
            
        Returns:
            tuple: (index_tumpukan, jumlah_stik_diambil)
            dict: Statistics (waktu, nodes explored, dll)
        """
        start_time = time.time()
        self.reset_counters()
        
        best_value = float('-inf')
        best_move = None
        
        moves = get_moves(state)
        
        for move in moves:
            next_state = apply_move(state, move)
            value = self.alphabeta(next_state, False, float('-inf'), float('inf'))
            
            if value > best_value:
                best_value = value
                best_move = move
        
        duration_ms = (time.time() - start_time) * 1000.0
        
        stats = {
            "algorithm": "Alpha-Beta",
            "duration_ms": duration_ms,
            "nodes_explored": self.nodes_explored,
            "pruning_count": self.pruning_count,
            "best_value": best_value,
            "total_possible_moves": len(moves)
        }
        
        return best_move, stats


def alphabeta_move(state):
    """
    Wrapper function untuk kompatibilitas dengan interface lain.
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        tuple: (move, stats)
    """
    agent = AlphaBetaAgent()
    return agent.get_best_move(state)