"""
Football Simulation Model
Main simulation model coordinating the match
"""
import mesa
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from player_agent import PlayerAgent, Position
from football_field import FootballField
from utils_logger import EventLogger


class FootballModel(mesa.Model):
    """Main football simulation model"""
    
    def __init__(self, match_duration_minutes: int = 90, seed: Optional[int] = None):
        super().__init__(seed=seed)
        
        # Match configuration
        self.match_duration_minutes = match_duration_minutes
        self.seconds_per_step = 10  # Each step = 10 seconds
        self.total_steps = (match_duration_minutes * 60) // self.seconds_per_step
        
        # Match state
        self.score_home = 0
        self.score_away = 0
        self.current_minute = 0
        self.current_second = 0
        
        # Ball and possession
        self.ball_zone = "C3"  # Start in center circle
        self.ball_carrier: Optional[PlayerAgent] = None
        self.current_possession_id = ""
        self.possession_count = 0
        
        # Components
        self.field = FootballField()
        self.logger = EventLogger()
        
        # Create teams
        self._create_teams()
        
        # Match initialization
        self._start_match()
        
        # Data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Home_Score": "score_home",
                "Away_Score": "score_away", 
                "Minute": "current_minute",
                "Possessions": "possession_count",
                "Total_xG_Home": lambda m: m.logger.get_stats().get("total_xg_home", 0),
                "Total_xG_Away": lambda m: m.logger.get_stats().get("total_xg_away", 0)
            }
        )
    
    def _create_teams(self):
        """Create both teams with realistic formations"""
        # Home team (4-3-3 formation)
        home_formation = [
            (Position.GK, 1, "Goalkeeper"),
            (Position.CB, 4, "Center Back"), (Position.CB, 5, "Center Back"),
            (Position.LB, 3, "Left Back"), (Position.RB, 2, "Right Back"),
            (Position.CDM, 6, "Defensive Mid"), (Position.CM, 8, "Central Mid"),
            (Position.CAM, 10, "Attacking Mid"), (Position.LW, 11, "Left Wing"),
            (Position.RW, 7, "Right Wing"), (Position.ST, 9, "Striker")
        ]
        
        # Away team (4-4-2 formation)
        away_formation = [
            (Position.GK, 1, "Goalkeeper"),
            (Position.CB, 4, "Center Back"), (Position.CB, 5, "Center Back"),
            (Position.LB, 3, "Left Back"), (Position.RB, 2, "Right Back"),
            (Position.CM, 6, "Central Mid"), (Position.CM, 8, "Central Mid"),
            (Position.LW, 11, "Left Mid"), (Position.RW, 7, "Right Mid"),
            (Position.ST, 9, "Striker"), (Position.ST, 10, "Second Striker")
        ]
        
        # Create home team players
        for position, number, role in home_formation:
            player = PlayerAgent(
                model=self,
                team="Home",
                position=position,
                jersey_number=number,
                name=f"Home {role}"
            )
            # Set initial positions
            player.zone = self._get_initial_zone(position, "Home")
        
        # Create away team players  
        for position, number, role in away_formation:
            player = PlayerAgent(
                model=self,
                team="Away",
                position=position,
                jersey_number=number,
                name=f"Away {role}"
            )
            # Set initial positions
            player.zone = self._get_initial_zone(position, "Away")
    
    def _get_initial_zone(self, position: Position, team: str) -> str:
        """Get initial zone for player based on position and team"""
        # Home team defends A zones, attacks D zones
        # Away team defends D zones, attacks A zones
        
        if team == "Home":
            formation_zones = {
                Position.GK: "A3",
                Position.CB: "A2", Position.LB: "A1", Position.RB: "A5",
                Position.CDM: "B3", Position.CM: "C2", Position.CAM: "C4",
                Position.LW: "C1", Position.RW: "C5", Position.ST: "D3"
            }
        else:  # Away team (flipped)
            formation_zones = {
                Position.GK: "D3",
                Position.CB: "D4", Position.LB: "D5", Position.RB: "D1",
                Position.CDM: "C3", Position.CM: "C4", Position.CAM: "C2",
                Position.LW: "C5", Position.RW: "C1", Position.ST: "A3"
            }
        
        return formation_zones.get(position, "C3")
    
    def _start_match(self):
        """Initialize match start"""
        self.running = True
        
        # Choose random team to start with ball
        starting_team = random.choice(["Home", "Away"])
        self._start_new_possession(starting_team)
        
        # Log match start
        self.logger.add({
            'possession_id': "MATCH_START",
            'team': starting_team,
            'player_id': 0,
            'action': 'KickOff',
            'zone': 'C3',
            'pressure': 0,
            'team_status': 'Tied',
            'outcome': 'Success',
            'xg_change': 0.0
        })
    
    def _start_new_possession(self, team: str):
        """Start a new possession sequence"""
        self.possession_count += 1
        self.current_possession_id = self.logger.generate_possession_id(
            team, f"M{self.steps:02d}"
        )
        
        # Find a suitable player to start possession
        team_players = [agent for agent in self.agents 
                       if isinstance(agent, PlayerAgent) and agent.team == team]
        
        if team_players:
            # Give ball to midfielder or similar
            midfielder_positions = [Position.CM, Position.CDM, Position.CAM, Position.ST]
            suitable_players = [p for p in team_players 
                              if p.position in midfielder_positions]
            
            if not suitable_players:
                suitable_players = team_players
                
            ball_receiver = random.choice(suitable_players)
            
            # Clear previous ball carrier
            if self.ball_carrier:
                self.ball_carrier.has_ball = False
                
            # Set new ball carrier
            ball_receiver.has_ball = True
            self.ball_carrier = ball_receiver
            self.ball_zone = ball_receiver.zone
            
            # Log possession start
            self.logger.add({
                'possession_id': self.current_possession_id,
                'team': team,
                'player_id': ball_receiver.jersey_number,
                'action': 'PossessionStart',
                'zone': ball_receiver.zone,
                'pressure': 0,
                'team_status': self._get_team_status(),
                'outcome': 'Success',
                'xg_change': 0.0
            })
    
    def _get_team_status(self) -> str:
        """Get current match status"""
        if self.score_home > self.score_away:
            return "Leading" if random.choice([True, False]) else "Tied"
        elif self.score_away > self.score_home:
            return "Trailing" if random.choice([True, False]) else "Tied" 
        else:
            return "Tied"
    
    def step(self):
        """Execute one simulation step"""
        if not self.running:
            return
            
        # Update match time
        self.current_second += self.seconds_per_step
        if self.current_second >= 60:
            self.current_minute += 1
            self.current_second = 0
            
        # Check if match should end
        if self.current_minute >= self.match_duration_minutes:
            self._end_match()
            return
            
        # Activate all players
        self.agents.do("step")
        
        # Random events (fouls, cards, injuries - simplified)
        if random.random() < 0.05:  # 5% chance per step
            self._random_event()
            
        # Collect data
        self.datacollector.collect(self)
        
        # Occasional possession changes due to interceptions, tackles
        if random.random() < 0.1 and self.ball_carrier:  # 10% chance
            self._attempt_defensive_action()
    
    def _random_event(self):
        """Handle random match events"""
        event_types = ['Foul', 'Interception', 'Clearance', 'BallRecovery']
        event_type = random.choice(event_types)
        
        # Choose random player
        all_players = [agent for agent in self.agents if isinstance(agent, PlayerAgent)]
        if not all_players:
            return
            
        player = random.choice(all_players)
        
        # Log the event
        self.logger.add({
            'possession_id': self.current_possession_id,
            'team': player.team,
            'player_id': player.jersey_number,
            'action': event_type,
            'zone': player.zone,
            'pressure': random.randint(0, 1),
            'team_status': self._get_team_status(),
            'outcome': random.choice(['Success', 'Failure']),
            'xg_change': 0.0
        })
        
        # Update player stats
        if event_type == 'Foul':
            player.stats['fouls'] += 1
        elif event_type == 'Interception':
            player.stats['interceptions'] += 1
        elif event_type == 'BallRecovery':
            player.stats['ball_recoveries'] += 1
    
    def _attempt_defensive_action(self):
        """Attempt defensive action (tackle, interception)"""
        if not self.ball_carrier:
            return
            
        # Find nearby opponents
        opponent_team = "Away" if self.ball_carrier.team == "Home" else "Home"
        nearby_opponents = []
        
        for agent in self.agents:
            if (isinstance(agent, PlayerAgent) and 
                agent.team == opponent_team):
                # Check if in same or adjacent zone
                if (agent.zone == self.ball_carrier.zone or 
                    agent.zone in self.field.get_adjacent_zones(self.ball_carrier.zone)):
                    nearby_opponents.append(agent)
        
        if not nearby_opponents:
            return
            
        # Choose defender to attempt action
        defender = random.choice(nearby_opponents)
        action_type = random.choice(['Tackle', 'Interception'])
        
        # Calculate success based on skills
        if action_type == 'Tackle':
            success_prob = defender.skills['tackling'] * 0.7
        else:
            success_prob = defender.skills['positioning'] * 0.6
            
        success = random.random() < success_prob
        outcome = "Success" if success else "Failure"
        
        # Log defensive action
        self.logger.add({
            'possession_id': self.current_possession_id,
            'team': defender.team,
            'player_id': defender.jersey_number,
            'action': action_type,
            'zone': defender.zone,
            'pressure': 1,
            'team_status': self._get_team_status(),
            'outcome': outcome,
            'xg_change': 0.0
        })
        
        # Update stats
        if action_type == 'Tackle':
            defender.stats['tackles'] += 1
        else:
            defender.stats['interceptions'] += 1
            
        if success:
            # Defender wins ball
            self.ball_carrier.has_ball = False
            defender.has_ball = True
            self.ball_carrier = defender
            self.ball_zone = defender.zone
            
            # Start new possession
            self._start_new_possession(defender.team)
    
    def _end_match(self):
        """End the match"""
        self.running = False
        
        # Log match end events
        self.logger.add({
            'possession_id': 'MATCH_END',
            'team': 'Home',
            'player_id': 0,
            'action': 'MatchEnd',
            'zone': 'C3',
            'pressure': 0,
            'team_status': self._get_final_result(),
            'outcome': 'Complete',
            'xg_change': 0.0
        })
        
        print(f"\n=== MATCH FINISHED ===")
        print(f"Final Score: Home {self.score_home} - {self.score_away} Away")
        print(f"Match Duration: {self.current_minute} minutes")
        print(f"Total Possessions: {self.possession_count}")
        
        # Print event statistics
        stats = self.logger.get_stats()
        print(f"\nEvent Statistics:")
        print(f"Total Events: {stats['total_events']}")
        print(f"xG Home: {stats.get('total_xg_home', 0):.2f}")
        print(f"xG Away: {stats.get('total_xg_away', 0):.2f}")
        
        if 'actions_breakdown' in stats:
            print(f"\nActions Breakdown:")
            for action, count in stats['actions_breakdown'].items():
                print(f"  {action}: {count}")
    
    def _get_final_result(self) -> str:
        """Get final match result"""
        if self.score_home > self.score_away:
            return "Home Win"
        elif self.score_away > self.score_home:
            return "Away Win"
        else:
            return "Draw"
    
    def export_logs(self, csv_path: str = None, xes_path: str = None):
        """Export match logs"""
        if csv_path:
            self.logger.dump_csv(csv_path)
        if xes_path:
            self.logger.dump_xes(xes_path)
    
    def get_match_summary(self) -> Dict[str, Any]:
        """Get comprehensive match summary"""
        return {
            'final_score': {'home': self.score_home, 'away': self.score_away},
            'duration_minutes': self.current_minute,
            'total_possessions': self.possession_count,
            'total_steps': self.steps,
            'event_stats': self.logger.get_stats(),
            'result': self._get_final_result()
        }
