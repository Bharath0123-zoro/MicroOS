"""
Safe-State Analysis: Effect of Resource-Demand Variability on the Probability
of Reaching an Unsafe State.

Author: T Bharath (USN: 25BTRCL269)
Course: Operating Systems - CA-2: OS Performance Investigation
"""

import sys
import os
import math
import random
import csv
import time
from typing import List, Tuple, Dict, Any

# =====================================================================
# 1. Banker's Algorithm Safety Engine
# =====================================================================

class BankersEngine:
    @staticmethod
    def is_safe(available: List[int], allocation: List[List[int]], max_matrix: List[List[int]]) -> Tuple[bool, List[int], int]:
        """
        Dijkstra's Banker's Algorithm Safety Verification.
        Returns:
            (is_safe: bool, safe_sequence: List[int], comparisons: int)
        """
        n = len(allocation)
        m = len(available)
        
        work = list(available)
        finish = [False] * n
        safe_seq = []
        comparisons = 0
        
        while len(safe_seq) < n:
            found = False
            for i in range(n):
                if not finish[i]:
                    comparisons += 1
                    # Vector inequality check: Need[i] <= Work
                    can_finish = True
                    for j in range(m):
                        comparisons += 1
                        need_j = max_matrix[i][j] - allocation[i][j]
                        if need_j > work[j]:
                            can_finish = False
                            break
                    if can_finish:
                        for j in range(m):
                            work[j] += allocation[i][j]
                        finish[i] = True
                        safe_seq.append(i)
                        found = True
                        break
            if not found:
                break
                
        return (len(safe_seq) == n, safe_seq, comparisons)

# =====================================================================
# 2. Resource Demand Distributions
# =====================================================================

def generate_demands(dist_type: str, n: int, m: int, total_capacity: List[int], rho: float, rng: random.Random) -> List[List[int]]:
    """
    Generates Max claim matrix according to target variability distribution and pressure rho.
    Total nominal claim per resource type j: D_j = rho * total_capacity[j].
    Mean claim per process: mu_j = D_j / n.
    """
    max_matrix = [[0] * m for _ in range(n)]
    
    for j in range(m):
        target_total = rho * total_capacity[j]
        mean_val = target_total / n
        raw_vals = []
        
        if dist_type == "uniform":
            # Low variability: Uniform [0.75 * mean, 1.25 * mean], CV ~ 0.14
            low = max(1.0, 0.75 * mean_val)
            high = 1.25 * mean_val
            raw_vals = [rng.uniform(low, high) for _ in range(n)]
            
        elif dist_type == "normal":
            # Moderate variability: Truncated Gaussian (mu, sigma=0.35*mu), clipped [1, 2*mu]
            sigma = 0.35 * mean_val
            for _ in range(n):
                val = rng.gauss(mean_val, sigma)
                val = max(1.0, min(2.0 * mean_val, val))
                raw_vals.append(val)
                
        elif dist_type == "bimodal":
            # High variability (Whale-Guppy): 80% light claims (0.25*mu), 20% heavy claims (4.0*mu)
            # E[X] = 0.8 * 0.25*mu + 0.2 * 4.0*mu = 1.0 * mu
            for _ in range(n):
                if rng.random() < 0.80:
                    val = rng.uniform(0.15 * mean_val, 0.35 * mean_val)
                else:
                    val = rng.uniform(3.50 * mean_val, 4.50 * mean_val)
                raw_vals.append(max(1.0, val))
                
        elif dist_type == "pareto":
            # Heavy-tailed Power Law: Bounded Pareto shape alpha = 1.6
            alpha = 1.6
            for _ in range(n):
                u = rng.random()
                val = (1.0 - u) ** (-1.0 / alpha)
                raw_vals.append(val)
            scale = mean_val / (sum(raw_vals) / n)
            raw_vals = [max(1.0, v * scale) for v in raw_vals]
            
        else:
            raise ValueError(f"Unknown distribution: {dist_type}")
            
        # Normalize sum to match target_total exactly
        current_sum = sum(raw_vals)
        factor = target_total / current_sum if current_sum > 0 else 1.0
        
        for i in range(n):
            val = int(round(raw_vals[i] * factor))
            # Claim cannot exceed physical system capacity
            val = max(1, min(total_capacity[j], val))
            max_matrix[i][j] = val
            
    return max_matrix

