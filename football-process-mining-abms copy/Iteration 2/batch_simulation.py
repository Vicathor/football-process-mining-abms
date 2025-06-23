"""
Batch Football Simulation - 30 Games Analysis
Run multiple football matches and perform comprehensive process mining analysis
"""
import os
import pandas as pd
import pm4py
from datetime import datetime, timedelta
from football_model import FootballModel
from process_mining_analysis import FootballProcessMiner
import warnings
warnings.filterwarnings('ignore')

class BatchFootballSimulation:
    """Run multiple football matches for comprehensive process mining analysis"""
    
    def __init__(self, num_games: int = 30, output_dir: str = "batch_outputs"):
        self.num_games = num_games
        self.output_dir = output_dir
        self.analysis_dir = "batch_analysis"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.analysis_dir, exist_ok=True)
        
        # Combined data storage
        self.combined_events = []
        self.match_results = []
        
    def run_single_match(self, match_id: int, seed: int = None) -> dict:
        """Run a single football match and return results"""
        if seed is None:
            seed = 42 + match_id  # Different seed for each match
            
        print(f"🏈 Running Match {match_id + 1}/{self.num_games} (seed: {seed})")
        
        # Create and run match
        model = FootballModel(match_duration_minutes=45, seed=seed)
        
        # Run the match
        step_count = 0
        while model.running and step_count < model.total_steps:
            model.step()
            step_count += 1
        
        # Get match results
        events = model.logger.events.copy()
        
        # Add match identifier to each event
        for event in events:
            event['match_id'] = f"M{match_id + 1:02d}"
            event['match_seed'] = seed
        
        # Calculate match statistics
        home_score = sum(1 for e in events if e.get('action') == 'Goal' and e.get('team') == 'Home')
        away_score = sum(1 for e in events if e.get('action') == 'Goal' and e.get('team') == 'Away')
        
        total_possessions = len(set(e.get('possession_id', '') for e in events if e.get('possession_id')))
        total_events = len(events)
        
        match_result = {
            'match_id': match_id + 1,
            'seed': seed,
            'home_score': home_score,
            'away_score': away_score,
            'total_events': total_events,
            'total_possessions': total_possessions,
            'duration_minutes': 45,
            'result': 'Home Win' if home_score > away_score else 'Away Win' if away_score > home_score else 'Draw'
        }
        
        print(f"   ⚽ Result: {match_result['result']} ({home_score}-{away_score})")
        print(f"   📊 Events: {total_events}, Possessions: {total_possessions}")
        
        return events, match_result
    
    def run_batch_simulation(self):
        """Run all matches in the batch"""
        print("🏆 BATCH FOOTBALL SIMULATION")
        print("=" * 50)
        print(f"Running {self.num_games} matches for comprehensive analysis...")
        print()
        
        start_time = datetime.now()
        
        for match_id in range(self.num_games):
            events, result = self.run_single_match(match_id)
            
            # Add to combined data
            self.combined_events.extend(events)
            self.match_results.append(result)
            
            # Progress update every 5 matches
            if (match_id + 1) % 5 == 0:
                elapsed = datetime.now() - start_time
                avg_time_per_match = elapsed.total_seconds() / (match_id + 1)
                remaining_time = avg_time_per_match * (self.num_games - match_id - 1)
                print(f"   ⏱️  Progress: {match_id + 1}/{self.num_games} matches complete")
                print(f"   🕐 Estimated time remaining: {remaining_time:.1f} seconds")
                print()
        
        total_time = datetime.now() - start_time
        print(f"✅ Batch simulation complete!")
        print(f"⏱️  Total time: {total_time.total_seconds():.1f} seconds")
        print(f"📊 Total events generated: {len(self.combined_events)}")
        print()
        
    def export_combined_data(self):
        """Export combined data from all matches"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export combined events
        if self.combined_events:
            # CSV export
            df = pd.DataFrame(self.combined_events)
            csv_path = f"{self.output_dir}/batch_matches_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            print(f"📄 Combined CSV exported: {csv_path}")
            
            # XES export
            xes_path = f"{self.output_dir}/batch_matches_{timestamp}.xes"
            
            # Prepare for XES export
            df_xes = df.copy()
            df_xes = df_xes.rename(columns={
                'possession_id': 'case:concept:name',
                'action': 'concept:name',
                'timestamp': 'time:timestamp'
            })
            
            # Ensure timestamp is datetime
            if 'time:timestamp' in df_xes.columns:
                df_xes['time:timestamp'] = pd.to_datetime(df_xes['time:timestamp'])
            
            # Convert to event log and export
            try:
                event_log = pm4py.convert_to_event_log(df_xes)
                pm4py.write_xes(event_log, xes_path)
                print(f"📊 Combined XES exported: {xes_path}")
            except Exception as e:
                print(f"⚠️  XES export failed: {e}")
        
        # Export match results
        if self.match_results:
            results_df = pd.DataFrame(self.match_results)
            results_path = f"{self.output_dir}/match_results_{timestamp}.csv"
            results_df.to_csv(results_path, index=False)
            print(f"🏆 Match results exported: {results_path}")
            
            # Print summary statistics
            print(f"\n🏆 BATCH RESULTS SUMMARY")
            print("=" * 30)
            print(f"Total matches: {len(self.match_results)}")
            print(f"Home wins: {sum(1 for r in self.match_results if r['result'] == 'Home Win')}")
            print(f"Away wins: {sum(1 for r in self.match_results if r['result'] == 'Away Win')}")
            print(f"Draws: {sum(1 for r in self.match_results if r['result'] == 'Draw')}")
            print(f"Average events per match: {sum(r['total_events'] for r in self.match_results) / len(self.match_results):.1f}")
            print(f"Average possessions per match: {sum(r['total_possessions'] for r in self.match_results) / len(self.match_results):.1f}")
        
        return csv_path, xes_path
    
    def run_complete_batch_analysis(self):
        """Run complete batch simulation and analysis"""
        print("🚀 STARTING COMPLETE BATCH ANALYSIS")
        print("=" * 60)
        
        # Step 1: Run batch simulation
        self.run_batch_simulation()
        
        # Step 2: Export combined data
        csv_path, xes_path = self.export_combined_data()
        
        # Step 3: Run process mining analysis
        print(f"\n🔬 RUNNING PROCESS MINING ANALYSIS")
        print("=" * 50)
        
        # Create process miner and run batch analysis
        miner = FootballProcessMiner(output_dir=self.output_dir)
        results = miner.run_batch_analysis()
        
        print(f"\n🎉 BATCH ANALYSIS COMPLETE!")
        print("=" * 40)
        print(f"📁 Results saved in: {miner.analysis_dir}/")
        print(f"📊 Combined data: {csv_path}")
        if results:
            print(f"🔬 Process mining results: {results['report_path']}")
            print(f"🎯 Analyzed {results['num_games']} games with {results['stats']['total_events']:,} total events")
        
        return results


def main():
    """Main function to run batch analysis"""
    print("🚀 BATCH FOOTBALL SIMULATION - 30 GAMES")
    print("=" * 60)
    
    # Create batch simulation
    batch_sim = BatchFootballSimulation(num_games=30)
    
    # Run complete analysis
    results = batch_sim.run_complete_batch_analysis()
    
    if results:
        print(f"\n🏆 ANALYSIS COMPLETE!")
        print(f"📊 {results['num_games']} games analyzed")
        print(f"📋 Report: {results['report_path']}")
    else:
        print(f"\n❌ Analysis failed")


if __name__ == "__main__":
    main()
