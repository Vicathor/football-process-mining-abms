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
        
        # Shot quality tracking (Home team only)
        if team == "Home":
            self.shot_quality_score = 0.0  # Running total of shot quality rewards
            self.last_shot_reward = 0.0    # Track reward from last shot
        
        # Possession-based tactics (Home team only)
        self.possession_preference = 1.5 if team == "Home" else 1.0  # Home team prefers possession
        self.pass_chain_bonus = 0.0  # Bonus for building pass chains
        
        # FINAL THIRD PENETRATION TACTICS (Home team only)
        self.final_third_penetration = team == "Home"  # Enable aggressive final third play
        self.final_third_bonus = 5.0  # +5 reward for entering final third
        self.key_chance_bonus = 10.0  # +10 reward for shots from final third
        
        # COUNTER-ATTACK SPIKE TACTIC (Home team only)
        self.counter_attack_mode = team == "Home"  # Enable counter-attack after interceptions
        self.counter_clock = 0  # Counter-attack timer (2 actions after regaining ball)
        self.counter_attack_bonus = 8.0  # +8 reward for quick counter-attacks
        
        # Match stats
        self.stats = {
            'passes_attempted': 0, 'passes_completed': 0,
            'shots': 0, 'goals': 0, 'tackles': 0, 'interceptions': 0,
            'ball_recoveries': 0, 'fouls': 0, 'saves': 0
        }
        
        # Home team additional stats for shot quality analysis
        if team == "Home":
            self.stats.update({
                'shots_on_target': 0,
                'low_xg_shots': 0,  # Shots with xG < 0.07
                'quality_shots': 0   # Shots with good xG or on target
            })
        
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
            
        # Check for counter-attack opportunities (Home team only)
        if self.counter_attack_mode and self.has_ball:
            self._check_for_counter_attack_trigger()
            
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
                base_confidence_gain = 0.05
                
                # HOME TEAM POSSESSION-BASED CONFIDENCE BONUS
                if self.team == "Home":
                    possession_length = self._get_current_possession_length()
                    # Extra confidence for contributing to good possession play
                    if possession_length >= 3:
                        base_confidence_gain *= 1.3  # 30% bonus for pass chain contributions
                    
                    # SHOT QUALITY CONFIDENCE ADJUSTMENT
                    if hasattr(self, 'last_shot_reward') and self.last_shot_reward != 0:
                        # Scale shot quality reward to confidence adjustment
                        shot_confidence_adj = self.last_shot_reward * 0.01  # Convert reward to confidence
                        base_confidence_gain += shot_confidence_adj
                        self.last_shot_reward = 0.0  # Reset after using
                
                self.confidence = min(1.0, self.confidence + base_confidence_gain)
            else:
                confidence_loss = 0.03
                
                # HOME TEAM: Reduced confidence loss during possession building
                if self.team == "Home":
                    possession_length = self._get_current_possession_length()
                    if possession_length >= 2:
                        confidence_loss *= 0.7  # Reduce confidence loss during possession building
                    
                    # SHOT QUALITY CONFIDENCE PENALTY
                    if hasattr(self, 'last_shot_reward') and self.last_shot_reward < 0:
                        # Increase confidence loss for poor shot selection
                        shot_confidence_penalty = abs(self.last_shot_reward) * 0.005
                        confidence_loss += shot_confidence_penalty
                        self.last_shot_reward = 0.0  # Reset after using
                
                self.confidence = max(0.1, self.confidence - confidence_loss)

    def _check_for_counter_attack_trigger(self):
        """Check if last event was an interception to trigger counter-attack mode"""
        if not self.counter_attack_mode:
            return
            
        # Check recent events in the match for interception by our team
        recent_events = []
        if hasattr(self.model, 'logger') and self.model.logger.events:
            # Get last few events
            recent_events = self.model.logger.events[-5:]  # Check last 5 events
            
        for event in reversed(recent_events):  # Most recent first
            if (event.get('team') == self.team and 
                event.get('action') == 'Interception' and
                event.get('outcome') == 'Success'):
                # We just regained the ball via interception!
                self.counter_clock = 2  # Give next 2 actions special status
                print(f"⚡ Counter-attack mode activated for {self.team} player {self.jersey_number}!")
                break
    
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
        
        # Get current possession sequence length for tactical decisions
        possession_length = self._get_current_possession_length()
        
        for action in actions:
            if action == 'Pass':
                weight = self.skills['passing'] * 0.6 + self.confidence * 0.4
                
                # HOME TEAM POSSESSION-BASED TACTICS
                if self.team == "Home":
                    # Reward building pass chains (3-4 passes)
                    if possession_length < 4:
                        # Increase pass preference for building possession
                        weight *= self.possession_preference
                        # Extra bonus for continuing short pass chains
                        if 2 <= possession_length <= 3:
                            weight *= 1.3  # 30% bonus for chain building
                    elif possession_length >= 4:
                        # Slight reduction after 4 passes to encourage finishing
                        weight *= 0.9
                
                # COUNTER-ATTACK SPIKE (Home team only)
                if self.counter_clock > 0:
                    # Check if this pass would penetrate final third
                    potential_targets = self._get_pass_targets()
                    for target in potential_targets:
                        if self._is_final_third_entry(self.zone, target.zone):
                            weight += self.counter_attack_bonus  # +8 massive bonus for counter-attack final third entry
                            print(f"⚡ Counter-attack pass bonus applied for {self.team} player {self.jersey_number}!")
                            break
                
                # FINAL THIRD PENETRATION TACTICS (Home team only)
                if self.final_third_penetration:
                    # Massive bonus for passes that penetrate final third
                    potential_targets = self._get_pass_targets()
                    for target in potential_targets:
                        if self._is_final_third_entry(self.zone, target.zone):
                            weight *= 2.5  # 150% bonus for final third penetration
                            break
                    
                    # Additional bonus for passes in final third 
                    if self._is_in_final_third():
                        weight *= 1.4  # 40% bonus for passes within final third
                        
            elif action == 'Dribble':
                weight = self.skills['dribbling'] * 0.7 + self.confidence * 0.3
                
                # HOME TEAM INTELLIGENT DRIBBLE FILTERING
                if self.team == "Home":
                    # Estimate dribble success probability based on context
                    p = self._estimate_dribble_success()
                    
                    # Strongly discourage low-success dribbles, reward high-value ones
                    if p < 0.65:
                        weight -= 5  # Strongly discourage low-probability dribbles
                    else:
                        weight += 4  # Reward only the good dribbling opportunities
                
                # AWAY TEAM POSSESSION-BASED TACTICS (unchanged)
                if self.team == "Away":
                    # Reduce dribbling preference to maintain possession
                    if possession_length < 3:
                        weight *= 0.7  # 30% reduction to favor passing
                
                # COUNTER-ATTACK SPIKE (Home team only)
                if self.counter_clock > 0:
                    # Check if this dribble would penetrate final third
                    adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
                    for adj_zone in adjacent_zones:
                        if self._is_final_third_entry(self.zone, adj_zone):
                            weight += self.counter_attack_bonus  # +8 massive bonus for counter-attack final third entry
                            print(f"⚡ Counter-attack dribble bonus applied for {self.team} player {self.jersey_number}!")
                            break
                
                # FINAL THIRD PENETRATION TACTICS (Home team only)
                if self.final_third_penetration:
                    # Bonus for dribbling into final third
                    adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
                    for adj_zone in adjacent_zones:
                        if self._is_final_third_entry(self.zone, adj_zone):
                            weight *= 2.0  # 100% bonus for dribbling into final third
                            break
                    
                    # Extra bonus for dribbling in final third
                    if self._is_in_final_third():
                        weight *= 1.6  # 60% bonus for dribbling in final third
                        
            elif action == 'Shot':
                weight = self.skills['shooting'] * 0.8 + self.confidence * 0.2
                # Increase weight if in good shooting position
                if self._is_in_shooting_position():
                    weight *= 1.5
                    
                # HOME TEAM POSSESSION-BASED TACTICS
                if self.team == "Home":
                    # Reward shots after good possession build-up
                    if possession_length >= 3:
                        weight *= 1.2  # 20% bonus for shots after pass chains
                    
                    # SHOT QUALITY FILTER - HOME TEAM ONLY
                    predicted_xg = self._calculate_shot_xg()
                    if predicted_xg < 0.07:  # Low xG long-shot
                        weight *= 0.3  # Heavily discourage low-quality shots
                
                # COUNTER-ATTACK SPIKE: Bonus for quick shots in final third
                if self.counter_clock > 0 and self._is_in_final_third():
                    weight += self.counter_attack_bonus * 0.6  # +4.8 bonus for counter-attack shots in final third
                    print(f"⚡ Counter-attack shot bonus applied for {self.team} player {self.jersey_number}!")
                
                # FINAL THIRD PENETRATION TACTICS (Home team only)
                if self.final_third_penetration:
                    # Massive bonus for key chances (shots from penalty area)
                    if self._is_key_chance_position():
                        weight *= 3.0  # 200% bonus for key chances
                    # Regular bonus for any shot in final third
                    elif self._is_in_final_third():
                        weight *= 1.8  # 80% bonus for final third shots
            else:
                weight = 0.3
                
            weights.append(max(0.1, weight))
            
        return weights
    
    def _is_in_shooting_position(self) -> bool:
        """Check if player is in good shooting position"""
        goal_zone = self.model.field.get_goal_zone_for_team(self.team)
        distance = self.model.field.calculate_distance(self.zone, goal_zone)
        return distance < 20  # Within shooting range
    
    def _calculate_shot_xg(self) -> float:
        """Calculate expected goals (xG) for a shot from current position"""
        shooting_skill = self.skills['shooting']
        finishing_skill = self.skills['finishing']
        
        # Calculate shot quality based on position and pressure
        goal_zone = self.model.field.get_goal_zone_for_team(self.team)
        distance = self.model.field.calculate_distance(self.zone, goal_zone)
        
        distance_factor = max(0.1, 1.0 - (distance / 50.0))
        pressure = self._get_current_pressure()
        pressure_penalty = pressure * 0.1
        
        shot_quality = (shooting_skill + finishing_skill) / 2
        shot_quality *= distance_factor
        shot_quality -= pressure_penalty
        
        # Calculate xG (expected goals)
        xg = max(0.01, min(0.99, shot_quality))
        return xg
    
    def _log_final_third_entry(self, from_zone: str, to_zone: str, action_type: str):
        """Log a special event for final third penetration"""
        if not self.final_third_penetration or not self._is_final_third_entry(from_zone, to_zone):
            return
            
        possession_id = self.model.current_possession_id
        self.model.logger.add({
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'FinalThirdEntry',
            'zone': to_zone,
            'from_zone': from_zone,
            'entry_type': action_type,  # 'Pass', 'Dribble', or 'Movement'
            'pressure': 0,
            'team_status': 'Tied',
            'outcome': 'Success',
            'tactical_bonus': self.final_third_bonus,
            'xg_change': 0.0
        })
    
    def _is_final_third_entry(self, from_zone: str, to_zone: str) -> bool:
        """Check if move represents entry into final third"""
        if not self.final_third_penetration:
            return False
            
        # For Home team: entering D zones from B/C zones
        if self.team == "Home":
            return (from_zone.startswith(('B', 'C')) and to_zone.startswith('D'))
        # For Away team: entering A zones from B/C zones  
        else:
            return (from_zone.startswith(('B', 'C')) and to_zone.startswith('A'))
    
    def _is_in_final_third(self) -> bool:
        """Check if player is currently in final third"""
        if self.team == "Home":
            return self.zone.startswith('D')
        else:
            return self.zone.startswith('A')
    
    def _is_key_chance_position(self) -> bool:
        """Check if player is in position for a key chance (shot from penalty area)"""
        if not self.final_third_penetration:
            return False
            
        # Key chances are shots from central final third zones
        if self.team == "Home":
            return self.zone in ['D2', 'D3', 'D4']  # Central attacking zones
        else:
            return self.zone in ['A2', 'A3', 'A4']  # Central attacking zones
    
    def _get_current_possession_length(self) -> int:
        """Get the length of current possession sequence (number of passes/events)"""
        if not hasattr(self.model, 'current_possession_id') or not self.model.current_possession_id:
            return 0
            
        current_possession_id = self.model.current_possession_id
        
        # Count events in current possession for this team
        possession_events = [
            event for event in self.model.logger.events 
            if (event.get('possession_id') == current_possession_id and 
                event.get('team') == self.team and
                event.get('action') in ['Pass', 'Dribble', 'Shot'])
        ]
        
        return len(possession_events)
    
    def _execute_action(self, action: str):
        """Execute the chosen action"""
        pressure = self._get_current_pressure()
        
        # Decrement counter-attack clock if active
        if self.counter_clock > 0:
            self.counter_clock -= 1
            if self.counter_clock == 0:
                print(f"⚡ Counter-attack mode expired for {self.team} player {self.jersey_number}")
        
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
        
        # Check for final third penetration before logging
        is_final_third_entry = self._is_final_third_entry(self.zone, target.zone) if success else False
        
        # Log event
        possession_id = self.model.current_possession_id
        pass_event = {
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Pass',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',  # Simplified
            'outcome': outcome,
            'xg_change': 0.0
        }
        
        # Add final third penetration bonus logging
        if is_final_third_entry:
            pass_event['final_third_entry'] = True
            pass_event['tactical_bonus'] = self.final_third_bonus
            
        # Add counter-attack bonus logging
        if self.counter_clock > 0 and is_final_third_entry:
            pass_event['counter_attack'] = True
            pass_event['counter_attack_bonus'] = self.counter_attack_bonus
            pass_event['action'] = 'CounterAttackPass'  # Special event type for process mining
        
        self.model.logger.add(pass_event)
        
        # Update stats
        self.stats['passes_attempted'] += 1
        if success:
            self.stats['passes_completed'] += 1
            self._recent_success = True
            
            # Log final third entry if applicable
            if is_final_third_entry:
                self._log_final_third_entry(self.zone, target.zone, 'Pass')
            
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
        
        # Check for potential final third entry via dribbling
        will_enter_final_third = False
        if success and self.final_third_penetration:
            adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
            for adj_zone in adjacent_zones:
                if self._is_final_third_entry(self.zone, adj_zone):
                    will_enter_final_third = True
                    break
        
        # Log event
        possession_id = self.model.current_possession_id
        dribble_event = {
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Dribble',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',
            'outcome': outcome,
            'xg_change': 0.0
        }
        
        # Add final third penetration bonus logging
        if will_enter_final_third:
            dribble_event['final_third_entry'] = True
            dribble_event['tactical_bonus'] = self.final_third_bonus
        elif self._is_in_final_third():
            dribble_event['final_third_dribble'] = True
            dribble_event['tactical_bonus'] = self.final_third_bonus * 0.6  # Smaller bonus for dribbling within
            
        # Add counter-attack bonus logging
        if self.counter_clock > 0 and will_enter_final_third:
            dribble_event['counter_attack'] = True
            dribble_event['counter_attack_bonus'] = self.counter_attack_bonus
            dribble_event['action'] = 'CounterAttackDribble'  # Special event type for process mining
        
        self.model.logger.add(dribble_event)
        
        if success:
            self._recent_success = True
            
            # Log final third entry if applicable
            if will_enter_final_third:
                # Find the zone we'll move to for logging
                adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
                for adj_zone in adjacent_zones:
                    if self._is_final_third_entry(self.zone, adj_zone):
                        self._log_final_third_entry(self.zone, adj_zone, 'Dribble')
                        break
            
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
        
        # Determine shot accuracy (on target) - better shots have higher chance of being on target
        on_target_prob = min(0.9, xg * 2.0 + 0.3)  # Base 30% + xG bonus
        on_target = random.random() < on_target_prob
        
        # Determine if it's a goal (only possible if on target)
        is_goal = False
        if on_target:
            is_goal = random.random() < (xg / on_target_prob)  # Conditional probability
        
        # HOME TEAM SHOT QUALITY FILTER - REWARD SYSTEM
        shot_quality_reward = 0.0
        if self.team == "Home":
            # Apply shot quality filter
            if xg < 0.07:  # Low xG long-shot
                shot_quality_reward -= 4  # Discourage low-quality shots
            elif on_target:
                shot_quality_reward += 3  # Encourage accuracy
            
            # Big bonus for goals
            if is_goal:
                shot_quality_reward += 10  # Big bonus for goals
        
        outcome = "Goal" if is_goal else ("OnTarget" if on_target else "Failure")
        
        # Check for key chance position
        is_key_chance = self._is_key_chance_position()
        
        # Log event
        possession_id = self.model.current_possession_id
        shot_event = {
            'possession_id': possession_id,
            'team': self.team,
            'player_id': self.jersey_number,
            'action': 'Shot',
            'zone': self.zone,
            'pressure': 1 if pressure > 0 else 0,
            'team_status': 'Tied',
            'outcome': outcome,
            'xg_change': xg
        }
        
        # Add key chance bonus logging
        if is_key_chance:
            shot_event['key_chance'] = True
            shot_event['tactical_bonus'] = self.key_chance_bonus
        elif self._is_in_final_third():
            shot_event['final_third_shot'] = True
            shot_event['tactical_bonus'] = self.final_third_bonus
            
        # Add counter-attack bonus logging
        if self.counter_clock > 0 and self._is_in_final_third():
            shot_event['counter_attack'] = True
            shot_event['counter_attack_bonus'] = self.counter_attack_bonus * 0.6
            shot_event['action'] = 'CounterAttackShot'  # Special event type for process mining
            
        # Add shot quality metrics (Home team only)
        if self.team == "Home":
            shot_event['shot_quality_reward'] = shot_quality_reward
            shot_event['on_target'] = on_target
            shot_event['xg_value'] = xg
        
        self.model.logger.add(shot_event)
        
        # Update stats
        self.stats['shots'] += 1
        
        # HOME TEAM: Track shot quality reward for learning
        if self.team == "Home" and hasattr(self, 'shot_quality_score'):
            self.shot_quality_score += shot_quality_reward
            self.last_shot_reward = shot_quality_reward
            
            # Track additional shot quality stats
            if on_target:
                self.stats['shots_on_target'] += 1
            if xg < 0.07:
                self.stats['low_xg_shots'] += 1
            if xg >= 0.07 or on_target:
                self.stats['quality_shots'] += 1
        
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
            
            # FINAL THIRD PENETRATION TACTICS (Home team only)
            if self.final_third_penetration:
                # MASSIVE priority for final third penetration passes
                if self._is_final_third_entry(self.zone, teammate.zone):
                    score += 1.5  # Huge bonus for final third entry
                
                # High priority for passes within final third  
                elif teammate.zone.startswith('D'):  # Teammate in final third
                    score += 0.8
                
                # Priority for progressive passes towards final third
                elif (not self._is_in_final_third() and 
                      teammate.zone.startswith('C') and 
                      teammate.zone > self.zone):  # Moving towards D zones
                    score += 0.4
            
            # Prefer forward passes (general tactical preference)
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
                
            # FINAL THIRD PENETRATION: Extra bonus for attackers in final third
            if (self.final_third_penetration and 
                teammate.position in [Position.ST, Position.CAM, Position.LW, Position.RW] and
                self._is_in_final_third() and teammate.zone.startswith('D')):
                score += 0.6
                
            scores.append(score)
        
        # Choose target with highest score
        best_idx = scores.index(max(scores))
        return teammates[best_idx]
    
    def _move_with_ball(self):
        """Move to an adjacent zone while maintaining possession"""
        adjacent_zones = self.model.field.get_adjacent_zones(self.zone)
        
        if not adjacent_zones:
            return
        
        # FINAL THIRD PENETRATION TACTICS (Home team only)
        if self.final_third_penetration:
            # Prioritize moves that enter final third
            final_third_zones = []
            for zone in adjacent_zones:
                if self._is_final_third_entry(self.zone, zone):
                    final_third_zones.append(zone)
            
            # If we can enter final third, do it!
            if final_third_zones:
                new_zone = random.choice(final_third_zones)
                self.zone = new_zone
                self.model.ball_zone = new_zone
                return
            
            # If already in final third, move towards goal aggressively
            if self._is_in_final_third():
                goal_zones = []
                for zone in adjacent_zones:
                    if self.team == "Home" and zone.startswith('D'):
                        goal_zones.append(zone)
                    elif self.team == "Away" and zone.startswith('A'):
                        goal_zones.append(zone)
                
                if goal_zones:
                    # Prefer central zones for better shooting angles
                    central_zones = [z for z in goal_zones if z.endswith(('2', '3', '4'))]
                    preferred_zones = central_zones if central_zones else goal_zones
                    
                    new_zone = random.choice(preferred_zones)
                    self.zone = new_zone
                    self.model.ball_zone = new_zone
                    return
            
        # Default movement logic - prefer forward direction
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
        
        # FINAL THIRD PENETRATION TACTICS (Home team only)
        if self.final_third_penetration:
            ball_zone = self.model.ball_carrier.zone
            
            # If ball carrier is approaching final third, make aggressive runs
            if (not ball_zone.startswith('D') and 
                self.position in [Position.ST, Position.CAM, Position.LW, Position.RW]):
                
                # Make runs into final third zones
                final_third_zones = ['D1', 'D2', 'D3', 'D4', 'D5']
                available_zones = []
                
                for zone in final_third_zones:
                    occupied = any(agent.zone == zone for agent in self.model.agents 
                                 if isinstance(agent, PlayerAgent) and agent != self)
                    if not occupied:
                        available_zones.append(zone)
                
                if available_zones:
                    # Prefer central zones for strikers and CAMs
                    if self.position in [Position.ST, Position.CAM]:
                        central_zones = [z for z in available_zones if z.endswith(('2', '3', '4'))]
                        preferred_zones = central_zones if central_zones else available_zones
                    # Prefer wide zones for wingers
                    elif self.position == Position.LW:
                        wide_zones = [z for z in available_zones if z.endswith(('1', '2'))]
                        preferred_zones = wide_zones if wide_zones else available_zones
                    elif self.position == Position.RW:
                        wide_zones = [z for z in available_zones if z.endswith(('4', '5'))]
                        preferred_zones = wide_zones if wide_zones else available_zones
                    else:
                        preferred_zones = available_zones
                    
                    self.zone = random.choice(preferred_zones)
                    return
            
            # If ball is in final third, make supporting runs within final third
            elif ball_zone.startswith('D'):
                adjacent_to_ball = self.model.field.get_adjacent_zones(ball_zone)
                final_third_adjacent = [z for z in adjacent_to_ball if z.startswith('D')]
                
                for zone in final_third_adjacent:
                    occupied = any(agent.zone == zone for agent in self.model.agents 
                                 if isinstance(agent, PlayerAgent) and agent != self)
                    if not occupied:
                        self.zone = zone
                        return
        
        # Default support movement - move towards ball carrier or into space
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
    
    def _estimate_dribble_success(self) -> float:
        """Estimate dribble success probability based on opponent density & space ahead"""
        # Base success from player skills
        base_success = self.skills['dribbling']
        
        # Factor 1: Opponent density in current and adjacent zones
        opponent_density = self._get_local_opponent_density()
        
        # Factor 2: Space ahead (attacking direction)
        space_ahead = self._get_space_ahead()
        
        # Factor 3: Current pressure level
        pressure = self._get_current_pressure()
        
        # Factor 4: Final third opportunity (high-value dribbles)
        final_third_potential = self._get_final_third_potential()
        
        # Combined probability calculation
        success_prob = base_success
        success_prob -= opponent_density * 0.3  # Heavy penalty for crowded areas
        success_prob += space_ahead * 0.2       # Bonus for open space ahead
        success_prob -= pressure * 0.15         # Penalty for high pressure
        success_prob += final_third_potential * 0.25  # Bonus for final third entry potential
        
        # Ensure probability is between 0.1 and 0.95
        return max(0.1, min(0.95, success_prob))
    
    def _get_local_opponent_density(self) -> float:
        """Calculate opponent density in current and adjacent zones"""
        zones_to_check = [self.zone] + self.model.field.get_adjacent_zones(self.zone)
        opponent_count = 0
        
        for agent in self.model.agents:
            if (isinstance(agent, PlayerAgent) and 
                agent.team != self.team and 
                agent.zone in zones_to_check):
                opponent_count += 1
        
        # Normalize: 0.0 = no opponents, 1.0 = heavily crowded
        return min(1.0, opponent_count / 3.0)
    
    def _get_space_ahead(self) -> float:
        """Calculate available space in attacking direction"""
        if self.team == "Home":
            # Home attacks towards D zones
            target_zones = []
            current_row = self.zone[0]
            current_col = int(self.zone[1])
            
            # Look for space in forward zones (C, D rows)
            for row in ['C', 'D']:
                for col_offset in [-1, 0, 1]:
                    new_col = current_col + col_offset
                    if 1 <= new_col <= 5:
                        target_zones.append(f"{row}{new_col}")
        else:
            # Away attacks towards A zones
            target_zones = []
            current_row = self.zone[0]
            current_col = int(self.zone[1])
            
            # Look for space in forward zones (B, A rows)
            for row in ['B', 'A']:
                for col_offset in [-1, 0, 1]:
                    new_col = current_col + col_offset
                    if 1 <= new_col <= 5:
                        target_zones.append(f"{row}{new_col}")
        
        # Count free zones ahead
        free_zones = 0
        for zone in target_zones:
            occupied = any(agent.zone == zone for agent in self.model.agents 
                         if isinstance(agent, PlayerAgent))
            if not occupied:
                free_zones += 1
        
        # Normalize: 0.0 = no space, 1.0 = plenty of space
        return min(1.0, free_zones / len(target_zones)) if target_zones else 0.0
    
    def _get_final_third_potential(self) -> float:
        """Calculate potential for dribble to lead to final third entry"""
        if self.team == "Home":
            # Check if dribble could lead to D zones (final third for Home)
            if self.zone.startswith('C'):
                # On the edge of final third - high potential
                return 1.0
            elif self.zone.startswith('B'):
                # Good potential from midfield
                return 0.6
            else:
                # Lower potential from defense
                return 0.2
        else:
            # Away team attacks towards A zones
            if self.zone.startswith('B'):
                return 1.0
            elif self.zone.startswith('C'):
                return 0.6
            else:
                return 0.2
