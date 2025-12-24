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
    VK_DELETE = 0x2E    # Delete key
    VK_LCONTROL = 0xA2  # Left Control key
    VK_RCONTROL = 0xA3  # Right Control key
    VK_LSHIFT = 0xA0    # Left Shift key
    VK_RSHIFT = 0xA1    # Right Shift key
    VK_LMENU = 0xA4     # Left Alt key
    VK_RMENU = 0xA5     # Right Alt key
    VK_MENU = 0x12      # Alt key (generic)
    VK_CONTROL = 0x11   # Control key (generic)
    VK_SHIFT = 0x10     # Shift key (generic)
    VK_D = 0x44         # D key (for Win+D)
    VK_E = 0x45         # E key (for Win+E)
    VK_R = 0x52         # R key (for Win+R)
    VK_L = 0x4C         # L key (for Win+L)
    VK_P = 0x50         # P key (for Win+P)
    VK_SPACE = 0x20     # Space key
    
    # Hook constants
    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_SYSKEYDOWN = 0x0104
    WM_SYSKEYUP = 0x0105
    
    # Flag for extended key (from KBDLLHOOKSTRUCT.flags)
    LLKHF_EXTENDED = 0x01
    LLKHF_ALTDOWN = 0x20
    
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
        
        # Track modifier key states
        self.alt_pressed = False
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.win_pressed = False
        
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
            self.ctrl_pressed = False
            self.shift_pressed = False
            self.win_pressed = False
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
                flags = kb_struct.flags
                
                is_key_down = w_param in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN)
                is_key_up = w_param in (self.WM_KEYUP, self.WM_SYSKEYUP)
                
                # Track modifier key states
                if vk_code in (self.VK_MENU, self.VK_LMENU, self.VK_RMENU):
                    self.alt_pressed = is_key_down
                elif vk_code in (self.VK_CONTROL, self.VK_LCONTROL, self.VK_RCONTROL):
                    self.ctrl_pressed = is_key_down
                elif vk_code in (self.VK_SHIFT, self.VK_LSHIFT, self.VK_RSHIFT):
                    self.shift_pressed = is_key_down
                elif vk_code in (self.VK_LWIN, self.VK_RWIN):
                    self.win_pressed = is_key_down
                
                # Check if this is a key press event
                if is_key_down:
                    
                    # Block Windows keys (prevents Start menu and Win+Tab)
                    if vk_code in (self.VK_LWIN, self.VK_RWIN):
                        print(f"[KeyboardBlocker] Blocked Windows key")
                        return 1  # Block the key
                    
                    # Block any key when Win is pressed (Win+Tab, Win+D, Win+E, etc.)
                    if self.win_pressed:
                        print(f"[KeyboardBlocker] Blocked Win+{hex(vk_code)}")
                        return 1
                    
                    # Block Alt+Tab (Task Switcher)
                    if self.alt_pressed and vk_code == self.VK_TAB:
                        print(f"[KeyboardBlocker] Blocked Alt+Tab")
                        return 1
                    
                    # Block Alt+Esc (Cycle windows)
                    if self.alt_pressed and vk_code == self.VK_ESCAPE:
                        print(f"[KeyboardBlocker] Blocked Alt+Esc")
                        return 1
                    
                    # Block Alt+F4 (Close window)
                    if self.alt_pressed and vk_code == self.VK_F4:
                        print(f"[KeyboardBlocker] Blocked Alt+F4")
                        return 1
                    
                    # Block Alt+Space (Window menu)
                    if self.alt_pressed and vk_code == self.VK_SPACE:
                        print(f"[KeyboardBlocker] Blocked Alt+Space")
                        return 1
                    
                    # Block Ctrl+Esc (Start menu)
                    if self.ctrl_pressed and vk_code == self.VK_ESCAPE:
                        print(f"[KeyboardBlocker] Blocked Ctrl+Esc")
                        return 1
                    
                    # Block Ctrl+Shift+Esc (Task Manager)
                    if self.ctrl_pressed and self.shift_pressed and vk_code == self.VK_ESCAPE:
                        print(f"[KeyboardBlocker] Blocked Ctrl+Shift+Esc")
                        return 1
                    
                    # Block Ctrl+Alt+Delete is not possible via keyboard hooks
                    # (it's handled by the system at a lower level)
            
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
