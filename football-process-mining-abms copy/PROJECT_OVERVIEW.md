# 🏆 Football Process Mining & Agent-Based Simulation: A Type III Integration Study

## 📋 Executive Summary

This repository contains the complete implementation of a groundbreaking research project that integrates **Process Mining** with **Agent-Based Modeling and Simulation (ABMS)** applied to football tactical analysis. The project demonstrates **Type III interaction** as defined by Bemthuis, featuring alternating and iterative integration between process mining and ABMS to enhance agent decision-making through data-driven tactical insights.

### 🎯 Research Objective

*"This thesis explores how process mining techniques can iteratively enhance agent decision-making in football simulations, focusing on improving tactical patterns. This research develops a feedback loop that refines agent behavior over successive simulations by simulating football scenarios, generating detailed event logs of player actions, and applying process mining methods such as discovery and conformance checking."*

---

## 🔬 Type III Integration Implementation

### **What is Type III Integration?**

**Type III** represents an **alternating interaction** with these characteristics:

- **Sequential Progression**: Sequential execution of both process mining and ABMS modules
- **Mutual Interdependence**: Both processes are mutually interdependent and can be invoked repeatedly
- **Iterative Approach**: Each iteration involves complete or partial execution of both techniques
- **Feedback Loop**: ABMS output serves as input for process mining, which identifies patterns to guide the next simulation run

### **Our Implementation**

This project implements a complete Type III cycle:

1. **🎮 Agent-Based Football Simulation** → Generates realistic match data with 11v11 gameplay
2. **📊 Event Log Generation** → Converts simulation data to process mining compatible format
3. **🔍 Process Mining Analysis** → Discovers tactical patterns and identifies optimization opportunities
4. **⚽ Agent Behavior Refinement** → Modifies agent decision-making based on process mining insights
5. **🔄 Iterative Enhancement** → Repeats the cycle with improved agent behaviors

---

## 🗂️ Project Structure & Iterations

The project evolved through **7 iterations** (Iteration 0-6), with each iteration representing a complete Type III cycle. Each iteration contains identical core files but with progressively enhanced agent behaviors based on process mining insights.

### **Core Components (Present in All Iterations)**

```
📁 Iteration X/
├── 🏆 football_model.py          # Main Mesa 3.x simulation engine
├── ⚽ player_agent.py            # Individual player AI with position-specific behaviors
├── 🏟️ football_field.py           # Zone-based field system (A1-D5 grid)
├── 📝 utils_logger.py            # Event logging system (CSV + XES export)
├── 🔍 process_mining_analysis.py # Dual algorithm process mining (Inductive + Heuristic)
├── 🎯 run_simulation.py          # Single game execution
├── 📊 batch_simulation.py        # 30-game batch processing
├── 🧪 run_30_games.py            # Statistical validation runner
├── 🛠️ requirements.txt           # Python dependencies
├── 📋 PROJECT_SUMMARY.md         # Iteration summary
├── 📖 README.md                  # Technical documentation
└── 📁 process_analysis/          # Generated reports and visualizations
    ├── 📈 *.png                  # Petri net visualizations
    ├── 📊 *.csv                  # Event logs
    ├── 🗂️ *.pnml                 # Process models
    └── 📄 *.md                   # Analysis reports
```

### **Iteration Evolution Timeline**

#### **🔧 Iteration 0: Foundation**
- **Focus**: Core simulation engine development
- **Achievement**: Mesa 3.x compliant 11v11 football simulation
- **Process Mining**: Basic inductive mining implementation
- **Agent Behavior**: Standard position-based behaviors

#### **⚙️ Iteration 1: Enhanced Realism**
- **Focus**: Improved player behaviors and event logging
- **Achievement**: Comprehensive event schema with xG integration
- **Process Mining**: Team-specific model discovery
- **Agent Behavior**: Energy and confidence systems

#### **📊 Iteration 2: Advanced Analytics**
- **Focus**: Dual mining algorithm implementation
- **Achievement**: Both Inductive and Heuristic mining
- **Process Mining**: Comparative algorithm analysis
- **Agent Behavior**: Pressure-based decision making

#### **🎯 Iteration 3: Shot Quality Optimization**
- **Focus**: Data-driven shot selection improvement
- **Achievement**: xG-based shot quality filter for Home team
- **Process Mining**: "FinalThirdEntry → Shot" pattern analysis
- **Agent Behavior**: Home team discouraged from low-xG shots (< 0.07)
- **Key Innovation**: First asymmetric tactical modification

#### **⚔️ Iteration 4: Counter-Attack Specialization**
- **Focus**: Advanced tactical pattern implementation
- **Achievement**: Counter-attack capabilities for Home team
- **Process Mining**: New event types (CounterAttackShot, CounterAttackPass)
- **Agent Behavior**: +8.0 pass/dribble bonuses, +4.8 shot bonuses during counter-attacks
- **Results**: Home team 63% win rate, +29 goal differential

#### **🔬 Iteration 5: Statistical Validation**
- **Focus**: Large-scale data collection and validation
- **Achievement**: 30-game batch processing with 24,000+ events
- **Process Mining**: Statistical significance validation
- **Agent Behavior**: Refined counter-attack patterns

#### **🏆 Iteration 6: Complete Dual Mining System**
- **Focus**: Final optimization and comprehensive reporting
- **Achievement**: Publication-ready dual algorithm analysis
- **Process Mining**: Side-by-side Inductive vs Heuristic comparison
- **Agent Behavior**: Optimized tactical behaviors based on 6 iterations of refinement

