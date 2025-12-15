
"""
Algoritma Reflex Agent untuk NIM Misere
Menggunakan strategi NIM-SUM (XOR) dengan adaptasi untuk Misere
"""

from functools import reduce
from operator import ixor
import time


def nim_sum(state):
    return reduce(ixor, state, 0)


def reflex_move(state):
    """
    Misère Nim strategy (optimal):
    - Jika semua heap non-zero bernilai 1: posisi menang jika jumlah heap-1 GENAP.
      (tetap ambil 1 dari heap mana pun; hasil menang/kalah ditentukan paritas)
    - Jika ada heap > 1:
        - Jika jumlah heap >1 hanya satu: mainkan paritas (reduce heap besar ke 1 atau 0)
        - Jika jumlah heap >1 >= 2: mainkan seperti Normal Nim (buat nim-sum = 0)
    """
    start_time = time.time()

    nonzero_indices = [i for i, p in enumerate(state) if p > 0]
    if not nonzero_indices:
        # state terminal; tidak ada move legal
        duration_ms = (time.time() - start_time) * 1000.0
        return None, {
            "algorithm": "Reflex",
            "duration_ms": duration_ms,
            "strategy": "Terminal state (no move)",
            "nim_sum_before": nim_sum(state),
            "nodes_explored": 0,
        }

    ones_count = sum(1 for p in state if p == 1)
    big_indices = [i for i, p in enumerate(state) if p > 1]
    bigs = len(big_indices)

    move = None
    strategy_used = ""

    # Case A: semua heap yang aktif adalah 1 (bigs == 0)
    if bigs == 0:
        strategy_used = "All active heaps are 1 (misère parity case)"
        # Ambil 1 dari heap mana pun (paritas menentukan menang/kalah)
        i = nonzero_indices[0]
        move = (i, 1)

    # Case B: tepat satu heap besar (>1)
    elif bigs == 1:
        big_i = big_indices[0]
        big_size = state[big_i]
        # Jika jumlah heap-1 GENAP -> reduce heap besar ke 1 (tinggalkan ganjil heap-1 utk lawan)
        # Jika jumlah heap-1 GANJIL -> habiskan heap besar (tinggalkan ganjil heap-1 utk lawan)
        if ones_count % 2 == 0:
            strategy_used = "Single big heap; ones even -> reduce big heap to 1"
            move = (big_i, big_size - 1)  # sisa jadi 1
        else:
            strategy_used = "Single big heap; ones odd -> remove big heap entirely"
            move = (big_i, big_size)      # sisa jadi 0

    # Case C: ada >=2 heap besar, main seperti normal nim
    else:
        nim = nim_sum(state)
        if nim == 0:
            strategy_used = "NIM-SUM = 0 (losing position) -> take 1 from first nonzero"
            i = nonzero_indices[0]
            move = (i, 1)
        else:
            strategy_used = "Force NIM-SUM = 0 (normal-nim move for misère)"
            for i, p in enumerate(state):
                target = p ^ nim
                if target < p:
                    k = p - target
                    move = (i, k)
                    break

    # Final fallback (harusnya tidak kejadian)
    if move is None:
        strategy_used = "Fallback strategy"
        i = nonzero_indices[0]
        move = (i, 1)

    duration_ms = (time.time() - start_time) * 1000.0
    stats = {
        "algorithm": "Reflex",
        "duration_ms": duration_ms,
        "strategy": strategy_used,
        "nim_sum_before": nim_sum(state),
        "nodes_explored": 0,
    }
    return move, stats