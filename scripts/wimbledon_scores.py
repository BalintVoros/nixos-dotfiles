#!/usr/bin/env python3
#
# wimbledon_scores.py (Qtile & NixOS verzió)
#
# Ez a szkript Qtile-hoz készült, hogy egyetlen gombként működjön a tenisz eredményekhez.
# A kattintásokat a Qtile konfigurációja kezeli.
# - Futtatás argumentum nélkül: a statikus ikon megjelenítése a sávon.
# - Futtatás 'full' argumentummal: a MAI meccsek teljes listájának generálása.
# - Futtatás 'full yesterday' argumentummal: a TEGNAPI eredmények listájának generálása.
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

def format_full_output(events_by_tournament):
    """Az összes csoportosított eseményt egy részletes, színes, szövegfájlba szánt sztringgé formázza."""
    if not events_by_tournament:
        return "Nincsenek megjeleníthető események."
    
    output_lines = []
    for tournament, events in sorted(events_by_tournament.items()):
        output_lines.append(f"{Colors.BOLD}{Colors.CYAN}--- {tournament} ---{Colors.RESET}")
        for event in events:
            p1_display = event['player1']
            p2_display = event['player2']

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
    main_tours = ['ATP', 'WTA', 'CHALLENGER']

    for stage in data.get('Stages', []):
        tour_category = stage.get('Cnm')
        tournament_name = stage.get('Snm', 'Ismeretlen Torna')
        is_main = tour_category in main_tours
        
        for event in stage.get('Events', []):
            try:
                status = event.get('Eps')
                if status not in allowed_statuses:
                    continue

                event_info = {
                    'player1': event.get('T1', [{}])[0].get('Nm', 'P1'),
                    'player2': event.get('T2', [{}])[0].get('Nm', 'P2'),
                    'details': {},
                    'server': None,
                    'winner': None,
                    'id': event.get('Eid'),
                    'is_main_tour': is_main
                }

                if status == 'In Progress':
                    p1_id = event.get('T1', [{}])[0].get('ID')
                    if event.get('Esv') == p1_id:
                        event_info['server'] = 'p1'
                    else:
                        event_info['server'] = 'p2'
                    
                    event_info['details']['sets'] = f"{event.get('Tr1', '0')}-{event.get('Tr2', '0')}"
                    p1_game = event.get('Tr1G')
                    p2_game = event.get('Tr2G')
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
                        if p1_id and str(winner_id) == str(p1_id):
                            event_info['winner'] = 'p1'
                        elif p2_id and str(winner_id) == str(p2_id):
                            event_info['winner'] = 'p2'
                    if event_info['winner'] is None:
                        try:
                            p1_sets = int(event.get('Tr1', '0'))
                            p2_sets = int(event.get('Tr2', '0'))
                            if p1_sets > p2_sets:
                                event_info['winner'] = 'p1'
                            elif p2_sets > p1_sets:
                                event_info['winner'] = 'p2'
                        except (ValueError, TypeError):
                            pass
                
                events_by_tournament[tournament_name].append(event_info)
            except (AttributeError, KeyError, IndexError):
                continue
    
    main_tour_events = {t:e for t,e in events_by_tournament.items() if any(match['is_main_tour'] for match in e)}
    if main_tour_events:
        return main_tour_events
    return events_by_tournament

def fetch_data(url):
    """Általános függvény adatok letöltéséhez egy URL-ről."""
    headers = {'User-Agent': 'i3blocks-tennis-script/1.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_all_events(period):
    """Letölti és feldolgozza egy adott időszak összes eseményét."""
    if period == 'today':
        live_url = "https://prod-public-api.livescore.com/v1/api/app/live/tennis/0"
        live_data = fetch_data(live_url)
        live_events = process_events(live_data, allowed_statuses=['In Progress'])

        date_str = datetime.now().strftime("%Y%m%d")
        date_url = f"https://prod-public-api.livescore.com/v1/api/app/date/tennis/{date_str}/0"
        date_data = fetch_data(date_url)
        upcoming_events = process_events(date_data, allowed_statuses=['NS'])

        combined_events = live_events
        live_event_ids = {event['id'] for tournament in live_events.values() for event in tournament}
        
        for tournament, events in upcoming_events.items():
            for event in events:
                if event['id'] not in live_event_ids:
                    combined_events[tournament].append(event)
        
        return filter_by_tour_priority(combined_events)

    else: # yesterday
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        url = f"https://prod-public-api.livescore.com/v1/api/app/date/tennis/{date_str}/0"
        data = fetch_data(url)
        finished_events = process_events(data, allowed_statuses=['Finished', 'FT', 'Ret.', 'W.O.'])
        return filter_by_tour_priority(finished_events)

if __name__ == "__main__":
    """Fő végrehajtási blokk."""
    try:
        args = sys.argv[1:]
        
        if 'full' in args:
            period = 'yesterday' if 'yesterday' in args else 'today'
            all_events = get_all_events(period)
            print(format_full_output(all_events))
        else:
            # Alapértelmezetten csak az ikont írja ki a sávra
            print("🎾")

    except Exception as e:
        print(f"🎾 Hiba: {e}")