---

## 🔬 Technical Innovation

### ** Football Simulation Engine**
- **Framework**: Mesa Agent-Based Modeling
- **Scale**: 11v11 realistic gameplay
- **Positions**: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
- **Formations**: Home (4-3-3) vs Away (4-4-2)
- **Field System**: 4x5 zone grid (A1-D5) for tactical analysis

### **📊 Comprehensive Event Logging**
```python
Event Schema:
- possession_id: Unique possession identifier
- timestamp: ISO-8601 formatted timestamp  
- team: "Home" or "Away"
- player_id: Jersey number
- action: Event type (Pass, Shot, Tackle, etc.)
- zone: Field zone (A1-D5)
- pressure: Pressure level (0/1)
- team_status: Match status ("Tied", "Leading", "Trailing")
- outcome: "Success" or "Failure"
- xg_change: Expected goals value
```

### **🔍 Dual Process Mining Algorithms**
- **Inductive Miner**: PM4Py's structured approach with guaranteed soundness
- **Heuristic Miner**: Frequency-based mining capturing complex patterns
- **Outputs**: Petri nets, PNML models, comprehensive analysis reports
- **Team Analysis**: Separate models for Home, Away, and Combined teams

### **⚽ Advanced Agent Behaviors**
- **Individual Skills**: Position-specific passing, shooting, tackling abilities
- **Dynamic Stats**: Energy, confidence, and pressure systems
- **Tactical Awareness**: Formation maintenance and team coordination
- **Learning Mechanism**: Behavior refinement based on process mining insights

---

## 📈 Key Research Findings

### **🎯 Type III Integration Success**
- **7 Complete Cycles**: Each iteration demonstrated full ABMS → Process Mining → Behavior Refinement
- **Measurable Improvements**: Home team performance increased from 50% to 63% win rate
- **Pattern Discovery**: Process mining successfully identified "FinalThirdEntry → Shot" optimization opportunities
- **Behavioral Adaptation**: Agents successfully adapted to data-driven tactical insights

### **📊 Statistical Validation**
- **Dataset Scale**: 24,626+ events across 30 games 
- **Model Complexity**: Up to 69 transitions in heuristic models
- **Algorithmic Comparison**: Inductive vs Heuristic mining revealed complementary insights

### **⚔️ Tactical Innovation**
- **Counter-Attack Implementation**: 10 successful counter-attack sequences logged
- **Shot Quality Filter**: 47% reduction in low-xG shots for modified team
- **Process Pattern Changes**: +9.3% increase in transition complexity for enhanced team
- **Asymmetric Behavior**: Successfully created measurable tactical differences between teams

---

## 🏆 Research Contributions

### **1. Methodological Innovation**
- First implementation of Type III ABMS-Process Mining integration in sports
- Novel dual mining algorithm approach for tactical analysis
- Scalable framework for iterative agent behavior refinement

### **2. Technical Achievements**
- Mesa compliant football simulation with 22 player agents
- Comprehensive event logging system with PM4Py integration
- Automated batch processing for statistical significance

### **3. Sports Analytics Advancement**
- Evidence-based approach to agent behavior optimization

### **4. Future Research Foundation**
- Extensible framework for other team sports
- Template for Type III integration in complex multi-agent systems
- Basis for advanced tactical AI development

---

## 🛠️ Technology Stack

### **Core Dependencies**
```python
mesa==3.1.1              # Agent-based modeling framework
pm4py==2.7.5             # Process mining algorithms
pandas==2.1.3            # Data manipulation
numpy==1.24.3            # Numerical computing
matplotlib==3.7.2        # Visualization
seaborn==0.12.2          # Statistical plotting
graphviz==0.20.1         # Petri net generation
python-dateutil==2.8.2   # Date handling
```

### **Output Formats**
- **CSV**: Raw event logs for analysis
- **XES**: IEEE standard for process mining
- **PNML**: Petri Net Markup Language
- **PNG**: High-quality visualizations
- **Markdown**: Comprehensive reports

---

## 🎯 Usage Instructions

### **Single Game Simulation**
```bash
cd "Iteration 6"
python run_simulation.py
```

### **30-Game Batch Analysis**
```bash
cd "Iteration 6" 
python run_30_games.py
```

### **Process Mining Analysis**
```bash
cd "Iteration 6"
python process_mining_analysis.py
```

## 🔮 Future Research Opportunities

### **Immediate Extensions**
1. **Multi-Iteration Learning**: Implement memory across iterations for cumulative learning
2. **Real-Time Adaptation**: Dynamic tactical adjustments during single matches
3. **Multi-Objective Optimization**: Balance multiple tactical goals simultaneously

### **Advanced Applications**
1. **Player Development**: Model individual player skill progression
2. **Opponent Modeling**: Adaptive strategies based on opponent analysis
3. **Formation Evolution**: Dynamic formation changes based on match state

### **Broader Applications**
1. **Other Sports**: Basketball, rugby, hockey tactical analysis
2. **Business Processes**: Team coordination in organizational settings
3. **Military Strategy**: Multi-agent tactical coordination

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

*This repository represents a complete Type III integration study, demonstrating how process mining techniques can iteratively enhance agent decision-making in complex multi-agent systems. The football domain provides a rich, realistic testbed for validating the effectiveness of this integration approach.*
