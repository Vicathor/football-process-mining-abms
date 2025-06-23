# 🏆 Football Process Mining & Agent-Based Simulation System

A groundbreaking 11v11 football simulation built with **Mesa 3.x** featuring **dual process mining algorithms** for comprehensive tactical analysis. This system combines realistic agent-based modeling with advanced process mining techniques using both **Inductive** and **Heuristic** mining algorithms.

## 🎯 Key Innovation

**World's First Football Process Mining System** with dual mining algorithms:
- ✅ **Inductive Mining**: Structured, guaranteed sound tactical models
- ✅ **Heuristic Mining**: Flexible, frequency-based pattern discovery
- ✅ **Comparative Analysis**: Side-by-side algorithm evaluation
- ✅ **30-Game Batch Processing**: Statistical significance with 24,626+ events

## ⭐ Features

### 🏈 Realistic Football Simulation
- **11v11 gameplay** with authentic player roles and formations
- **Multiple player positions**: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
- **Team formations**: Home (4-3-3) vs Away (4-4-2)
- **Zone-based field**: 4x5 grid system (A1-D5) for tactical analysis

### 🔬 Dual Process Mining Algorithms
- **Inductive Miner**: PM4Py's structured approach with guaranteed soundness
- **Heuristic Miner**: Frequency-based mining capturing complex patterns
- **Algorithm Comparison**: Comprehensive side-by-side analysis
- **Petri Net Generation**: Separate visualizations for each algorithm
- **Batch Analysis**: 30-game datasets for statistical significance

### ⚽ Player Behaviors
- **Individual skills** based on position (passing, shooting, tackling, etc.)
- **Realistic decision-making**: Pass, dribble, shoot based on context
- **Pressure system**: Performance affected by nearby opponents
- **Energy and confidence**: Dynamic stats affecting performance
- **Formation-based positioning**: Players maintain tactical structure

### 📊 Event Logging System
All events are logged with the following schema:
- `possession_id`: Unique possession identifier
- `timestamp`: ISO-8601 formatted timestamp
- `team`: "Home" or "Away"
- `player_id`: Jersey number
- `action`: Event type (Pass, Shot, Tackle, etc.)
- `zone`: Field zone (A1-D5)
- `pressure`: Pressure level (0/1)
- `team_status`: Match status ("Tied", "Leading", "Trailing")
- `outcome`: "Success" or "Failure"
- `xg_change`: Expected goals value

### 🎯 Event Types Logged
**On-ball actions:**
- Pass, Dribble, Shot, Tackle, Clearance, Interception
- BallRecovery, Save, Foul

**Contextual events:**
- PossessionStart, PossessionEnd
- SupportRequest, FormationChange
- Goal, KickOff, MatchEnd

### 📈 Export Formats
- **CSV**: For data analysis and visualization
- **XES**: For process mining with PM4Py

## 🚀 Quick Start

### Single Match Analysis
```bash
# Run a single football match with process mining
python run_simulation.py
```

### 30-Game Batch Analysis (Recommended)
```bash
# Run comprehensive 30-game analysis with dual mining algorithms
python run_30_games.py
```

### Custom Analysis
```python
from process_mining_analysis import FootballProcessMiner

# Initialize analyzer
miner = FootballProcessMiner()

# Run single match analysis with both algorithms
results = miner.run_full_analysis()

# Run batch analysis (30 games) with dual mining
batch_results = miner.run_batch_analysis()
```

## 📊 Generated Outputs

### Process Mining Models
**Inductive Mining Models (PNML):**
- `combined_teams_model.pnml` - All teams combined
- `home_team_model.pnml` - Home team specific patterns
- `away_team_model.pnml` - Away team specific patterns

**Heuristic Mining Models (PNML):**
- `heuristic_combined_teams_model.pnml` - Combined heuristic model
- `heuristic_home_team_model.pnml` - Home team heuristic patterns
- `heuristic_away_team_model.pnml` - Away team heuristic patterns

