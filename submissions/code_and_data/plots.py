"""
Visualization Generator for Safe-State Investigation.
Generates publication-quality SVG plots for all 8 experimental figures.

Author: T Bharath (USN: 25BTRCL269)
"""

import os
import csv
from typing import Dict, List

def create_svg_line_chart(title: str, x_label: str, y_label: str, x_vals: List, 
                          series: Dict[str, List[float]], output_path: str, y_max: float = 1.0):
    width, height = 750, 450
    margin_l, margin_r, margin_t, margin_b = 90, 160, 60, 60
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    
    colors = ["#2563EB", "#DC2626", "#059669", "#D97706"]
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background-color: #ffffff; font-family: Segoe UI, Arial, sans-serif;">',
        f'<text x="{width/2}" y="32" font-size="16" font-weight="bold" text-anchor="middle" fill="#1e293b">{title}</text>',
        # Grid and axes
        f'<rect x="{margin_l}" y="{margin_t}" width="{plot_w}" height="{plot_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>'
    ]
    
    # Y-axis ticks
    num_y_ticks = 5
    for i in range(num_y_ticks + 1):
        y_val = (y_max / num_y_ticks) * i
        y_pos = margin_t + plot_h - (i / num_y_ticks) * plot_h
        svg.append(f'<line x1="{margin_l}" y1="{y_pos}" x2="{margin_l + plot_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{margin_l - 12}" y="{y_pos + 4}" font-size="11" text-anchor="end" fill="#64748b">{y_val:.2f}</text>')
        
    # X-axis ticks
    num_x = len(x_vals)
    x_coords = []
    for i, x in enumerate(x_vals):
        x_pos = margin_l + (i / max(1, num_x - 1)) * plot_w if num_x > 1 else margin_l + plot_w / 2
        x_coords.append(x_pos)
        svg.append(f'<line x1="{x_pos}" y1="{margin_t}" x2="{x_pos}" y2="{margin_t + plot_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{x_pos}" y="{margin_t + plot_h + 20}" font-size="11" text-anchor="middle" fill="#64748b">{x}</text>')
        
    # Axis labels
    svg.append(f'<text x="{margin_l + plot_w/2}" y="{height - 15}" font-size="13" font-weight="600" text-anchor="middle" fill="#334155">{x_label}</text>')
    svg.append(f'<text x="25" y="{margin_t + plot_h/2}" font-size="13" font-weight="600" text-anchor="middle" fill="#334155" transform="rotate(-90 25 {margin_t + plot_h/2})">{y_label}</text>')
    
    # Series curves and legend
    leg_x = margin_l + plot_w + 20
    leg_y = margin_t + 20
    
    for s_idx, (name, y_data) in enumerate(series.items()):
        col = colors[s_idx % len(colors)]
        pts = []
        for x_pos, y_val in zip(x_coords, y_data):
            y_clamped = max(0.0, min(y_max, y_val))
            y_pos = margin_t + plot_h - (y_clamped / y_max) * plot_h
            pts.append((x_pos, y_pos))
            
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        svg.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.5" points="{pts_str}"/>')
        for x_pos, y_pos in pts:
            svg.append(f'<circle cx="{x_pos:.1f}" cy="{y_pos:.1f}" r="4.5" fill="{col}" stroke="#ffffff" stroke-width="1.5"/>')
            
        # Legend item
        svg.append(f'<line x1="{leg_x}" y1="{leg_y + s_idx * 24}" x2="{leg_x + 20}" y2="{leg_y + s_idx * 24}" stroke="{col}" stroke-width="3"/>')
        svg.append(f'<circle cx="{leg_x + 10}" cy="{leg_y + s_idx * 24}" r="3.5" fill="{col}"/>')
        svg.append(f'<text x="{leg_x + 28}" y="{leg_y + s_idx * 24 + 4}" font-size="11" fill="#334155">{name}</text>')
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated plot: {output_path}")

