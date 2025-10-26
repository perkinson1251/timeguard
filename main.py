import tkinter as tk
import blocker
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw
import threading

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.blocker = blocker.Blocker(self.root)
        self.icon = None

    def create_image(self):
        # Generate an image for the icon
        width = 64
        height = 64
        color1 = 'black'
        color2 = 'white'
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)
        return image

    def setup_tray(self):
        menu = (
            item('Настройки', self.blocker.open_settings),
            item('Заблокировать сейчас', self.blocker.lock_now),
            pystray.Menu.SEPARATOR,
            item('Выход', self.stop_app)
        )
        self.icon = pystray.Icon("name", self.create_image(), "Blocker", menu)
        self.icon.run()

    def stop_app(self):
        self.blocker.stop()
        if self.icon:
            self.icon.stop()
        self.root.quit()

    def run(self):
        # Run tray icon in a separate thread
        tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        tray_thread.start()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
