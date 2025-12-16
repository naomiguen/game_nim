"""
Algoritma Reflex Agent untuk NIM Misere
Menggunakan strategi NIM-SUM (XOR) dengan variasi Random saat posisi kalah.
"""

from functools import reduce
from operator import ixor
import time
import random 

def nim_sum(state):
    """Hitung XOR dari semua tumpukan (NIM-SUM)."""
    return reduce(ixor, state, 0)

def reflex_move(state):
    """
    Strategi:
    1. End Game: Jika sisa tumpukan cuma angka 1 semua, atur biar ganjil/genap (Misere).
    2. Winning Position (Nim-Sum != 0): Cari langkah pasti biar Nim-Sum jadi 0.
    3. Losing Position (Nim-Sum == 0): Ambil acak (biar tidak kaku).
    """
    start_time = time.time()
    
    # Hitung jumlah tumpukan yang isinya cuma 1 (ones) dan lebih dari 1 (bigs)
    ones = sum(1 for p in state if p == 1)
    bigs = sum(1 for p in state if p > 1)
    
    move = None
    strategy_used = ""
    
    # KASUS 1: END GAME (Semua tumpukan isinya tinggal 1 atau 0)
    if bigs == 0:
        strategy_used = "End Game (All 1s)"
        # Cari tumpukan yang masih ada isinya
        available_piles = [i for i, p in enumerate(state) if p > 0]
        
        # Di Misere, kita ingin menyisakan 1 batang terakhir untuk lawan.
        # Jadi total batang yang tersisa setelah giliran kita harus GANJIL (1, 3, 5...).
        # Saat ini jumlah batang = 'ones'.
        
        # Jika 'ones' genap, kita ambil 1 biar sisa ganjil (Kita Menang)
        # Jika 'ones' ganjil, kita terpaksa ambil 1 dan sisa genap (Kita Kalah)
        # Apapun kondisinya di sini, langkah terbaik cuma bisa ambil 1.
        if available_piles:
            move = (available_piles[0], 1)

 
    # KASUS 2: NORMAL GAME (Masih ada tumpukan besar)
    else:
        nim = nim_sum(state)
        
        # -POSISI KALAH (Losing Position)
        if nim == 0:
            strategy_used = "NIM-SUM = 0 (Random Move)"
            
            # Cari semua tumpukan yang ada isinya
            valid_piles = [i for i, p in enumerate(state) if p > 0]
            
            # PERBAIKAN: Pilih tumpukan acak & jumlah acak
            if valid_piles:
                pile_idx = random.choice(valid_piles)     # Pilih tumpukan acak
                max_sticks = state[pile_idx]
                amount = random.randint(1, max_sticks)    # Pilih jumlah acak (1 s.d. habis)
                move = (pile_idx, amount)

        # POSISI MENANG (Winning Position) 
        else:
            strategy_used = "Force NIM-SUM = 0"
            
            # Kita cari move yang membuat NIM-SUM jadi 0
            for i, p in enumerate(state):
                target = p ^ nim
                if target < p:
                    # Normal Nim Strategy
                    k = p - target
                    
                    # Trik Khusus Misere:
                    # Jika langkah ini membuat sisa tumpukan HANYA berisi angka 1 (tidak ada bigs lagi),
                    # Kita harus pastikan jumlah tumpukan angka 1 yang tersisa adalah GANJIL.
                    
                    remaining_bigs = bigs - (1 if p > 1 and target <= 1 else 0)
                    
                    if remaining_bigs == 0:
                        # Ini langkah krusial transisi ke End Game
                        if target == 0:
                            # Jika kita mau habiskan tumpukan ini, cek sisa 'ones'
                            # Kita mau sisa total tumpukan (termasuk yang lain) ganjil.
                            # current ones (selain pile ini) = ones
                            if ones % 2 == 0:
                                # Sisa genap -> bahaya. Kita harus sisakan 1 batang di sini, bukan 0.
                                # (Kecuali p memang 1, tapi itu masuk kasus End Game di atas)
                                k = p - 1 # Sisakan 1
                            else:
                                k = p # Habiskan
                        else:
                             # Jika targetnya jadi 1 (karena XOR), berarti total ones nambah 1
                             if (ones + 1) % 2 == 0:
                                 k = p # Habiskan saja tumpukan ini kalau bisa
                                 pass 

                    move = (i, k)
                    break

    # Fallback (Jaga-jaga jika logika di atas miss, ambil random 1)
    if move is None:
        strategy_used = "Fallback"
        valid_piles = [i for i, p in enumerate(state) if p > 0]
        if valid_piles:
            move = (valid_piles[0], 1)

    duration_ms = (time.time() - start_time) * 1000.0
    
    stats = {
        "algorithm": "Reflex",
        "duration_ms": duration_ms,
        "strategy": strategy_used,
        "nodes_explored": 0
    }
    
    return move, stats