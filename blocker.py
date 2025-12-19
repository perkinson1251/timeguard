import json
import os
from datetime import datetime, timedelta
import time
import tkinter as tk
from tkinter import messagebox
import ctypes
from ctypes import wintypes
import gui
import bcrypt
import win32gui
import win32con
from localization import get_localization, _
from keyboard_blocker import KeyboardBlocker

# Audio control imports
try:
    from comtypes import CLSCTX_ALL, CoInitialize
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    AUDIO_AVAILABLE = True
    print("[System] Audio control libraries loaded successfully")
except ImportError as e:
    print(f"[System] Audio control not available: {e}")
    AUDIO_AVAILABLE = False

CONFIG_FILE = "config.json"

def stop_all_media():
    """Stop all media playback using multiple methods."""
    try:
        user32 = ctypes.windll.user32
        
        # Method 1: Windows Media Key commands (most reliable)
        VK_MEDIA_STOP = 0xB2
        VK_MEDIA_PAUSE = 0xB3
        
        # Simulate media stop key press
        user32.keybd_event(VK_MEDIA_STOP, 0, 0, 0)  # Key down
        user32.keybd_event(VK_MEDIA_STOP, 0, 2, 0)  # Key up
        
        time.sleep(0.1)
        
        # Simulate media pause key press as backup
        user32.keybd_event(VK_MEDIA_PAUSE, 0, 0, 0)  # Key down
        user32.keybd_event(VK_MEDIA_PAUSE, 0, 2, 0)  # Key up
        
        # Method 2: App command approach (backup)
        WM_APPCOMMAND = 0x319
        APPCOMMAND_MEDIA_STOP = 13
        APPCOMMAND_MEDIA_PAUSE = 14
        
        hwnd = user32.GetDesktopWindow()
        user32.SendMessageW(hwnd, WM_APPCOMMAND, 0, APPCOMMAND_MEDIA_STOP << 16)
        user32.SendMessageW(hwnd, WM_APPCOMMAND, 0, APPCOMMAND_MEDIA_PAUSE << 16)
        
        print("Media stop commands sent")
        
    except Exception as e:
        print(f"Error stopping media: {e}")

def minimize_fullscreen_windows():
    """Minimize all fullscreen windows to ensure the block screen is visible."""
    try:
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and hwnd != extra:
                # Check if window is fullscreen
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    # Get screen dimensions
                    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
                    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
                    
                    # If window covers the entire screen, minimize it
                    if (rect[2] - rect[0] >= screen_width and 
                        rect[3] - rect[1] >= screen_height):
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                except:
                    pass
            return True
        
        # Get our block window handle to avoid minimizing it
        desktop = win32gui.GetDesktopWindow()
        win32gui.EnumWindows(callback, desktop)
        
    except Exception as e:
        print(f"Error minimizing fullscreen windows: {e}")

