"""
Analysis and Statistical Aggregation for Safe-State Investigation.

Author: T Bharath (USN: 25BTRCL269)
"""

import os
import csv
import math
from collections import defaultdict

def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0

def std_err(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    variance = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
    return math.sqrt(variance / len(vals))

def ci95(vals):
    return 1.96 * std_err(vals)

def run_analysis():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "raw_results.csv")
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Loaded {len(rows)} raw experiment records.")
    
    groups = defaultdict(list)
    for r in rows:
        key = (r["experiment"], r["param_name"], r["param_value"])
        groups[key].append(r)
        
    summary_rows = []
    
    print("\n" + "=" * 105)
    print("EXPERIMENT 1: DEMAND VARIABILITY TYPE (E1: n=15, m=3, rho=1.30, hold=6, 1000 events)")
    print("=" * 105)
    print(f"{'Dist':<10} | {'P(Unsafe)':<12} | {'MTTU (steps)':<14} | {'Util @ Unsafe':<14} | {'Unsafe Frac':<13} | {'Bankers Denial':<15} | {'Comps':<8}")
    print("-" * 105)
    
    for dist in ["uniform", "normal", "bimodal", "pareto"]:
        k = ("E1", "distribution", dist)
        items = groups[k]
        p_unsafe = mean([float(x["greedy_unsafe"]) for x in items])
        p_unsafe_ci = ci95([float(x["greedy_unsafe"]) for x in items])
        mttu = mean([float(x["greedy_mttu"]) for x in items])
        mttu_ci = ci95([float(x["greedy_mttu"]) for x in items])
        util_un = mean([float(x["greedy_util_first_unsafe"]) for x in items])
        util_un_ci = ci95([float(x["greedy_util_first_unsafe"]) for x in items])
        unsafe_frac = mean([float(x["greedy_unsafe_frac"]) for x in items])
        denial = mean([float(x["bankers_denial_rate"]) for x in items])
        denial_ci = ci95([float(x["bankers_denial_rate"]) for x in items])
        comps = mean([float(x["greedy_comps"]) for x in items])
        
        print(f"{dist:<10} | {p_unsafe:.3f}±{p_unsafe_ci:.3f}   | {mttu:6.1f}±{mttu_ci:4.1f}   | {util_un:.3f}±{util_un_ci:.3f}  | {unsafe_frac:.3f}         | {denial:.3f}±{denial_ci:.3f}   | {comps:6.1f}")
        
        summary_rows.append({
            "experiment": "E1",
            "condition": dist,
            "p_unsafe": round(p_unsafe, 4),
            "p_unsafe_ci": round(p_unsafe_ci, 4),
            "mttu": round(mttu, 2),
            "mttu_ci": round(mttu_ci, 2),
            "util_first_unsafe": round(util_un, 4),
            "util_first_unsafe_ci": round(util_un_ci, 4),
            "unsafe_fraction": round(unsafe_frac, 4),
            "bankers_denial_rate": round(denial, 4),
            "bankers_denial_ci": round(denial_ci, 4),
            "comps": round(comps, 2)
        })
        
    print("\n" + "=" * 105)
    print("EXPERIMENT 2: RESOURCE ALLOCATION PRESSURE (RHO) SWEEP (E2: n=15, m=3, hold=6)")
    print("=" * 105)
    print(f"{'Workload':<10} | {'Rho':<6} | {'P(Unsafe)':<12} | {'MTTU (steps)':<14} | {'Util @ Unsafe':<14} | {'Bankers Denial':<15} | {'Comps':<8}")
    print("-" * 105)
    
    for dist in ["uniform", "bimodal"]:
        for rho in ["0.8", "1.0", "1.2", "1.4", "1.6", "2.0"]:
            k = ("E2", f"{dist}_rho", rho)
            items = groups[k]
            p_unsafe = mean([float(x["greedy_unsafe"]) for x in items])
            p_unsafe_ci = ci95([float(x["greedy_unsafe"]) for x in items])
            mttu = mean([float(x["greedy_mttu"]) for x in items])
            util_un = mean([float(x["greedy_util_first_unsafe"]) for x in items])
            denial = mean([float(x["bankers_denial_rate"]) for x in items])
            denial_ci = ci95([float(x["bankers_denial_rate"]) for x in items])
            comps = mean([float(x["greedy_comps"]) for x in items])
            
            print(f"{dist:<10} | {rho:<6} | {p_unsafe:.3f}±{p_unsafe_ci:.3f}   | {mttu:6.1f}         | {util_un:.3f}         | {denial:.3f}±{denial_ci:.3f}   | {comps:6.1f}")
            
            summary_rows.append({
                "experiment": "E2",
                "condition": f"{dist}_rho_{rho}",
                "p_unsafe": round(p_unsafe, 4),
                "p_unsafe_ci": round(p_unsafe_ci, 4),
                "mttu": round(mttu, 2),
                "mttu_ci": 0.0,
                "util_first_unsafe": round(util_un, 4),
                "util_first_unsafe_ci": 0.0,
                "unsafe_fraction": 0.0,
                "bankers_denial_rate": round(denial, 4),
                "bankers_denial_ci": round(denial_ci, 4),
                "comps": round(comps, 2)
            })

    print("\n" + "=" * 105)
    print("EXPERIMENT 3: CONCURRENCY SCALE (N) (E3: rho=1.30, hold=6)")
    print("=" * 105)
    print(f"{'Workload':<10} | {'N':<4} | {'P(Unsafe)':<12} | {'MTTU':<10} | {'Search Comps (O(m*n^2))':<24} | {'Bankers Denial':<15}")
    print("-" * 105)
    for dist in ["uniform", "bimodal"]:
        for n_val in ["5", "10", "15", "25", "50"]:
            k = ("E3", f"{dist}_n", n_val)
            items = groups[k]
            p_unsafe = mean([float(x["greedy_unsafe"]) for x in items])
            mttu = mean([float(x["greedy_mttu"]) for x in items])
            comps = mean([float(x["greedy_comps"]) for x in items])
            comps_ci = ci95([float(x["greedy_comps"]) for x in items])
            denial = mean([float(x["bankers_denial_rate"]) for x in items])
            denial_ci = ci95([float(x["bankers_denial_rate"]) for x in items])
            
            print(f"{dist:<10} | {n_val:<4} | {p_unsafe:.3f}        | {mttu:6.1f}     | {comps:6.1f}±{comps_ci:4.1f}            | {denial:.3f}±{denial_ci:.3f}")
            
            summary_rows.append({
                "experiment": "E3",
                "condition": f"{dist}_n_{n_val}",
                "p_unsafe": round(p_unsafe, 4),
                "p_unsafe_ci": 0.0,
                "mttu": round(mttu, 2),
                "mttu_ci": 0.0,
                "util_first_unsafe": 0.0,
                "util_first_unsafe_ci": 0.0,
                "unsafe_fraction": 0.0,
                "bankers_denial_rate": round(denial, 4),
                "bankers_denial_ci": round(denial_ci, 4),
                "comps": round(comps, 2)
            })

    print("\n" + "=" * 105)
    print("EXPERIMENT 4: PROCESS HOLDING DURATION (TAU) (E4: n=15, rho=1.30)")
    print("=" * 105)
    print(f"{'Workload':<10} | {'Hold (tau)':<10} | {'P(Unsafe)':<12} | {'MTTU':<10} | {'Util @ Unsafe':<14} | {'Bankers Denial':<15}")
    print("-" * 105)
    for dist in ["uniform", "bimodal"]:
        for hold_val in ["1", "3", "6", "10", "16"]:
            k = ("E4", f"{dist}_hold", hold_val)
            items = groups[k]
            p_unsafe = mean([float(x["greedy_unsafe"]) for x in items])
            mttu = mean([float(x["greedy_mttu"]) for x in items])
            util_un = mean([float(x["greedy_util_first_unsafe"]) for x in items])
            denial = mean([float(x["bankers_denial_rate"]) for x in items])
            denial_ci = ci95([float(x["bankers_denial_rate"]) for x in items])
            
            print(f"{dist:<10} | {hold_val:<10} | {p_unsafe:.3f}        | {mttu:6.1f}     | {util_un:.3f}         | {denial:.3f}±{denial_ci:.3f}")
            
            summary_rows.append({
                "experiment": "E4",
                "condition": f"{dist}_hold_{hold_val}",
                "p_unsafe": round(p_unsafe, 4),
                "p_unsafe_ci": 0.0,
                "mttu": round(mttu, 2),
                "mttu_ci": 0.0,
                "util_first_unsafe": round(util_un, 4),
                "util_first_unsafe_ci": 0.0,
                "unsafe_fraction": 0.0,
                "bankers_denial_rate": round(denial, 4),
                "bankers_denial_ci": round(denial_ci, 4),
                "comps": 0.0
            })

    # Paired differences analysis: Bimodal vs Uniform on identical streams
    print("\n" + "=" * 105)
    print("PAIRED DIFFERENCES: Bimodal minus Uniform (Identical 30 Seeds)")
    print("=" * 105)
    paired_configs = [
        ("Base Case (rho=1.30, n=15, tau=6)", "E1", "distribution", "bimodal", "uniform"),
        ("Moderate Pressure (rho=1.20, n=15, tau=6)", "E2", "rho", "1.2", "1.2"),
        ("Overload Pressure (rho=1.60, n=15, tau=6)", "E2", "rho", "1.6", "1.6"),
        ("Extreme Pressure (rho=2.00, n=15, tau=6)", "E2", "rho", "2.0", "2.0"),
        ("Low Scale (n=5, rho=1.30, tau=6)", "E3", "n", "5", "5"),
        ("High Scale (n=50, rho=1.30, tau=6)", "E3", "n", "50", "50"),
        ("Long Holding Time (tau=16, rho=1.30, n=15)", "E4", "hold", "16", "16"),
    ]
    
    print(f"{'Configuration':<42} | {'Delta P(Unsafe)':<18} | {'Delta MTTU':<18} | {'Delta Denial Rate':<18}")
    print("-" * 105)
    
    for label, exp, ptype, val_bim, val_uni in paired_configs:
        if exp == "E1":
            b_items = groups[(exp, "distribution", val_bim)]
            u_items = groups[(exp, "distribution", val_uni)]
        elif exp == "E2":
            b_items = groups[(exp, f"bimodal_{ptype}", val_bim)]
            u_items = groups[(exp, f"uniform_{ptype}", val_uni)]
        elif exp == "E3":
            b_items = groups[(exp, f"bimodal_{ptype}", val_bim)]
            u_items = groups[(exp, f"uniform_{ptype}", val_uni)]
        elif exp == "E4":
            b_items = groups[(exp, f"bimodal_{ptype}", val_bim)]
            u_items = groups[(exp, f"uniform_{ptype}", val_uni)]
            
        delta_p = [float(b["greedy_unsafe"]) - float(u["greedy_unsafe"]) for b, u in zip(b_items, u_items)]
        delta_mttu = [float(b["greedy_mttu"]) - float(u["greedy_mttu"]) for b, u in zip(b_items, u_items)]
        delta_den = [float(b["bankers_denial_rate"]) - float(u["bankers_denial_rate"]) for b, u in zip(b_items, u_items)]
        
        m_dp, ci_dp = mean(delta_p), ci95(delta_p)
        m_dm, ci_dm = mean(delta_mttu), ci95(delta_mttu)
        m_dd, ci_dd = mean(delta_den), ci95(delta_den)
        
        worse_count = sum(1 for d in delta_mttu if d < 0)
        
        print(f"{label:<42} | {m_dp:+.3f} ± {ci_dp:.3f}     | {m_dm:+6.1f} ± {ci_dm:4.1f}    | {m_dd:+.3f} ± {ci_dd:.3f}")

    # Save summary_means.csv
    out_path = os.path.join(base_dir, "summary_means.csv")
    with open(out_path, "w", newline="") as f:
        fieldnames = ["experiment", "condition", "p_unsafe", "p_unsafe_ci", "mttu", "mttu_ci", 
                      "util_first_unsafe", "util_first_unsafe_ci", "unsafe_fraction", 
                      "bankers_denial_rate", "bankers_denial_ci", "comps"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\nSaved summary means to {out_path}")

if __name__ == "__main__":
    run_analysis()
