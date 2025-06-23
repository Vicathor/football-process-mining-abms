"""
Football Player Agent
Represents individual players with roles, skills, and behaviors
"""
import mesa
import numpy as np
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import random


class Position(Enum):
    """Player positions"""
    GK = "Goalkeeper"
    CB = "Center Back"
    LB = "Left Back"
    RB = "Right Back"
    CDM = "Defensive Midfielder"
    CM = "Central Midfielder"
    CAM = "Attacking Midfielder"
    LW = "Left Winger"
    RW = "Right Winger"
    ST = "Striker"


class PlayerAgent(mesa.Agent):
    """Football player agent with realistic behaviors"""
    
    def __init__(self, model, team: str, position: Position, jersey_number: int,
                 name: str = None):
        super().__init__(model)
        
        # Basic info
        self.team = team
        self.position = position
        self.jersey_number = jersey_number
        self.name = name or f"{team} Player {jersey_number}"
        
        # Current state
        self.zone = "C3"  # Start in center
        self.has_ball = False
        self.energy = 100.0  # 0-100
        self.confidence = 0.5  # 0-1
        
        # Skills (0-1, higher is better)
        self.skills = self._generate_skills()
        
        # Tactical info
        self.formation_position = self._get_formation_position()
        self.current_instruction = "maintain_position"
        
        # Match stats
        self.stats = {
            'passes_attempted': 0, 'passes_completed': 0,
            'shots': 0, 'goals': 0, 'tackles': 0, 'interceptions': 0,
            'ball_recoveries': 0, 'fouls': 0, 'saves': 0
        }
        
    def _generate_skills(self) -> Dict[str, float]:
        """Generate player skills based on position"""
        base_skills = {
            'passing': 0.5, 'shooting': 0.3, 'tackling': 0.4,
            'dribbling': 0.4, 'positioning': 0.5, 'crossing': 0.3,
            'finishing': 0.3, 'saving': 0.1, 'speed': 0.5, 'strength': 0.5
        }
        
        # Modify based on position
        position_modifiers = {
            Position.GK: {'saving': 0.8, 'positioning': 0.7, 'passing': 0.4},
            Position.CB: {'tackling': 0.7, 'positioning': 0.7, 'strength': 0.7},
            Position.LB: {'speed': 0.6, 'crossing': 0.6, 'tackling': 0.6},
            Position.RB: {'speed': 0.6, 'crossing': 0.6, 'tackling': 0.6},
            Position.CDM: {'tackling': 0.7, 'passing': 0.7, 'positioning': 0.7},
            Position.CM: {'passing': 0.8, 'positioning': 0.6, 'dribbling': 0.6},
            Position.CAM: {'passing': 0.7, 'dribbling': 0.8, 'shooting': 0.7},
            Position.LW: {'speed': 0.8, 'dribbling': 0.8, 'crossing': 0.7},
            Position.RW: {'speed': 0.8, 'dribbling': 0.8, 'crossing': 0.7},
            Position.ST: {'shooting': 0.9, 'finishing': 0.9, 'positioning': 0.7}
        }
        
        if self.position in position_modifiers:
            for skill, value in position_modifiers[self.position].items():
                base_skills[skill] = min(0.95, value + random.uniform(-0.1, 0.1))
                
        return base_skills
    
    def _get_formation_position(self) -> str:
        """Get default formation zone for position"""
        formation_zones = {
            Position.GK: "A3",
            Position.CB: "A2" if self.jersey_number % 2 == 0 else "A4",
            Position.LB: "B1", Position.RB: "B5",
            Position.CDM: "B3", Position.CM: "C3",
            Position.CAM: "C3", Position.LW: "C1", Position.RW: "C5",
            Position.ST: "D3"
        }
        return formation_zones.get(self.position, "C3")
    
    def step(self):
        """Player step - main decision making"""
        if not self.model.running:
            return
            
        # Update energy and confidence
        self._update_energy()
        self._update_confidence()
        
        # Decide action based on current situation
        if self.has_ball:
            self._decide_with_ball()
        else:
            self._decide_without_ball()
    
    def _update_energy(self):
        """Update player energy based on activity"""
        energy_loss = random.uniform(0.1, 0.3)
        self.energy = max(0, self.energy - energy_loss)
    
    def _update_confidence(self):
        """Update confidence based on recent performance"""
        # Simplified confidence system
        if hasattr(self, '_recent_success'):
            if self._recent_success:
                self.confidence = min(1.0, self.confidence + 0.05)
            else:
                self.confidence = max(0.1, self.confidence - 0.03)
    
    def _decide_with_ball(self):
        """Decision making when player has the ball"""
        actions = self._get_available_actions()
        
        if not actions:
            return
            
        # Weighted decision based on position and situation
        action_weights = self._calculate_action_weights(actions)
        chosen_action = random.choices(actions, weights=action_weights)[0]
        
        # Execute action
        self._execute_action(chosen_action)
    
    def _decide_without_ball(self):
        """Decision making when player doesn't have ball"""
        # Move towards tactical position or support ball carrier
        if self.model.ball_carrier and self.model.ball_carrier.team == self.team:
            self._support_attack()
        else:
            self._defensive_positioning()
    
    def _get_available_actions(self) -> List[str]:
        """Get available actions for player with ball"""
        actions = ['Pass', 'Dribble']
        
        # Add shooting if in attacking position
        current_zone = self.zone
        if (self.team == "Home" and current_zone.startswith(('C', 'D'))) or \
           (self.team == "Away" and current_zone.startswith(('A', 'B'))):
            actions.append('Shot')
            
        return actions
    
    def _calculate_action_weights(self, actions: List[str]) -> List[float]:
        """Calculate weights for available actions"""
        weights = []
        
        for action in actions:
            if action == 'Pass':
                weight = self.skills['passing'] * 0.6 + self.confidence * 0.4
            elif action == 'Dribble':
                weight = self.skills['dribbling'] * 0.7 + self.confidence * 0.3
            elif action == 'Shot':
                weight = self.skills['shooting'] * 0.8 + self.confidence * 0.2
                # Increase weight if in good shooting position
                if self._is_in_shooting_position():
                    weight *= 1.5
            else:
                weight = 0.3
                
            weights.append(max(0.1, weight))
            
        return weights
    
    def _is_in_shooting_position(self) -> bool:
        """Check if player is in good shooting position"""
        goal_zone = self.model.field.get_goal_zone_for_team(self.team)
        distance = self.model.field.calculate_distance(self.zone, goal_zone)
        return distance < 20  # Within shooting range
    
    def _execute_action(self, action: str):
        """Execute the chosen action"""
        pressure = self._get_current_pressure()
        
        if action == 'Pass':
            self._attempt_pass(pressure)
        elif action == 'Dribble':
            self._attempt_dribble(pressure)
        elif action == 'Shot':
            self._attempt_shot(pressure)
    
    def _get_current_pressure(self) -> int:
        """Get current pressure level on player"""
        # Get opponent positions in nearby zones
        opponent_positions = []
        opponent_team = "Away" if self.team == "Home" else "Home"
        
        for agent in self.model.agents:
            if isinstance(agent, PlayerAgent) and agent.team == opponent_team:
                opponent_positions.append(agent.zone)
                
        return self.model.field.get_pressure_level(self.zone, opponent_positions)
    
    def _attempt_pass(self, pressure: int):
        """Attempt to pass the ball"""
        # Find potential pass targets
        teammates = self._get_pass_targets()
        
        if not teammates:
            # No pass available, try dribble
            self._attempt_dribble(pressure)
            return
            
        # Choose target based on position and skills
        target = self._choose_pass_target(teammates)
        
        # Calculate pass success probability
        pass_skill = self.skills['passing']
        pressure_penalty = pressure * 0.1
        success_prob = max(0.1, pass_skill - pressure_penalty)
        
        # Execute pass
        success = random.random() < success_prob
        outcome = "Success" if success else "Failure"
        
        # Log event
        possession_id = self.model.current_possession_id
        self.model.logger.add({
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Pass',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',  # Simplified
            'outcome': outcome,
            'xg_change': 0.0
        })
        
        # Update stats
        self.stats['passes_attempted'] += 1
        if success:
            self.stats['passes_completed'] += 1
            self._recent_success = True
            # Transfer ball to target
            self.has_ball = False
            target.has_ball = True
            self.model.ball_carrier = target
            self.model.ball_zone = target.zone
        else:
            self._recent_success = False
            # Ball goes to opponent or out of play
            self._lose_ball()
    
    def _attempt_dribble(self, pressure: int):
        """Attempt to dribble past opponents"""
        dribble_skill = self.skills['dribbling']
        pressure_penalty = pressure * 0.15
        success_prob = max(0.2, dribble_skill - pressure_penalty)
        
        success = random.random() < success_prob
        outcome = "Success" if success else "Failure"
        
        # Log event
        possession_id = self.model.current_possession_id
        self.model.logger.add({
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Dribble',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',
            'outcome': outcome,
            'xg_change': 0.0
        })
        
        if success:
            self._recent_success = True
            # Move to adjacent zone
            self._move_with_ball()
        else:
            self._recent_success = False
            self._lose_ball()
    
    def _attempt_shot(self, pressure: int):
        """Attempt to shoot at goal"""
        shooting_skill = self.skills['shooting']
        finishing_skill = self.skills['finishing']
        
        # Calculate shot quality based on position and pressure
        goal_zone = self.model.field.get_goal_zone_for_team(self.team)
        distance = self.model.field.calculate_distance(self.zone, goal_zone)
        
        distance_factor = max(0.1, 1.0 - (distance / 50.0))
        pressure_penalty = pressure * 0.1
        
        shot_quality = (shooting_skill + finishing_skill) / 2
        shot_quality *= distance_factor
        shot_quality -= pressure_penalty
        
        # Calculate xG (expected goals)
        xg = max(0.01, min(0.99, shot_quality))
        
        # Determine if it's a goal
        is_goal = random.random() < xg
        outcome = "Goal" if is_goal else "Failure"
        
        # Log event
        possession_id = self.model.current_possession_id
        self.model.logger.add({
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Shot',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',
            'outcome': outcome,
            'xg_change': xg
        })
        
        # Update stats
        self.stats['shots'] += 1
        
        if is_goal:
            self.stats['goals'] += 1
            self._recent_success = True
            # Update model score
            if self.team == "Home":
                self.model.score_home += 1
            else:
                self.model.score_away += 1
            
            # Log goal and possession end
            self.model.logger.add({
                'possession_id': possession_id,
                'team': self.team,
                'player_id': self.jersey_number,
                'action': 'Goal',
                'zone': self.zone,
                'pressure': 0,
                'team_status': 'Tied',
                'outcome': 'Success',
                'xg_change': 0.0
            })
            
            self._end_possession("Goal")
        else:
            self._recent_success = False
            self._lose_ball()
    
    def _get_pass_targets(self) -> List['PlayerAgent']:
        """Get available teammates for passing"""
        teammates = []
        for agent in self.model.agents:
            if (isinstance(agent, PlayerAgent) and 
                agent.team == self.team and 
                agent != self and
                not agent.has_ball):
                teammates.append(agent)
        return teammates
    
    def _choose_pass_target(self, teammates: List['PlayerAgent']) -> 'PlayerAgent':
        """Choose best pass target from available teammates"""
        if not teammates:
            return None
            
        # Score each teammate based on position and situation
        scores = []
        for teammate in teammates:
            score = 0.5  # Base score
            
            # Prefer forward passes
            if self.team == "Home":
                if teammate.zone > self.zone:  # Moving towards D zones
                    score += 0.3
            else:
                if teammate.zone < self.zone:  # Moving towards A zones
                    score += 0.3
            
            # Prefer less pressured positions
            teammate_pressure = teammate._get_current_pressure()
            score -= teammate_pressure * 0.1
            
            # Prefer players in good positions for their role
            if teammate.position in [Position.ST, Position.CAM]:
                score += 0.2
                
            scores.append(score)
        
        # Choose target with highest score
        best_idx = scores.index(max(scores))
        return teammates[best_idx]
    
    def _move_with_ball(self):
        """Move to an adjacent zone while maintaining possession"""
        adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
        
        if not adjacent_zones:
            return
            
        # Choose direction based on team attacking direction
        preferred_zones = []
        for zone in adjacent_zones:
            if self.team == "Home" and zone > self.zone:  # Forward for Home
                preferred_zones.append(zone)
            elif self.team == "Away" and zone < self.zone:  # Forward for Away
                preferred_zones.append(zone)
        
        if not preferred_zones:
            preferred_zones = adjacent_zones
            
        new_zone = random.choice(preferred_zones)
        self.zone = new_zone
        self.model.ball_zone = new_zone
    
    def _lose_ball(self):
        """Lose possession of the ball"""
        self.has_ball = False
        self.model.ball_carrier = None
        
        # Ball goes to random opponent or out of play
        self._end_possession("Lost")
    
    def _end_possession(self, reason: str):
        """End current possession"""
        # Log possession end
        self.model.logger.add({
            'possession_id': self.model.current_possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'PossessionEnd',
            'zone': self.zone,
            'pressure': 0,
            'team_status': 'Tied',
            'outcome': reason,
            'xg_change': 0.0
        })
        
        # Start new possession with other team
        other_team = "Away" if self.team == "Home" else "Home"
        self.model._start_new_possession(other_team)
    
    def _support_attack(self):
        """Move to support attacking teammate"""
        if not self.model.ball_carrier:
            return
            
        # Move towards ball carrier or into space
        ball_zone = self.model.ball_carrier.zone
        adjacent_to_ball = self.model.field.get_adjacent_zones(ball_zone)
        
        # Find free adjacent zone
        for zone in adjacent_to_ball:
            occupied = any(agent.zone == zone for agent in self.model.agents 
                         if isinstance(agent, PlayerAgent))
            if not occupied:
                self.zone = zone
                break
    
    def _defensive_positioning(self):
        """Move to defensive position"""
        # Simple defensive positioning - move towards formation position
        formation_zone = self.formation_position
        
        # Adjust based on team defending direction
        if self.team == "Home":
            # Home defends A zones
            if not formation_zone.startswith('A'):
                formation_zone = "A" + formation_zone[1]
        else:
            # Away defends D zones  
            if not formation_zone.startswith('D'):
                formation_zone = "D" + formation_zone[1]
                
        self.zone = formation_zone