# =====================================================================
# 3. Discrete Event Simulator
# =====================================================================

class Simulator:
    def __init__(self, n: int, m: int, total_capacity: List[int], max_matrix: List[List[int]], 
                 num_events: int, p_alloc: float, hold_duration: int, rng_seed: int, step_max: int = 4):
        self.n = n
        self.m = m
        self.total = list(total_capacity)
        self.max_matrix = [list(r) for r in max_matrix]
        self.num_events = num_events
        self.p_alloc = p_alloc
        self.hold_duration = hold_duration
        self.rng_seed = rng_seed
        self.step_max = step_max

    def generate_event_stream(self) -> List[Dict]:
        """Pre-generates identical request stream for strict paired comparisons."""
        rng = random.Random(self.rng_seed)
        events = []
        for _ in range(self.num_events):
            p_idx = rng.randint(0, self.n - 1)
            is_alloc = (rng.random() < self.p_alloc)
            req_vec = [rng.randint(1, self.step_max) for _ in range(self.m)]
            events.append({
                "process": p_idx,
                "is_alloc": is_alloc,
                "req": req_vec
            })
        return events

    def run_greedy(self, events: List[Dict]) -> Dict:
        """
        Unconstrained / Greedy Allocation (Hazard Monitoring).
        Grants whenever Available >= Request.
        Monitors transition to Unsafe state.
        """
        available = list(self.total)
        allocation = [[0] * self.m for _ in range(self.n)]
        hold_timer = [0] * self.n
        
        reached_unsafe = False
        step_first_unsafe = -1
        util_at_first_unsafe = 0.0
        unsafe_steps_count = 0
        total_safety_comparisons = 0
        safety_eval_count = 0
        granted_requests = 0
        sum_util = 0.0
        
        for step_idx, ev in enumerate(events):
            # Invariant check: Conservation of resources
            for j in range(self.m):
                alloc_sum = sum(allocation[i][j] for i in range(self.n))
                assert alloc_sum + available[j] == self.total[j], f"Conservation broken at step {step_idx}"
                
            # Process releases upon task completion
            for i in range(self.n):
                if hold_timer[i] > 0:
                    hold_timer[i] -= 1
                    if hold_timer[i] == 0:
                        # Task finished: release all held resources
                        for j in range(self.m):
                            available[j] += allocation[i][j]
                            allocation[i][j] = 0
                            
            current_util = sum(sum(allocation[i]) for i in range(self.n)) / sum(self.total)
            sum_util += current_util
            
            p = ev["process"]
            needs = [self.max_matrix[p][j] - allocation[p][j] for j in range(self.m)]
            
            if ev["is_alloc"] and any(nd > 0 for nd in needs) and hold_timer[p] == 0:
                req = [min(ev["req"][j], needs[j]) for j in range(self.m)]
                
                # Check physical availability
                if all(req[j] <= available[j] for j in range(self.m)):
                    for j in range(self.m):
                        available[j] -= req[j]
                        allocation[p][j] += req[j]
                    granted_requests += 1
                    
                    # If process satisfied its full max claim, start holding duration
                    if all(allocation[p][j] == self.max_matrix[p][j] for j in range(self.m)):
                        hold_timer[p] = self.hold_duration
                        
                    # Evaluate safety state
                    safe, _, comps = BankersEngine.is_safe(available, allocation, self.max_matrix)
                    safety_eval_count += 1
                    total_safety_comparisons += comps
                    
                    if not safe:
                        unsafe_steps_count += 1
                        if not reached_unsafe:
                            reached_unsafe = True
                            step_first_unsafe = step_idx
                            util_at_first_unsafe = sum(sum(allocation[i]) for i in range(self.n)) / sum(self.total)
                            
        if not reached_unsafe:
            step_first_unsafe = self.num_events
            util_at_first_unsafe = current_util
            
        avg_comps = total_safety_comparisons / max(1, safety_eval_count)
        mean_util = sum_util / self.num_events
        
        return {
            "policy": "greedy",
            "reached_unsafe": 1 if reached_unsafe else 0,
            "step_first_unsafe": step_first_unsafe,
            "unsafe_steps_fraction": round(unsafe_steps_count / max(1, safety_eval_count), 4),
            "util_at_first_unsafe": round(util_at_first_unsafe, 4),
            "mean_utilization": round(mean_util, 4),
            "granted_requests": granted_requests,
            "avg_safety_comparisons": round(avg_comps, 2)
        }

    def run_bankers(self, events: List[Dict]) -> Dict:
        """
        Banker's Deadlock Avoidance.
        Speculatively allocates; denies/defers any request leading to an unsafe state.
        """
        available = list(self.total)
        allocation = [[0] * self.m for _ in range(self.n)]
        hold_timer = [0] * self.n
        
        denied_unsafe_count = 0
        granted_requests = 0
        total_safety_comparisons = 0
        safety_eval_count = 0
        sum_util = 0.0
        
        for step_idx, ev in enumerate(events):
            # Invariant check
            for j in range(self.m):
                alloc_sum = sum(allocation[i][j] for i in range(self.n))
                assert alloc_sum + available[j] == self.total[j], f"Conservation broken at step {step_idx}"
                
            for i in range(self.n):
                if hold_timer[i] > 0:
                    hold_timer[i] -= 1
                    if hold_timer[i] == 0:
                        for j in range(self.m):
                            available[j] += allocation[i][j]
                            allocation[i][j] = 0
                            
            current_util = sum(sum(allocation[i]) for i in range(self.n)) / sum(self.total)
            sum_util += current_util
            
            p = ev["process"]
            needs = [self.max_matrix[p][j] - allocation[p][j] for j in range(self.m)]
            
            if ev["is_alloc"] and any(nd > 0 for nd in needs) and hold_timer[p] == 0:
                req = [min(ev["req"][j], needs[j]) for j in range(self.m)]
                
                if all(req[j] <= available[j] for j in range(self.m)):
                    # Speculative allocation
                    for j in range(self.m):
                        available[j] -= req[j]
                        allocation[p][j] += req[j]
                        
                    safe, _, comps = BankersEngine.is_safe(available, allocation, self.max_matrix)
                    safety_eval_count += 1
                    total_safety_comparisons += comps
                    
                    if safe:
                        granted_requests += 1
                        if all(allocation[p][j] == self.max_matrix[p][j] for j in range(self.m)):
                            hold_timer[p] = self.hold_duration
                    else:
                        # Rollback!
                        for j in range(self.m):
                            available[j] += req[j]
                            allocation[p][j] -= req[j]
                        denied_unsafe_count += 1
                        
        total_attempts = granted_requests + denied_unsafe_count
        denial_rate = denied_unsafe_count / max(1, total_attempts)
        avg_comps = total_safety_comparisons / max(1, safety_eval_count)
        mean_util = sum_util / self.num_events
        
        return {
            "policy": "bankers",
            "denial_rate": round(denial_rate, 4),
            "denied_count": denied_unsafe_count,
            "granted_requests": granted_requests,
            "mean_utilization": round(mean_util, 4),
            "avg_safety_comparisons": round(avg_comps, 2)
        }