def generate_all_plots():
    base_dir = os.path.dirname(__file__)
    
    # Fig 1: P(Unsafe) vs Allocation Pressure (rho)
    create_svg_line_chart(
        title="Fig 1: Probability of Reaching Unsafe State vs. Resource Pressure (rho)",
        x_label="Resource Pressure (rho)",
        y_label="Probability of Reaching Unsafe State P(Unsafe)",
        x_vals=["0.80", "1.00", "1.20", "1.40", "1.60", "2.00"],
        series={
            "Uniform (Low Var)": [0.000, 0.000, 0.000, 0.033, 0.633, 1.000],
            "Bimodal (Whale-Guppy)": [0.000, 0.000, 0.000, 0.600, 0.967, 1.000]
        },
        output_path=os.path.join(base_dir, "fig1_punsafe_pressure.svg"),
        y_max=1.05
    )

    # Fig 2: Mean Time to Unsafe (MTTU) vs Resource Pressure (rho)
    create_svg_line_chart(
        title="Fig 2: Mean Time-to-Unsafe State (MTTU) vs. Resource Pressure (rho)",
        x_label="Resource Pressure (rho)",
        y_label="Mean Time to Unsafe State (MTTU steps)",
        x_vals=["0.80", "1.00", "1.20", "1.40", "1.60", "2.00"],
        series={
            "Uniform (Low Var)": [1000.0, 1000.0, 1000.0, 996.0, 686.1, 164.6],
            "Bimodal (Whale-Guppy)": [1000.0, 1000.0, 1000.0, 671.0, 332.7, 195.1]
        },
        output_path=os.path.join(base_dir, "fig2_mttu_pressure.svg"),
        y_max=1050.0
    )

    # Fig 3: Banker's Denial Rate vs Resource Pressure (rho)
    create_svg_line_chart(
        title="Fig 3: Banker's Deadlock Avoidance Denial Rate vs. Resource Pressure",
        x_label="Resource Pressure (rho)",
        y_label="Request Denial Rate (Fraction Deferred)",
        x_vals=["0.80", "1.00", "1.20", "1.40", "1.60", "2.00"],
        series={
            "Uniform (Low Var)": [0.000, 0.000, 0.000, 0.000, 0.003, 0.120],
            "Bimodal (Whale-Guppy)": [0.000, 0.000, 0.000, 0.016, 0.078, 0.213]
        },
        output_path=os.path.join(base_dir, "fig3_denial_pressure.svg"),
        y_max=0.25
    )

    # Fig 4: System Utilization at First Unsafe State vs Resource Pressure
    create_svg_line_chart(
        title="Fig 4: Resource Utilization at First Unsafe Transition vs. Pressure",
        x_label="Resource Pressure (rho)",
        y_label="Capacity Utilization at First Unsafe State",
        x_vals=["0.80", "1.00", "1.20", "1.40", "1.60", "2.00"],
        series={
            "Uniform (Low Var)": [0.392, 0.491, 0.580, 0.693, 0.906, 0.962],
            "Bimodal (Whale-Guppy)": [0.414, 0.535, 0.621, 0.817, 0.885, 0.812]
        },
        output_path=os.path.join(base_dir, "fig4_util_pressure.svg"),
        y_max=1.05
    )

    # Fig 5: P(Unsafe) vs Concurrency Scale (n)
    create_svg_line_chart(
        title="Fig 5: Probability of Reaching Unsafe State vs. Concurrency Scale (n)",
        x_label="Process Count (n)",
        y_label="Probability of Reaching Unsafe State P(Unsafe)",
        x_vals=["5", "10", "15", "25", "50"],
        series={
            "Uniform (Low Var)": [0.967, 0.067, 0.000, 0.000, 0.000],
            "Bimodal (Whale-Guppy)": [0.967, 0.633, 0.133, 0.000, 0.000]
        },
        output_path=os.path.join(base_dir, "fig5_punsafe_concurrency.svg"),
        y_max=1.05
    )

    # Fig 6: Algorithmic Search Comparisons vs Concurrency Scale (n)
    create_svg_line_chart(
        title="Fig 6: Safety Algorithm Comparisons vs. Concurrency Scale (n)",
        x_label="Process Count (n)",
        y_label="Vector Comparisons per Safety Test",
        x_vals=["5", "10", "15", "25", "50"],
        series={
            "Uniform (Low Var)": [20.3, 40.2, 60.0, 100.0, 200.0],
            "Bimodal (Whale-Guppy)": [24.2, 46.8, 64.2, 100.5, 200.0]
        },
        output_path=os.path.join(base_dir, "fig6_search_cost_concurrency.svg"),
        y_max=220.0
    )

    # Fig 7: P(Unsafe) across Demand Variability Workload Types
    create_svg_line_chart(
        title="Fig 7: Unsafe Probability across Workload Demand Variability (E1)",
        x_label="Workload Distribution Type",
        y_label="Probability of Reaching Unsafe State",
        x_vals=["Uniform", "Normal", "Pareto", "Bimodal"],
        series={
            "Greedy Allocator": [0.000, 0.000, 0.000, 0.133]
        },
        output_path=os.path.join(base_dir, "fig7_punsafe_distributions.svg"),
        y_max=0.20
    )

    # Fig 8: P(Unsafe) and Denial vs Process Holding Duration (tau)
    create_svg_line_chart(
        title="Fig 8: Impact of Holding Duration (tau) on Safety Metrics (Bimodal)",
        x_label="Holding Duration tau (steps)",
        y_label="P(Unsafe) / Denial Rate (Bimodal)",
        x_vals=["1", "3", "6", "10", "16"],
        series={
            "P(Unsafe) [Greedy]": [0.200, 0.167, 0.133, 0.200, 0.200],
            "Banker's Denial Rate": [0.001, 0.001, 0.001, 0.001, 0.002]
        },
        output_path=os.path.join(base_dir, "fig8_hold_duration_effects.svg"),
        y_max=0.25
    )
    print("All 8 figures successfully generated!")

if __name__ == "__main__":
    generate_all_plots()
