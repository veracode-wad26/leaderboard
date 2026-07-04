#!/usr/bin/env python3
"""
Aggregates all event files in events/ into a leaderboard.json.

Reads all JSON files from events/{repo}/*.json and creates a sorted leaderboard.

Output format:
{
  "generated_at": "2026-07-09T14:32:15Z",
  "leaderboard": [
    {
      "rank": 1,
      "participant_alias": "caffeinated-phoenix",
      "repo": "verademo-javascript-api",
      "score": 25,
      "time": "2026-07-09T10:53:55.01234Z"
    },
    ...
  ]
}
"""

import json
import os
from pathlib import Path
from datetime import datetime


def aggregate_leaderboard():
    """Aggregate all event files into a leaderboard."""
    events_dir = Path('events')

    if not events_dir.exists():
        print("❌ events/ directory not found")
        return

    # Collect all events
    all_events = []

    for repo_dir in events_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        repo_name = repo_dir.name

        for event_file in repo_dir.glob('*.json'):
            try:
                with open(event_file, 'r') as f:
                    event = json.load(f)
                    all_events.append(event)
            except Exception as e:
                print(f"⚠️  Error reading {event_file}: {e}")

    # Group by participant + repo, keep latest event for each combo
    latest_per_repo = {}
    for event in all_events:
        key = (event['participant_alias'], event['repo'])
        if key not in latest_per_repo or event['time'] > latest_per_repo[key]['time']:
            latest_per_repo[key] = event

    # Now aggregate by participant, summing scores from latest events per repo
    participants = {}
    for event in latest_per_repo.values():
        alias = event['participant_alias']
        if alias not in participants:
            participants[alias] = {
                'participant_alias': alias,
                'total_score': 0,
                'latest_time': event['time'],
                'repos': []
            }

        participants[alias]['total_score'] += event['score']
        participants[alias]['repos'].append(event['repo'])

        # Keep the latest timestamp
        if event['time'] > participants[alias]['latest_time']:
            participants[alias]['latest_time'] = event['time']

    # Convert to list and sort by total score (descending), then by latest time (ascending)
    all_events = list(participants.values())
    all_events.sort(key=lambda x: (-x['total_score'], x['latest_time']))

    # Add rank
    for rank, event in enumerate(all_events, 1):
        event['rank'] = rank

    # Create leaderboard structure
    leaderboard = {
        'generated_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'leaderboard': all_events,
    }

    # Write leaderboard.json
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f, indent=2)

    print(f"✅ Updated leaderboard.json with {len(all_events)} entries")

    # Print top 10
    if all_events:
        print("\n🏆 Top 10:")
        for event in all_events[:10]:
            repos = ', '.join(event['repos'])
            print(f"  {event['rank']:2d}. {event['participant_alias']:20s} - {event['total_score']} fixed ({repos})")


if __name__ == '__main__':
    aggregate_leaderboard()
