#!/usr/bin/env python3
"""
Counter-Attack Pattern Analysis
Analyzes the effectiveness of the counter-attack spike tactic implementation
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_counter_attack_patterns():
    """Analyze counter-attack patterns from the 30-game dataset"""
    
    # Load the data
    df = pd.read_csv('batch_outputs/football_30games_20250616_213147.csv')
    
    print("=== COUNTER-ATTACK SPIKE TACTIC ANALYSIS ===")
    print(f"Total events analyzed: {len(df)}")
    print(f"Total matches: {df['match_id'].nunique()}")
    
    # 1. Counter-attack event frequency analysis
    counter_events = df[df['activity'].str.contains('CounterAttack', na=False)]
    print(f"\n1. COUNTER-ATTACK EVENT FREQUENCY:")
    print(f"   Total counter-attack events: {len(counter_events)}")
    print(f"   Counter-attack events per game: {len(counter_events) / df['match_id'].nunique():.2f}")
    
    # Breakdown by type
    ca_types = counter_events['activity'].value_counts()
    print(f"   Counter-attack event types:")
    for event_type, count in ca_types.items():
        print(f"     - {event_type}: {count}")
    
    # 2. Counter-attack success rate analysis
    ca_shots = counter_events[counter_events['activity'] == 'CounterAttackShot']
    goals = len(ca_shots[ca_shots['outcome'] == 'Goal'])
    on_target = len(ca_shots[ca_shots['outcome'] == 'OnTarget'])
    total_shots = len(ca_shots)
    
    print(f"\n2. COUNTER-ATTACK EFFECTIVENESS:")
    print(f"   Counter-attack shots: {total_shots}")
    print(f"   Goals scored: {goals} ({100*goals/total_shots:.1f}%)")
    print(f"   Shots on target: {on_target} ({100*on_target/total_shots:.1f}%)")
    print(f"   Shot conversion rate: {100*goals/total_shots:.1f}%")
    
    # 3. Analyze sequences leading to counter-attacks
    print(f"\n3. COUNTER-ATTACK SEQUENCE ANALYSIS:")
    
    # Group by possession to analyze sequences
    sequences = []
    for match_id in df['match_id'].unique():
        match_data = df[df['match_id'] == match_id].sort_values('timestamp')
        
        current_possession = []
        current_possession_id = None
        
        for _, row in match_data.iterrows():
            if row['activity'] == 'PossessionStart':
                if current_possession:
                    sequences.append(current_possession)
                current_possession = [row]
                current_possession_id = row['possession_id']
            elif current_possession_id == row.get('possession_id', None):
                current_possession.append(row)
            elif row['activity'] == 'PossessionEnd':
                current_possession.append(row)
                sequences.append(current_possession)
                current_possession = []
                current_possession_id = None
    
    # Find sequences with counter-attacks
    ca_sequences = []
    for seq in sequences:
        activities = [event['activity'] if isinstance(event, dict) else event.activity for event in seq]
        if any('CounterAttack' in str(activity) for activity in activities):
            ca_sequences.append(seq)
    
    print(f"   Total possessions analyzed: {len(sequences)}")
    print(f"   Possessions with counter-attacks: {len(ca_sequences)}")
    
    # Analyze the patterns in counter-attack sequences
    ca_patterns = []
    for seq in ca_sequences:
        pattern = []
        for event in seq:
            activity = event['activity'] if isinstance(event, dict) else event.activity
            if activity in ['Interception', 'Pass', 'Dribble', 'CounterAttackShot', 'CounterAttackPass', 'CounterAttackDribble']:
                pattern.append(activity)
        if pattern:
            ca_patterns.append(' → '.join(pattern))
    
    print(f"\n   Counter-attack sequence patterns:")
    pattern_counts = Counter(ca_patterns)
    for pattern, count in pattern_counts.most_common():
        print(f"     {pattern}: {count} occurrences")
    
    # 4. Compare Home vs Away team performance
    print(f"\n4. HOME vs AWAY TEAM COMPARISON:")
    
    home_events = df[df['team'] == 'Home']
    away_events = df[df['team'] == 'Away']
    
    print(f"   Home team events: {len(home_events)}")
    print(f"   Away team events: {len(away_events)}")
    
    # Goals comparison
    home_goals = len(home_events[(home_events['activity'] == 'Shot') & (home_events['outcome'] == 'Goal')])
    away_goals = len(away_events[(away_events['activity'] == 'Shot') & (away_events['outcome'] == 'Goal')])
    
    print(f"   Home team goals: {home_goals}")
    print(f"   Away team goals: {away_goals}")
    print(f"   Home team advantage: {home_goals - away_goals} goals")
    
    # Shot statistics
    home_shots = len(home_events[home_events['activity'].str.contains('Shot', na=False)])
    away_shots = len(away_events[away_events['activity'].str.contains('Shot', na=False)])
    
    print(f"   Home team shots: {home_shots}")
    print(f"   Away team shots: {away_shots}")
    
    # 5. Final third analysis
    print(f"\n5. FINAL THIRD PENETRATION ANALYSIS:")
    
    # Analyze events in zones D1-D5 (final third)
    final_third_zones = ['D1', 'D2', 'D3', 'D4', 'D5']
    
    home_final_third = home_events[home_events['zone'].isin(final_third_zones)]
    away_final_third = away_events[away_events['zone'].isin(final_third_zones)]
    
    print(f"   Home team final third events: {len(home_final_third)}")
    print(f"   Away team final third events: {len(away_final_third)}")
    
    # Counter-attack final third events
    ca_final_third = counter_events[counter_events['zone'].isin(final_third_zones)]
    print(f"   Counter-attack final third events: {len(ca_final_third)}")
    
    return {
        'total_events': len(df),
        'counter_attack_events': len(counter_events),
        'counter_attack_goals': goals,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'patterns': pattern_counts
    }

if __name__ == "__main__":
    results = analyze_counter_attack_patterns()
