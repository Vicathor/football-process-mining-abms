"""
Football Simulation Runner
Main script to run football simulations and export logs
"""
import os
from datetime import datetime
from football_model import FootballModel


def run_simulation(match_duration: int = 90, seed: int = None, output_dir: str = "output"):
    """Run a single football simulation"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("="*60)
    print("🏈 FOOTBALL SIMULATION STARTING")
    print("="*60)
    print(f"Match Duration: {match_duration} minutes")
    print(f"Random Seed: {seed}")
    print(f"Output Directory: {output_dir}")
    print()
    
    # Create and run the model
    model = FootballModel(match_duration_minutes=match_duration, seed=seed)
    
    print("⚽ Match in progress...")
    print(f"Teams: Home vs Away")
    print(f"Formation: Home (4-3-3) vs Away (4-4-2)")
    print()
    
    # Run the simulation
    step_count = 0
    while model.running and step_count < model.total_steps:
        model.step()
        step_count += 1
        
        # Print periodic updates
        if step_count % 54 == 0:  # Every ~9 minutes (54 steps * 10 seconds)
            minute = step_count * 10 // 60
            print(f"  {minute:2d}' - Score: {model.score_home}-{model.score_away} | "
                  f"Possessions: {model.possession_count}")
    
    # Get final match summary
    summary = model.get_match_summary()
    
    print("\n" + "="*60)
    print("🏆 MATCH COMPLETED")
    print("="*60)
    print(f"Final Score: Home {summary['final_score']['home']} - "
          f"{summary['final_score']['away']} Away")
    print(f"Result: {summary['result']}")
    print(f"Duration: {summary['duration_minutes']} minutes")
    print(f"Total Possessions: {summary['total_possessions']}")
    print(f"Total Events: {summary['event_stats']['total_events']}")
    
    # Export logs
    csv_filename = f"{output_dir}/football_match_{timestamp}.csv"
    xes_filename = f"{output_dir}/football_match_{timestamp}.xes"
    
    print(f"\n📊 Exporting match data...")
    model.export_logs(csv_path=csv_filename, xes_path=xes_filename)
    
    # Print detailed statistics
    print(f"\n📈 Match Statistics:")
    event_stats = summary['event_stats']
    print(f"  Expected Goals (xG):")
    print(f"    Home: {event_stats.get('total_xg_home', 0):.2f}")
    print(f"    Away: {event_stats.get('total_xg_away', 0):.2f}")
    
    if 'actions_breakdown' in event_stats:
        print(f"  Action Breakdown:")
        for action, count in sorted(event_stats['actions_breakdown'].items()):
            print(f"    {action:15s}: {count:3d}")
    
    print(f"\n💾 Files exported:")
    print(f"  CSV: {csv_filename}")
    print(f"  XES: {xes_filename}")
    
    # Print sample events for verification
    print(f"\n🔍 Sample Events (first 10):")
    sample_events = model.logger.events[:10]
    for i, event in enumerate(sample_events):
        print(f"  {i+1:2d}. {event['action']:12s} | {event['team']:4s} #{event['player_id']:2d} | "
              f"{event['zone']:2s} | {event['outcome']:7s}")
    
    print(f"\n✅ Simulation completed successfully!")
    return model, summary


def run_multiple_simulations(num_matches: int = 3, match_duration: int = 45, 
                           output_dir: str = "output"):
    """Run multiple football simulations"""
    
    print("="*60)
    print(f"🏈 RUNNING {num_matches} FOOTBALL SIMULATIONS")
    print("="*60)
    
    results = []
    
    for match_num in range(1, num_matches + 1):
        print(f"\n🎯 MATCH {match_num}/{num_matches}")
        print("-" * 40)
        
        # Use different seed for each match
        seed = 1000 + match_num
        
        model, summary = run_simulation(
            match_duration=match_duration,
            seed=seed,
            output_dir=output_dir
        )
        
        results.append({
            'match': match_num,
            'seed': seed,
            'summary': summary
        })
    
    # Print overall statistics
    print(f"\n" + "="*60)
    print(f"📊 OVERALL STATISTICS ({num_matches} matches)")
    print("="*60)
    
    total_goals_home = sum(r['summary']['final_score']['home'] for r in results)
    total_goals_away = sum(r['summary']['final_score']['away'] for r in results)
    total_events = sum(r['summary']['event_stats']['total_events'] for r in results)
    
    print(f"Total Goals: Home {total_goals_home} - {total_goals_away} Away")
    print(f"Total Events Logged: {total_events}")
    print(f"Average Events per Match: {total_events / num_matches:.1f}")
    
    # Results breakdown
    home_wins = sum(1 for r in results if r['summary']['result'] == 'Home Win')
    away_wins = sum(1 for r in results if r['summary']['result'] == 'Away Win')
    draws = sum(1 for r in results if r['summary']['result'] == 'Draw')
    
    print(f"\nResults:")
    print(f"  Home Wins: {home_wins}")
    print(f"  Away Wins: {away_wins}")
    print(f"  Draws: {draws}")
    
    return results


if __name__ == "__main__":
    # Run a single detailed simulation
    print("Running single football simulation...")
    model, summary = run_simulation(match_duration=45, seed=42)
    
    print("\n" + "="*60)
    print("🎮 SIMULATION OPTIONS")
    print("="*60)
    print("1. Run another single match")
    print("2. Run multiple matches (3x 45min)")
    print("3. Run full 90-minute match")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            run_simulation(match_duration=45, seed=None)
        elif choice == "2":
            run_multiple_simulations(num_matches=3, match_duration=45)
        elif choice == "3":
            run_simulation(match_duration=90, seed=None)
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting...")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n🏁 Program finished.")
