# TimeGuard

A Windows desktop application for time-based computer access control. TimeGuard allows you to set specific time windows when the computer can be accessed, blocking usage outside of these periods.

## Features

- **Flexible scheduling**: Set different allowed time periods for each day of the week with minute precision
- **Password protection**: Admin password required to access settings or temporarily unlock the system
- **System tray integration**: Convenient access to settings and controls via system tray icon
- **Temporary unlock**: Enter admin password to grant 1-hour temporary access
- **Media control**: Automatically stops media playback (music, videos) when blocking activates
- **Transparent overlay**: Semi-transparent black screen during blocking periods
- **Auto-startup support**: Can be added to Windows startup for automatic protection

## Screenshots

*Coming soon*

## Installation

### Option 1: Download Pre-built Release (Recommended)

1. Download the latest release from the [Releases](https://github.com/perkinson1251/timeguard/releases) page
2. Extract the ZIP file to your desired location (e.g., `C:\TimeGuard\`)
3. Run `TimeGuard.exe`

### Option 2: Build from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/perkinson1251/timeguard.git
   cd timeguard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. (Optional) Build executable:
   ```bash
   pip install pyinstaller
   pyinstaller TimeGuard.spec
   ```

## Configuration

### First Run
- Default admin password: `123123`
- **Important**: Change the default password immediately after first setup!

### Setting Up Schedule
1. Right-click the system tray icon
2. Select "Settings" and enter admin password
3. Configure allowed time periods for each day:
   - Format: HH:MM (24-hour format)
   - Example: Monday 10:15 - 14:31, Tuesday 09:00 - 16:00
4. Enable/disable the blocking feature
5. Change admin password if needed

## Adding to Windows Startup

### Method 1: Create Shortcut in Startup Folder (Recommended)
1. Place `TimeGuard.exe` in a permanent location (e.g., `C:\Program Files\TimeGuard\` or `C:\TimeGuard\`)
2. Right-click on `TimeGuard.exe` and select "Create shortcut"
3. Press `Win + R`, type `shell:startup`, press Enter
4. Move the shortcut to the opened startup folder

### Method 2: Registry Entry
1. Place `TimeGuard.exe` in a permanent location (e.g., `C:\Program Files\TimeGuard\`)
2. Press `Win + R`, type `regedit`, press Enter
3. Navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
4. Create new String Value named `TimeGuard`
5. Set value to full path of `TimeGuard.exe` (e.g., `C:\Program Files\TimeGuard\TimeGuard.exe`)

### Method 3: Task Scheduler (Most Reliable)
1. Place `TimeGuard.exe` in a permanent location (e.g., `C:\Program Files\TimeGuard\`)
2. Press `Win + R`, type `taskschd.msc`, press Enter
3. Click "Create Basic Task" in the right panel
4. Name: `TimeGuard`, Description: `Time-based computer access control`
5. Trigger: "When I log on"
6. Action: "Start a program"
7. Program: Browse to your `TimeGuard.exe` location
8. Finish the wizard

**Note**: All methods require placing the exe in a permanent location first, so the config file will be created in the same directory as the executable.

## Usage

### System Tray Menu
- **Settings**: Configure schedule and change password (requires admin password)
- **Lock Now**: Immediately activate blocking (cancels temporary unlock)
- **Exit**: Close the application

### During Blocking
- Semi-transparent overlay appears on screen
- Media playback automatically stops
- Enter admin password to unlock for 1 hour
- Access settings to modify configuration

## Technical Details

- **Platform**: Windows 10/11
- **Language**: Python 3.8+
- **Dependencies**: tkinter, bcrypt, pystray, Pillow
- **Size**: ~25MB (compiled executable)

## Requirements

- Windows 10 or later
- Administrative privileges (for workstation locking feature)

## Development

### Project Structure
```
timeguard/
├── main.py              # Application entry point and system tray
├── blocker.py           # Core blocking logic and time management
├── gui.py              # Settings window and password dialogs
├── config.json         # Configuration file (auto-generated)
├── requirements.txt    # Python dependencies
├── TimeGuard.spec     # PyInstaller build configuration
└── README.md          # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## Security Note

This application is designed for time management and parental control purposes. It should not be considered a security solution against determined users with administrative access to the system.