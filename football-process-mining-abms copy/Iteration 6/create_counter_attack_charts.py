#!/usr/bin/env python3
"""
Counter-Attack Visual Analysis
Creates visualizations of counter-attack patterns and effectiveness
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_counter_attack_visualizations():
    """Create comprehensive visualizations of counter-attack analysis"""
    
    # Load data
    df = pd.read_csv('batch_outputs/football_30games_20250616_213147.csv')
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Counter-Attack Spike Tactic Analysis - 30 Games', fontsize=16, fontweight='bold')
    
    # 1. Goals per match comparison
    goals = df[(df['action'].str.contains('Shot', na=False)) & (df['outcome'] == 'Goal')]
    match_goals = goals.groupby(['match_id', 'team']).size().unstack(fill_value=0)
    
    matches = range(1, len(match_goals) + 1)
    home_goals = match_goals['Home'].values
    away_goals = match_goals['Away'].values
    
    ax1.bar([x - 0.2 for x in matches], home_goals, width=0.4, label='Home (Counter-Attack)', alpha=0.8, color='red')
    ax1.bar([x + 0.2 for x in matches], away_goals, width=0.4, label='Away (Baseline)', alpha=0.8, color='blue')
    ax1.set_xlabel('Match Number')
    ax1.set_ylabel('Goals Scored')
    ax1.set_title('Goals per Match: Home vs Away Teams')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add summary stats
    home_total = sum(home_goals)
    away_total = sum(away_goals)
    ax1.text(0.02, 0.98, f'Total: Home {home_total}, Away {away_total}', 
             transform=ax1.transAxes, verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 2. Shot comparison
    home_shots = df[(df['team'] == 'Home') & (df['action'].str.contains('Shot', na=False))]
    away_shots = df[(df['team'] == 'Away') & (df['action'].str.contains('Shot', na=False))]
    
    shot_data = [len(home_shots), len(away_shots)]
    teams = ['Home\n(Counter-Attack)', 'Away\n(Baseline)']
    colors = ['red', 'blue']
    
    bars = ax2.bar(teams, shot_data, color=colors, alpha=0.8)
    ax2.set_ylabel('Total Shots')
    ax2.set_title('Total Shots: Home vs Away Teams')
    ax2.grid(True, alpha=0.3)
    
    # Add values on bars
    for bar, value in zip(bars, shot_data):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(value),
                ha='center', va='bottom', fontweight='bold')
    
    # 3. Counter-attack event analysis
    counter_events = df[df['action'].str.contains('CounterAttack', na=False)]
    
    # Counter-attack shots by zone
    ca_shots = counter_events[counter_events['action'] == 'CounterAttackShot']
    zone_counts = ca_shots['zone'].value_counts()
    
    if len(zone_counts) > 0:
        ax3.bar(zone_counts.index, zone_counts.values, color='orange', alpha=0.8)
        ax3.set_xlabel('Zone')
        ax3.set_ylabel('Counter-Attack Shots')
        ax3.set_title('Counter-Attack Shots by Zone')
        ax3.grid(True, alpha=0.3)
        
        # Add total and goal info
        ca_goals = len(ca_shots[ca_shots['outcome'] == 'Goal'])
        ax3.text(0.02, 0.98, f'Total CA Shots: {len(ca_shots)}\nCA Goals: {ca_goals}', 
                 transform=ax3.transAxes, verticalalignment='top', fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    else:
        ax3.text(0.5, 0.5, 'No Counter-Attack Events Found', 
                 transform=ax3.transAxes, ha='center', va='center', fontsize=12)
        ax3.set_title('Counter-Attack Shots by Zone')
    
    # 4. Win/Loss/Draw analysis
    home_wins = (match_goals['Home'] > match_goals['Away']).sum()
    away_wins = (match_goals['Away'] > match_goals['Home']).sum()
    draws = (match_goals['Home'] == match_goals['Away']).sum()
    
    results = [home_wins, away_wins, draws]
    result_labels = ['Home Wins', 'Away Wins', 'Draws']
    result_colors = ['red', 'blue', 'gray']
    
    wedges, texts, autotexts = ax4.pie(results, labels=result_labels, colors=result_colors, 
                                       autopct='%1.1f%%', startangle=90)
    ax4.set_title('Match Results Distribution')
    
    # Add total matches
    total_matches = len(match_goals)
    ax4.text(0.02, 0.98, f'Total Matches: {total_matches}', 
             transform=ax4.transAxes, verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('process_analysis/counter_attack_analysis_charts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print summary statistics
    print("=== COUNTER-ATTACK ANALYSIS SUMMARY ===")
    print(f"Total matches analyzed: {total_matches}")
    print(f"Home team record: {home_wins}-{away_wins}-{draws}")
    print(f"Total goals: Home {home_total}, Away {away_total}")
    print(f"Goal differential: +{home_total - away_total} (Home advantage)")
    print(f"Total shots: Home {len(home_shots)}, Away {len(away_shots)}")
    print(f"Counter-attack events: {len(counter_events)}")
    print(f"Counter-attack shots: {len(ca_shots)}")
    if len(ca_shots) > 0:
        ca_goals = len(ca_shots[ca_shots['outcome'] == 'Goal'])
        print(f"Counter-attack goals: {ca_goals}")
        print(f"Counter-attack conversion rate: {100*ca_goals/len(ca_shots):.1f}%")
    
    return {
        'matches': total_matches,
        'home_wins': home_wins,
        'away_wins': away_wins,
        'draws': draws,
        'home_goals': home_total,
        'away_goals': away_total,
        'counter_attack_events': len(counter_events),
        'counter_attack_goals': ca_goals if len(ca_shots) > 0 else 0
    }

if __name__ == "__main__":
    results = create_counter_attack_visualizations()
