import tkinter as tk
from tkinter import scrolledtext, Scale, simpledialog, messagebox, Menu, filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import win32api
import win32con
import win32gui
import time
import ctypes
import os
import json
import webbrowser
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import logging
import re
import keyring
import numpy as np
import subprocess
import sys

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Ensure logging configuration is set up properly
if not logger.hasHandlers():
    # Create a file handler for logging
    file_handler = logging.FileHandler('C:\\MechPUGCommander\\app.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

VK_CODE = {
    'ctrl': 0x11,
    'alt': 0x12,
    'down': 0x28
}

HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Email:").grid(row=0)
        tk.Label(master, text="Password:").grid(row=1)

        self.email_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show="*")
        self.remember_var = tk.BooleanVar()
        self.remember_checkbox = tk.Checkbutton(master, text="Remember me", variable=self.remember_var)

        self.email_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        self.remember_checkbox.grid(row=2, columnspan=2)
        return self.email_entry

    def apply(self):
        self.result = (self.email_entry.get(), self.password_entry.get(), self.remember_var.get())

class FriendEditor(simpledialog.Dialog):
    def __init__(self, parent, title, friend_name="", notes=""):
        self.friend_name = friend_name
        self.notes = notes
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Name:").grid(row=0)
        tk.Label(master, text="Notes:").grid(row=1)

        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.insert(0, self.friend_name)

        self.notes_entry = tk.Text(master, height=5, width=30)
        self.notes_entry.grid(row=1, column=1)
        self.notes_entry.insert(tk.END, self.notes)

        return self.name_entry

    def apply(self):
        self.result = (self.name_entry.get(), self.notes_entry.get("1.0", tk.END).strip())

class SettingsDialog(simpledialog.Dialog):
    def __init__(self, parent, title, username="", team_file="", enemy_file=""):
        self.username = username
        self.team_file = team_file
        self.enemy_file = enemy_file
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="In-game Name:").grid(row=0)
        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.insert(0, self.username)

        tk.Label(master, text="Team File:").grid(row=1)
        self.team_file_entry = tk.Entry(master)
        self.team_file_entry.grid(row=1, column=1)
        self.team_file_entry.insert(0, self.team_file)
        self.browse_team_button = tk.Button(master, text="Browse", command=self.browse_team_file)
        self.browse_team_button.grid(row=1, column=2)

        tk.Label(master, text="Enemy File:").grid(row=2)
        self.enemy_file_entry = tk.Entry(master)
        self.enemy_file_entry.grid(row=2, column=1)
        self.enemy_file_entry.insert(0, self.enemy_file)
        self.browse_enemy_button = tk.Button(master, text="Browse", command=self.browse_enemy_file)
        self.browse_enemy_button.grid(row=2, column=2)

        return self.name_entry

    def browse_team_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.team_file_entry.delete(0, tk.END)
            self.team_file_entry.insert(0, file_path)

    def browse_enemy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.enemy_file_entry.delete(0, tk.END)
            self.enemy_file_entry.insert(0, file_path)

    def apply(self):
        self.result = (self.name_entry.get(), self.team_file_entry.get(), self.enemy_file_entry.get())

class OverlayWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PUG Friends by Kal Sinn")
        self.root.geometry("600x800+10+10")
        self.root.configure(bg='#1e1e1e')
        self.root.attributes("-topmost", True)

        self.frame = tk.Frame(self.root, bg='#1e1e1e')
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.header_frame = tk.Frame(self.frame, bg='#1e1e1e')
        self.header_frame.pack(fill=tk.X, pady=(5, 0))

        script_dir = resource_path('C:\\MechPUGCommander\\')  # Base directory of the executable
        logo_path = os.path.join(script_dir, "KalSinn_Patchyt.png")
        settings_path = os.path.join(script_dir, 'settings.json')
        friends_path = os.path.join(script_dir, 'friends.json')

        if os.path.exists(logo_path):
            self.logo = Image.open(logo_path)
            self.logo = self.logo.resize((50, 50), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(self.logo)
            self.logo_label = tk.Label(self.header_frame, image=self.logo_tk, bg='#1e1e1e')
            self.logo_label.pack(side=tk.LEFT, padx=(5, 10))
        else:
            logger.error(f"Logo file not found at {logo_path}")

        self.title_label = tk.Label(self.header_frame, text="PUG Friends by Kal Sinn",
                                    bg='#1e1e1e', fg='#a0a0a0', cursor="hand2")
        self.title_label.pack(side=tk.LEFT, pady=5)
        self.title_label.bind("<Button-1>", self.open_website)

        self.transparency_slider = Scale(self.frame, from_=39, to=255, orient=tk.HORIZONTAL,
                                         command=self.update_transparency,
                                         bg='#1e1e1e', fg='#a0a0a0', troughcolor='#2b2b2b',
                                         highlightthickness=0, length=300)
        self.transparency_slider.set(128)
        self.transparency_slider.pack(pady=(10, 5))

        self.button_frame = tk.Frame(self.frame, bg='#1e1e1e')
        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        self.add_friend_button = tk.Button(self.button_frame, text="Add Friend", command=self.add_friend,
                                           bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.add_friend_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = tk.Button(self.button_frame, text="Settings", command=self.open_settings,
                                         bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.import_button = tk.Button(self.button_frame, text="Import Image", command=self.import_image,
                                       bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.import_teams_button = tk.Button(self.button_frame, text="Import Teams", command=self.import_teams,
                                             bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.import_teams_button.pack(side=tk.LEFT, padx=5)

        self.clear_teams_button = tk.Button(self.button_frame, text="Clear Teams", command=self.clear_teams,
                                            bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.clear_teams_button.pack(side=tk.LEFT, padx=5)

        self.refresh_stats_button = tk.Button(self.button_frame, text="Refresh Stats", command=self.refresh_stats,
                                              bg='#3c3f41', fg='#a0a0a0', highlightthickness=0)
        self.refresh_stats_button.pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_friend_list)
        self.search_entry = tk.Entry(self.frame, textvariable=self.search_var, bg='#3c3f41', fg='#a0a0a0')
        self.search_entry.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.scroll_text = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, bg='#2b2b2b', fg='#a0a0a0')
        self.scroll_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scroll_text.bind("<Double-Button-1>", self.edit_friend)
        self.scroll_text.bind("<Button-3>", self.show_context_menu)

        self.match_players = {"Your Team": [], "Your Enemy": []}
        self.username = ""
        self.team_file = ""
        self.enemy_file = ""
        self.settings_path = settings_path
        self.friends_path = friends_path
        self.load_settings()
        self.load_friends()
        self.populate_friend_list()

        self.window_visible = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.after_idle(self.set_overlay_transparency)
        self.root.after(100, self.check_hotkey)

        self.session = None

        self.root.resizable(True, True)
        self.root.bind("<Configure>", self.on_window_resize)

    def on_closing(self):
        self.window_visible = False
        self.root.withdraw()

    def on_window_resize(self, event):
        self.adjust_font_size()

    def adjust_font_size(self):
        window_width = self.root.winfo_width()
        font_size = max(8, min(16, int(window_width / 50)))
        self.scroll_text.configure(font=("TkDefaultFont", font_size))

    def login(self):
        dialog = LoginDialog(self.root, "Login to MechWarrior Online")
        if dialog.result:
            email, password, remember = dialog.result
            self.session = requests.Session()
            login_url = "https://mwomercs.com/do/login"
            login_data = {
                "email": email,
                "password": password,
                "return": "/profile/leaderboards/quickplay?type=0"
            }
            response = self.session.post(login_url, data=login_data)
            logger.info(f"Login attempt for email: {email}")
            logger.debug(f"Login response status code: {response.status_code}")
            logger.debug(f"Login response headers: {response.headers}")
            if "Sign in" not in response.text:
                logger.info("Login successful")
                if remember:
                    keyring.set_password("MWOApp", "email", email)
                    keyring.set_password("MWOApp", "password", password)
                return True
            else:
                logger.warning("Login failed")
        return False

    def auto_login(self):
        email = keyring.get_password("MWOApp", "email")
        password = keyring.get_password("MWOApp", "password")
        if email and password:
            self.session = requests.Session()
            login_url = "https://mwomercs.com/do/login"
            login_data = {
                "email": email,
                "password": password,
                "return": "/profile/leaderboards/quickplay?type=0"
            }
            response = self.session.post(login_url, data=login_data)
            logger.info(f"Auto-login attempt for email: {email}")
            logger.debug(f"Auto-login response status code: {response.status_code}")
            logger.debug(f"Auto-login response headers: {response.headers}")
            return "Sign in" not in response.text
        return False

    def load_settings(self):
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                self.username = settings.get('username', '')
                self.team_file = settings.get('team_file', '')
                self.enemy_file = settings.get('enemy_file', '')
        except FileNotFoundError:
            pass

    def save_settings(self):
        with open(self.settings_path, 'w') as f:
            json.dump({
                'username': self.username,
                'team_file': self.team_file,
                'enemy_file': self.enemy_file
            }, f)

    def open_settings(self):
        dialog = SettingsDialog(self.root, "User Settings", self.username, self.team_file, self.enemy_file)
        if dialog.result:
            self.username, self.team_file, self.enemy_file = dialog.result
            self.save_settings()
            self.populate_friend_list()

    def load_friends(self):
        try:
            with open(self.friends_path, 'r') as f:
                self.friends = json.load(f)
        except FileNotFoundError:
            self.friends = {}
            self.save_friends()

    def save_friends(self):
        with open(self.friends_path, 'w') as f:
            json.dump(self.friends, f)

    def add_friend(self):
        dialog = FriendEditor(self.root, "Add Friend")
        if dialog.result:
            name, notes = dialog.result
            if name and name not in self.friends:
                self.friends[name] = notes
                self.save_friends()
                self.populate_friend_list()

    def edit_friend(self, event):
        index = self.scroll_text.index(f"@{event.x},{event.y}")
        line_start = self.scroll_text.index(f"{index} linestart")
        line_end = self.scroll_text.index(f"{index} lineend")
        line = self.scroll_text.get(line_start, line_end)
        name = line.split("\n")[0].strip()
        if name in self.friends:
            notes = self.friends[name]
        else:
            notes = ""
        dialog = FriendEditor(self.root, "Edit Friend", name, notes)
        if dialog.result:
            new_name, new_notes = dialog.result
            if new_name != name:
                # Update the name in match_players if it exists
                for team in self.match_players.values():
                    if name in team:
                        team[team.index(name)] = new_name

                # Update the name in friends dictionary
                if name in self.friends:
                    self.friends[new_name] = self.friends.pop(name)
                else:
                    self.friends[new_name] = new_notes
            else:
                self.friends[name] = new_notes

            self.save_friends()
            self.populate_friend_list()

    def delete_friend(self, name):
        if name in self.friends:
            if messagebox.askyesno("Delete Friend", f"Are you sure you want to delete {name}?"):
                del self.friends[name]
                self.save_friends()
                self.populate_friend_list()

    def show_context_menu(self, event):
        index = self.scroll_text.index(f"@{event.x},{event.y}")
        line_start = self.scroll_text.index(f"{index} linestart")
        line_end = self.scroll_text.index(f"{index} lineend")
        line = self.scroll_text.get(line_start, line_end)
        name = line.split("\n")[0].strip()

        menu = Menu(self.root, tearoff=0)
        if name in self.friends:
            menu.add_command(label="Delete", command=lambda: self.delete_friend(name))
        else:
            menu.add_command(label="Add to Friends", command=lambda: self.add_friend_from_menu(name))
        menu.tk_popup(event.x_root, event.y_root)

    def add_friend_from_menu(self, name):
        if name not in self.friends:
            self.friends[name] = ""
            self.save_friends()
            self.populate_friend_list()

    def update_friend_list(self, *args):
        self.populate_friend_list()

    def populate_friend_list(self):
        search_query = self.search_var.get().lower()
        self.scroll_text.config(state=tk.NORMAL)
        self.scroll_text.delete('1.0', tk.END)

        if self.username and self.username in self.friends:
            user_stats = self.friends[self.username]
            self.scroll_text.insert(tk.END, f"Your Stats:\n{self.username}\n{user_stats}\n\n")

        for team, players in self.match_players.items():
            self.scroll_text.insert(tk.END, f"{team}:\n")
            for player in sorted(players, key=lambda x: self.get_rank(self.friends.get(x, ""))):
                if search_query in player.lower() or search_query in self.friends.get(player, "").lower():
                    stats = self.friends.get(player, "")
                    self.scroll_text.insert(tk.END, f"{player}\n{stats}\n\n")
            self.scroll_text.insert(tk.END, "\n")

        self.scroll_text.insert(tk.END, "Other Friends:\n")
        for friend, stats in sorted(self.friends.items(), key=lambda x: self.get_rank(x[1])):
            if friend not in self.match_players["Your Team"] and friend not in self.match_players["Your Enemy"]:
                if search_query in friend.lower() or search_query in stats.lower():
                    self.scroll_text.insert(tk.END, f"{friend}\n{stats}\n\n")

        self.scroll_text.config(state=tk.DISABLED)

    def get_rank(self, stats):
        match = re.search(r'Rank: (\d+)', stats)
        return int(match.group(1)) if match else float('inf')

    def toggle_window(self):
        if self.window_visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.force_top()
        self.window_visible = not self.window_visible

    def refresh_stats(self):
        if not self.session:
            if not self.login():
                messagebox.showerror("Login Failed", "Unable to log in to MechWarrior Online")
                return

        self.show_loading_message("Updating friend stats...")
        all_players = set(self.friends.keys()) | set(self.match_players["Your Team"]) | set(
            self.match_players["Your Enemy"])
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_friend = {executor.submit(self.fetch_friend_stats, friend): friend for friend in all_players}
            for future in concurrent.futures.as_completed(future_to_friend):
                friend = future_to_friend[future]
                try:
                    stats = future.result()
                    if stats:
                        self.friends[friend] = stats
                    else:
                        self.friends[friend] = "NOT FOUND"
                except Exception as exc:
                    logging.error(f'{friend} generated an exception: {exc}')
                    self.friends[friend] = "ERROR"

        self.save_friends()
        self.populate_friend_list()
        self.hide_loading_message()

    def show_loading_message(self, message):
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.attributes("-topmost", True)
        self.loading_window.overrideredirect(True)
        self.loading_window.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        tk.Label(self.loading_window, text=message, padx=20, pady=10).pack()

    def hide_loading_message(self):
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def fetch_friend_stats(self, friend_name):
        if not self.session:
            return "ERROR: Not logged in"

        url = f"https://mwomercs.com/profile/leaderboards/quickplay?type=0&user={friend_name}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching stats for {friend_name} from URL: {url} (Attempt {attempt + 1})")
                response = self.session.get(url, timeout=10)
                logging.info(f"Response status code for {friend_name}: {response.status_code}")
                logging.debug(f"Response headers for {friend_name}: {response.headers}")
                logging.debug(f"Response content for {friend_name}: {response.text[:500]}...")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', class_='table table-striped')
                if table:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header row
                        columns = row.find_all('td')
                        if columns and columns[1].text.strip().lower() == friend_name.lower():
                            rank = columns[0].text.strip()
                            total_wins = columns[2].text.strip()
                            total_losses = columns[3].text.strip()
                            wl_ratio = columns[4].text.strip()
                            total_kills = columns[5].text.strip()
                            total_deaths = columns[6].text.strip()
                            kd_ratio = columns[7].text.strip()
                            games_played = columns[8].text.strip()
                            avg_match_score = columns[9].text.strip()
                            return (f"Rank: {rank}, W: {total_wins}, L: {total_losses}, W/L: {wl_ratio}, "
                                    f"K: {total_kills}, D: {total_deaths}, K/D: {kd_ratio}, "
                                    f"Games: {games_played}, Avg Score: {avg_match_score}")
                return "NOT FOUND"
            except requests.RequestException as e:
                logging.error(f"Error fetching stats for {friend_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return "ERROR"

    def set_overlay_transparency(self):
        self.update_transparency()

    def update_transparency(self, *args):
        alpha = self.transparency_slider.get()
        self.root.attributes('-alpha', alpha / 255)

    def check_hotkey(self):
        if (win32api.GetAsyncKeyState(VK_CODE['ctrl']) & 0x8000 and
                win32api.GetAsyncKeyState(VK_CODE['alt']) & 0x8000 and
                win32api.GetAsyncKeyState(VK_CODE['down']) & 0x8000):
            self.toggle_window()
            time.sleep(0.3)
        self.root.after(100, self.check_hotkey)

    def force_top(self):
        hwnd = self.root.winfo_id()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        ctypes.windll.user32.SetForegroundWindow(hwnd)

    def open_website(self, event):
        webbrowser.open_new("http://PUGFKalSinn.free.com")

    def import_image(self):
        subprocess.Popen(r'C:\MechPUGCommander\ImageParserApp.exe')

    def import_teams(self):
        if not self.team_file or not self.enemy_file:
            messagebox.showerror("Error", "Team or enemy file path not set. Please check settings.")
            return

        if os.path.exists(self.team_file):
            with open(self.team_file, 'r') as f:
                self.match_players["Your Team"] = [line.strip() for line in f.readlines()]
        else:
            messagebox.showerror("Error", f"Team file not found: {self.team_file}")

        if os.path.exists(self.enemy_file):
            with open(self.enemy_file, 'r') as f:
                self.match_players["Your Enemy"] = [line.strip() for line in f.readlines()]
        else:
            messagebox.showerror("Error", f"Enemy file not found: {self.enemy_file}")

        # Add all players to self.friends if they're not already there
        for team in self.match_players.values():
            for player in team:
                if player not in self.friends:
                    self.friends[player] = ""

        self.save_friends()
        self.populate_friend_list()

    def clear_teams(self):
        self.match_players = {"Your Team": [], "Your Enemy": []}
        self.populate_friend_list()


if __name__ == "__main__":
    app = OverlayWindow()
    if not app.auto_login():
        app.login()
    try:
        app.root.mainloop()
    finally:
        if app.session:
            app.session.close()
