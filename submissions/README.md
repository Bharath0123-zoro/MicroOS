# Academic Submissions & Coursework Portfolio

## 🎓 Student & Institutional Credentials
- **Student Name**: T Bharath
- **University Seat Number (USN)**: `25BTRCL269`
- **Institutional Email**: `juug25btech18691@jainuniversity.ac.in`
- **Institution**: Faculty of Engineering and Technology, Jain (Deemed-to-be University)
- **Department**: Department of Computer Science & Engineering
- **Course**: Operating Systems (Theory & Practical Lab)
- **Faculty Guide / Instructor**: Dr. Sujeet S Jagtap
- **GitHub Repository**: [https://github.com/Bharath0123-zoro/MicroOS](https://github.com/Bharath0123-zoro/MicroOS)
- **Hugging Face Repository**: [https://huggingface.co/Bharath2025/MicroOS](https://huggingface.co/Bharath2025/MicroOS)

---

## 📑 Coursework Submissions Index

| Document Title | File Name | Pages | Description & Coverage | Direct Link |
| :--- | :--- | :---: | :--- | :---: |
| **OS Lab Practical Record** | `OS_Lab_Record_T_Bharath_(1).pdf` | 118 | Comprehensive laboratory record covering 20 chapters (Experiments 2.24 to 21.02): Process scheduling, IPC, multithreading, synchronization primitives, Banker's deadlock avoidance, memory paging, page replacement, disk scheduling, and VM simulation. | [View PDF](./OS_Lab_Record_T_Bharath_(1).pdf) |
| **Continuous Assessment 2 (CA-2)** | `performance_ivestigation_(1).pdf` | 6 | **OS Performance Investigation**: *Safe-State Analysis: Effect of Resource-Demand Variability on Reaching an Unsafe State*. Empirical study across Uniform, Normal, Bimodal, Pareto, and Exponential workloads. | [View PDF](./performance_ivestigation_(1).pdf) |
| **Continuous Assessment 3 (CA-3)** | `design_and_debugging_(1).pdf` | 8 | **OS Design & Debugging Challenge**: Safe-State Analysis & Banker's algorithm fault-injection, concurrency race condition fixes, state-mutation bugs, and reference solver validation. | [View PDF](./design_and_debugging_(1).pdf) |
| **Continuous Assessment 5 (CA-5)** | `Bharath_269_linux_(1).pdf` | 7 | **Linux Systems Engineering Challenge**: Safe-State Analysis with kernel `/proc` instrumentation, memory pressure metrics, and benchmarking under multicore load. | [View PDF](./Bharath_269_linux_(1).pdf) |

---

## 🔬 Detailed Overview of Submissions

### 1. Operating Systems Practical Lab Record (`OS_Lab_Record_T_Bharath_(1).pdf`)
- **Total Pages**: 118
- **Author**: T Bharath (`25BTRCL269`)
- **Course Faculty**: Dr. Sujeet S Jagtap
- **Scope & Experiments Covered**:
  - **Chapter 2 - Process Management & Scheduling**: Fork-exec process lifecycle, orphan and zombie processes, priority scheduling, preemptive Round-Robin, Multilevel Feedback Queues (MLFQ).
  - **Chapter 3 - Inter-Process Communication (IPC)**: POSIX pipes, named FIFOs, System V / POSIX shared memory, message queues.
  - **Chapter 4 - POSIX Multithreading (Pthreads)**: Thread creation, synchronization barriers, joinable vs detached states, thread-local storage.
  - **Chapter 5 - Mutexes, Semaphores & Condition Variables**: Critical section protection, counting semaphores, binary mutexes, spurious wakeup handling.
  - **Chapter 6 - Classical Synchronization Problems**: Producer-Consumer (bounded buffer), Readers-Writers (starvation avoidance), Dining Philosophers (resource hierarchy).
  - **Chapter 7 - Deadlock Management & Banker's Algorithm**: Resource Allocation Graphs (RAG), cycle detection, Banker's safety state evaluation, dynamic resource request checking.
  - **Chapter 8 & 9 - Memory Management & Paging**: Contiguous allocation (First-Fit, Best-Fit, Worst-Fit), two-level paging, inverted page tables, TLB hit/miss simulation.
  - **Chapter 10 - Virtual Memory & Page Replacement**: FIFO, Least Recently Used (LRU), Optimal (OPT), Clock / Second-Chance algorithms with Belady's Anomaly demonstrations.
  - **Chapter 11 - Storage & Disk Scheduling**: FCFS, Shortest Seek Time First (SSTF), SCAN (Elevator), C-SCAN, LOOK, and C-LOOK seek-time optimizations.
  - **Chapter 12 - File Systems & Inodes**: File control blocks, directory tree traversals, inode allocation, soft vs hard links.
  - **Chapter 13 - Protection & Linux Security**: POSIX permissions, user/group IDs, Linux capabilities (`cap_setuid`, `cap_net_raw`), chroot sandboxing.
  - **Chapter 21 - Virtual Machine & Microkernel Simulation**: Minimal x86_64 virtualization model and microkernel message-passing IPC architecture.

---

### 2. CA-2: OS Performance Investigation (`performance_ivestigation_(1).pdf`)
- **Investigation Title**: *Safe-State Analysis: Effect of Resource-Demand Variability on Reaching an Unsafe State*
- **Research Question**: How does stochastic variability in resource requests impact the probability of entering an unsafe deadlock-prone state ($P_{\text{unsafe}}$) and Mean Time to Unsafe ($MTTU$)?
- **Workload Distributions Evaluated**:
  1. *Uniform Distribution* ($U[0, \text{Max}]$) — Baseline uniform random allocation.
  2. *Normal Distribution* ($\mathcal{N}(\mu, \sigma^2)$) — Concentrated resource demands around mean load.
  3. *Bimodal Distribution* — Mixture modeling alternating lightweight and heavy bursts.
  4. *Pareto / Heavy-Tailed Distribution* — Modeling realistic bursty processes with 80/20 power laws.
  5. *Exponential Distribution* — Memoryless arrival processes.
- **Key Findings**:
  - Higher resource variability significantly accelerates transitions into unsafe states even when total system utilization remains identical.
  - Heavy-tailed (Pareto) distributions exhibit the lowest $MTTU$ and highest rejection rates during dynamic allocation requests.

---

### 3. CA-3: OS Design & Debugging Challenge (`design_and_debugging_(1).pdf`)
- **Challenge Title**: *OS Design & Debugging Challenge: Safe-State Analysis & Banker's Algorithm Implementation*
- **Objective**: Identifying and repairing critical edge-case bugs and race conditions in deadlock avoidance solvers.
- **Root Cause Analyses & Bug Fixes**:
  - **Fault 1 (State Mutation During Evaluation)**: The safety-checking algorithm accidentally mutated the global `available` and `allocation` matrices during hypothetical lookaheads instead of evaluating on work copies. *Fixed using deep-copy state snapshots*.
  - **Fault 2 (Need Vector Recalculation)**: Off-by-one errors in resource index indexing during dynamic `need = max - alloc` updates. *Resolved with vectorized matrix comparisons*.
  - **Fault 3 (Concurrent Allocation Race Conditions)**: Simultaneous thread requests causing non-atomic safety checks leading to phantom safe states. *Resolved with mutex-locked atomic transaction boundaries*.
- **Verified Code Included**: Contains the complete, battle-tested `safe_state.py` implementation with zero assertion errors.

---

### 4. CA-5: Linux Systems Engineering Challenge (`Bharath_269_linux_(1).pdf`)
- **Challenge Title**: *Linux Systems Engineering Challenge: Safe-State Analysis with /proc Instrumentation and Benchmarking*
- **Core Topics**:
  - Extraction and analysis of Linux kernel resource states using `/proc` and `/sys` virtual filesystems (`/proc/meminfo`, `/proc/sys/kernel/`, `/proc/loadavg`).
  - Correlating real Linux kernel memory pressure indicators (`MemAvailable`, `CommitLimit`, `Committed_AS`) with theoretical safe-state avoidance bounds.
  - High-concurrency benchmark harness measuring algorithm latency, request denial throughput, and CPU cache performance.

---

## 💻 Accompanying Reproducible Source Code

The complete benchmark harness, plotting scripts, and raw simulation datasets are provided in the [`code_and_data/`](./code_and_data/) directory:
- [`safe_state_experiment.py`](./code_and_data/safe_state_experiment.py) — Core simulation engine executing 10,000+ Monte Carlo trials across varying concurrency and distributions.
- [`analyze.py`](./code_and_data/analyze.py) — Statistical aggregation, confidence intervals, and hypothesis testing.
- [`plots.py`](./code_and_data/plots.py) — Vector graphics generation for academic publication charts.
- [`raw_results.csv`](./code_and_data/raw_results.csv) — Raw trial execution telemetry.
- [`summary_means.csv`](./code_and_data/summary_means.csv) — Aggregated means and standard deviations.

---

## 🚀 MicroOS Project Artifacts
- **MicroOS GUI Desktop ISO (3.63 MB)**: [Download microos-gui.iso](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos-gui.iso)
- **MicroOS VirtualBox VDI Disk (5.24 MB)**: [Download microos-gui.vdi](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos-gui.vdi)
- **MicroOS Terminal CLI ISO (12.77 MB)**: [Download microos.iso](https://huggingface.co/Bharath2025/MicroOS/resolve/main/release/microos.iso)
