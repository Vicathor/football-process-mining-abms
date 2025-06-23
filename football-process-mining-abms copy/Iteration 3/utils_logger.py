"""
Event Logger for Football Simulation
Handles CSV and XES export for process mining analysis
"""
import pandas as pd
import pm4py
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any
import os


class EventLogger:
    """Event logger for football simulation with CSV and XES export capabilities"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.possession_counter = 0
        
    def generate_possession_id(self, team: str, match_id: str = "M01") -> str:
        """Generate a unique possession ID"""
        self.possession_counter += 1
        return f"{match_id}-{team[0]}{self.possession_counter:03d}"
    
    def add(self, event_dict: Dict[str, Any]) -> None:
        """Add an event to the buffer"""
        # Ensure timestamp is in ISO format
        if 'timestamp' not in event_dict:
            event_dict['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Validate required fields
        required_fields = ['possession_id', 'timestamp', 'team', 'player_id', 
                          'action', 'zone', 'pressure', 'team_status', 'outcome']
        for field in required_fields:
            if field not in event_dict:
                event_dict[field] = None
                
        # Add xg_change if not present
        if 'xg_change' not in event_dict:
            event_dict['xg_change'] = 0.0
            
        self.events.append(event_dict.copy())
    
    def dump_csv(self, path: str) -> None:
        """Export events to CSV file"""
        if not self.events:
            print("No events to export")
            return
            
        df = pd.DataFrame(self.events)
        
        # Ensure proper column order
        columns = ['possession_id', 'timestamp', 'team', 'player_id', 'action', 
                  'zone', 'pressure', 'team_status', 'outcome', 'xg_change']
        
        # Reorder columns, keeping extra columns at the end
        existing_columns = [col for col in columns if col in df.columns]
        extra_columns = [col for col in df.columns if col not in columns]
        final_columns = existing_columns + extra_columns
        
        df = df[final_columns]
        df.to_csv(path, index=False)
        print(f"Events exported to CSV: {path}")
    
    def dump_xes(self, path: str) -> None:
        """Export events to XES format for PM4Py"""
        if not self.events:
            print("No events to export")
            return
            
        # Convert to DataFrame first
        df = pd.DataFrame(self.events)
        
        # Convert timestamp to datetime if it's string
        if df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Rename columns for PM4Py compatibility
        df_xes = df.rename(columns={
            'possession_id': 'case:concept:name',
            'action': 'concept:name',
            'timestamp': 'time:timestamp'
        })
        
        # Add additional attributes required by PM4Py
        df_xes['lifecycle:transition'] = 'complete'
        
        # Convert to event log
        event_log = pm4py.convert_to_event_log(df_xes)
        
        # Export to XES
        pm4py.write_xes(event_log, path)
        print(f"Events exported to XES: {path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics about logged events"""
        if not self.events:
            return {"total_events": 0}
            
        df = pd.DataFrame(self.events)
        stats = {
            "total_events": len(self.events),
            "unique_possessions": df['possession_id'].nunique(),
            "actions_breakdown": df['action'].value_counts().to_dict(),
            "teams": df['team'].unique().tolist(),
            "total_xg_home": df[(df['team'] == 'Home')]['xg_change'].sum(),
            "total_xg_away": df[(df['team'] == 'Away')]['xg_change'].sum()
        }
        return stats
    
    def clear(self) -> None:
        """Clear all events from buffer"""
        self.events.clear()
        self.possession_counter = 0
