
from gui.game_gui import SetupWindow, GameWindow, ResultWindow


def main():
    """
    Fungsi utama untuk menjalankan aplikasi.
    
    Flow:
    1. SetupWindow - User pilih mode & settings
    2. GameWindow - Jalankan pertandingan
    3. ResultWindow - Tampilkan hasil (untuk AI vs AI)
       atau kembali ke Setup (untuk Player vs AI)
    """
    def on_start_match(settings):
        """Callback ketika user start match dari setup window."""
        game = GameWindow(settings, on_match_finish)
        game.run()
    
    def on_match_finish(summary, settings):
        """Callback ketika match AI vs AI selesai."""
        result = ResultWindow(summary, settings)
        result.run()
    
    # Mulai dari setup window
    setup = SetupWindow(on_start_match)
    setup.run()


if __name__ == "__main__":
    main()