"""
Football Field and Zone Management
Defines the football field layout and zone system (A1-D5)
"""
import mesa
import numpy as np
from typing import Tuple, List, Dict, Any
from enum import Enum


class Zone(Enum):
    """Football field zones in a 4x5 grid (A1-D5)"""
    # Defensive zones (own goal area)
    A1 = "A1"  # Left defensive corner
    A2 = "A2"  # Left defensive mid
    A3 = "A3"  # Center defensive
    A4 = "A4"  # Right defensive mid  
    A5 = "A5"  # Right defensive corner
    
    # Defensive third
    B1 = "B1"  # Left defensive third
    B2 = "B2"  # Left-center defensive third
    B3 = "B3"  # Center defensive third
    B4 = "B4"  # Right-center defensive third
    B5 = "B5"  # Right defensive third
    
    # Midfield
    C1 = "C1"  # Left midfield
    C2 = "C2"  # Left-center midfield
    C3 = "C3"  # Center midfield
    C4 = "C4"  # Right-center midfield
    C5 = "C5"  # Right midfield
    
    # Attacking third
    D1 = "D1"  # Left attacking third
    D2 = "D2"  # Left-center attacking third
    D3 = "D3"  # Center attacking third
    D4 = "D4"  # Right-center attacking third
    D5 = "D5"  # Right attacking third


class FootballField:
    """Manages the football field layout and zone system"""
    
    def __init__(self, width: int = 50, height: int = 80):
        self.width = width
        self.height = height
        self.zones = self._create_zone_mapping()
        
    def _create_zone_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Create mapping between zones and field coordinates"""
        zones = {}
        
        # Calculate zone dimensions (4 rows x 5 columns)
        zone_height = self.height // 4
        zone_width = self.width // 5
        
        rows = ['A', 'B', 'C', 'D']
        
        for i, row in enumerate(rows):
            for j in range(1, 6):  # Columns 1-5
                zone_name = f"{row}{j}"
                
                # Calculate zone boundaries
                x_start = j * zone_width - zone_width
                x_end = j * zone_width
                y_start = i * zone_height
                y_end = (i + 1) * zone_height
                
                zones[zone_name] = {
                    'x_range': (x_start, x_end),
                    'y_range': (y_start, y_end),
                    'center': (x_start + zone_width // 2, y_start + zone_height // 2),
                    'type': self._get_zone_type(row, j)
                }
                
        return zones
    
    def _get_zone_type(self, row: str, col: int) -> str:
        """Determine zone type based on position"""
        if row == 'A':
            return 'defensive_box'
        elif row == 'B':
            return 'defensive_third'
        elif row == 'C':
            return 'midfield'
        elif row == 'D':
            return 'attacking_third'
        return 'unknown'
    
    def get_zone_from_position(self, x: int, y: int) -> str:
        """Get zone name from field coordinates"""
        # Clamp coordinates to field boundaries
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        
        for zone_name, zone_data in self.zones.items():
            x_range = zone_data['x_range']
            y_range = zone_data['y_range']
            
            if (x_range[0] <= x < x_range[1] and 
                y_range[0] <= y < y_range[1]):
                return zone_name
                
        return "C3"  # Default to center if not found
    
    def get_zone_center(self, zone: str) -> Tuple[int, int]:
        """Get center coordinates of a zone"""
        if zone in self.zones:
            return self.zones[zone]['center']
        return (self.width // 2, self.height // 2)  # Default center
    
    def get_adjacent_zones(self, zone: str) -> List[str]:
        """Get list of adjacent zones"""
        if zone not in self.zones:
            return []
            
        row = zone[0]
        col = int(zone[1])
        adjacent = []
        
        # Check all 8 directions (including diagonals)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            new_row_idx = ord(row) - ord('A') + dr
            new_col = col + dc
            
            if (0 <= new_row_idx < 4 and 1 <= new_col <= 5):
                new_row = chr(ord('A') + new_row_idx)
                adjacent_zone = f"{new_row}{new_col}"
                adjacent.append(adjacent_zone)
                
        return adjacent
    
    def calculate_distance(self, zone1: str, zone2: str) -> float:
        """Calculate distance between two zones"""
        if zone1 not in self.zones or zone2 not in self.zones:
            return float('inf')
            
        center1 = self.zones[zone1]['center']
        center2 = self.zones[zone2]['center']
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def is_goal_scoring_zone(self, zone: str) -> bool:
        """Check if zone is in goal scoring area"""
        return zone in ['A2', 'A3', 'A4']  # Central goal area
    
    def is_defensive_zone(self, zone: str, team: str) -> bool:
        """Check if zone is defensive for given team"""
        if team == "Home":
            return zone.startswith('A') or zone.startswith('B')
        else:  # Away team
            return zone.startswith('D') or zone.startswith('C')
    
    def is_attacking_zone(self, zone: str, team: str) -> bool:
        """Check if zone is attacking for given team"""
        if team == "Home":
            return zone.startswith('D') or zone.startswith('C')
        else:  # Away team
            return zone.startswith('A') or zone.startswith('B')
    
    def get_pressure_level(self, zone: str, defending_team_positions: List[str]) -> int:
        """Calculate pressure level in a zone based on defending players"""
        if zone not in self.zones:
            return 0
            
        # Count defenders in same zone and adjacent zones
        pressure = 0
        adjacent_zones = self.get_adjacent_zones(zone)
        
        for defender_zone in defending_team_positions:
            if defender_zone == zone:
                pressure += 2  # High pressure for same zone
            elif defender_zone in adjacent_zones:
                pressure += 1  # Medium pressure for adjacent zones
                
        return min(pressure, 3)  # Cap at 3 for high pressure
    
    def get_goal_zone_for_team(self, team: str) -> str:
        """Get the goal zone for a team"""
        if team == "Home":
            return "D3"  # Home attacks towards D zones
        else:
            return "A3"  # Away attacks towards A zones
