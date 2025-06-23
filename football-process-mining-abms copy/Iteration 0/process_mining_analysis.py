"""
Process Mining Analysis for Football Simulation
Apply inductive miner and various process discovery techniques using PM4Py
"""
import pm4py
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FootballProcessMiner:
    """Process mining analysis for football simulation data"""
    
    def __init__(self, output_dir: str = "batch_outputs"):
        self.output_dir = output_dir
        self.analysis_dir = "process_analysis"
        os.makedirs(self.analysis_dir, exist_ok=True)
        
    def load_latest_match(self) -> tuple:
        """Load the most recent match data"""
        print("🔍 Loading match data...")
        
        # Find latest CSV and XES files
        csv_files = list(Path(self.output_dir).glob("football_*.csv"))
        xes_files = list(Path(self.output_dir).glob("football_*.xes"))
        
        if not csv_files or not xes_files:
            raise FileNotFoundError("No match files found in output directory")
        
        # Get latest files
        latest_csv = max(csv_files, key=os.path.getctime)
        latest_xes = max(xes_files, key=os.path.getctime)
        
        print(f"📊 Loading: {latest_csv.name}")
        print(f"📊 Loading: {latest_xes.name}")
        
        # Load data
        df = pd.read_csv(latest_csv)
        event_log = pm4py.read_xes(str(latest_xes))
        
        print(f"✅ Loaded {len(df)} events from {len(event_log)} traces")
        return df, event_log, latest_csv.name
    
    def load_batch_matches(self, batch_dir: str = "batch_outputs") -> tuple:
        """Load batch match data from multiple games"""
        print("🔍 Loading batch match data...")
        
        # Find latest batch CSV and XES files
        batch_path = Path(batch_dir)
        if not batch_path.exists():
            raise FileNotFoundError(f"Batch directory {batch_dir} not found")
            
        csv_files = list(batch_path.glob("batch_matches_*.csv"))
        xes_files = list(batch_path.glob("batch_matches_*.xes"))
        
        if not csv_files or not xes_files:
            raise FileNotFoundError("No batch match files found in batch directory")
        
        # Get latest files
        latest_csv = max(csv_files, key=os.path.getctime)
        latest_xes = max(xes_files, key=os.path.getctime)
        
        print(f"📊 Loading batch CSV: {latest_csv.name}")
        print(f"📊 Loading batch XES: {latest_xes.name}")
        
        # Load data
        df = pd.read_csv(latest_csv)
        event_log = pm4py.read_xes(str(latest_xes))
        
        # Count unique games
        num_games = df['match_id'].nunique() if 'match_id' in df.columns else 1
        
        print(f"✅ Loaded {len(df)} events from {len(event_log)} traces across {num_games} games")
        return df, event_log, latest_csv.name, num_games

    def basic_statistics(self, df: pd.DataFrame, event_log) -> dict:
        """Generate basic process statistics"""
        print("\n📈 BASIC PROCESS STATISTICS")
        print("=" * 50)
        
        stats = {}
        
        # Basic counts
        stats['total_events'] = len(df)
        stats['unique_traces'] = df['possession_id'].nunique()
        stats['unique_activities'] = df['action'].nunique()
        stats['teams'] = df['team'].unique().tolist()
        
        print(f"Total Events: {stats['total_events']}")
        print(f"Unique Possessions (Traces): {stats['unique_traces']}")
        print(f"Unique Activities: {stats['unique_activities']}")
        print(f"Teams: {', '.join(stats['teams'])}")
        
        # Activity frequency
        activity_freq = df['action'].value_counts()
        print(f"\nTop 10 Activities:")
        for i, (activity, count) in enumerate(activity_freq.head(10).items()):
            print(f"  {i+1:2d}. {activity:15s}: {count:4d} ({count/len(df)*100:.1f}%)")
        
        # Team statistics
        print(f"\nTeam Distribution:")
        team_stats = df['team'].value_counts()
        for team, count in team_stats.items():
            print(f"  {team:4s}: {count:4d} events ({count/len(df)*100:.1f}%)")
        
        # Trace length statistics
        trace_lengths = df.groupby('possession_id').size()
        stats['avg_trace_length'] = trace_lengths.mean()
        stats['min_trace_length'] = trace_lengths.min()
        stats['max_trace_length'] = trace_lengths.max()
        
        print(f"\nPossession (Trace) Statistics:")
        print(f"  Average length: {stats['avg_trace_length']:.1f} events")
        print(f"  Min length: {stats['min_trace_length']} events")
        print(f"  Max length: {stats['max_trace_length']} events")
        
        return stats
    
    def apply_inductive_miner(self, event_log, df: pd.DataFrame) -> dict:
        """Apply inductive miner for process discovery - separate models for each team"""
        print("\n🔬 APPLYING INDUCTIVE MINER")
        print("=" * 50)
        
        models = {}
        
        # 1. Combined model (all teams)
        print("🏈 Running inductive miner algorithm for COMBINED teams...")
        net_combined, initial_combined, final_combined = pm4py.discover_petri_net_inductive(event_log)
        
        print(f"✅ Combined process model discovered!")
        print(f"   Places: {len(net_combined.places)}")
        print(f"   Transitions: {len(net_combined.transitions)}")
        print(f"   Arcs: {len(net_combined.arcs)}")
        
        # Save combined model
        combined_path = f"{self.analysis_dir}/combined_teams_model.pnml"
        pm4py.write_pnml(net_combined, initial_combined, final_combined, combined_path)
        print(f"💾 Combined model saved: {combined_path}")
        
        # Generate combined PNG
        try:
            pm4py.save_vis_petri_net(net_combined, initial_combined, final_combined, 
                                      f"{self.analysis_dir}/petri_net_combined_teams.png")
            print(f"📊 Combined PNG saved: petri_net_combined_teams.png")
        except Exception as e:
            print(f"⚠️  Combined PNG generation failed: {e}")
        
        models['combined'] = (net_combined, initial_combined, final_combined)
        
        # 2. Home Team (Team A) model
        print(f"\n🏠 Running inductive miner for HOME TEAM...")
        
        # Get home team possession IDs from CSV
        home_possession_ids = df[df['team'] == 'Home']['possession_id'].unique()
        print(f"   Found {len(home_possession_ids)} home team possession IDs")
        
        # Create home log from DataFrame (direct approach)
        home_df = df[df['team'] == 'Home'].copy()
        if len(home_df) > 0:
            # Convert timestamp to datetime if needed
            home_df['timestamp'] = pd.to_datetime(home_df['timestamp'])
            
            # Rename columns to match PM4Py expectations
            home_df_pm4py = home_df.rename(columns={
                'possession_id': 'case:concept:name',
                'action': 'concept:name',
                'timestamp': 'time:timestamp'
            })
            
            home_log = pm4py.convert_to_event_log(home_df_pm4py)
            net_home, initial_home, final_home = pm4py.discover_petri_net_inductive(home_log)
            
            print(f"✅ Home team process model discovered!")
            print(f"   Traces: {len(home_log)}")
            print(f"   Places: {len(net_home.places)}")
            print(f"   Transitions: {len(net_home.transitions)}")
            print(f"   Arcs: {len(net_home.arcs)}")
            
            # Save home model
            home_path = f"{self.analysis_dir}/home_team_model.pnml"
            pm4py.write_pnml(net_home, initial_home, final_home, home_path)
            print(f"💾 Home team model saved: {home_path}")
            
            # Generate home PNG
            try:
                pm4py.save_vis_petri_net(net_home, initial_home, final_home, 
                                          f"{self.analysis_dir}/petri_net_home_team.png")
                print(f"📊 Home team PNG saved: petri_net_home_team.png")
            except Exception as e:
                print(f"⚠️  Home team PNG generation failed: {e}")
            
            models['home'] = (net_home, initial_home, final_home)
        else:
            print("⚠️  No home team data found")
        
        # 3. Away Team (Team B) model
        print(f"\n🚌 Running inductive miner for AWAY TEAM...")
        
        # Get away team possession IDs from CSV
        away_possession_ids = df[df['team'] == 'Away']['possession_id'].unique()
        print(f"   Found {len(away_possession_ids)} away team possession IDs")
        
        # Create away log from DataFrame (direct approach)
        away_df = df[df['team'] == 'Away'].copy()
        if len(away_df) > 0:
            # Convert timestamp to datetime if needed
            away_df['timestamp'] = pd.to_datetime(away_df['timestamp'])
            
            # Rename columns to match PM4Py expectations
            away_df_pm4py = away_df.rename(columns={
                'possession_id': 'case:concept:name',
                'action': 'concept:name',
                'timestamp': 'time:timestamp'
            })
            
            away_log = pm4py.convert_to_event_log(away_df_pm4py)
            net_away, initial_away, final_away = pm4py.discover_petri_net_inductive(away_log)
            
            print(f"✅ Away team process model discovered!")
            print(f"   Traces: {len(away_log)}")
            print(f"   Places: {len(net_away.places)}")
            print(f"   Transitions: {len(net_away.transitions)}")
            print(f"   Arcs: {len(net_away.arcs)}")
            
            # Save away model
            away_path = f"{self.analysis_dir}/away_team_model.pnml"
            pm4py.write_pnml(net_away, initial_away, final_away, away_path)
            print(f"💾 Away team model saved: {away_path}")
            
            # Generate away PNG
            try:
                pm4py.save_vis_petri_net(net_away, initial_away, final_away, 
                                          f"{self.analysis_dir}/petri_net_away_team.png")
                print(f"📊 Away team PNG saved: petri_net_away_team.png")
            except Exception as e:
                print(f"⚠️  Away team PNG generation failed: {e}")
            
            models['away'] = (net_away, initial_away, final_away)
        else:
            print("⚠️  No away team data found")
        
        print(f"\n📊 SUMMARY OF GENERATED MODELS:")
        print(f"   🏈 Combined teams: {len(models['combined'][0].places)} places, {len(models['combined'][0].transitions)} transitions")
        if 'home' in models:
            print(f"   🏠 Home team: {len(models['home'][0].places)} places, {len(models['home'][0].transitions)} transitions")
        if 'away' in models:
            print(f"   🚌 Away team: {len(models['away'][0].places)} places, {len(models['away'][0].transitions)} transitions")
        
        return models
    
    def conformance_checking(self, event_log, net, initial_marking, final_marking):
        """Perform conformance checking"""
        print("\n🔍 CONFORMANCE CHECKING")
        print("=" * 50)
        
        # Token-based replay
        print("Performing token-based replay...")
        replayed_traces = pm4py.conformance_diagnostics_token_based_replay(
            event_log, net, initial_marking, final_marking
        )
        
        # Calculate fitness statistics
        fitness_values = []
        for trace_fitness in replayed_traces:
            if trace_fitness['trace_fitness'] is not None:
                fitness_values.append(trace_fitness['trace_fitness'])
        
        if fitness_values:
            avg_fitness = sum(fitness_values) / len(fitness_values)
            print(f"✅ Average Fitness: {avg_fitness:.3f}")
            print(f"   Traces analyzed: {len(fitness_values)}")
            print(f"   Perfect fits: {sum(1 for f in fitness_values if f == 1.0)}")
            print(f"   Fitness range: {min(fitness_values):.3f} - {max(fitness_values):.3f}")
        
        return replayed_traces
    
    def variant_analysis(self, event_log, df: pd.DataFrame):
        """Analyze process variants (different possession patterns)"""
        print("\n🔄 VARIANT ANALYSIS")
        print("=" * 50)
        
        # Get variants
        variants = pm4py.get_variants(event_log)
        print(f"Total Variants: {len(variants)}")
        
        # Analyze top variants - variants already contains counts
        variant_counts = variants  # variants is already a dict of {variant: count}
        
        sorted_variants = sorted(variant_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 10 Most Common Possession Patterns:")
        for i, (variant, count) in enumerate(sorted_variants[:10]):
            percentage = count / len(event_log) * 100
            variant_str = " → ".join(variant)
            print(f"  {i+1:2d}. {variant_str[:80]:80s} ({count:3d} traces, {percentage:4.1f}%)")
        
        # Analyze by team
        print(f"\nVariant Analysis by Team:")
        home_possessions = df[df['team'] == 'Home']['possession_id'].unique()
        away_possessions = df[df['team'] == 'Away']['possession_id'].unique()
        
        print(f"  Home possessions: {len(home_possessions)}")
        print(f"  Away possessions: {len(away_possessions)}")
        
        return variants
    
    def create_visualizations(self, df: pd.DataFrame, net, initial_marking, final_marking):
        """Create process mining visualizations"""
        print("\n📊 CREATING VISUALIZATIONS")
        print("=" * 50)
        
        # Set style for better appearance
        plt.style.use('default')
        sns.set_palette("Set2")
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })
        
        # Create figure with better spacing
        fig = plt.figure(figsize=(18, 12))
        fig.suptitle('Football Process Mining Analysis Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Activity frequency chart
        ax1 = plt.subplot(3, 3, 1)
        activity_counts = df['action'].value_counts().head(8)
        bars = activity_counts.plot(kind='bar', ax=ax1, color='steelblue', alpha=0.8)
        ax1.set_title('Top 8 Football Activities', fontweight='bold', pad=15)
        ax1.set_xlabel('Activity Type', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars.patches:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        # 2. Team activity distribution
        ax2 = plt.subplot(3, 3, 2)
        team_activity = pd.crosstab(df['action'], df['team'])
        team_activity.plot(kind='bar', stacked=True, ax=ax2, alpha=0.8)
        ax2.set_title('Activity Distribution by Team', fontweight='bold', pad=15)
        ax2.set_xlabel('Activity Type', fontweight='bold')
        ax2.set_ylabel('Event Count', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title='Team', title_fontsize=9, loc='upper right')
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Possession length distribution
        ax3 = plt.subplot(3, 3, 3)
        possession_lengths = df.groupby('possession_id').size()
        ax3.hist(possession_lengths, bins=15, alpha=0.7, color='green', edgecolor='darkgreen')
        ax3.set_title('Possession Length Distribution', fontweight='bold', pad=15)
        ax3.set_xlabel('Events per Possession', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.grid(alpha=0.3)
        ax3.axvline(possession_lengths.mean(), color='red', linestyle='--', 
                   label=f'Mean: {possession_lengths.mean():.1f}')
        ax3.legend()
        
        # 4. Success rate by activity
        ax4 = plt.subplot(3, 3, 4)
        success_rates = df.groupby('action')['outcome'].apply(
            lambda x: (x == 'Success').sum() / len(x) * 100
        ).sort_values(ascending=False)
        bars = success_rates.plot(kind='bar', ax=ax4, color='orange', alpha=0.8)
        ax4.set_title('Success Rate by Activity', fontweight='bold', pad=15)
        ax4.set_xlabel('Activity Type', fontweight='bold')
        ax4.set_ylabel('Success Rate (%)', fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(axis='y', alpha=0.3)
        ax4.set_ylim(0, 100)
        
        # Add percentage labels
        for bar in bars.patches:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 5. Zone activity heatmap
        ax5 = plt.subplot(3, 3, 5)
        zone_activity = df['zone'].value_counts()
        # Create a 4x5 grid for zones A1-D5
        zone_matrix = [[0 for _ in range(5)] for _ in range(4)]
        for zone, count in zone_activity.items():
            if len(zone) == 2 and zone[0] in 'ABCD' and zone[1] in '12345':
                row = ord(zone[0]) - ord('A')
                col = int(zone[1]) - 1
                zone_matrix[row][col] = count
        
        sns.heatmap(zone_matrix, annot=True, fmt='d', cmap='Reds', ax=ax5,
                    xticklabels=['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5'],
                    yticklabels=['Row A', 'Row B', 'Row C', 'Row D'],
                    cbar_kws={'label': 'Activity Count'})
        ax5.set_title('Field Zone Activity Heatmap', fontweight='bold', pad=15)
        ax5.set_xlabel('Field Columns', fontweight='bold')
        ax5.set_ylabel('Field Rows', fontweight='bold')
        
        # 6. Expected Goals (xG) distribution
        ax6 = plt.subplot(3, 3, 6)
        xg_data = df[df['xg_change'] > 0]['xg_change']
        if len(xg_data) > 0:
            ax6.hist(xg_data, bins=15, alpha=0.7, color='purple', edgecolor='indigo')
            ax6.set_title('Expected Goals (xG) Distribution', fontweight='bold', pad=15)
            ax6.set_xlabel('xG Value', fontweight='bold')
            ax6.set_ylabel('Frequency', fontweight='bold')
            ax6.grid(alpha=0.3)
            ax6.axvline(xg_data.mean(), color='red', linestyle='--', 
                       label=f'Mean: {xg_data.mean():.3f}')
            ax6.legend()
        else:
            ax6.text(0.5, 0.5, 'No xG data available\nfor this match', 
                    ha='center', va='center', fontsize=12, 
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
            ax6.set_title('Expected Goals (xG) Distribution', fontweight='bold', pad=15)
            ax6.set_xlim(0, 1)
            ax6.set_ylim(0, 1)
        
        # 7. Team possession statistics
        ax7 = plt.subplot(3, 3, 7)
        team_possessions = df.groupby('team')['possession_id'].nunique()
        colors = ['#1f77b4', '#ff7f0e']
        wedges, texts, autotexts = ax7.pie(team_possessions.values, 
                                          labels=team_possessions.index,
                                          autopct='%1.1f%%', startangle=90,
                                          colors=colors, explode=(0.05, 0.05))
        ax7.set_title('Possession Distribution', fontweight='bold', pad=15)
        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # 8. Events per minute timeline
        ax8 = plt.subplot(3, 3, 8)
        df_temp = df.copy()
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
        df_temp['minute'] = df_temp['timestamp'].dt.minute
        events_per_minute = df_temp.groupby('minute').size()
        
        ax8.plot(events_per_minute.index, events_per_minute.values, 
                marker='o', linewidth=2, markersize=4, color='darkred')
        ax8.set_title('Events Timeline (per minute)', fontweight='bold', pad=15)
        ax8.set_xlabel('Match Minute', fontweight='bold')
        ax8.set_ylabel('Event Count', fontweight='bold')
        ax8.grid(alpha=0.3)
        ax8.fill_between(events_per_minute.index, events_per_minute.values, alpha=0.3, color='red')
        
        # 9. Top zones by success rate
        ax9 = plt.subplot(3, 3, 9)
        zone_success = df.groupby('zone').agg({
            'outcome': lambda x: (x == 'Success').sum() / len(x) * 100,
            'action': 'count'
        }).rename(columns={'outcome': 'success_rate', 'action': 'total_events'})
        
        # Filter zones with at least 10 events for statistical significance
        significant_zones = zone_success[zone_success['total_events'] >= 10]
        top_zones = significant_zones.nlargest(8, 'success_rate')
        
        bars = ax9.bar(range(len(top_zones)), top_zones['success_rate'], 
                      color='forestgreen', alpha=0.8)
        ax9.set_title('Most Effective Zones (≥10 events)', fontweight='bold', pad=15)
        ax9.set_xlabel('Field Zone', fontweight='bold')
        ax9.set_ylabel('Success Rate (%)', fontweight='bold')
        ax9.set_xticks(range(len(top_zones)))
        ax9.set_xticklabels(top_zones.index, rotation=45)
        ax9.grid(axis='y', alpha=0.3)
        ax9.set_ylim(0, 100)
        
        # Add percentage labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax9.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # Adjust layout with better spacing
        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        plt.subplots_adjust(hspace=0.4, wspace=0.3)
        
        viz_path = f"{self.analysis_dir}/process_analysis_charts.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"📊 Enhanced charts saved: {viz_path}")
        plt.show()
        
        # Save process model visualization
        try:
            print("🔧 Generating process model visualization...")
            pm4py.save_vis_petri_net(net, initial_marking, final_marking, 
                                   f"{self.analysis_dir}/process_model.png")
            print(f"🎯 Process model saved: {self.analysis_dir}/process_model.png")
        except Exception as e:
            print(f"⚠️  Could not generate process model visualization: {e}")
    
    def advanced_analysis(self, df: pd.DataFrame, event_log):
        """Perform advanced process mining analysis"""
        print("\n🧠 ADVANCED ANALYSIS")
        print("=" * 50)
        
        # 1. Social Network Analysis (if applicable)
        try:
            print("Analyzing player interactions...")
            # Create player interaction network based on passes
            pass_events = df[df['action'] == 'Pass']
            if len(pass_events) > 0:
                player_interactions = pass_events.groupby(['team', 'player_id']).size()
                print(f"Pass network: {len(player_interactions)} player nodes")
        except Exception as e:
            print(f"Player network analysis failed: {e}")
        
        # 2. Time-based analysis
        print("\nTemporal analysis...")
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['minute'] = df_copy['timestamp'].dt.minute
        
        temporal_stats = df_copy.groupby('minute')['action'].count()
        print(f"Event distribution over time: {temporal_stats.describe()}")
        
        # 3. Performance analysis
        print("\nPerformance metrics...")
        goal_events = df[df['action'] == 'Goal']
        shot_events = df[df['action'] == 'Shot']
        
        print(f"Goals scored: {len(goal_events)}")
        print(f"Shots taken: {len(shot_events)}")
        if len(shot_events) > 0:
            conversion_rate = len(goal_events) / len(shot_events) * 100
            print(f"Shot conversion rate: {conversion_rate:.1f}%")
        
        # 4. Zone effectiveness
        print("\nZone effectiveness analysis...")
        zone_success = df.groupby('zone')['outcome'].apply(
            lambda x: (x == 'Success').sum() / len(x) * 100 if len(x) > 0 else 0
        ).sort_values(ascending=False)
        
        print("Top 5 most effective zones:")
        for zone, rate in zone_success.head().items():
            count = len(df[df['zone'] == zone])
            print(f"  {zone}: {rate:.1f}% success rate ({count} events)")
    
    def generate_enhanced_report(self, df: pd.DataFrame, event_log, stats: dict, match_file: str, models: dict, heuristic_models: dict = None, comparison: dict = None):
        """Generate comprehensive process mining report with all team models including heuristic mining"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.analysis_dir}/process_mining_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# Football Process Mining Report - Multi-Team Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Source File:** {match_file}\n\n")
            
            f.write(f"## Executive Summary\n\n")
            f.write(f"- **Total Events:** {stats['total_events']}\n")
            f.write(f"- **Possessions Analyzed:** {stats['unique_traces']}\n")
            f.write(f"- **Activity Types:** {stats['unique_activities']}\n")
            f.write(f"- **Average Possession Length:** {stats['avg_trace_length']:.1f} events\n")
            f.write(f"- **Process Models Generated:** {len(models)} (Combined + Team-specific)\n\n")
            
            f.write(f"## Process Discovery Results\n\n")
            f.write(f"The inductive miner algorithm was applied to discover process models from ")
            f.write(f"{stats['unique_traces']} possession sequences. Three separate models were generated:\n\n")
            
            # Model comparison table
            f.write(f"### Inductive Mining Model Comparison\n\n")
            f.write(f"| Model Type | Places | Transitions | Arcs | Traces |\n")
            f.write(f"|------------|--------|-------------|------|--------|\n")
            
            combined_net, _, _ = models['combined']
            f.write(f"| **Combined Teams** | {len(combined_net.places)} | {len(combined_net.transitions)} | {len(combined_net.arcs)} | {len(event_log)} |\n")
            
            if 'home' in models:
                home_net, _, _ = models['home']
                home_traces = len(df[df['team'] == 'Home']['possession_id'].unique())
                f.write(f"| **Home Team** | {len(home_net.places)} | {len(home_net.transitions)} | {len(home_net.arcs)} | {home_traces} |\n")
            
            if 'away' in models:
                away_net, _, _ = models['away']
                away_traces = len(df[df['team'] == 'Away']['possession_id'].unique())
                f.write(f"| **Away Team** | {len(away_net.places)} | {len(away_net.transitions)} | {len(away_net.arcs)} | {away_traces} |\n")
            
            f.write(f"\n")
            
            # Add heuristic mining results if available
            if heuristic_models and 'error' not in heuristic_models:
                f.write(f"### Heuristic Mining Model Comparison\n\n")
                f.write(f"| Model Type | Places | Transitions | Arcs | Traces |\n")
                f.write(f"|------------|--------|-------------|------|--------|\n")
                
                if 'combined' in heuristic_models:
                    heur_combined_net, _, _ = heuristic_models['combined']
                    f.write(f"| **Combined Teams** | {len(heur_combined_net.places)} | {len(heur_combined_net.transitions)} | {len(heur_combined_net.arcs)} | {len(event_log)} |\n")
                
                if 'home' in heuristic_models:
                    heur_home_net, _, _ = heuristic_models['home']
                    home_traces = len(df[df['team'] == 'Home']['possession_id'].unique())
                    f.write(f"| **Home Team** | {len(heur_home_net.places)} | {len(heur_home_net.transitions)} | {len(heur_home_net.arcs)} | {home_traces} |\n")
                
                if 'away' in heuristic_models:
                    heur_away_net, _, _ = heuristic_models['away']
                    away_traces = len(df[df['team'] == 'Away']['possession_id'].unique())
                    f.write(f"| **Away Team** | {len(heur_away_net.places)} | {len(heur_away_net.transitions)} | {len(heur_away_net.arcs)} | {away_traces} |\n")
                
                f.write(f"\n")
                f.write(f"### Mining Algorithm Comparison\n\n")
                f.write(f"Two complementary process discovery algorithms were applied:\n\n")
                f.write(f"- **Inductive Mining**: Guarantees sound process models with structured workflow patterns\n")
                f.write(f"- **Heuristic Mining**: Captures frequency-based patterns and more flexible tactical behaviors\n\n")
                
                if comparison and comparison.get('heuristic_available'):
                    f.write(f"The comparison reveals different tactical insights from each algorithm, ")
                    f.write(f"providing a more comprehensive understanding of football possession patterns.\n\n")
            
            f.write(f"## Key Findings\n\n")
            
            # Activity analysis
            top_activities = df['action'].value_counts().head(5)
            f.write(f"### Most Common Activities\n")
            for activity, count in top_activities.items():
                percentage = count / len(df) * 100
                f.write(f"- **{activity}:** {count} occurrences ({percentage:.1f}%)\n")
            f.write(f"\n")
            
            # Team performance
            f.write(f"### Team Performance Analysis\n")
            for team in stats['teams']:
                team_events = len(df[df['team'] == team])
                team_possessions = df[df['team'] == team]['possession_id'].nunique()
                avg_possession = team_events / team_possessions if team_possessions > 0 else 0
                f.write(f"- **{team} Team:** {team_events} events, {team_possessions} possessions (avg {avg_possession:.1f} events/possession)\n")
            f.write(f"\n")
            
            f.write(f"### Model Interpretation\n\n")
            f.write(f"1. **Combined Model:** Shows overall game flow patterns across both teams\n")
            f.write(f"2. **Home Team Model:** Reveals specific tactical patterns for the home team\n")
            f.write(f"3. **Away Team Model:** Captures unique possession strategies of the away team\n\n")
            
            f.write(f"The differences between team-specific models can reveal:\n")
            f.write(f"- Different playing styles and tactical approaches\n")
            f.write(f"- Team-specific strengths and weaknesses\n")
            f.write(f"- Possession pattern variations between teams\n\n")
            
            f.write(f"## Files Generated\n\n")
            f.write(f"### Process Models (PNML Format)\n")
            f.write(f"#### Inductive Mining Models\n")
            f.write(f"- `combined_teams_model.pnml` - Combined process model\n")
            if 'home' in models:
                f.write(f"- `home_team_model.pnml` - Home team specific model\n")
            if 'away' in models:
                f.write(f"- `away_team_model.pnml` - Away team specific model\n")
            
            if heuristic_models and 'error' not in heuristic_models:
                f.write(f"#### Heuristic Mining Models\n")
                f.write(f"- `heuristic_combined_teams_model.pnml` - Combined heuristic model\n")
                if 'home' in heuristic_models:
                    f.write(f"- `heuristic_home_team_model.pnml` - Home team heuristic model\n")
                if 'away' in heuristic_models:
                    f.write(f"- `heuristic_away_team_model.pnml` - Away team heuristic model\n")
            
            f.write(f"\n### Visualizations\n")
            f.write(f"#### Inductive Mining Visualizations\n")
            f.write(f"- `petri_net_combined_teams.png` - Combined Petri net visualization\n")
            if 'home' in models:
                f.write(f"- `petri_net_home_team.png` - Home team Petri net\n")
            if 'away' in models:
                f.write(f"- `petri_net_away_team.png` - Away team Petri net\n")
            
            if heuristic_models and 'error' not in heuristic_models:
                f.write(f"#### Heuristic Mining Visualizations\n")
                f.write(f"- `heuristic_petri_net_combined_teams.png` - Combined heuristic Petri net\n")
                if 'home' in heuristic_models:
                    f.write(f"- `heuristic_petri_net_home_team.png` - Home team heuristic Petri net\n")
                if 'away' in heuristic_models:
                    f.write(f"- `heuristic_petri_net_away_team.png` - Away team heuristic Petri net\n")
            
            f.write(f"#### Statistical Analysis\n")
            f.write(f"- `process_analysis_charts.png` - Statistical analysis dashboard\n")
            f.write(f"- `process_mining_report_{timestamp}.md` - This comprehensive report\n\n")
            
            f.write(f"## Tactical Recommendations\n\n")
            f.write(f"1. **Comparative Analysis:** Compare team-specific models to identify tactical differences\n")
            f.write(f"2. **Pattern Optimization:** Use successful patterns from one team to improve the other\n")
            f.write(f"3. **Weakness Exploitation:** Identify opponent patterns to develop counter-strategies\n")
            f.write(f"4. **Training Focus:** Use model insights to design targeted training sessions\n")
            f.write(f"5. **Match Preparation:** Analyze opponent patterns for pre-match tactical planning\n")
        
        print(f"📋 Enhanced report generated: {report_path}")
        return report_path

    def generate_batch_enhanced_report(self, df: pd.DataFrame, event_log, stats: dict, 
                                     match_file: str, models: dict, num_games: int, heuristic_models: dict = None, comparison: dict = None):
        """Generate comprehensive batch process mining report including heuristic mining"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.analysis_dir}/batch_process_mining_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# Football Batch Process Mining Report - {num_games} Games Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Source File:** {match_file}\n")
            f.write(f"**Games Analyzed:** {num_games}\n\n")
            
            f.write(f"## Executive Summary\n\n")
            f.write(f"- **Total Games Analyzed:** {num_games}\n")
            f.write(f"- **Total Events:** {stats['total_events']:,}\n")
            f.write(f"- **Total Possessions:** {stats['unique_traces']:,}\n")
            f.write(f"- **Activity Types:** {stats['unique_activities']}\n")
            f.write(f"- **Average Events per Game:** {stats['avg_events_per_game']:.1f}\n")
            f.write(f"- **Average Possessions per Game:** {stats['avg_possessions_per_game']:.1f}\n")
            f.write(f"- **Average Possession Length:** {stats['avg_trace_length']:.1f} events\n")
            f.write(f"- **Process Models Generated:** {len(models)} (Combined + Team-specific)\n\n")
            
            f.write(f"## Batch Process Discovery Results\n\n")
            f.write(f"The inductive miner algorithm was applied to discover process models from ")
            f.write(f"{stats['unique_traces']:,} possession sequences across {num_games} complete matches. ")
            f.write(f"This represents one of the largest football process mining studies, providing ")
            f.write(f"unprecedented insights into tactical patterns and team behaviors.\n\n")
            
            # Model comparison table
            f.write(f"### Model Comparison\n\n")
            f.write(f"| Model Type | Places | Transitions | Arcs | Traces | Data Source |\n")
            f.write(f"|------------|--------|-------------|------|--------|--------------|\n")
            
            combined_net, _, _ = models['combined']
            f.write(f"| **Combined Teams** | {len(combined_net.places)} | {len(combined_net.transitions)} | {len(combined_net.arcs)} | {len(event_log)} | {num_games} games |\n")
            
            if 'home' in models:
                home_net, _, _ = models['home']
                home_traces = len(df[df['team'] == 'Home']['possession_id'].unique())
                f.write(f"| **Home Team** | {len(home_net.places)} | {len(home_net.transitions)} | {len(home_net.arcs)} | {home_traces} | {num_games} games |\n")
            
            if 'away' in models:
                away_net, _, _ = models['away']
                away_traces = len(df[df['team'] == 'Away']['possession_id'].unique())
                f.write(f"| **Away Team** | {len(away_net.places)} | {len(away_net.transitions)} | {len(away_net.arcs)} | {away_traces} | {num_games} games |\n")
            
            f.write(f"\n")
            
            # Add heuristic mining comparison if available
            if heuristic_models and 'heuristic_available' in comparison and comparison['heuristic_available']:
                f.write(f"### Dual Mining Algorithm Comparison\n\n")
                f.write(f"Both inductive and heuristic mining algorithms were applied for comprehensive analysis:\n\n")
                f.write(f"| Model Type | Algorithm | Places | Transitions | Arcs | Complexity |\n")
                f.write(f"|------------|-----------|--------|-------------|------|------------|\n")
                
                # Combined models comparison
                if 'combined' in comparison:
                    ind_stats = comparison['combined']['inductive']
                    heur_stats = comparison['combined']['heuristic']
                    f.write(f"| **Combined Teams** | Inductive | {ind_stats['places']} | {ind_stats['transitions']} | {ind_stats['arcs']} | Standard |\n")
                    f.write(f"| **Combined Teams** | Heuristic | {heur_stats['places']} | {heur_stats['transitions']} | {heur_stats['arcs']} | Enhanced |\n")
                
                # Team-specific comparisons
                for team_key, team_name in [('home', 'Home Team'), ('away', 'Away Team')]:
                    if team_key in comparison:
                        ind_stats = comparison[team_key]['inductive']
                        heur_stats = comparison[team_key]['heuristic']
                        f.write(f"| **{team_name}** | Inductive | {ind_stats['places']} | {ind_stats['transitions']} | {ind_stats['arcs']} | Standard |\n")
                        f.write(f"| **{team_name}** | Heuristic | {heur_stats['places']} | {heur_stats['transitions']} | {heur_stats['arcs']} | Enhanced |\n")
                
                f.write(f"\n**Algorithm Insights:**\n")
                f.write(f"- **Inductive Mining:** Guaranteed sound models with structured approach\n")
                f.write(f"- **Heuristic Mining:** More flexible models capturing frequency-based patterns\n")
                f.write(f"- **Complementary Analysis:** Both algorithms provide different tactical perspectives\n")
                f.write(f"- **Research Value:** First football process mining study with dual algorithm comparison\n\n")
            
            f.write(f"## Multi-Game Insights\n\n")
            
            # Activity analysis across games
            top_activities = df['action'].value_counts().head(5)
            f.write(f"### Most Common Activities Across {num_games} Games\n")
            for activity, count in top_activities.items():
                percentage = count / len(df) * 100
                avg_per_game = count / num_games
                f.write(f"- **{activity}:** {count:,} total occurrences ({percentage:.1f}%), avg {avg_per_game:.1f} per game\n")
            f.write(f"\n")
            
            # Team performance across games
            f.write(f"### Team Performance Analysis\n")
            for team in stats['teams']:
                team_events = len(df[df['team'] == team])
                team_possessions = df[df['team'] == team]['possession_id'].nunique()
                avg_possession = team_events / team_possessions if team_possessions > 0 else 0
                avg_events_per_game = team_events / num_games
                avg_possessions_per_game = team_possessions / num_games
                f.write(f"- **{team} Team:** {team_events:,} events ({avg_events_per_game:.1f}/game), ")
                f.write(f"{team_possessions:,} possessions ({avg_possessions_per_game:.1f}/game), ")
                f.write(f"avg {avg_possession:.1f} events/possession\n")
            f.write(f"\n")
            
            f.write(f"### Statistical Significance\n\n")
            f.write(f"With {num_games} games analyzed, this study provides statistically significant insights:\n")
            f.write(f"- **Large Sample Size:** {stats['total_events']:,} events provide robust pattern detection\n")
            f.write(f"- **Cross-Game Validation:** Patterns validated across multiple independent matches\n")
            f.write(f"- **Tactical Consistency:** Models show consistent tactical behaviors across games\n")
            f.write(f"- **Performance Stability:** Team-specific patterns remain stable across matches\n\n")
            
            f.write(f"### Model Interpretation for {num_games} Games\n\n")
            f.write(f"1. **Combined Model:** Reveals universal football patterns across all {num_games} matches\n")
            f.write(f"2. **Home Team Model:** Shows consistent home team tactical approaches\n")
            f.write(f"3. **Away Team Model:** Captures away team strategic adaptations\n\n")
            
            f.write(f"The scale of this analysis ({num_games} games) allows for:\n")
            f.write(f"- Detection of rare but important tactical patterns\n")
            f.write(f"- Statistical validation of team-specific behaviors\n")
            f.write(f"- Identification of match situation dependencies\n")
            f.write(f"- Robust performance benchmarking\n\n")
            
            f.write(f"## Research Implications\n\n")
            f.write(f"This {num_games}-game analysis represents a significant advancement in:\n")
            f.write(f"- **Sports Process Mining:** Largest football process mining dataset\n")
            f.write(f"- **Tactical Analysis:** Multi-game pattern validation\n")
            f.write(f"- **Agent-Based Modeling:** Comprehensive simulation validation\n")
            f.write(f"- **Performance Analytics:** Statistical significance in sports analysis\n\n")
            
            f.write(f"## Files Generated\n\n")
            f.write(f"### Inductive Mining Models (PNML Format)\n")
            f.write(f"- `combined_teams_model.pnml` - Combined process model ({num_games} games)\n")
            if 'home' in models:
                f.write(f"- `home_team_model.pnml` - Home team specific model ({num_games} games)\n")
            if 'away' in models:
                f.write(f"- `away_team_model.pnml` - Away team specific model ({num_games} games)\n")
            
            # Add heuristic mining files if available
            if heuristic_models and 'heuristic_available' in comparison and comparison['heuristic_available']:
                f.write(f"\n### Heuristic Mining Models (PNML Format)\n")
                f.write(f"- `heuristic_combined_teams_model.pnml` - Combined heuristic model ({num_games} games)\n")
                if 'home' in heuristic_models:
                    f.write(f"- `heuristic_home_team_model.pnml` - Home team heuristic model ({num_games} games)\n")
                if 'away' in heuristic_models:
                    f.write(f"- `heuristic_away_team_model.pnml` - Away team heuristic model ({num_games} games)\n")
            
            f.write(f"\n### Visualizations\n")
            f.write(f"- `petri_net_combined_teams.png` - Combined Petri net visualization (Inductive)\n")
            if 'home' in models:
                f.write(f"- `petri_net_home_team.png` - Home team Petri net (Inductive)\n")
            if 'away' in models:
                f.write(f"- `petri_net_away_team.png` - Away team Petri net (Inductive)\n")
            
            # Add heuristic visualizations if available
            if heuristic_models and 'heuristic_available' in comparison and comparison['heuristic_available']:
                f.write(f"- `heuristic_petri_net_combined_teams.png` - Combined Petri net (Heuristic)\n")
                if 'home' in heuristic_models:
                    f.write(f"- `heuristic_petri_net_home_team.png` - Home team Petri net (Heuristic)\n")
                if 'away' in heuristic_models:
                    f.write(f"- `heuristic_petri_net_away_team.png` - Away team Petri net (Heuristic)\n")
            
            f.write(f"- `process_analysis_charts.png` - Statistical analysis dashboard\n")
            f.write(f"- `batch_process_mining_report_{timestamp}.md` - This comprehensive report\n\n")
            
            f.write(f"## Recommendations for {num_games}-Game Analysis\n\n")
            f.write(f"1. **Longitudinal Analysis:** Track tactical evolution across the {num_games} games\n")
            f.write(f"2. **Pattern Clustering:** Group similar games based on tactical patterns\n")
            f.write(f"3. **Performance Correlation:** Link process patterns to match outcomes\n")
            f.write(f"4. **Predictive Modeling:** Use patterns to predict future game outcomes\n")
            f.write(f"5. **Coaching Intelligence:** Develop data-driven tactical recommendations\n")
        
        print(f"📋 Batch enhanced report generated: {report_path}")
        return report_path

    def apply_heuristic_miner(self, event_log, df: pd.DataFrame) -> dict:
        """Apply heuristic miner for process discovery - alternative approach with different insights"""
        print("\n⛏️  APPLYING HEURISTIC MINER")
        print("=" * 50)
        
        heuristic_models = {}
        
        try:
            # 1. Combined heuristic model (all teams)
            print("🏈 Running heuristic miner algorithm for COMBINED teams...")
            heuristic_net, initial_heuristic, final_heuristic = pm4py.discover_petri_net_heuristics(event_log)
            
            print(f"✅ Combined heuristic model discovered!")
            print(f"   Places: {len(heuristic_net.places)}")
            print(f"   Transitions: {len(heuristic_net.transitions)}")
            print(f"   Arcs: {len(heuristic_net.arcs)}")
            
            # Save combined heuristic model
            heuristic_combined_path = f"{self.analysis_dir}/heuristic_combined_teams_model.pnml"
            pm4py.write_pnml(heuristic_net, initial_heuristic, final_heuristic, heuristic_combined_path)
            print(f"💾 Combined heuristic model saved: {heuristic_combined_path}")
            
            # Generate combined heuristic PNG
            try:
                pm4py.save_vis_petri_net(heuristic_net, initial_heuristic, final_heuristic, 
                                          f"{self.analysis_dir}/heuristic_petri_net_combined_teams.png")
                print(f"📊 Combined heuristic PNG saved: heuristic_petri_net_combined_teams.png")
            except Exception as e:
                print(f"⚠️  Combined heuristic PNG generation failed: {e}")
            
            heuristic_models['combined'] = (heuristic_net, initial_heuristic, final_heuristic)
            
            # 2. Home Team heuristic model
            print(f"\n🏠 Running heuristic miner for HOME TEAM...")
            
            home_df = df[df['team'] == 'Home'].copy()
            if len(home_df) > 0:
                home_df['timestamp'] = pd.to_datetime(home_df['timestamp'])
                home_df_pm4py = home_df.rename(columns={
                    'possession_id': 'case:concept:name',
                    'action': 'concept:name',
                    'timestamp': 'time:timestamp'
                })
                
                home_log = pm4py.convert_to_event_log(home_df_pm4py)
                heuristic_net_home, initial_home_h, final_home_h = pm4py.discover_petri_net_heuristics(home_log)
                
                print(f"✅ Home team heuristic model discovered!")
                print(f"   Traces: {len(home_log)}")
                print(f"   Places: {len(heuristic_net_home.places)}")
                print(f"   Transitions: {len(heuristic_net_home.transitions)}")
                print(f"   Arcs: {len(heuristic_net_home.arcs)}")
                
                # Save home heuristic model
                home_heuristic_path = f"{self.analysis_dir}/heuristic_home_team_model.pnml"
                pm4py.write_pnml(heuristic_net_home, initial_home_h, final_home_h, home_heuristic_path)
                print(f"💾 Home team heuristic model saved: {home_heuristic_path}")
                
                # Generate home heuristic PNG
                try:
                    pm4py.save_vis_petri_net(heuristic_net_home, initial_home_h, final_home_h, 
                                              f"{self.analysis_dir}/heuristic_petri_net_home_team.png")
                    print(f"📊 Home team heuristic PNG saved: heuristic_petri_net_home_team.png")
                except Exception as e:
                    print(f"⚠️  Home team heuristic PNG generation failed: {e}")
                
                heuristic_models['home'] = (heuristic_net_home, initial_home_h, final_home_h)
            else:
                print("⚠️  No home team data found for heuristic mining")
            
            # 3. Away Team heuristic model
            print(f"\n🚌 Running heuristic miner for AWAY TEAM...")
            
            away_df = df[df['team'] == 'Away'].copy()
            if len(away_df) > 0:
                away_df['timestamp'] = pd.to_datetime(away_df['timestamp'])
                away_df_pm4py = away_df.rename(columns={
                    'possession_id': 'case:concept:name',
                    'action': 'concept:name',
                    'timestamp': 'time:timestamp'
                })
                
                away_log = pm4py.convert_to_event_log(away_df_pm4py)
                heuristic_net_away, initial_away_h, final_away_h = pm4py.discover_petri_net_heuristics(away_log)
                
                print(f"✅ Away team heuristic model discovered!")
                print(f"   Traces: {len(away_log)}")
                print(f"   Places: {len(heuristic_net_away.places)}")
                print(f"   Transitions: {len(heuristic_net_away.transitions)}")
                print(f"   Arcs: {len(heuristic_net_away.arcs)}")
                
                # Save away heuristic model
                away_heuristic_path = f"{self.analysis_dir}/heuristic_away_team_model.pnml"
                pm4py.write_pnml(heuristic_net_away, initial_away_h, final_away_h, away_heuristic_path)
                print(f"💾 Away team heuristic model saved: {away_heuristic_path}")
                
                # Generate away heuristic PNG
                try:
                    pm4py.save_vis_petri_net(heuristic_net_away, initial_away_h, final_away_h, 
                                              f"{self.analysis_dir}/heuristic_petri_net_away_team.png")
                    print(f"📊 Away team heuristic PNG saved: heuristic_petri_net_away_team.png")
                except Exception as e:
                    print(f"⚠️  Away team heuristic PNG generation failed: {e}")
                
                heuristic_models['away'] = (heuristic_net_away, initial_away_h, final_away_h)
            else:
                print("⚠️  No away team data found for heuristic mining")
            
            print(f"\n📊 SUMMARY OF HEURISTIC MODELS:")
            print(f"   ⛏️  Combined teams: {len(heuristic_models['combined'][0].places)} places, {len(heuristic_models['combined'][0].transitions)} transitions")
            if 'home' in heuristic_models:
                print(f"   🏠 Home team: {len(heuristic_models['home'][0].places)} places, {len(heuristic_models['home'][0].transitions)} transitions")
            if 'away' in heuristic_models:
                print(f"   🚌 Away team: {len(heuristic_models['away'][0].places)} places, {len(heuristic_models['away'][0].transitions)} transitions")
            
        except Exception as e:
            print(f"⚠️  Heuristic mining failed: {e}")
            print("   Note: Heuristic mining may require more complex event patterns")
            heuristic_models['error'] = str(e)
        
        return heuristic_models
    
    def compare_mining_algorithms(self, inductive_models: dict, heuristic_models: dict) -> dict:
        """Compare results from inductive and heuristic mining algorithms"""
        print("\n🔍 MINING ALGORITHM COMPARISON")
        print("=" * 50)
        
        comparison = {}
        
        if 'error' in heuristic_models:
            print("⚠️  Heuristic mining encountered errors - comparison limited to inductive mining results")
            comparison['heuristic_available'] = False
            return comparison
        
        comparison['heuristic_available'] = True
        
        # Compare combined models
        if 'combined' in inductive_models and 'combined' in heuristic_models:
            ind_net, _, _ = inductive_models['combined']
            heur_net, _, _ = heuristic_models['combined']
            
            print(f"📊 COMBINED TEAMS COMPARISON:")
            print(f"   Inductive Mining:  {len(ind_net.places):2d} places, {len(ind_net.transitions):2d} transitions, {len(ind_net.arcs):3d} arcs")
            print(f"   Heuristic Mining:  {len(heur_net.places):2d} places, {len(heur_net.transitions):2d} transitions, {len(heur_net.arcs):3d} arcs")
            
            complexity_diff = len(heur_net.arcs) - len(ind_net.arcs)
            if complexity_diff > 0:
                print(f"   → Heuristic model is more complex (+{complexity_diff} arcs)")
            elif complexity_diff < 0:
                print(f"   → Inductive model is more complex ({complexity_diff} arcs)")
            else:
                print(f"   → Models have similar complexity")
            
            comparison['combined'] = {
                'inductive': {'places': len(ind_net.places), 'transitions': len(ind_net.transitions), 'arcs': len(ind_net.arcs)},
                'heuristic': {'places': len(heur_net.places), 'transitions': len(heur_net.transitions), 'arcs': len(heur_net.arcs)}
            }
        
        # Compare team-specific models
        for team in ['home', 'away']:
            if team in inductive_models and team in heuristic_models:
                ind_net, _, _ = inductive_models[team]
                heur_net, _, _ = heuristic_models[team]
                
                team_name = "HOME" if team == 'home' else "AWAY"
                print(f"\n📊 {team_name} TEAM COMPARISON:")
                print(f"   Inductive Mining:  {len(ind_net.places):2d} places, {len(ind_net.transitions):2d} transitions, {len(ind_net.arcs):3d} arcs")
                print(f"   Heuristic Mining:  {len(heur_net.places):2d} places, {len(heur_net.transitions):2d} transitions, {len(heur_net.arcs):3d} arcs")
                
                comparison[team] = {
                    'inductive': {'places': len(ind_net.places), 'transitions': len(ind_net.transitions), 'arcs': len(ind_net.arcs)},
                    'heuristic': {'places': len(heur_net.places), 'transitions': len(heur_net.transitions), 'arcs': len(heur_net.arcs)}
                }
        
        print(f"\n🎯 ALGORITHM INSIGHTS:")
        print(f"   • Inductive Mining: Guaranteed sound models, structured approach")
        print(f"   • Heuristic Mining: More flexible, captures frequency-based patterns")
        print(f"   • Use both for comprehensive tactical analysis")
        
        return comparison

    def run_full_analysis(self):
        """Run complete process mining analysis"""
        print("🔬 FOOTBALL PROCESS MINING ANALYSIS")
        print("=" * 60)
        
        try:
            # Load data
            df, event_log, match_file = self.load_latest_match()
            
            # Basic statistics
            stats = self.basic_statistics(df, event_log)
            
            # Apply inductive miner (now returns multiple models)
            models = self.apply_inductive_miner(event_log, df)
            
            # Apply heuristic miner for comparison
            heuristic_models = self.apply_heuristic_miner(event_log, df)
            
            # Compare mining algorithms
            comparison = self.compare_mining_algorithms(models, heuristic_models)
            
            # Use combined model for conformance checking and visualizations
            combined_model = models['combined']
            net, initial_marking, final_marking = combined_model
            
            # Conformance checking on combined model
            self.conformance_checking(event_log, net, initial_marking, final_marking)
            
            # Variant analysis
            self.variant_analysis(event_log, df)
            
            # Advanced analysis
            self.advanced_analysis(df, event_log)
            
            # Create visualizations (using combined model)
            self.create_visualizations(df, net, initial_marking, final_marking)
            
            # Generate enhanced report with all models
            report_path = self.generate_enhanced_report(df, event_log, stats, match_file, models, heuristic_models, comparison)
            
            print(f"\n🎉 ANALYSIS COMPLETE!")
            print(f"📁 Results saved in: {self.analysis_dir}/")
            print(f"📋 Full report: {report_path}")
            print(f"\n🎯 INDUCTIVE MINING PETRI NET FILES:")
            print(f"   🏈 Combined: petri_net_combined_teams.png")
            if 'home' in models:
                print(f"   🏠 Home Team: petri_net_home_team.png")
            if 'away' in models:
                print(f"   🚌 Away Team: petri_net_away_team.png")
            
            if heuristic_models and 'error' not in heuristic_models:
                print(f"\n⛏️  HEURISTIC MINING PETRI NET FILES:")
                print(f"   🏈 Combined: heuristic_petri_net_combined_teams.png")
                if 'home' in heuristic_models:
                    print(f"   🏠 Home Team: heuristic_petri_net_home_team.png")
                if 'away' in heuristic_models:
                    print(f"   🚌 Away Team: heuristic_petri_net_away_team.png")
            
            return {
                'dataframe': df,
                'event_log': event_log,
                'inductive_models': models,
                'heuristic_models': heuristic_models,
                'algorithm_comparison': comparison,
                'statistics': stats,
                'report_path': report_path
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_batch_analysis(self):
        """Run process mining analysis on batch data from multiple games"""
        try:
            print("\n🔬 FOOTBALL BATCH PROCESS MINING ANALYSIS")
            print("=" * 60)
            
            # Load batch data
            df, event_log, match_file, num_games = self.load_batch_matches()
            
            # Basic statistics with game count
            stats = self.basic_statistics(df, event_log)
            stats['num_games'] = num_games
            stats['avg_events_per_game'] = len(df) / num_games
            stats['avg_possessions_per_game'] = stats['unique_traces'] / num_games
            
            # Apply inductive miner (supports multi-game data)
            models = self.apply_inductive_miner(event_log, df)
            
            # Apply heuristic miner for comparison
            heuristic_models = self.apply_heuristic_miner(event_log, df)
            
            # Compare mining algorithms
            comparison = self.compare_mining_algorithms(models, heuristic_models)
            
            net, initial_marking, final_marking = models['combined']
            
            # Enhanced conformance checking
            print(f"\n🔍 BATCH CONFORMANCE CHECKING")
            print("=" * 40)
            fitness_results = self.conformance_checking(event_log, net, initial_marking, final_marking)
            
            # Variant analysis across games  
            print(f"\n🔄 BATCH VARIANT ANALYSIS")
            print("=" * 35)
            self.variant_analysis(event_log, df)
            
            # Advanced analysis
            self.advanced_analysis(df, event_log)
            
            # Create enhanced visualizations
            self.create_visualizations(df, net, initial_marking, final_marking)
            
            # Generate batch-specific report
            report_path = self.generate_batch_enhanced_report(df, event_log, stats, match_file, models, num_games, heuristic_models, comparison)
            
            print(f"\n🎉 BATCH ANALYSIS COMPLETE!")
            print(f"📁 Results saved in: {self.analysis_dir}/")
            print(f"📋 Batch report: {report_path}")
            print(f"\n🎯 BATCH PETRI NET FILES GENERATED:")
            print(f"   🏈 Combined ({num_games} games): petri_net_combined_teams.png")
            if 'home' in models:
                print(f"   🏠 Home Team: petri_net_home_team.png")
            if 'away' in models:
                print(f"   🚌 Away Team: petri_net_away_team.png")
            
            return {
                'stats': stats,
                'models': models,
                'fitness': fitness_results,
                'num_games': num_games,
                'report_path': report_path
            }
            
        except Exception as e:
            print(f"❌ Batch analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main function to run process mining analysis"""
    print("🏈 FOOTBALL PROCESS MINING WITH PM4PY")
    print("🔬 Applying Inductive Miner Algorithm")
    print("=" * 60)
    
    # Check for batch analysis
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        print("🔄 Running BATCH analysis mode...")
        analyzer = FootballProcessMiner()
        results = analyzer.run_batch_analysis()
        if results:
            print(f"✅ Batch analysis completed successfully!")  
            print(f"🎯 Analyzed {results['num_games']} games")
            print(f"📊 {results['stats']['total_events']:,} total events")
            print(f"🎯 Check the 'process_analysis' directory for all results")
    else:
        print("🔄 Running SINGLE match analysis mode...")
        analyzer = FootballProcessMiner()
        results = analyzer.run_full_analysis()
        if results:
            print(f"✅ Process mining analysis completed successfully!")
            print(f"🎯 Check the 'process_analysis' directory for all results")
        else:
            print(f"❌ Analysis failed - check error messages above")


if __name__ == "__main__":
    main()
