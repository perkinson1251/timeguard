import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import bcrypt
import blocker
from localization import get_localization, _

class SettingsWindow:
    def __init__(self, parent, config_path="config.json", on_save_callback=None):
        self.parent = parent
        self.config_path = config_path
        self.config = self.load_config()
        self.localization = get_localization()
        self.on_save_callback = on_save_callback

        self.window = tk.Toplevel(parent)
        self.window.title(_('settings_title'))
        self.window.geometry("450x550")
        self.window.resizable(False, False)

        self.days = [_('monday'), _('tuesday'), _('wednesday'), _('thursday'), _('friday'), _('saturday'), _('sunday')]
        self.time_entries = {}
        
        self.language_names = {}
        self.language_codes = {}
        for lang_code in self.localization.get_supported_languages():
            lang_name = self.localization.get_language_name(lang_code)
            self.language_names[lang_code] = lang_name
            self.language_codes[lang_name] = lang_code

        self.create_widgets()
        self.load_settings()

    def on_language_change(self, event=None):
        selected_language_name = self.language_var.get()
        new_language_code = self.language_codes.get(selected_language_name)
        if new_language_code and new_language_code != self.localization.get_current_language():
            self.localization.set_language(new_language_code)
            messagebox.showinfo(_('success'), _('settings_saved'))

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return blocker.create_default_config()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Language settings
        language_frame = tk.LabelFrame(main_frame, text=_('language_settings'))
        language_frame.pack(fill=tk.X, pady=5)
        
        lang_select_frame = tk.Frame(language_frame)
        lang_select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(lang_select_frame, text=_('language') + ':').pack(side=tk.LEFT)
        
        current_lang_code = self.localization.get_current_language()
        current_lang_name = self.language_names.get(current_lang_code, current_lang_code)
        
        self.language_var = tk.StringVar(value=current_lang_name)
        language_names_list = [self.language_names[code] for code in self.localization.get_supported_languages()]
        self.language_combo = ttk.Combobox(lang_select_frame, textvariable=self.language_var, 
                                          values=language_names_list,
                                          state="readonly", width=15)
        self.language_combo.pack(side=tk.LEFT, padx=5)
        
        # Bind language change event
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)

        # Schedule settings
        schedule_frame = tk.LabelFrame(main_frame, text=_('schedule_settings'))
        schedule_frame.pack(fill=tk.X, pady=5)

        for i, day in enumerate(self.days):
            day_frame = tk.Frame(schedule_frame)
            day_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(day_frame, text=day, width=12, anchor='w').pack(side=tk.LEFT)
            
            start_entry = tk.Entry(day_frame, width=8)
            start_entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(day_frame, text="-").pack(side=tk.LEFT)
            
            end_entry = tk.Entry(day_frame, width=8)
            end_entry.pack(side=tk.LEFT, padx=5)
            
            self.time_entries[str(i)] = (start_entry, end_entry)

        # Program status
        status_frame = tk.LabelFrame(main_frame, text=_('program_status'))
        status_frame.pack(fill=tk.X, pady=10)
        
        self.enabled_var = tk.BooleanVar()
        enabled_check = tk.Checkbutton(status_frame, text=_('enable_blocking'), variable=self.enabled_var)
        enabled_check.pack(anchor='w')

        # Password change
        password_frame = tk.LabelFrame(main_frame, text=_('password_change'))
        password_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(password_frame, text=_('new_password')).pack(side=tk.LEFT)
        self.new_password_entry = tk.Entry(password_frame, show="*")
        self.new_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Save button
        save_button = tk.Button(main_frame, text=_('save'), command=self.save_settings)
        save_button.pack(pady=10)

    def load_settings(self):
        self.enabled_var.set(self.config.get("enabled", True))
        
        # Load language setting
        saved_language_code = self.config.get("language", self.localization.get_current_language())
        if saved_language_code in self.localization.get_supported_languages():
            saved_language_name = self.language_names.get(saved_language_code, saved_language_code)
            self.language_var.set(saved_language_name)
        
        schedule = self.config.get("schedule", {})
        for i in range(7):
            day_schedule = schedule.get(str(i), {"start": "00:00", "end": "00:00"})
            self.time_entries[str(i)][0].insert(0, day_schedule["start"])
            self.time_entries[str(i)][1].insert(0, day_schedule["end"])

    def save_settings(self):
        # Update schedule
        new_schedule = {}
        for i in range(7):
            start_time = self.time_entries[str(i)][0].get()
            end_time = self.time_entries[str(i)][1].get()
            if not (blocker.is_valid_time_format(start_time) and blocker.is_valid_time_format(end_time)):
                messagebox.showerror(_('error'), _('invalid_time_format', day=self.days[i]))
                return
            new_schedule[str(i)] = {"start": start_time, "end": end_time}
        self.config["schedule"] = new_schedule

        # Update enabled status
        self.config["enabled"] = self.enabled_var.get()

        # Save language preference (convert from name back to code)
        selected_language_name = self.language_var.get()
        selected_language_code = self.language_codes.get(selected_language_name)
        if selected_language_code:
            self.config["language"] = selected_language_code

        # Update password
        new_password = self.new_password_entry.get()
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            self.config["admin_password"] = hashed_password.decode('utf-8')
            messagebox.showinfo(_('success'), _('password_changed'))
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Call the callback to update the blocker immediately
            if self.on_save_callback:
                self.on_save_callback()
            
            messagebox.showinfo(_('success'), _('settings_saved'))
            self.window.destroy()
        except Exception as e:
            messagebox.showerror(_('error'), _('settings_save_error', error=str(e)))

def ask_password(config):
    password = simpledialog.askstring(_('password'), _('admin_password'), show='*')
    if password:
        hashed_password = config.get("admin_password", "").encode('utf-8')
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
        # First time setup or empty password
        elif not hashed_password:
             # This allows setting the password for the first time
            return True
    messagebox.showwarning(_('error'), _('invalid_password'))
    return False
