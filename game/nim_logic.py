"""
Core logic untuk permainan NIM versi Misere
(Pemain yang mengambil stik terakhir KALAH)

State  : List[int] -> jumlah stik di setiap tumpukan
Move   : (i, k)    -> ambil k stik dari tumpukan index i
"""

from __future__ import annotations
from typing import Iterable, List, Tuple, Dict

State = List[int]
Move = Tuple[int, int]


def validate_state(state: State) -> None:
    """Validasi state agar tidak korup."""
    if not isinstance(state, list) or len(state) == 0:
        raise ValueError("state harus berupa list non-kosong.")

    for p in state:
        if not isinstance(p, int):
            raise TypeError("Setiap nilai pile harus int.")
        if p < 0:
            raise ValueError("Nilai pile tidak boleh negatif.")


def is_terminal(state: State) -> bool:
    """
    Game selesai jika semua tumpukan kosong (0).
    """
    validate_state(state)
    return all(pile == 0 for pile in state)


def is_valid_move(state: State, move: Move) -> bool:
    """
    Cek apakah move legal untuk state saat ini.
    """
    validate_state(state)

    if not (isinstance(move, tuple) and len(move) == 2):
        return False

    i, k = move
    if not isinstance(i, int) or not isinstance(k, int):
        return False

    if i < 0 or i >= len(state):
        return False

    if k <= 0 or k > state[i]:
        return False

    return True


def iter_moves(state: State) -> Iterable[Move]:
    """
    Generator semua langkah legal (lebih hemat memori dibanding list besar).
    """
    validate_state(state)
    for i, pile in enumerate(state):
        for k in range(1, pile + 1):
            yield (i, k)


def get_moves(state: State) -> List[Move]:
    """
    Menghasilkan semua langkah legal dari state saat ini.
    """
    return list(iter_moves(state))


def apply_move(state: State, move: Move, *, strict: bool = True) -> State:
    """
    Mengembalikan state baru setelah langkah dilakukan.

    strict=True  -> kalau move invalid, raise ValueError (disarankan untuk stabilitas)
    strict=False -> kalau move invalid, kembalikan copy state (lebih toleran, tapi bisa menutupi bug)
    """
    if strict and not is_valid_move(state, move):
        raise ValueError(f"Move tidak valid {move} untuk state {state}")

    if not strict and not is_valid_move(state, move):
        return state.copy()

    i, k = move
    new_state = state.copy()
    new_state[i] -= k  # aman karena sudah tervalidasi
    return new_state


def winner_if_terminal_misere(state: State, player_to_move: int, *, num_players: int = 2) -> int:
    """
    Menentukan pemenang JIKA state sudah terminal.

    Aturan Misère: pemain yang mengambil stik terakhir kalah.
    Artinya: jika state terminal pada awal giliran player_to_move,
    maka player_to_move MENANG.

    Return: index pemain pemenang (0..num_players-1)
    """
    if num_players < 2:
        raise ValueError("num_players minimal 2.")
    if not isinstance(player_to_move, int):
        raise TypeError("player_to_move harus int.")

    if not is_terminal(state):
        raise ValueError("winner_if_terminal_misere hanya boleh dipanggil pada state terminal.")

    return player_to_move % num_players


def get_game_info(state: State) -> Dict[str, int]:
    """
    Mendapatkan informasi statistik dari state saat ini.
    """
    validate_state(state)
    return {
        "total_sticks": sum(state),
        "active_piles": sum(1 for p in state if p > 0),
        "total_piles": len(state),
        "empty_piles": sum(1 for p in state if p == 0),
    }
