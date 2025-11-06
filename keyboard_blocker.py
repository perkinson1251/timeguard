"""
Keyboard Blocker Module
Blocks system hotkeys (Win, Alt+Tab, etc.) during screen lock
"""

import ctypes
from ctypes import wintypes, POINTER, Structure, c_int, c_long, c_longlong
import atexit

# LRESULT is a pointer-sized integer
if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit
    LRESULT = c_longlong
else:  # 32-bit
    LRESULT = c_long

# Define KBDLLHOOKSTRUCT
class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", POINTER(wintypes.ULONG))
    ]

class KeyboardBlocker:
    """
    Blocks system keyboard shortcuts using low-level Windows keyboard hooks.
    Prevents access to Start Menu, Task Switcher, and other system functions.
    """
    
    # Virtual key codes
    VK_LWIN = 0x5B      # Left Windows key
    VK_RWIN = 0x5C      # Right Windows key
    VK_TAB = 0x09       # Tab key
    VK_ESCAPE = 0x1B    # Escape key
    VK_F4 = 0x73        # F4 key
    
    # Hook constants
    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104
    
    def __init__(self):
        """Initialize the keyboard blocker."""
        self.hook_id = None
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Define CallNextHookEx with proper types
        self.user32.CallNextHookEx.argtypes = [wintypes.HHOOK, c_int, wintypes.WPARAM, wintypes.LPARAM]
        self.user32.CallNextHookEx.restype = LRESULT
        
        # Define the hook callback type
        self.LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
            LRESULT,
            c_int,
            wintypes.WPARAM,
            wintypes.LPARAM
        )
        
        # Create callback function
        self.hook_callback = self.LowLevelKeyboardProc(self._keyboard_hook_callback)
        
        # Track Alt key state
        self.alt_pressed = False
        
        # Register cleanup on exit
        atexit.register(self.stop)
        
        print("[KeyboardBlocker] Initialized")
    
    def start(self):
        """Install the keyboard hook to start blocking keys."""
        if self.hook_id is not None:
            print("[KeyboardBlocker] Already running")
            return True
        
        try:
            # For low-level keyboard hooks, we can pass NULL (0) as hMod
            # This is the correct approach for WH_KEYBOARD_LL hooks
            self.hook_id = self.user32.SetWindowsHookExW(
                self.WH_KEYBOARD_LL,
                self.hook_callback,
                None,  # hMod can be NULL for low-level hooks
                0      # dwThreadId = 0 means all threads
            )
            
            if self.hook_id:
                print("[KeyboardBlocker] Hook installed successfully")
                return True
            else:
                # Get last error for debugging
                error_code = self.kernel32.GetLastError()
                print(f"[KeyboardBlocker] Failed to install hook. Error code: {error_code}")
                return False
                
        except Exception as e:
            print(f"[KeyboardBlocker] Error starting: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self):
        """Remove the keyboard hook to stop blocking keys."""
        if self.hook_id is None:
            return
        
        try:
            self.user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
            self.alt_pressed = False
            print("[KeyboardBlocker] Hook removed successfully")
        except Exception as e:
            print(f"[KeyboardBlocker] Error stopping: {e}")
    
    def _keyboard_hook_callback(self, n_code, w_param, l_param):
        """
        Low-level keyboard hook callback.
        Intercepts keyboard events and blocks specific keys.
        """
        try:
            # Only process if n_code is HC_ACTION (0)
            if n_code >= 0:
                # Get the virtual key code from the structure
                kb_struct = ctypes.cast(l_param, POINTER(KBDLLHOOKSTRUCT)).contents
                vk_code = kb_struct.vkCode
                
                # Track Alt key state
                if vk_code == 0x12:  # VK_MENU (Alt)
                    if w_param in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN):
                        self.alt_pressed = True
                    else:
                        self.alt_pressed = False
                
                # Check if this is a key press event
                if w_param in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN):
                    
                    # Block Windows keys
                    if vk_code in (self.VK_LWIN, self.VK_RWIN):
                        print(f"[KeyboardBlocker] Blocked Windows key")
                        return 1  # Block the key
                    
                    # Block Alt+Tab
                    if self.alt_pressed and vk_code == self.VK_TAB:
                        print(f"[KeyboardBlocker] Blocked Alt+Tab")
                        return 1
                    
                    # Block Alt+Esc
                    if self.alt_pressed and vk_code == self.VK_ESCAPE:
                        print(f"[KeyboardBlocker] Blocked Alt+Esc")
                        return 1
                    
                    # Block Alt+F4
                    if self.alt_pressed and vk_code == self.VK_F4:
                        print(f"[KeyboardBlocker] Blocked Alt+F4")
                        return 1
            
            # Pass the event to the next hook
            return self.user32.CallNextHookEx(self.hook_id, n_code, w_param, l_param)
            
        except Exception as e:
            print(f"[KeyboardBlocker] Error in callback: {e}")
            # On error, pass the event through
            try:
                return self.user32.CallNextHookEx(self.hook_id, n_code, w_param, l_param)
            except:
                return 0
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop()


# Test function
if __name__ == "__main__":
    import time
    
    print("Testing KeyboardBlocker...")
    print("Will block Windows key, Alt+Tab, Alt+Esc, Alt+F4 for 10 seconds")
    print("Press Ctrl+C to stop early")
    
    blocker = KeyboardBlocker()
    blocker.start()
    
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    blocker.stop()
    print("Test completed")
