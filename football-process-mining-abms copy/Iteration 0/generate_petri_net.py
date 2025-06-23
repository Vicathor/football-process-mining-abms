#!/usr/bin/env python3
"""
Enhanced Petri Net Generator for Football Process Mining
Generates high-quality Petri net visualizations from inductive miner results
"""

import pm4py
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

def generate_petri_net_visualizations():
    """Generate comprehensive Petri net visualizations"""
    print("🎯 GENERATING PETRI NET VISUALIZATIONS")
    print("=" * 50)
    
    # Load the latest match data
    print("📊 Loading match data...")
    xes_files = list(Path('output').glob('*.xes'))
    if not xes_files:
        print("❌ No XES files found in output directory")
        return
    
    latest_xes = max(xes_files, key=os.path.getctime)
    print(f"📁 Loading: {latest_xes.name}")
    
    # Load XES event log
    event_log = pm4py.read_xes(str(latest_xes))
    print(f"✅ Loaded {len(event_log)} possession traces")
    
    # Apply inductive miner
    print("\n🔬 Applying inductive miner algorithm...")
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(event_log)
    
    print(f"✅ Process model discovered!")
    print(f"   📍 Places (states): {len(net.places)}")
    print(f"   🔄 Transitions (activities): {len(net.transitions)}")
    print(f"   ➡️  Arcs (connections): {len(net.arcs)}")
    
    # Create output directory
    os.makedirs('process_analysis', exist_ok=True)
    
    # Save model in multiple formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Save PNML (Petri Net Markup Language) file
    pnml_path = f'process_analysis/football_inductive_model_{timestamp}.pnml'
    pm4py.write_pnml(net, initial_marking, final_marking, pnml_path)
    print(f"💾 PNML model saved: {pnml_path}")
    
    # 2. Generate PNG visualization (high quality)
    try:
        png_path = f'process_analysis/football_petri_net_{timestamp}.png'
        pm4py.save_vis_petri_net(net, initial_marking, final_marking, png_path)
        print(f"🖼️  PNG visualization saved: {png_path}")
    except Exception as e:
        print(f"⚠️  PNG generation failed: {e}")
    
    # 3. Generate SVG visualization (vector format)
    try:
        svg_path = f'process_analysis/football_petri_net_{timestamp}.svg'
        pm4py.save_vis_petri_net(net, initial_marking, final_marking, svg_path)
        print(f"🖼️  SVG visualization saved: {svg_path}")
    except Exception as e:
        print(f"⚠️  SVG generation failed: {e}")
    
    # 4. Generate detailed model statistics
    print(f"\n📈 PROCESS MODEL STATISTICS")
    print("=" * 50)
    
    # Analyze transitions (activities)
    print(f"🔄 Activities in the model:")
    for i, transition in enumerate(sorted(net.transitions, key=lambda t: str(t.label or t.name)), 1):
        label = transition.label or transition.name or f"tau_{i}"
        if transition.label:  # Visible transition
            print(f"   {i:2d}. {label}")
        else:  # Silent transition (tau)
            print(f"   {i:2d}. [τ{i}] (silent transition)")
    
    # Count visible vs silent transitions
    visible_transitions = [t for t in net.transitions if t.label]
    silent_transitions = [t for t in net.transitions if not t.label]
    
    print(f"\n📊 Transition Analysis:")
    print(f"   Visible transitions: {len(visible_transitions)}")
    print(f"   Silent transitions (τ): {len(silent_transitions)}")
    
    # Analyze places
    print(f"\n📍 Places Analysis:")
    print(f"   Total places: {len(net.places)}")
    print(f"   Initial marking: {len(initial_marking)} tokens")
    print(f"   Final marking: {len(final_marking)} tokens")
    
    # Model complexity metrics
    print(f"\n🔍 Model Complexity Metrics:")
    print(f"   Nodes (places + transitions): {len(net.places) + len(net.transitions)}")
    print(f"   Edges (arcs): {len(net.arcs)}")
    print(f"   Connectivity density: {len(net.arcs) / (len(net.places) + len(net.transitions)):.2f}")
    
    # Generate summary report
    report_path = f'process_analysis/petri_net_report_{timestamp}.md'
    with open(report_path, 'w') as f:
        f.write(f"# Football Petri Net Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Source:** {latest_xes.name}\n")
        f.write(f"**Algorithm:** Inductive Miner\n\n")
        
        f.write(f"## Model Structure\n\n")
        f.write(f"- **Places:** {len(net.places)} (process states)\n")
        f.write(f"- **Transitions:** {len(net.transitions)} ({len(visible_transitions)} visible, {len(silent_transitions)} silent)\n")
        f.write(f"- **Arcs:** {len(net.arcs)} (flow connections)\n")
        f.write(f"- **Traces Analyzed:** {len(event_log)} possession sequences\n\n")
        
        f.write(f"## Activity Coverage\n\n")
        f.write(f"The Petri net model captures the following football activities:\n\n")
        for transition in sorted(visible_transitions, key=lambda t: t.label):
            f.write(f"- {transition.label}\n")
        
        f.write(f"\n## Model Interpretation\n\n")
        f.write(f"This Petri net represents the discovered process model for football possessions. ")
        f.write(f"Each place represents a state in the possession flow, while transitions represent ")
        f.write(f"the actual football events (Pass, Shot, Tackle, etc.). The model shows:\n\n")
        f.write(f"1. **Sequential Flow:** How events follow each other in typical possessions\n")
        f.write(f"2. **Parallel Behavior:** Activities that can occur simultaneously\n")
        f.write(f"3. **Choice Points:** Where teams can choose between different actions\n")
        f.write(f"4. **Loop Structures:** Repeating patterns in possession sequences\n\n")
        
        f.write(f"## Files Generated\n\n")
        f.write(f"- `{os.path.basename(pnml_path)}` - PNML model file\n")
        f.write(f"- `football_petri_net_{timestamp}.png` - PNG visualization\n")
        f.write(f"- `football_petri_net_{timestamp}.svg` - SVG visualization\n")
        f.write(f"- `petri_net_report_{timestamp}.md` - This report\n")
    
    print(f"📋 Report generated: {report_path}")
    
    print(f"\n🎉 PETRI NET GENERATION COMPLETE!")
    print(f"📁 All files saved in: process_analysis/")
    print(f"🖼️  View your Petri net: football_petri_net_{timestamp}.png")
    
    return {
        'net': net,
        'initial_marking': initial_marking,
        'final_marking': final_marking,
        'files_generated': [pnml_path, f'process_analysis/football_petri_net_{timestamp}.png', report_path]
    }

if __name__ == "__main__":
    generate_petri_net_visualizations()