# =====================================================================
# 4. Correctness Evidence Verification
# =====================================================================

def run_correctness_verification():
    print("=" * 70)
    print("CORRECTNESS EVIDENCE: Dijkstra's Banker's Algorithm Test")
    print("=" * 70)
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
    max_m = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ]
    avail = [3, 3, 2]
    is_safe, seq, steps = BankersEngine.is_safe(avail, allocation, max_m)
    print(f"Testbook state safety check: Is Safe = {is_safe}")
    print(f"Discovered safe sequence: <{', '.join('P' + str(p) for p in seq)}> in {steps} comparisons.")
    assert is_safe, "Textbook example must be safe!"
    
    # Check invariant that sequence successfully finishes all processes
    work = list(avail)
    for p in seq:
        for j in range(3):
            assert max_m[p][j] - allocation[p][j] <= work[j]
            work[j] += allocation[p][j]
    assert work == [10, 5, 7], "Final work vector must equal total capacity [10, 5, 7]!"
    print("All processes safely finish. Final resource vector matches total capacity [10, 5, 7].")
    
    # Perturb to an unsafe state: Available [1, 0, 0], Allocations unchanged
    avail_unsafe = [1, 0, 0]
    is_safe_bad, _, _ = BankersEngine.is_safe(avail_unsafe, allocation, max_m)
    print(f"Perturbed unsafe check: Is Safe = {is_safe_bad} (Expected False)")
    assert not is_safe_bad, "Perturbed state must be unsafe!"
    print("Correctness verification passed successfully!\n")

