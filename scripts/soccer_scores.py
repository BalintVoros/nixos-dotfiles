#!/usr/bin/env python3
#
# soccer_scores.py (Qtile & NixOS verzió)
#
# Ez a szkript Qtile-hoz készült, hogy egyetlen gombként működjön a foci eredményekhez.
# A kattintásokat a Qtile konfigurációja kezeli, és csak a top ligákat mutatja.
# - Futtatás argumentum nélkül: a statikus ikon megjelenítése a sávon.
# - Futtatás 'full' argumentummal: a MAI meccsek teljes listájának generálása.
# - Futtatás 'full yesterday' argumentummal: az ELMÚLT HÉT eredményeinek listájának generálása.
#
# Függőségek:
# - python3
# - python3Packages.requests (NixOS-ben)
#

import os
import sys
import json
import requests
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

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

def format_daily_output(events_by_tournament, title=""):
    """Egyetlen nap eseményeit formázza meg, opcionális főcímmel."""
    if not events_by_tournament:
        return ""
    
    output_lines = []
    if title:
        output_lines.append(f"{Colors.BOLD}{Colors.WHITE}📅 {title}{Colors.RESET}")

    for tournament, events in sorted(events_by_tournament.items()):
        output_lines.append(f"{Colors.BOLD}{Colors.CYAN}--- {tournament} ---{Colors.RESET}")
        for event in events:
            t1_display = event['team1']
            t2_display = event['team2']

            if event.get('winner') == 't1':
                t1_display = f"{Colors.GREEN}{t1_display}{Colors.RESET}"
                t2_display = f"{Colors.RED}{t2_display}{Colors.RESET}"
            elif event.get('winner') == 't2':
                t2_display = f"{Colors.GREEN}{t2_display}{Colors.RESET}"
                t1_display = f"{Colors.RED}{t1_display}{Colors.RESET}"

            details = event['details']
            score_str = ""
            status_str = ""
            
            if details.get('status') == 'Upcoming':
                status_str = f"{Colors.DIM}(Hamarosan){Colors.RESET}"
            else:
                score_str = f"[{Colors.YELLOW}{details['score']}{Colors.RESET}]"
                status_str = f"({Colors.YELLOW}{details['status']}{Colors.RESET})"

            match_line = f"  {t1_display} vs {t2_display}"
            if score_str:
                match_line += f" {score_str}"
            if status_str:
                match_line += f" {status_str}"
            
            output_lines.append(match_line)
        output_lines.append("")
        
    return "\n".join(output_lines)

def process_events(data):
    """Segédfüggvény a foci API adatok feldolgozásához, csak a fontos ligákra szűrve."""
    events_by_tournament = defaultdict(list)
    
    IMPORTANT_LEAGUES = {
        "England": ["Premier League"],
        "Spain": ["LaLiga"],
        "Germany": ["Bundesliga"],
        "Italy": ["Serie A"],
        "France": ["Ligue 1"],
        "Europe": ["Champions League", "Europa League", "Europa Conference League", "European Championship"],
        "World": ["World Cup"],
        "South America": ["Copa America"]
    }

    sorted_stages = sorted(data.get('Stages', []), key=lambda s: (s.get('Cnm', ''), s.get('Snm', '')))

    for stage in sorted_stages:
        country_name = stage.get('Cnm', '')
        league_name = stage.get('Snm', 'Unknown League')
        
        if not (country_name in IMPORTANT_LEAGUES and league_name in IMPORTANT_LEAGUES[country_name]):
            continue

        tournament_name = f"{country_name} - {league_name}"
        
        for event in stage.get('Events', []):
            try:
                event_info = {
                    'team1': event.get('T1', [{}])[0].get('Nm', 'Csapat 1'),
                    'team2': event.get('T2', [{}])[0].get('Nm', 'Csapat 2'),
                    'details': {},
                    'winner': None
                }
                status = event.get('Eps')
                
                if status == 'NS':
                    event_info['details']['status'] = 'Upcoming'
                else:
                    score1_str = event.get('Tr1', '0')
                    score2_str = event.get('Tr2', '0')
                    event_info['details']['score'] = f"{score1_str} - {score2_str}"
                    
                    live_minute = event.get('Epr')
                    if live_minute and status not in ['FT', 'HT', 'AET', 'AP']:
                        event_info['details']['status'] = f"{live_minute}'"
                    else:
                        event_info['details']['status'] = status
                    
                    if status == 'FT':
                        try:
                            score1 = int(score1_str)
                            score2 = int(score2_str)
                            if score1 > score2:
                                event_info['winner'] = 't1'
                            elif score2 > score1:
                                event_info['winner'] = 't2'
                        except (ValueError, TypeError):
                            pass

                events_by_tournament[tournament_name].append(event_info)
            except (AttributeError, KeyError, IndexError):
                continue
    
    return events_by_tournament

def fetch_data(url):
    """Általános függvény adatok letöltéséhez egy URL-ről."""
    headers = {'User-Agent': 'i3blocks-soccer-script/1.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_events_for_day(date_str):
    """Letölti és feldolgozza egy adott nap összes eseményét."""
    url = f"https://prod-public-api.livescore.com/v1/api/app/date/soccer/{date_str}/0"
    try:
        data = fetch_data(url)
        return process_events(data)
    except Exception:
        return None

if __name__ == "__main__":
    """Fő végrehajtási blokk."""
    try:
        args = sys.argv[1:]
        
        if 'full' in args:
            if 'yesterday' in args:
                weekly_output_lines = []
                found_matches = False
                for i in range(1, 8):
                    day = datetime.now() - timedelta(days=i)
                    date_str_api = day.strftime("%Y%m%d")
                    date_str_display = day.strftime("%Y-%m-%d (%A)")
                    
                    daily_events = get_events_for_day(date_str_api)
                    if daily_events:
                        found_matches = True
                        weekly_output_lines.append(format_daily_output(daily_events, title=date_str_display))
                
                if not found_matches:
                    print("Nincsenek eredmények az elmúlt héten a top ligákban.")
                else:
                    print("\n\n".join(weekly_output_lines))
            else:
                today_str = datetime.now().strftime("%Y%m%d")
                events_today = get_events_for_day(today_str)
                if not events_today:
                    print("Nincsenek mai meccsek a top ligákban.")
                else:
                    print(format_daily_output(events_today))
        else:
            print("⚽")

    except Exception as e:
        print(f"⚽ Hiba: {e}")

