
"""
Core logic untuk permainan NIM versi Misere
(Pemain yang mengambil stik terakhir KALAH)
"""

def is_terminal(state):
    """
    Cek apakah game sudah selesai (semua tumpukan kosong).
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        bool: True jika semua tumpukan kosong
    """
    return all(pile == 0 for pile in state)


def get_moves(state):
    """
    Menghasilkan semua langkah legal dari state saat ini.
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        List of tuple: [(index_tumpukan, jumlah_stik_diambil), ...]
    """
    moves = []
    for i, pile in enumerate(state):
        for k in range(1, pile + 1):
            moves.append((i, k))
    return moves


def apply_move(state, move):
    """
    Mengembalikan state baru setelah langkah dilakukan.
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        move: Tuple (index_tumpukan, jumlah_stik_diambil)
        
    Returns:
        List: State baru setelah move diterapkan
    """
    i, k = move

    # Validasi: pastikan hanya satu pile dan jumlah legal
    if not (0 <= i < len(state)):
        raise ValueError(f"Invalid pile index: {i}")
    if k <= 0 or k > state[i]:
        raise ValueError(f"Invalid move: cannot take {k} from pile {i} with {state[i]} sticks")

    new_state = state.copy()
    new_state[i] -= k
    return new_state



def get_game_info(state):
    """
    Mendapatkan informasi statistik dari state saat ini.
    
    Args:
        state: List berisi jumlah stik di setiap tumpukan
        
    Returns:
        dict: Informasi game (total stik, jumlah tumpukan aktif, dll)
    """
    return {
        "total_sticks": sum(state),
        "active_piles": sum(1 for p in state if p > 0),
        "total_piles": len(state),
        "empty_piles": sum(1 for p in state if p == 0)
    }