### Visualizations
**Inductive Mining Petri Nets:**
- `petri_net_combined_teams.png`
- `petri_net_home_team.png`
- `petri_net_away_team.png`

**Heuristic Mining Petri Nets:**
- `heuristic_petri_net_combined_teams.png`
- `heuristic_petri_net_home_team.png`
- `heuristic_petri_net_away_team.png`

### Analysis Reports
- `batch_process_mining_report_[timestamp].md` - Comprehensive dual-algorithm analysis
- `process_analysis_charts.png` - Statistical dashboard
- `process_model.png` - Combined process visualization

### Raw Data
- `football_30games_[timestamp].csv` - Combined match events
- `football_30games_[timestamp].xes` - PM4Py compatible format
- `match_results_[timestamp].csv` - Match outcomes and statistics

## 📈 Performance Metrics

### Recent 30-Game Analysis Results:
```
📊 DATASET SCALE:
- Total Games: 30
- Total Events: 24,626
- Total Possessions: 4,955
- Perfect Conformance: 1.000 fitness

🔬 INDUCTIVE MINING RESULTS:
- Combined Model: 39 places, 56 transitions, 122 arcs
- Home Team: 22 places, 38 transitions, 78 arcs
- Away Team: 20 places, 34 transitions, 70 arcs

⛏️  HEURISTIC MINING RESULTS:
- Combined Model: 32 places, 69 transitions, 150 arcs
- Home Team: 27 places, 68 transitions, 142 arcs
- Away Team: 24 places, 55 transitions, 117 arcs
```

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements.txt

## 🏗️ Project Structure

### Core Simulation Files
```
football_model.py           # Main Mesa 3.x simulation coordinator
player_agent.py            # Individual player AI with position-specific behaviors
football_field.py           # Zone system and tactical positioning
utils_logger.py             # Advanced event logging system
```

### Process Mining & Analysis
```
process_mining_analysis.py  # Dual mining algorithms (Inductive + Heuristic)
generate_petri_net.py      # Petri net visualization generator
batch_simulation.py         # 30-game batch processing system
```

### Execution Scripts
```
run_simulation.py           # Single match with process mining
run_30_games.py            # 30-game batch analysis (Recommended)
```

### Output Directories
```
batch_outputs/             # 30-game datasets and match results
process_analysis/          # All generated models and reports
```

## 🎓 Research Impact

### Academic Contributions
- **First Dual-Mining Football System**: Pioneering combination of inductive and heuristic mining
- **Largest Football Dataset**: 24,626+ events across statistical significant sample size
- **Agent-Based Validation**: Mesa 3.x framework ensures realistic tactical behaviors
- **Comprehensive Benchmarking**: Algorithm comparison framework for sports analytics

### Applications
- **Tactical Analysis**: Identify team-specific patterns and strategies
- **Performance Analytics**: Data-driven insights for coaching decisions
- **Sports Research**: Foundation for advanced football analytics research
- **Process Mining**: Novel application domain for PM4Py algorithms

## 📋 System Requirements
   - Tactical positioning and pressure calculation
   - Field geometry and distance calculations

4. **EventLogger** (`utils_logger.py`)
   - Event recording and management
   - CSV and XES export functionality
   - Process mining compatibility

### Mesa 3.x Features Used
- **Agent-based modeling** with PlayerAgent
- **Model coordination** with automatic step counting
- **AgentSet operations** for team management
- **Data collection** for match statistics
- **Modern API** with proper initialization

## Field Layout

```
D1  D2  D3  D4  D5  ← Away Goal (attacking for Home)
C1  C2  C3  C4  C5  ← Midfield
B1  B2  B3  B4  B5  ← Defensive Third
A1  A2  A3  A4  A5  ← Home Goal (attacking for Away)
```

## Process Mining

The XES output is compatible with PM4Py for advanced process mining analysis:

