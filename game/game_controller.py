"""
Controller untuk menjalankan pertandingan komputer vs komputer (Misère Nim)
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from game.nim_logic import (
    is_terminal,
    apply_move,
    is_valid_move,
)

from algorithms.reflex import reflex_move
from algorithms.alpha_beta import alphabeta_move

State = List[int]
Move = Tuple[int, int]


class GameController:
    """
    Controller untuk mengelola pertandingan NIM antara dua AI.
    """

    def __init__(self, initial_state: State, player1_algo: str, player2_algo: str):
        self.initial_state = initial_state.copy()
        self.state = initial_state.copy()

        self.player1_algo = player1_algo
        self.player2_algo = player2_algo

        self.current_player = 1
        self.game_over = False
        self.winner: Optional[int] = None

        # Statistik
        self.move_history: List[Dict[str, Any]] = []
        self.total_moves = 0
        self.match_start_time: Optional[float] = None
        self.match_duration = 0.0

        # Algoritma mapping
        self.algo_map = {
            "Reflex": reflex_move,
            "Alpha-Beta": alphabeta_move,
        }

        # Guard teoritis: maksimal langkah = total stik (tiap langkah minimal ambil 1)
        self.max_moves_guard = sum(self.initial_state)

        # Jika state awal terminal, langsung set game over (Misère: pemain yang giliran sekarang menang)
        if is_terminal(self.state):
            self.game_over = True
            self.winner = self.current_player

    def reset(self):
        """Reset game ke kondisi awal."""
        self.state = self.initial_state.copy()
        self.current_player = 1
        self.game_over = False
        self.winner = None

        self.move_history = []
        self.total_moves = 0
        self.match_start_time = None
        self.match_duration = 0.0

        self.max_moves_guard = sum(self.initial_state)

        if is_terminal(self.state):
            self.game_over = True
            self.winner = self.current_player

    def get_current_algo(self) -> str:
        """Mendapatkan algoritma untuk pemain saat ini."""
        return self.player1_algo if self.current_player == 1 else self.player2_algo

    @staticmethod
    def _fallback_move(state: State) -> Move:
        """Move paling aman: ambil 1 dari pile pertama yang masih > 0."""
        for i, p in enumerate(state):
            if p > 0:
                return (i, 1)
        return (0, 0)  # state terminal; seharusnya tidak dipakai

    def _safe_get_move(self, algo_name: str) -> Tuple[Move, Dict[str, Any]]:
        """
        Ambil move dari AI dengan proteksi:
        - kalau AI error -> fallback
        - kalau AI menghasilkan move invalid -> fallback
        """
        algo_func = self.algo_map.get(algo_name)
        if algo_func is None:
            # jangan dibiarkan KeyError; ini kesalahan konfigurasi
            raise ValueError(f"Algoritma tidak dikenal: {algo_name}")

        stats: Dict[str, Any] = {}
        try:
            result = algo_func(self.state)
            if isinstance(result, tuple) and len(result) == 2:
                move, stats = result
            else:
                move, stats = result, {}

        except Exception as e:
            move = self._fallback_move(self.state)
            stats = {
                "duration_ms": 0,
                "error": f"AI exception: {type(e).__name__}: {e}",
                "fallback_used": True,
            }
            return move, stats

        # Validasi move
        if not is_valid_move(self.state, move):
            fallback = self._fallback_move(self.state)
            stats = dict(stats) if isinstance(stats, dict) else {}
            stats.update({
                "invalid_move": move,
                "fallback_used": True,
                "fallback_move": fallback,
            })
            move = fallback

        return move, stats

    def play_one_move(self) -> Optional[Dict[str, Any]]:
        """
        Mainkan satu langkah dari pemain saat ini.

        Returns:
            dict: Informasi tentang langkah yang dimainkan
        """
        if self.game_over:
            return None

        # Terminal safety (kalau state jadi terminal karena reset/bug eksternal)
        if is_terminal(self.state):
            self.game_over = True
            self.winner = self.current_player  # Misère: giliran sekarang menang
            return {
                "move_number": self.total_moves,
                "player": self.current_player,
                "algorithm": self.get_current_algo(),
                "move": None,
                "state_after": self.state.copy(),
                "stats": {},
                "game_over": True,
                "winner": self.winner,
                "note": "Terminal state reached before move.",
            }

        # Mulai timer match pada move pertama
        if self.match_start_time is None:
            self.match_start_time = time.time()

        # Guard: kalau melewati batas teoritis, stop (indikasi ada bug invalid move / state tidak berkurang)
        if self.total_moves >= self.max_moves_guard and self.max_moves_guard > 0:
            self.game_over = True
            self.winner = None
            self.match_duration = time.time() - self.match_start_time
            return {
                "move_number": self.total_moves,
                "player": self.current_player,
                "algorithm": self.get_current_algo(),
                "move": None,
                "state_after": self.state.copy(),
                "stats": {"guard_triggered": True},
                "game_over": True,
                "winner": None,
                "note": "Move guard triggered. Possible invalid-move loop or state not decreasing.",
            }

        algo_name = self.get_current_algo()
        move, stats = self._safe_get_move(algo_name)

        # Terapkan move (strict)
        try:
            self.state = apply_move(self.state, move)
        except Exception as e:
            # Kalau apply_move strict melempar error, fallback sekali lagi
            fallback = self._fallback_move(self.state)
            self.state = apply_move(self.state, fallback)
            stats = dict(stats) if isinstance(stats, dict) else {}
            stats.update({
                "apply_move_error": f"{type(e).__name__}: {e}",
                "fallback_used": True,
                "fallback_move": fallback,
            })
            move = fallback

        self.total_moves += 1

        move_info: Dict[str, Any] = {
            "move_number": self.total_moves,
            "player": self.current_player,
            "algorithm": algo_name,
            "move": move,
            "state_after": self.state.copy(),
            "stats": stats if isinstance(stats, dict) else {},
        }
        self.move_history.append(move_info)

        # Cek apakah game selesai
        if is_terminal(self.state):
            self.game_over = True
            # Misère: pemain yang mengambil stik terakhir kalah -> pemenang adalah lawannya
            self.winner = 2 if self.current_player == 1 else 1
            self.match_duration = time.time() - (self.match_start_time or time.time())

            move_info["game_over"] = True
            move_info["winner"] = self.winner
            move_info["loser"] = self.current_player
        else:
            move_info["game_over"] = False
            self.current_player = 2 if self.current_player == 1 else 1

        return move_info

    def run_to_end(self, delay_sec: float = 0.0) -> Dict[str, Any]:
        """
        Jalankan sampai selesai (berguna untuk mode CPU vs CPU tanpa GUI).
        """
        while not self.game_over:
            self.play_one_move()
            if delay_sec > 0:
                time.sleep(delay_sec)
        return self.get_match_summary() or {}

    def get_match_summary(self) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan ringkasan pertandingan.
        """
        if not self.game_over:
            return None

        p1_moves = [m for m in self.move_history if m.get("player") == 1]
        p2_moves = [m for m in self.move_history if m.get("player") == 2]

        def _sum_duration(moves: List[Dict[str, Any]]) -> float:
            total = 0.0
            for m in moves:
                s = m.get("stats") or {}
                total += float(s.get("duration_ms", 0))
            return total

        def _sum_nodes(moves: List[Dict[str, Any]]) -> int:
            total = 0
            for m in moves:
                s = m.get("stats") or {}
                total += int(s.get("nodes_explored", 0))
            return total

        p1_total_time = _sum_duration(p1_moves)
        p2_total_time = _sum_duration(p2_moves)

        p1_total_nodes = _sum_nodes(p1_moves)
        p2_total_nodes = _sum_nodes(p2_moves)

        summary = {
            "winner": self.winner,
            "loser": (2 if self.winner == 1 else 1) if self.winner in (1, 2) else None,
            "total_moves": self.total_moves,
            "match_duration_sec": self.match_duration,
            "player1": {
                "algorithm": self.player1_algo,
                "moves_count": len(p1_moves),
                "total_time_ms": p1_total_time,
                "avg_time_ms": (p1_total_time / len(p1_moves)) if p1_moves else 0,
                "total_nodes": p1_total_nodes,
            },
            "player2": {
                "algorithm": self.player2_algo,
                "moves_count": len(p2_moves),
                "total_time_ms": p2_total_time,
                "avg_time_ms": (p2_total_time / len(p2_moves)) if p2_moves else 0,
                "total_nodes": p2_total_nodes,
            },
        }
        return summary
