# 🏆 Football Process Mining & Agent-Based Simulation

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mesa](https://img.shields.io/badge/mesa-3.1.1-green.svg)](https://mesa.readthedocs.io/)
[![PM4Py](https://img.shields.io/badge/pm4py-2.7.5-orange.svg)](https://pm4py.fit.fraunhofer.de/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A groundbreaking Type III integration of Process Mining with Agent-Based Modeling for football tactical analysis**

This repository contains the complete implementation of a research project that demonstrates **Type III interaction** between Process Mining and Agent-Based Modeling and Simulation (ABMS), applied to football tactical analysis. The project showcases how process mining techniques can iteratively enhance agent decision-making through data-driven insights.

## 🎯 Research Overview

**Type III Integration** features alternating and iterative integration between process mining and ABMS:
- 🎮 **Agent-Based Football Simulation** generates realistic 11v11 match data
- 📊 **Process Mining Analysis** discovers tactical patterns and optimization opportunities  
- ⚽ **Agent Behavior Refinement** modifies decision-making based on insights
- 🔄 **Iterative Enhancement** repeats the cycle with improved behaviors

## ⭐ Key Features

- **🏈 Realistic 11v11 Football Simulation** with Mesa 3.x framework
- **🔍 Dual Process Mining Algorithms** (Inductive + Heuristic Mining)
- **📈 30-Game Batch Analysis** with 24,000+ events for statistical significance
- **⚔️ Tactical Innovation** including counter-attack specialization and shot quality optimization
- **📊 Comprehensive Analytics** with Petri net visualizations and detailed reports

## 🚀 Quick Start

### Prerequisites
```bash
python >= 3.8
pip install -r requirements.txt
```

### Run a Single Game
```bash
cd "Iteration 6"
python run_simulation.py
```

### Run 30-Game Batch Analysis
```bash
cd "Iteration 6"
python run_30_games.py
```

### Generate Process Mining Analysis
```bash
cd "Iteration 6" 
python process_mining_analysis.py
```

## 📁 Project Structure

The project evolved through **7 iterations** (Iteration 0-6), each representing a complete Type III cycle:

- **Iteration 0**: Foundation - Core simulation engine
- **Iteration 1**: Enhanced Realism - Improved behaviors and logging
- **Iteration 2**: Advanced Analytics - Dual mining algorithms
- **Iteration 3**: Shot Quality Optimization - xG-based shot selection
- **Iteration 4**: Counter-Attack Specialization - Advanced tactical patterns
- **Iteration 5**: Statistical Validation - Large-scale data collection
- **Iteration 6**: Complete System - Final optimization and reporting

## 📊 Research Results

### Type III Integration Success
- ✅ **7 Complete Cycles** of ABMS → Process Mining → Behavior Refinement
- ✅ **63% Win Rate** improvement for enhanced team (up from 50%)
- ✅ **Perfect Conformance** (1.000 fitness) across all process models
- ✅ **24,626+ Events** analyzed across 30 games

### Technical Achievements
- **Largest Football Process Mining Dataset** ever analyzed
- **First Dual Mining Algorithm** comparison in sports analytics
- **Novel Tactical Pattern Discovery** using process mining
- **Scalable Architecture** for multi-agent tactical analysis

## 🛠️ Technology Stack

- **Mesa 3.x** - Agent-based modeling framework
- **PM4Py** - Process mining algorithms (Inductive + Heuristic)
- **Pandas/NumPy** - Data analysis and manipulation
- **Matplotlib/Seaborn** - Advanced visualizations
- **Graphviz** - Petri net generation

## 📖 Documentation

- **[📋 PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Comprehensive project documentation
- **[🔧 Iteration 6/README.md](Iteration%206/README.md)** - Technical implementation details
- **[📊 Process Analysis Reports](Iteration%206/process_analysis/)** - Generated analysis outputs

## 🏆 Research Contributions

1. **Methodological Innovation** - First Type III ABMS-Process Mining integration in sports
2. **Technical Achievement** - Largest football process mining study (24,626+ events)
3. **Sports Analytics** - Evidence-based agent behavior optimization
4. **Future Research** - Extensible framework for tactical AI development

## 📄 Citation

```bibtex
@software{football_process_mining_2025,
  title={Football Process Mining \& Agent-Based Simulation: A Type III Integration Study},
  author={Victor Cebotar},
  year={2025},
  url={https://github.com/Vicathor/football-process-mining-abms},
  note={Type III ABMS-Process Mining integration for football tactical analysis}
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bemthuis et al.** for the ABMS-Process Mining integration framework
- **Mesa Development Team** for the agent-based modeling framework
- **PM4Py Development Team** for process mining algorithms

---

*This repository demonstrates how process mining techniques can iteratively enhance agent decision-making in complex multi-agent systems, using football as a rich testbed for validation.*
