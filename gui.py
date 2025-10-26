import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import bcrypt
import blocker

class SettingsWindow:
    def __init__(self, parent, config_path="config.json"):
        self.parent = parent
        self.config_path = config_path
        self.config = self.load_config()

        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("400x450")
        self.window.resizable(False, False)

        self.days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        self.time_entries = {}

        self.create_widgets()
        self.load_settings()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return blocker.create_default_config()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Schedule settings
        schedule_frame = tk.LabelFrame(main_frame, text="Расписание доступа")
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
        status_frame = tk.LabelFrame(main_frame, text="Статус программы")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.enabled_var = tk.BooleanVar()
        enabled_check = tk.Checkbutton(status_frame, text="Включить блокировку", variable=self.enabled_var)
        enabled_check.pack(anchor='w')

        # Password change
        password_frame = tk.LabelFrame(main_frame, text="Смена пароля")
        password_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(password_frame, text="Новый пароль:").pack(side=tk.LEFT)
        self.new_password_entry = tk.Entry(password_frame, show="*")
        self.new_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Save button
        save_button = tk.Button(main_frame, text="Сохранить", command=self.save_settings)
        save_button.pack(pady=10)

    def load_settings(self):
        self.enabled_var.set(self.config.get("enabled", True))
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
                messagebox.showerror("Ошибка", f"Неверный формат времени для дня '{self.days[i]}'. Используйте ЧЧ:ММ.")
                return
            new_schedule[str(i)] = {"start": start_time, "end": end_time}
        self.config["schedule"] = new_schedule

        # Update enabled status
        self.config["enabled"] = self.enabled_var.get()

        # Update password
        new_password = self.new_password_entry.get()
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            self.config["admin_password"] = hashed_password.decode('utf-8')
            messagebox.showinfo("Успех", "Пароль успешно изменен.")
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Успех", "Настройки сохранены. Перезапустите программу, чтобы они вступили в силу.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")

def ask_password(config):
    password = simpledialog.askstring("Пароль", "Введите пароль администратора:", show='*')
    if password:
        hashed_password = config.get("admin_password", "").encode('utf-8')
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
        # First time setup or empty password
        elif not hashed_password:
             # This allows setting the password for the first time
            return True
    messagebox.showwarning("Ошибка", "Неверный пароль.")
    return False
