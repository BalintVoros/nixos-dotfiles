# ============== QTILE CONFIGURATION ==============
import os
import subprocess
from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy

# --- Basic Setup ---
mod = "mod4"        # Super key (Windows key)
terminal = "alacritty"
browser = "firefox"
file_manager = "pcmanfm"
font_name = "FiraCode Nerd Font" # Make sure this font is installed

# --- Autostart ---
@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    try:
        subprocess.Popen([home])
    except FileNotFoundError:
        pass

# --- Keybindings ---
keys = [
    # Window Navigation & Manipulation
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "space", lazy.layout.next()),
    Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod, "control"], "h", lazy.layout.grow_left()),
    Key([mod, "control"], "l", lazy.layout.grow_right()),
    Key([mod, "control"], "j", lazy.layout.grow_down()),
    Key([mod, "control"], "k", lazy.layout.grow_up()),
    Key([mod], "n", lazy.layout.normalize()),

    # Application Shortcuts
    Key([mod], "q", lazy.window.kill()),
    Key([mod], "b", lazy.spawn(browser)),
    Key([mod], "f", lazy.spawn(file_manager)),
    Key([mod], "d", lazy.spawn("rofi -show drun")),
    Key([mod], "Return", lazy.spawn(terminal)),

    # Qtile Management
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    
    # --- Scratchpad & Screenshot ---
    Key([mod], "a", lazy.group['scratchpad'].dropdown_toggle('term')),
    Key([mod, "shift"], "s", lazy.spawn("flameshot gui"), desc="Take a screenshot with Flameshot"),
]

# --- Groups (Workspaces with Icons) ---
groups = [
    Group("1", label=""), Group("2", label=""), Group("3", label=""),
    Group("4", label="󰈙"), Group("5", label=""),
]

# --- Add ScratchPad Group ---
groups.append(ScratchPad("scratchpad", [
    # MODIFIED: Changed width and height to 0.6 and adjusted x/y to keep it centered.
    DropDown("term", "alacritty", width=0.6, height=0.6, x=0.2, y=0.2, opacity=1),
]))

# --- Group Keybindings ---
for i in groups:
    # We skip the scratchpad group for regular keybindings
    if i.name != "scratchpad":
        keys.extend([
            Key([mod], i.name, lazy.group[i.name].toscreen(), desc=f"Switch to group {i.name}"),
            Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=True), desc=f"Move window to group {i.name}"),
        ])

# --- Layouts ---
layout_theme = { "border_width": 2, "margin": 8, "border_focus": "#ff79c6", "border_normal": "#282a36" }
layouts = [ layout.Columns(**layout_theme), layout.Max(**layout_theme) ]

# --- Bar and Widgets ---
widget_defaults = dict(font=font_name, fontsize=14, padding=3, background="#282a36", foreground="#f8f8f2")

# --- Function to call the email script ---
def check_email_script():
    script_path = os.path.expanduser("~/.config/qtile/scripts/check_email.py")
    try:
        return subprocess.check_output(script_path).decode("utf-8").strip()
    except Exception:
        return " SCRIPT ERR"

screens = [
    Screen(
        top=bar.Bar([
            widget.GroupBox(
                fontsize=24, active="#f8f8f2", inactive="#6272a4",
                highlight_method="block", this_current_screen_border="#bd93f9",
                padding_x=5, borderwidth=3
            ),
            widget.WindowName(foreground="#bd93f9", padding=5),
            widget.Systray(),
            widget.Spacer(bar.STRETCH),
            widget.Pomodoro(
                color_active="#50fa7b", color_inactive="#ff5555",
                prefix_inactive='POMO', padding=5
            ),
            widget.GenPollText(
                func=check_email_script, update_interval=300,
                foreground="#8be9fd", mouse_callbacks={'Button1': lazy.spawn(f"{browser} https://mail.google.com")},
                padding=5,
            ),
            widget.Battery(
                format='{char} {percent:2.0%}', charge_char='', discharge_char='',
                full_char='', unknown_char='', foreground="#50fa7b",
                low_foreground="#ff5555", padding=5
            ),
            #   widget.CPU(format=' {load_percent}%', foreground="#ffb86c", padding=5),
            widget.Memory(format='󰍛 {MemUsed:.0f}{mm}', foreground="#50fa7b", measure_mem='G', padding=5),
            widget.PulseVolume(fmt='󰕾 {}', foreground="#f1fa8c", padding=5),
            widget.Clock(format=" %Y-%m-%d %a %I:%M %p", foreground="#8be9fd", padding=10),
            widget.QuickExit(default_text='', countdown_format='[{}]', fontsize=20, foreground="#ff5555", padding=5),
        ], 30, opacity=0.9),
    ),
]

# --- Final Settings ---
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wmname = "LG3D"

