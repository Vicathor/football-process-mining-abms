#!/usr/bin/env python3
"""
30 Game Batch Football Simulation
Simple, direct implementation for running 30 games and process mining analysis
"""
import os
import pandas as pd
import pm4py
from datetime import datetime
from football_model import FootballModel
from process_mining_analysis import FootballProcessMiner
import warnings
warnings.filterwarnings('ignore')

def run_30_game_batch():
    """Run 30 football games and perform process mining analysis"""
    print("🚀 30-GAME FOOTBALL BATCH SIMULATION")
    print("=" * 60)
    
    # Setup
    num_games = 30
    output_dir = "batch_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    combined_events = []
    match_results = []
    
    start_time = datetime.now()
    
    # Run 30 games
    for game_num in range(num_games):
        print(f"🏈 Game {game_num + 1}/30 (seed: {42 + game_num})")
        
        # Create and run match
        model = FootballModel(match_duration_minutes=45, seed=42 + game_num)
        
        # Run full match
        while model.running:
            model.step()
        
        # Collect events
        events = model.logger.events.copy()
        
        # Add match identifier
        for event in events:
            event['match_id'] = f"M{game_num + 1:02d}"
            event['game_number'] = game_num + 1
        
        combined_events.extend(events)
        
        # Calculate match stats
        home_goals = sum(1 for e in events if e.get('action') == 'Goal' and e.get('team') == 'Home')
        away_goals = sum(1 for e in events if e.get('action') == 'Goal' and e.get('team') == 'Away')
        total_possessions = len(set(e.get('possession_id', '') for e in events if e.get('possession_id')))
        
        result = 'Draw'
        if home_goals > away_goals:
            result = 'Home Win'
        elif away_goals > home_goals:
            result = 'Away Win'
        
        match_results.append({
            'game': game_num + 1,
            'seed': 42 + game_num,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'total_events': len(events),
            'total_possessions': total_possessions,
            'result': result
        })
        
        print(f"   ⚽ {result}: {home_goals}-{away_goals} | Events: {len(events)} | Possessions: {total_possessions}")
        
        # Progress update every 5 games
        if (game_num + 1) % 5 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time = elapsed / (game_num + 1)
            remaining = avg_time * (num_games - game_num - 1)
            print(f"   ⏱️  Progress: {game_num + 1}/30 | Est. remaining: {remaining:.0f}s")
            print()
    
    total_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ All 30 games completed in {total_time:.1f} seconds!")
    
    # Export combined data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. CSV Export
    df = pd.DataFrame(combined_events)
    csv_path = f"{output_dir}/football_30games_{timestamp}.csv"
    df.to_csv(csv_path, index=False)
    print(f"📄 Combined CSV: {csv_path}")
    
    # 2. XES Export for PM4Py
    df_xes = df.copy()
    df_xes = df_xes.rename(columns={
        'possession_id': 'case:concept:name',
        'action': 'concept:name', 
        'timestamp': 'time:timestamp'
    })
    df_xes['time:timestamp'] = pd.to_datetime(df_xes['time:timestamp'])
    
    xes_path = f"{output_dir}/football_30games_{timestamp}.xes"
    try:
        event_log = pm4py.convert_to_event_log(df_xes)
        pm4py.write_xes(event_log, xes_path)
        print(f"📊 Combined XES: {xes_path}")
    except Exception as e:
        print(f"⚠️  XES export failed: {e}")
        return None
    
    # 3. Match Results Summary
    results_df = pd.DataFrame(match_results)
    results_path = f"{output_dir}/match_results_{timestamp}.csv"
    results_df.to_csv(results_path, index=False)
    print(f"🏆 Match results: {results_path}")
    
    # Print summary statistics
    print(f"\n📊 30-GAME BATCH SUMMARY")
    print("=" * 30)
    print(f"Total events: {len(combined_events):,}")
    print(f"Total possessions: {df['possession_id'].nunique():,}")
    print(f"Average events/game: {len(combined_events) / num_games:.1f}")
    print(f"Average possessions/game: {df['possession_id'].nunique() / num_games:.1f}")
    
    home_wins = sum(1 for r in match_results if r['result'] == 'Home Win')
    away_wins = sum(1 for r in match_results if r['result'] == 'Away Win')
    draws = sum(1 for r in match_results if r['result'] == 'Draw')
    
    print(f"Match results: {home_wins} Home, {away_wins} Away, {draws} Draws")
    print(f"Total goals: {sum(r['home_goals'] + r['away_goals'] for r in match_results)}")
    
    return csv_path, xes_path, len(combined_events), df['possession_id'].nunique()

def run_process_mining_on_batch(csv_path, xes_path, total_events, total_possessions):
    """Run process mining analysis on the 30-game batch"""
    print(f"\n🔬 PROCESS MINING ANALYSIS - 30 GAMES")
    print("=" * 50)
    print(f"Analyzing {total_events:,} events from {total_possessions:,} possessions")
    
    # Load the data
    df = pd.read_csv(csv_path)
    event_log = pm4py.read_xes(xes_path)
    
    print(f"✅ Data loaded: {len(df)} events, {len(event_log)} traces")
    
    # Run process mining with the existing analyzer
    # We'll use the process_mining_analysis.py with --batch flag
    import subprocess
    import sys
    
    # Copy files to the expected location for batch analysis
    import shutil
    batch_dir = "batch_outputs"
    expected_csv = f"{batch_dir}/batch_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    expected_xes = f"{batch_dir}/batch_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xes"
    
    shutil.copy2(csv_path, expected_csv)
    shutil.copy2(xes_path, expected_xes)
    
    print(f"📁 Copied files for batch analysis:")
    print(f"   CSV: {expected_csv}")
    print(f"   XES: {expected_xes}")
    
    # Run the process mining analysis
    result = subprocess.run([
        sys.executable, "process_mining_analysis.py", "--batch"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Process mining analysis completed successfully!")
        print(result.stdout)
    else:
        print("❌ Process mining analysis failed:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """Main function to run the complete 30-game analysis"""
    print("🎯 STARTING 30-GAME FOOTBALL ANALYSIS")
    print("=" * 50)
    
    # Step 1: Run 30 games
    result = run_30_game_batch()
    if not result:
        print("❌ Batch simulation failed")
        return
    
    csv_path, xes_path, total_events, total_possessions = result
    
    # Step 2: Run process mining analysis
    success = run_process_mining_on_batch(csv_path, xes_path, total_events, total_possessions)
    
    if success:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"✅ 30 games simulated")
        print(f"✅ {total_events:,} events generated")
        print(f"✅ Process mining analysis completed")
        print(f"✅ Petri nets generated for 30-game dataset")
        print(f"\n📁 Check 'process_analysis' directory for results!")
    else:
        print(f"\n⚠️  Simulation completed but process mining analysis had issues")
        print(f"📊 Data available in: {csv_path}")

if __name__ == "__main__":
    main()
