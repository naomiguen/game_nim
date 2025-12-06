# main.py
"""
Entry point untuk Game NIM Misère - AI vs AI
Menggunakan multiple windows: Setup -> Game -> Result
"""

from gui.game_gui import SetupWindow, GameWindow, ResultWindow


def main():
    """
    Fungsi utama untuk menjalankan aplikasi.
    
    Flow:
    1. SetupWindow - User pilih settings
    2. GameWindow - Jalankan pertandingan
    3. ResultWindow - Tampilkan hasil
    4. Loop back ke SetupWindow jika user mau main lagi
    """
    def on_start_match(settings):
        """Callback ketika user start match dari setup window."""
        game = GameWindow(settings, on_match_finish)
        game.run()
    
    def on_match_finish(summary, settings):
        """Callback ketika match selesai."""
        result = ResultWindow(summary, settings)
        result.run()
    
    # Mulai dari setup window
    setup = SetupWindow(on_start_match)
    setup.run()


if __name__ == "__main__":
    main()