
"""
Algoritma Reflex Agent untuk NIM Misere
Menggunakan strategi NIM-SUM (XOR) dengan adaptasi untuk Misere
"""

from functools import reduce
from operator import ixor
import time


def nim_sum(state):
    """
    Hitung XOR dari semua tumpukan (NIM-SUM).
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        int: Hasil XOR dari semua nilai tumpukan
    """
    return reduce(ixor, state, 0)


def reflex_move(state):
    """
    Menentukan langkah terbaik berdasarkan aturan Misere NIM.
    
    Strategi:
    - Jika semua tumpukan berisi 1 stik: ambil 1 stik dari sembarang tumpukan
    - Jika NIM-SUM = 0: posisi jelek, ambil 1 stik dari sembarang tumpukan
    - Jika NIM-SUM ≠ 0: cari langkah yang membuat NIM-SUM = 0
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        tuple: (index_tumpukan, jumlah_stik_diambil)
        dict: Statistics (waktu eksekusi, dll)
    """
    start_time = time.time()
    
    ones = sum(1 for p in state if p == 1)
    bigs = sum(1 for p in state if p > 1)
    
    move = None
    strategy_used = ""
    
    # Kasus 1: Semua tumpukan berisi 1 stik
    if bigs == 0:
        strategy_used = "All piles have 1 stick"
        for i, p in enumerate(state):
            if p > 0:
                move = (i, 1)
                break
    
    # Kasus 2: Ada tumpukan lebih dari 1 stik
    else:
        nim = nim_sum(state)
        
        if nim == 0:
            # Posisi jelek (losing position)
            strategy_used = "NIM-SUM = 0 (losing position)"
            for i, p in enumerate(state):
                if p > 0:
                    move = (i, 1)
                    break
        else:
            # Cari langkah yang membuat NIM-SUM = 0
            strategy_used = "Force NIM-SUM = 0 (winning position)"
            for i, p in enumerate(state):
                target = p ^ nim
                if target < p:
                    k = p - target
                    move = (i, k)
                    break
    
    # Fallback (seharusnya tidak pernah terjadi)
    if move is None:
        strategy_used = "Fallback strategy"
        for i, p in enumerate(state):
            if p > 0:
                move = (i, 1)
                break
    
    duration_ms = (time.time() - start_time) * 1000.0
    
    stats = {
        "algorithm": "Reflex",
        "duration_ms": duration_ms,
        "strategy": strategy_used,
        "nim_sum_before": nim_sum(state),
        "nodes_explored": 0  # Reflex tidak explore nodes
    }
    
    return move, stats