# =====================================================================
# 5. Full Experimental Suite Driver
# =====================================================================

def run_all_experiments():
    run_correctness_verification()
    
    SEEDS = [10000 * k + 42 for k in range(30)] # 30 paired repetitions
    BASE_N = 15
    BASE_M = 3
    BASE_TOTAL = [100, 100, 100]
    BASE_RHO = 1.30
    BASE_P_ALLOC = 0.65
    BASE_HOLD = 6
    BASE_EVENTS = 1000
    
    raw_records = []
    
    print("Running Experiment 1 (E1): Resource-Demand Variability Type...")
    for dist in ["uniform", "normal", "bimodal", "pareto"]:
        for s_idx, seed in enumerate(SEEDS):
            rng_demand = random.Random(seed + 1)
            max_m = generate_demands(dist, BASE_N, BASE_M, BASE_TOTAL, BASE_RHO, rng_demand)
            sim = Simulator(BASE_N, BASE_M, BASE_TOTAL, max_m, BASE_EVENTS, BASE_P_ALLOC, BASE_HOLD, seed)
            events = sim.generate_event_stream()
            
            res_greedy = sim.run_greedy(events)
            res_bankers = sim.run_bankers(events)
            
            raw_records.append({
                "experiment": "E1",
                "param_name": "distribution",
                "param_value": dist,
                "seed": seed,
                "n": BASE_N,
                "m": BASE_M,
                "rho": BASE_RHO,
                "p_alloc": BASE_P_ALLOC,
                "hold_duration": BASE_HOLD,
                "greedy_unsafe": res_greedy["reached_unsafe"],
                "greedy_mttu": res_greedy["step_first_unsafe"],
                "greedy_util_first_unsafe": res_greedy["util_at_first_unsafe"],
                "greedy_mean_util": res_greedy["mean_utilization"],
                "greedy_unsafe_frac": res_greedy["unsafe_steps_fraction"],
                "greedy_comps": res_greedy["avg_safety_comparisons"],
                "bankers_denial_rate": res_bankers["denial_rate"],
                "bankers_denied_count": res_bankers["denied_count"],
                "bankers_mean_util": res_bankers["mean_utilization"],
                "bankers_comps": res_bankers["avg_safety_comparisons"]
            })
            
    print("Running Experiment 2 (E2): Resource Allocation Pressure (rho)...")
    for dist in ["uniform", "bimodal"]:
        for rho_val in [0.80, 1.00, 1.20, 1.40, 1.60, 2.00]:
            for s_idx, seed in enumerate(SEEDS):
                rng_demand = random.Random(seed + 1)
                max_m = generate_demands(dist, BASE_N, BASE_M, BASE_TOTAL, rho_val, rng_demand)
                sim = Simulator(BASE_N, BASE_M, BASE_TOTAL, max_m, BASE_EVENTS, BASE_P_ALLOC, BASE_HOLD, seed)
                events = sim.generate_event_stream()
                
                res_greedy = sim.run_greedy(events)
                res_bankers = sim.run_bankers(events)
                
                raw_records.append({
                    "experiment": "E2",
                    "param_name": f"{dist}_rho",
                    "param_value": rho_val,
                    "seed": seed,
                    "n": BASE_N,
                    "m": BASE_M,
                    "rho": rho_val,
                    "p_alloc": BASE_P_ALLOC,
                    "hold_duration": BASE_HOLD,
                    "greedy_unsafe": res_greedy["reached_unsafe"],
                    "greedy_mttu": res_greedy["step_first_unsafe"],
                    "greedy_util_first_unsafe": res_greedy["util_at_first_unsafe"],
                    "greedy_mean_util": res_greedy["mean_utilization"],
                    "greedy_unsafe_frac": res_greedy["unsafe_steps_fraction"],
                    "greedy_comps": res_greedy["avg_safety_comparisons"],
                    "bankers_denial_rate": res_bankers["denial_rate"],
                    "bankers_denied_count": res_bankers["denied_count"],
                    "bankers_mean_util": res_bankers["mean_utilization"],
                    "bankers_comps": res_bankers["avg_safety_comparisons"]
                })

    print("Running Experiment 3 (E3): Concurrency Scale (Number of Processes n)...")
    for dist in ["uniform", "bimodal"]:
        for n_val in [5, 10, 15, 25, 50]:
            for s_idx, seed in enumerate(SEEDS):
                rng_demand = random.Random(seed + 1)
                max_m = generate_demands(dist, n_val, BASE_M, BASE_TOTAL, BASE_RHO, rng_demand)
                sim = Simulator(n_val, BASE_M, BASE_TOTAL, max_m, BASE_EVENTS, BASE_P_ALLOC, BASE_HOLD, seed)
                events = sim.generate_event_stream()
                
                res_greedy = sim.run_greedy(events)
                res_bankers = sim.run_bankers(events)
                
                raw_records.append({
                    "experiment": "E3",
                    "param_name": f"{dist}_n",
                    "param_value": n_val,
                    "seed": seed,
                    "n": n_val,
                    "m": BASE_M,
                    "rho": BASE_RHO,
                    "p_alloc": BASE_P_ALLOC,
                    "hold_duration": BASE_HOLD,
                    "greedy_unsafe": res_greedy["reached_unsafe"],
                    "greedy_mttu": res_greedy["step_first_unsafe"],
                    "greedy_util_first_unsafe": res_greedy["util_at_first_unsafe"],
                    "greedy_mean_util": res_greedy["mean_utilization"],
                    "greedy_unsafe_frac": res_greedy["unsafe_steps_fraction"],
                    "greedy_comps": res_greedy["avg_safety_comparisons"],
                    "bankers_denial_rate": res_bankers["denial_rate"],
                    "bankers_denied_count": res_bankers["denied_count"],
                    "bankers_mean_util": res_bankers["mean_utilization"],
                    "bankers_comps": res_bankers["avg_safety_comparisons"]
                })

    print("Running Experiment 4 (E4): Process Holding Duration (tau)...")
    for dist in ["uniform", "bimodal"]:
        for hold_val in [1, 3, 6, 10, 16]:
            for s_idx, seed in enumerate(SEEDS):
                rng_demand = random.Random(seed + 1)
                max_m = generate_demands(dist, BASE_N, BASE_M, BASE_TOTAL, BASE_RHO, rng_demand)
                sim = Simulator(BASE_N, BASE_M, BASE_TOTAL, max_m, BASE_EVENTS, BASE_P_ALLOC, hold_val, seed)
                events = sim.generate_event_stream()
                
                res_greedy = sim.run_greedy(events)
                res_bankers = sim.run_bankers(events)
                
                raw_records.append({
                    "experiment": "E4",
                    "param_name": f"{dist}_hold",
                    "param_value": hold_val,
                    "seed": seed,
                    "n": BASE_N,
                    "m": BASE_M,
                    "rho": BASE_RHO,
                    "p_alloc": BASE_P_ALLOC,
                    "hold_duration": hold_val,
                    "greedy_unsafe": res_greedy["reached_unsafe"],
                    "greedy_mttu": res_greedy["step_first_unsafe"],
                    "greedy_util_first_unsafe": res_greedy["util_at_first_unsafe"],
                    "greedy_mean_util": res_greedy["mean_utilization"],
                    "greedy_unsafe_frac": res_greedy["unsafe_steps_fraction"],
                    "greedy_comps": res_greedy["avg_safety_comparisons"],
                    "bankers_denial_rate": res_bankers["denial_rate"],
                    "bankers_denied_count": res_bankers["denied_count"],
                    "bankers_mean_util": res_bankers["mean_utilization"],
                    "bankers_comps": res_bankers["avg_safety_comparisons"]
                })

    # Save raw_results.csv
    csv_path = os.path.join(os.path.dirname(__file__), "raw_results.csv")
    fieldnames = list(raw_records[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(raw_records)
    print(f"Saved {len(raw_records)} runs to {csv_path}")

if __name__ == "__main__":
    t0 = time.time()
    run_all_experiments()
    print(f"All experiments successfully completed in {time.time() - t0:.2f} seconds.")