def get_volume_interface():
    """Get the audio volume interface."""
    if not AUDIO_AVAILABLE:
        print("[Volume] Audio control libraries not available")
        return None
    
    try:
        # Initialize COM
        try:
            CoInitialize()
        except:
            pass  # Already initialized
        
        # Get default audio device
        devices = AudioUtilities.GetSpeakers()
        
        # Check if devices has _dev attribute (newer pycaw)
        if hasattr(devices, '_dev'):
            print("[Volume] Using _dev attribute for newer pycaw")
            interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        else:
            # Older pycaw API
            print("[Volume] Using direct Activate for older pycaw")
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        
        # Cast to IAudioEndpointVolume pointer
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        print(f"[Volume] Successfully obtained volume interface")
        return volume
    except Exception as e:
        print(f"[Volume] Error getting volume interface: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_current_volume():
    """Get current system volume level (0.0 to 1.0)."""
    try:
        volume = get_volume_interface()
        if volume:
            current_volume = volume.GetMasterVolumeLevelScalar()
            print(f"[Volume] Current volume level: {current_volume * 100:.0f}%")
            return current_volume
        else:
            print("[Volume] Failed to get volume interface")
    except Exception as e:
        print(f"[Volume] Error getting current volume: {e}")
        import traceback
        traceback.print_exc()
    return None

def set_volume(level):
    """Set system volume level (0.0 to 1.0)."""
    try:
        volume = get_volume_interface()
        if volume:
            # Clamp value between 0.0 and 1.0
            level = max(0.0, min(1.0, level))
            volume.SetMasterVolumeLevelScalar(level, None)
            print(f"[Volume] Volume set to: {level * 100:.0f}%")
            return True
        else:
            print("[Volume] Failed to get volume interface for setting")
    except Exception as e:
        print(f"[Volume] Error setting volume: {e}")
        import traceback
        traceback.print_exc()
    return False

def minimize_all_windows():
    """Minimize all windows (show desktop)."""
    try:
        # Simulate Win+D to show desktop
        # This is more reliable than manually minimizing windows
        shell = ctypes.windll.shell32
        shell.SHGetSpecialFolderPathW(0, None, 0, False)
        
        # Alternative: use keybd_event to simulate Win+D
        user32 = ctypes.windll.user32
        VK_LWIN = 0x5B
        VK_D = 0x44
        
        # Press Win key
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        time.sleep(0.05)
        # Press D key
        user32.keybd_event(VK_D, 0, 0, 0)
        time.sleep(0.05)
        # Release D key
        user32.keybd_event(VK_D, 0, 2, 0)
        time.sleep(0.05)
        # Release Win key
        user32.keybd_event(VK_LWIN, 0, 2, 0)
        
        print("All windows minimized (desktop shown)")
    except Exception as e:
        print(f"Error minimizing all windows: {e}")

def is_valid_time_format(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def create_default_config():
    password = "123123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return {
        "admin_password": hashed_password.decode('utf-8'),
        "enabled": True,
        "schedule": {str(i): {"start": "10:00", "end": "15:00"} for i in range(7)}
    }

def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = create_default_config()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return create_default_config()

class Blocker:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.is_blocked = False
        self.block_window = None
        self.temporarily_unlocked_until = None
        self.timer = None
        self.keyboard_blocker = None  # Keyboard blocker instance
        self.password_entry = None  # Password entry field on block screen
        self.error_label = None  # Error label on block screen
        self.saved_volume = None  # Save volume level before blocking

        self.check_time()

    def is_time_to_block(self):
        if self.temporarily_unlocked_until and datetime.now() < self.temporarily_unlocked_until:
            return False # Temporarily unlocked

        if not self.config.get("enabled", False):
            return False

        now = datetime.now()
        weekday = str(now.weekday()) # Monday is 0, Sunday is 6
        
        schedule = self.config.get("schedule", {})
        day_schedule = schedule.get(weekday)

        if not day_schedule:
            return True # Block if no schedule for today

        try:
            start_time = datetime.strptime(day_schedule['start'], '%H:%M').time()
            end_time = datetime.strptime(day_schedule['end'], '%H:%M').time()
            current_time = now.time()

            if start_time <= end_time:
                return not (start_time <= current_time <= end_time)
            else: # Overnight schedule
                return not (current_time >= start_time or current_time <= end_time)
        except (ValueError, KeyError):
            return True # Block on error

    def check_time(self):
        if self.is_time_to_block():
            if not self.is_blocked:
                self.show_block_screen()
        else:
            if self.is_blocked:
                self.hide_block_screen()
        
        self.timer = self.root.after(10000, self.check_time) # Check every 10 seconds

    def show_block_screen(self):
        self.is_blocked = True
        if self.block_window is None or not self.block_window.winfo_exists():
            print("[Blocker] ===== STARTING BLOCK SCREEN =====")
            
            # Save current volume level
            print("[Blocker] Saving current volume level...")
            self.saved_volume = get_current_volume()
            if self.saved_volume is not None:
                print(f"[Blocker] Saved volume: {self.saved_volume * 100:.0f}%")
            else:
                print("[Blocker] WARNING: Could not save current volume!")
            
            # Set volume to 0
            print("[Blocker] Setting volume to 0%...")
            success = set_volume(0.0)
            if success:
                print("[Blocker] Volume muted successfully")
            else:
                print("[Blocker] WARNING: Failed to mute volume!")
            
            # Minimize all windows to show desktop
            print("[Blocker] Minimizing all windows...")
            minimize_all_windows()
            
            # Small delay to let desktop show
            time.sleep(0.1)
            
            # Stop all media playback
            print("[Blocker] Stopping media playback...")
            stop_all_media()
            minimize_fullscreen_windows()

            # Start keyboard blocker to prevent Win key and system shortcuts
            try:
                if self.keyboard_blocker is None:
                    self.keyboard_blocker = KeyboardBlocker()
                self.keyboard_blocker.start()
                print("[Blocker] Keyboard blocking activated")
            except Exception as e:
                print(f"[Blocker] Failed to start keyboard blocker: {e}")

            self.block_window = tk.Toplevel(self.root)
            self.block_window.title(_('access_restricted'))
            self.block_window.attributes("-fullscreen", True)
            self.block_window.attributes("-topmost", True)
            self.block_window.attributes("-alpha", 0.85) # Make window semi-transparent
            self.block_window.protocol("WM_DELETE_WINDOW", self.do_nothing) # Prevent closing
            
            # Lock workstation as an additional measure
            try:
                ctypes.windll.user32.LockWorkStation()
            except AttributeError:
                pass # Not on Windows or something went wrong

            main_frame = tk.Frame(self.block_window, bg='black')
            main_frame.pack(expand=True, fill=tk.BOTH)

            center_frame = tk.Frame(main_frame, bg='black')
            center_frame.pack(expand=True, fill=tk.BOTH)
            
            title_label = tk.Label(center_frame, 
                                 text=_('access_restricted'), 
                                 font=("Helvetica", 36, "bold"), 
                                 bg='black', 
                                 fg='white')
            title_label.pack(pady=(100, 40))
            
            # Password input frame
            password_frame = tk.Frame(center_frame, bg='black')
            password_frame.pack(pady=30)
            
            password_label = tk.Label(password_frame, 
                                    text=_('admin_password') + ":", 
                                    font=("Helvetica", 16), 
                                    bg='black', 
                                    fg='white')
            password_label.pack(pady=(0, 10))
            
            self.password_entry = tk.Entry(password_frame, 
                                          show='*',
                                          font=("Helvetica", 18),
                                          width=20,
                                          bg='#34495e',
                                          fg='white',
                                          insertbackground='white',
                                          relief='flat',
                                          bd=5)
            self.password_entry.pack(pady=10)
            self.password_entry.focus_set()  # Set focus to password entry
            
            # Bind Enter key to check password
            self.password_entry.bind('<Return>', lambda e: self.check_password_inline())
            
            unlock_button = tk.Button(center_frame, 
                                    text=_('unlock'),
                                    command=self.check_password_inline,
                                    font=("Helvetica", 18, "bold"),
                                    bg='#2c3e50',
                                    fg='white',
                                    activebackground='#3498db',
                                    activeforeground='white',
                                    relief='flat',
                                    bd=0,
                                    padx=40,
                                    pady=15,
                                    cursor='hand2')
            unlock_button.pack(pady=30)
            
            def on_enter(e):
                unlock_button.config(bg='#3498db')
            
            def on_leave(e):
                unlock_button.config(bg='#2c3e50')
            
            unlock_button.bind("<Enter>", on_enter)
            unlock_button.bind("<Leave>", on_leave)
            
            # Error message label (initially hidden)
            self.error_label = tk.Label(center_frame,
                                       text="",
                                       font=("Helvetica", 14),
                                       bg='black',
                                       fg='#e74c3c')
            self.error_label.pack(pady=10)

    def hide_block_screen(self):
        self.is_blocked = False
        
        print("[Blocker] ===== HIDING BLOCK SCREEN =====")
        
        # Restore volume to previous level
        if self.saved_volume is not None:
            print(f"[Blocker] Restoring volume to {self.saved_volume * 100:.0f}%...")
            success = set_volume(self.saved_volume)
            if success:
                print(f"[Blocker] Volume restored successfully to {self.saved_volume * 100:.0f}%")
            else:
                print("[Blocker] WARNING: Failed to restore volume!")
            self.saved_volume = None
        else:
            print("[Blocker] No saved volume to restore")
        
        # Stop keyboard blocker
        try:
            if self.keyboard_blocker:
                self.keyboard_blocker.stop()
                print("[Blocker] Keyboard blocking deactivated")
        except Exception as e:
            print(f"[Blocker] Error stopping keyboard blocker: {e}")
        
        if self.block_window and self.block_window.winfo_exists():
            self.block_window.destroy()
            self.block_window = None
        
        print("[Blocker] Block screen hidden")

    def check_password_inline(self):
        """Check password directly from the block screen without opening a dialog."""
        password = self.password_entry.get()
        
        if not password:
            self.error_label.config(text=_('password') + " " + _('required'))
            self.password_entry.delete(0, tk.END)
            return
        
        hashed_password = self.config.get("admin_password", "").encode('utf-8')
        
        try:
            if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # Password is correct
                self.hide_block_screen()
                # Temporarily disable for 1 hour
                self.temporarily_unlocked_until = datetime.now() + timedelta(hours=1)
                messagebox.showinfo(_('unlocked'), _('unlocked_message'))
            else:
                # Wrong password
                self.error_label.config(text=_('invalid_password'))
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus_set()
        except Exception as e:
            print(f"Error checking password: {e}")
            self.error_label.config(text=_('error'))
            self.password_entry.delete(0, tk.END)

    def ask_for_unlock(self):
        """Legacy method - now handled inline in the block screen."""
        pass

    def open_settings(self):
        # Schedule the settings dialog to run in the main thread
        self.root.after(0, self._open_settings_main_thread)

    def _open_settings_main_thread(self):
        if gui.ask_password(self.config):
            # Hide the block screen to show the settings
            if self.is_blocked:
                self.hide_block_screen()
            
            # Create callback to reload config immediately after save
            def reload_config():
                self.config = load_config()
                self.check_time()
            
            settings_win = gui.SettingsWindow(self.root, on_save_callback=reload_config)
            self.root.wait_window(settings_win.window)
            
            # Reload config and re-evaluate blocking status (in case window was closed without saving)
            self.config = load_config()
            self.check_time()

    def lock_now(self):
        """Immediately locks the screen, cancelling any temporary unlock."""
        # Schedule the lock to run in the main thread
        self.root.after(0, self._lock_now_main_thread)

    def _lock_now_main_thread(self):
        self.temporarily_unlocked_until = None
        if not self.is_blocked:
            self.show_block_screen()

    def stop(self):
        """Stops the blocker's timer and keyboard blocker."""
        if self.timer:
            self.root.after_cancel(self.timer)
        
        # Ensure keyboard blocker is stopped
        try:
            if self.keyboard_blocker:
                self.keyboard_blocker.stop()
                print("[Blocker] Keyboard blocker stopped on exit")
        except Exception as e:
            print(f"[Blocker] Error stopping keyboard blocker on exit: {e}")

    def do_nothing(self):
        pass