```python
import pm4py

# Load the exported XES file
log = pm4py.read_xes("match_events.xes")

# Discover process model
model = pm4py.discover_petri_net_inductive(log)

# Analyze possession patterns
possession_patterns = pm4py.get_variants(log)
```

## Tactical Analysis

The simulation enables analysis of:
- **Possession sequences**: From start to end with all intermediate events
- **Passing networks**: Player interaction patterns
- **Zone effectiveness**: Performance by field area
- **Pressure impact**: How defensive pressure affects success rates
- **Formation dynamics**: How team shape influences play

## Configuration

### Match Settings
- Duration: 45 or 90 minutes (configurable)
- Time granularity: 10-second steps
- Random seed: For reproducible results

### Team Formations
- **Home Team**: 4-3-3 (attacking formation)
- **Away Team**: 4-4-2 (balanced formation)

### Skill System
Players have realistic skills based on position:
- **Goalkeepers**: High saving, positioning
- **Defenders**: High tackling, strength
- **Midfielders**: High passing, positioning
- **Attackers**: High shooting, dribbling

## Output Files

Each simulation generates:
- `football_match_YYYYMMDD_HHMMSS.csv`: Event log in CSV format
- `football_match_YYYYMMDD_HHMMSS.xes`: Event log in XES format

## Future Enhancements

This simulation is designed for tactical analysis and process mining. Future extensions could include:
- Machine learning-based player behavior optimization
- Real-time tactical adjustments based on match state
- Advanced formation changes during gameplay
- Player substitutions and fatigue modeling
- Set pieces (corners, free kicks)
- Referee decisions and VAR events

## Process Mining Applications

```bash
# Clone repository
git clone https://github.com/Vicathor/FootballPM_ABMS.git
cd FootballPM_ABMS

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install mesa[rec] pm4py pandas matplotlib seaborn networkx
```

## ⚡ Performance Optimization

### System Specifications
- **Python**: 3.8+ recommended
- **RAM**: 4GB minimum, 8GB+ for 30-game analysis
- **Processing**: Multi-core CPU recommended for batch analysis
- **Storage**: ~50MB for complete 30-game dataset

### Optimization Tips
- Use `run_30_games.py` for comprehensive analysis
- Single games complete in ~1 second
- 30-game batch processes in ~17 seconds
- Results cached for repeated analysis

## 🔍 Algorithm Comparison

### Inductive Mining
- **Guarantees**: Sound and complete process models
- **Approach**: Structured divide-and-conquer algorithm
- **Best For**: Formal verification and compliance checking
- **Output**: Clean, hierarchical process structures

### Heuristic Mining
- **Approach**: Frequency-based pattern mining
- **Flexibility**: Handles noise and incomplete data better
- **Best For**: Discovering complex, real-world patterns
- **Output**: More detailed transition networks

### Combined Benefits
Using both algorithms provides:
- **Comprehensive Coverage**: Different perspectives on same data
- **Pattern Validation**: Cross-algorithm verification
- **Tactical Depth**: Both structured and flexible insights
- **Research Robustness**: Multiple analytical approaches

## 📊 Use Cases

The generated process mining models can be used for:
- **Tactical Analysis**: Understanding team-specific attack/defense patterns
- **Performance Optimization**: Identifying successful vs unsuccessful sequences
- **Strategic Planning**: Data-driven tactical preparation
- **Player Development**: Individual role analysis within team play
- **Match Prediction**: Forecasting outcomes based on process patterns
- **Coaching Intelligence**: Evidence-based tactical recommendations

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🎯 Citation

If you use this system in your research, please cite:

```bibtex
@software{football_process_mining_2025,
  title={Football Process Mining & Agent-Based Simulation System},
  author={Football Analytics Research Team},
  year={2025},
  url={https://github.com/Vicathor/FootballPM_ABMS},
  note={Dual mining algorithms for football tactical analysis}
}
```

---

**🏆 Achievement**: World's first football simulation system with dual process mining algorithms, providing unprecedented tactical intelligence through complementary analytical approaches.
