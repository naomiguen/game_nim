import time
from game.nim_logic import is_terminal, get_moves, apply_move


class AlphaBetaAgent:
    def __init__(self):
        self.nodes_explored = 0
        self.pruning_count = 0
        self.memo = {}  # (tuple(state), is_max_turn) -> value

    def reset_counters(self):
        self.nodes_explored = 0
        self.pruning_count = 0
        self.memo.clear()

    def alphabeta(self, state, is_max_turn, alpha, beta):
        self.nodes_explored += 1

        key = (tuple(state), is_max_turn)
        if key in self.memo:
            return self.memo[key]

        if is_terminal(state):
            val = 1 if is_max_turn else -1
            self.memo[key] = val
            return val

        moves = get_moves(state)

        if is_max_turn:
            value = float("-inf")
            for move in moves:
                next_state = apply_move(state, move)
                value = max(value, self.alphabeta(next_state, False, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.pruning_count += 1
                    break
            self.memo[key] = value
            return value
        else:
            value = float("inf")
            for move in moves:
                next_state = apply_move(state, move)
                value = min(value, self.alphabeta(next_state, True, alpha, beta))
                beta = min(beta, value)
                if beta <= alpha:
                    self.pruning_count += 1
                    break
            self.memo[key] = value
            return value

    def get_best_move(self, state):
        start_time = time.time()
        self.reset_counters()

        if is_terminal(state):
            duration_ms = (time.time() - start_time) * 1000.0
            return None, {
                "algorithm": "Alpha-Beta",
                "duration_ms": duration_ms,
                "nodes_explored": 0,
                "pruning_count": 0,
                "best_value": None,
                "total_possible_moves": 0,
                "note": "Terminal state (no move)",
            }

        best_value = float("-inf")
        best_move = None

        moves = get_moves(state)
        for move in moves:
            next_state = apply_move(state, move)
            value = self.alphabeta(next_state, False, float("-inf"), float("inf"))

            if value > best_value:
                best_value = value
                best_move = move

            # Early-exit: kalau sudah pasti menang, stop cari
            if best_value == 1:
                break

        duration_ms = (time.time() - start_time) * 1000.0
        stats = {
            "algorithm": "Alpha-Beta",
            "duration_ms": duration_ms,
            "nodes_explored": self.nodes_explored,
            "pruning_count": self.pruning_count,
            "best_value": best_value,
            "total_possible_moves": len(moves),
        }
        return best_move, stats


def alphabeta_move(state):
    agent = AlphaBetaAgent()
    return agent.get_best_move(state)
