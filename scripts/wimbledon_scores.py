#!/usr/bin/env python3
#
# wimbledon_scores.py (Qtile & NixOS verzió)
#
# Ez a szkript Qtile-hoz készült, hogy egyetlen gombként működjön a tenisz eredményekhez.
# A kattintásokat a Qtile konfigurációja kezeli. A tornákat fontosság szerint rendezi.
# Támogatja a kedvenc játékosok kiemelését és a rendszerértesítéseket.
#
# Függőségek:
# - python3
# - python3Packages.requests (NixOS-ben)
# - libnotify (a rendszerértesítésekhez)
#

import os
import sys
import json
import requests
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

# --- KONFIGURÁCIÓS FÁJLOK ---
FAVORITES_FILE = os.path.expanduser("~/.config/qtile/scripts/tennis_favorites.json")
STATE_FILE = "/tmp/tennis_notification_state.json"

class Colors:
    """ANSI színkódok a terminálos megjelenítéshez."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'

def load_favorites():
    """Betölti a kedvenc játékosok listáját a JSON fájlból."""
    try:
        with open(FAVORITES_FILE, 'r') as f:
            return [player.lower() for player in json.load(f)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def format_full_output(events_by_tournament, favorites):
    """Az összes csoportosított eseményt egy részletes, színes, szövegfájlba szánt sztringgé formázza."""
    if not events_by_tournament:
        return "Nincsenek megjeleníthető események."
    
    output_lines = []
    # Rendezés a torna prioritása szerint
    sorted_tournaments = sorted(events_by_tournament.items(), key=lambda item: item[1][0]['priority'])
    
    for tournament, events in sorted_tournaments:
        output_lines.append(f"{Colors.BOLD}{Colors.CYAN}--- {tournament} ---{Colors.RESET}")
        for event in events:
            p1_display = event['player1']
            p2_display = event['player2']

            if p1_display.lower() in favorites:
                p1_display = f"{Colors.MAGENTA}⭐ {p1_display}{Colors.RESET}"
            if p2_display.lower() in favorites:
                p2_display = f"{Colors.MAGENTA}⭐ {p2_display}{Colors.RESET}"

            if event.get('server') == 'p1':
                p1_display = f"{Colors.GREEN}●{Colors.RESET} {p1_display}"
            elif event.get('server') == 'p2':
                p2_display = f"{Colors.GREEN}●{Colors.RESET} {p2_display}"
            
            if event.get('winner') == 'p1':
                p1_display = f"{Colors.GREEN}{p1_display}{Colors.RESET}"
                p2_display = f"{Colors.RED}{p2_display}{Colors.RESET}"
            elif event.get('winner') == 'p2':
                p2_display = f"{Colors.GREEN}{p2_display}{Colors.RESET}"
                p1_display = f"{Colors.RED}{p1_display}{Colors.RESET}"

            details = event['details']
            if details.get('game'):
                score_str = f"[{Colors.YELLOW}{details['sets']}{Colors.RESET}] ({Colors.YELLOW}{details['game']}{Colors.RESET})"
            elif details.get('status') == 'Upcoming':
                score_str = f"{Colors.DIM}(Hamarosan){Colors.RESET}"
            else:
                score_str = f"[{Colors.YELLOW}{details['sets']}{Colors.RESET}]"

            output_lines.append(f"  {p1_display} v {p2_display} {score_str}")
        output_lines.append("")
        
    return "\n".join(output_lines)

def process_events(data, allowed_statuses):
    """Segédfüggvény a tenisz API adatok feldolgozásához, a megadott státuszok alapján."""
    events_by_tournament = defaultdict(list)
    main_tours = ['ATP', 'WTA', 'Grand Slam']

    for stage in data.get('Stages', []):
        tour_category = stage.get('Cnm')
        tournament_name = stage.get('Snm', 'Ismeretlen Torna')
        
        for event in stage.get('Events', []):
            try:
                status = event.get('Eps')
                if status not in allowed_statuses:
                    continue

                event_info = {
                    'player1': event.get('T1', [{}])[0].get('Nm', 'P1'),
                    'player2': event.get('T2', [{}])[0].get('Nm', 'P2'),
                    'details': {}, 'server': None, 'winner': None,
                    'id': event.get('Eid'),
                    'priority': 0 if tour_category in main_tours else 1
                }

                if status == 'In Progress':
                    p1_id = event.get('T1', [{}])[0].get('ID')
                    if event.get('Esv') == p1_id: event_info['server'] = 'p1'
                    else: event_info['server'] = 'p2'
                    event_info['details']['sets'] = f"{event.get('Tr1', '0')}-{event.get('Tr2', '0')}"
                    p1_game = event.get('Tr1G'); p2_game = event.get('Tr2G')
                    if p1_game is not None and p2_game is not None:
                        event_info['details']['game'] = f"{p1_game}-{p2_game}"
                    
                elif status == 'NS':
                    event_info['details']['status'] = 'Upcoming'
                    
                elif status in ['Finished', 'FT', 'Ret.', 'W.O.']:
                    event_info['details']['sets'] = f"{event.get('Tr1', '0')}-{event.get('Tr2', '0')}"
                    winner_id = event.get('Ewt')
                    p1_id = event.get('T1', [{}])[0].get('ID')
                    p2_id = event.get('T2', [{}])[0].get('ID')
                    if winner_id:
                        if p1_id and str(winner_id) == str(p1_id): event_info['winner'] = 'p1'
                        elif p2_id and str(winner_id) == str(p2_id): event_info['winner'] = 'p2'
                    if event_info['winner'] is None:
                        try:
                            p1_sets = int(event.get('Tr1', '0')); p2_sets = int(event.get('Tr2', '0'))
                            if p1_sets > p2_sets: event_info['winner'] = 'p1'
                            elif p2_sets > p1_sets: event_info['winner'] = 'p2'
                        except (ValueError, TypeError): pass
                
                events_by_tournament[tournament_name].append(event_info)
            except (AttributeError, KeyError, IndexError):
                continue
    
    return events_by_tournament

def fetch_data(url):
    """Általános függvény adatok letöltéséhez egy URL-ről."""
    headers = {'User-Agent': 'i3blocks-tennis-script/1.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_events_for_day(date_str, allowed_statuses):
    """Letölti és feldolgozza egy adott nap összes eseményét."""
    url = f"https://prod-public-api.livescore.com/v1/api/app/date/tennis/{date_str}/0"
    try:
        data = fetch_data(url)
        return process_events(data, allowed_statuses=allowed_statuses)
    except Exception:
        return None

def send_notification(title, body):
    """Rendszerértesítést küld a notify-send paranccsal."""
    try:
        subprocess.Popen(['notify-send', '-i', 'dialog-information', title, body])
    except FileNotFoundError:
        pass

def check_for_notifications(favorites):
    """Ellenőrzi a kedvenc játékosok meccseit és értesítést küld a változásokról."""
    if not favorites: return
    try:
        try:
            with open(STATE_FILE, 'r') as f: old_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): old_state = {}

        live_url = "https://prod-public-api.livescore.com/v1/api/app/live/tennis/0"
        live_data = fetch_data(live_url)
        live_events = process_events(live_data, allowed_statuses=['In Progress'])
        
        new_state = {}
        for events in live_events.values():
            for event in events:
                is_favorite_match = event['player1'].lower() in favorites or event['player2'].lower() in favorites
                if is_favorite_match:
                    score = f"[{event['details']['sets']}]"
                    if event['details'].get('game'):
                        score += f" ({event['details']['game']})"
                    new_state[event['id']] = f"{event['player1']} vs {event['player2']} {score}"

        for event_id, score in new_state.items():
            if event_id not in old_state:
                send_notification("Meccs Kezdődött!", score)

        for event_id, score in old_state.items():
            if event_id not in new_state:
                send_notification("Meccs Befejeződött!", score)
        
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f)
    except Exception: pass

if __name__ == "__main__":
    """Fő végrehajtási blokk."""
    try:
        args = sys.argv[1:]
        favorites = load_favorites()

        if 'check-notify' in args:
            check_for_notifications(favorites)
            sys.exit(0)
        
        if 'full' in args:
            period = 'yesterday' if 'yesterday' in args else 'today'
            all_events = get_events_for_day(period, ['In Progress', 'NS'] if period == 'today' else ['Finished', 'FT', 'Ret.', 'W.O.'])
            print(format_full_output(all_events, favorites))
        else:
            print("🎾")

    except Exception as e:
        print(f"🎾 Hiba: {e}")

