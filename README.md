# FLOOD EVACUATION PRIORITY SYSTEM USING MERGE SORT
### College Design and Analysis of Algorithms (DAA) FA-2 Project
**Paradigm:** Divide and Conquer  
**Technique:** Manual Recursive Merge Sort (Zero external sorting libraries)  
**Theme:** Modern Professional Light Theme (Educational Desktop Simulation)  
**Platform:** Python 3 Desktop Simulation (Pygame) + C++ Backend Reference

---

## 1. Project Overview & Motivation

During severe monsoon flooding events in metropolitan areas (e.g., Pune), disaster response authorities face critical resource constraints. Emergency vehicles, rescue boats, and personnel cannot be dispatched everywhere simultaneously.

### The Algorithmic Solution
To prevent casualties, affected areas must be triaged strictly by danger level. This system collects real-time water-level telemetry across **20 urban sectors** and applies **Merge Sort** to arrange sectors in **strictly descending order of flood water level**. Areas with the deepest water levels receive immediate priority for evacuation to safety shelters.

```
REAL-WORLD PROBLEM (Monsoon Flood Crisis)
                 ↓
WATER LEVEL TELEMETRY (20 Monitored Sectors)
                 ↓
INPUT ARRAY (Original Administrative Order)
                 ↓
MERGE SORT (Divide and Conquer Decomposition)
                 ↓
RECURSIVE DIVIDE (Halving step-by-step: 20 → 10,10 → 5s → base)
                 ↓
COMPARE & SELECT (Pointer HUD, directional arrows, larger water level chosen)
                 ↓
MERGE SUBARRAYS (Step-by-step card placement into descending buffer)
                 ↓
FINAL MERGE (Combining two 10-element sorted halves)
                 ↓
FINAL EVACUATION RANKING (Critical → High → Medium → Low)
                 ↓
PRIORITY RESCUE DISPATCH SIMULATION
                 ↓
ALGORITHM COMPLEXITY & DAA ANALYSIS
```

---

## 2. Directory Structure

```
c:\Users\Saleha Shaikh\OneDrive\Desktop\DAA FA-2\
├── flood_areas.csv              # Exact 20-sector Pune dataset (ID, Name, Water Level, Population)
├── merge_sort.py                # Pure manual Merge Sort implementation with fine-grained event tracer
├── merge_sort.cpp               # C++ reference implementation compiled with g++ (65 comps, 19 merges)
├── merge_sort_backend.exe       # Standalone compiled C++ executable
├── simulation_state.py          # State controller, speed settings, stepping logic, and progress tracking
├── ui_components.py             # Professional Light Theme design tokens, buttons with vector icons, HUD cards, arrows
├── scenes.py                    # Dedicated renderers for all 9 simulation stages
├── main.py                      # Pygame application loop (1280x720, 60 FPS, keyboard & mouse controls)
├── test_simulation.py           # Headless automated test suite verifying all scenes and stepping
├── generate_screenshots.py      # Screenshot generator producing high-res PNGs of all scenes
├── screenshots/                 # Captured high-res demonstration screenshots
└── README.md                    # DAA academic report & presentation viva guide
```

---

## 3. How to Run the Simulation

### Prerequisites
- Python 3.10+ installed
- Pygame (`pygame >= 2.5.0`)

### Installation & Launch
Open PowerShell or Command Prompt in the project folder:

```powershell
# 1. Run the desktop application window
.\.venv\Scripts\python.exe main.py

# (Or run python main.py if pygame is installed globally)
```

### Running the C++ Backend (Optional for Viva)
```powershell
# The C++ backend can be executed directly:
.\merge_sort_backend.exe

# Or recompiled using MinGW g++:
C:\MinGW\bin\g++.exe -O2 -std=c++17 merge_sort.cpp -o merge_sort_backend.exe
```

### Automated Validation Suite
You can verify the entire algorithm, data correctness, and all scene renderers headlessly:

```powershell
.\.venv\Scripts\python.exe test_simulation.py
```

---

## 4. User Interface & Interactive Controls

The software runs as a fixed **1280 × 720** desktop application window with a clean, modern **Light Theme**:
- Off-white background (`#F8FAFC`)
- Crisp white panels (`#FFFFFF`) with subtle slate borders (`#CBD5E1`)
- Deep navy/charcoal high-contrast text (`#0F172A`)
- Royal blue primary accent (`#2563EB`)
- Amber/soft yellow comparison highlights (`#FEF3C7` / `#D97706`)
- Emerald green selection/merged highlights (`#D1FAE5` / `#059669`)
- Red exclusively for critical flood levels (`#FEE2E2` / `#DC2626`)

### Top Bar HUD
- **Application Title**: Flood Evacuation Priority System (DAA FA-2)
- **Visual Breadcrumb Tracker**: Real-time progress through all 9 stages (`INTRO` → `DATA` → `SCAN` → `INPUT` → `DIVIDE` → `MERGE` → `RANK` → `EVAC` → `ANALYSIS`)
- **Stage & Progress Indicator**: Displays current stage name and percentage complete
- **Status Badge**: `[RUNNING]`, `[PAUSED]`, or `[DEMO (STEP)]`

### Bottom Control Dock
- **`[ || PAUSE ]` / `[ ▶ PLAY ]`**: Toggle automated animation
- **`[ ◀ PREV ]`**: Step backward one algorithmic action or previous scene
- **`[ ▶ NEXT ]`**: Step forward one algorithmic action or next scene
- **`[ ↻ RESET ]`**: Restart simulation from Scene 1
- **`[ DAA DEMO MODE ]`**: Toggles step-by-step presentation mode (pauses on comparisons/merges for instructor explanation)
- **`[ SLOW ]` `[ MED ]` `[ FAST ]`**: Adjusts animation velocity (1.2s, 0.55s, 0.15s per operation)
- **`[ ✕ EXIT ]`**: Safely closes the desktop simulation

### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| **`SPACE`** | Toggle Pause / Play |
| **`RIGHT ARROW (→)`** | Step Forward (Next Step) |
| **`LEFT ARROW (←)`** | Step Backward (Previous Step) |
| **`R`** | Reset to Intro Scene |
| **`D`** | Toggle DAA Demo Mode |
| **`1`, `2`, `3`** | Switch Speed (1: Slow, 2: Med, 3: Fast) |
| **`ESC`** | Exit Application |

---

## 5. Walkthrough of the 9 Simulation Scenes

### Scene 1: Professional Intro Screen
- High-level overview of the emergency problem statement.
- Summary cards detailing the algorithm (Merge Sort), input size (20 zones), and output objective (Triage ranking).
- Interactive **`[ ▶ START SIMULATION ]`** button.

### Scene 2: Pune Metropolitan Flood Map
- 5 columns × 4 rows grid of all 20 monitored locations.
- Visual elements: Residential building icon, water depth level bar gauge, numerical water level (e.g. `8.2 m`), affected population, and color-coded priority dot.
- High water levels feature a light-blue flood tint at the base of each card.

### Scene 3: Telemetry Scanning & Risk Detection
- Animated radar inspection that sweeps through sectors one by one.
- Sensor Feed HUD spotlighting active measurements: Area ID, Name, Water Level in meters, Priority classification, and population at risk.
- Transitions automatically once all 20 areas have been captured.

### Scene 4: Input Data Array (Unsorted Order)
- Visualizes the raw input array exactly as parsed from `flood_areas.csv`.
- Each card displays its array index (`[0]..[19]`), sector name, and water level.
- Emphasizes that administrative order does not match urgency, necessitating algorithm sorting.

### Scene 5: Divide & Conquer (Recursive Tree & Step-by-Step Halving)
- Intermediate divide steps:
  - **Step 1 / 4**: 20 Elements root array `[A01..A20]` (compact cards)
  - **Step 2 / 4**: Two 10-element halves: Left `[A01..A10]` and Right `[A11..A20]` (medium cards)
  - **Step 3 / 4**: Four 5-element quarters: `[A01..A05]`, `[A06..A10]`, `[A11..A15]`, `[A16..A20]` (large cards)
  - **Step 4 / 4**: Base cases of 2-3 elements down to atomic single elements (extra large readable cards)
- Dynamic card scaling ensures data remains readable at every level.

### Scene 6: Step-by-Step Merge with Directional Arrows & Pointer HUD
- Shows **Left Sorted Subarray** (with `L-PTR` pointer) and **Right Sorted Subarray** (with `R-PTR` pointer).
- Visual directional arrows point from the compared elements into the **Active Comparison Spotlight**.
- Decision banner: `Comparison: 7.1 m >= 6.3 m` → `Selected: A04 Hinjewadi (7.1 m)`.
- Downward directional arrow drops the selected element into the **Merged Result Buffer**.
- Merged array builds card-by-card in real time (`[ ]` → `[7.1]` → `[7.1, 6.3]` → `[7.1, 6.3, 4.6]` ...).
- Right HUD displays live pointer tracking: `Left pointer: A05 → 4.6 m`, `Right pointer: A06 → 6.3 m`.
- Displays dedicated **Final Merge banner** when the two 10-element halves merge into the final 20-element array.

### Scene 7: Final Sorted Result (Evacuation Priority Table)
- Displays all 20 sectors ranked strictly from **Rank #1 to Rank #20**.
- Categorized priority tiers:
  - **CRITICAL** (≥ 7.5 m): Hadapsar (8.2m), Yerawada (7.9m), Bhosari (7.6m)
  - **HIGH** (6.0 m – 7.4 m): Hinjewadi (7.1m), Pimpri (6.9m), Swargate (6.5m), Baner (6.3m), Katraj (6.1m)
  - **MEDIUM** (4.0 m – 5.9 m): Kothrud (5.8m), Lohegaon (5.5m), Chinchwad (5.1m), Dapodi (4.8m), Wakad (4.6m), Dhankawadi (4.2m)
  - **LOW** (< 4.0 m): Kharadi (3.9m), Camp (3.7m), Warje (3.5m), Viman Nagar (3.2m), Aundh (2.8m), Shivaji Nagar (2.5m)

### Scene 8: Priority Rescue Dispatch Simulation
- Visual blueprint map of Pune flood zones with a designated **Central Relief Shelter**.
- Animated evacuation boats/transports dispatched in exact priority order to the top 5 critical zones (#1 Hadapsar down to #5 Pimpri).
- Real-time **Rescue Log (Triage Queue)** showing statuses: `QUEUED` → `IN TRANSIT...` → `SAFE (EVACUATED)`.

### Scene 9: Algorithm Analysis & Theoretical Complexity
- Theoretical complexity table: Best, Average, Worst time: $\mathcal{O}(n \log n)$, Space: $\mathcal{O}(n)$.
- Mathematical recurrence relation: $T(n) = 2T(n/2) + \mathcal{O}(n)$, solved by Master Theorem.
- Full architectural pipeline diagram from Flood Sensors to Rescue Dispatch.
- Live telemetry metrics from this execution: **20 Elements, 65 Comparisons, 19 Merges, Depth 5**.

---

## 6. Academic Complexity & Recurrence Proof

### Time Complexity using Master Theorem

For Merge Sort, the recursive divide-and-conquer recurrence relation is:

$$
T(n) = 2T(n/2) + O(n)
$$

Where:
* **a = 2** → number of recursive subproblems
* **b = 2** → input size is divided by 2
* **f(n) = O(n)** → time required to merge two sorted subarrays

Using the Master Theorem standard form:

$$
T(n) = aT(n/b) + f(n)
$$

**Step 1: Calculate the critical exponent:**

$$
n^{\log_b a} = n^{\log_2 2} = n^1 = n
$$

**Step 2: Compare $f(n)$ with $n^{\log_b a}$:**

$$
f(n) = O(n) = \Theta(n^{\log_2 2}) = \Theta(n)
$$

**Step 3: Apply Master Theorem Case 2:**
Since $f(n) = \Theta(n^{\log_b a})$, **Case 2** of the Master Theorem applies directly:

$$
T(n) = \Theta(n^{\log_b a} \log n) = \Theta(n \log n)
$$

#### Visual Step-by-Step Derivation Flow
```
T(n) = 2T(n/2) + O(n)
        ↓
a = 2,  b = 2,  f(n) = O(n)
        ↓
n^(log_b a) = n^(log₂2) = n
        ↓
f(n) = Θ(n^(log₂2))
        ↓
Master Theorem Case 2 Applies
        ↓
T(n) = Θ(n log n)
```

**Final Time Complexity:**
* Best Case: **O(n log n)**
* Average Case: **O(n log n)**
* Worst Case: **O(n log n)**

**Space Complexity:**
* **O(n)** auxiliary space because Merge Sort requires temporary buffers during subarray recombination.

| Case | Time Complexity | Explanation |
| :--- | :--- | :--- |
| **Best Case** | $\mathcal{O}(n \log n)$ | Tree height is always $\lceil \log_2 n \rceil$ regardless of initial order |
| **Average Case** | $\mathcal{O}(n \log n)$ | Expected number of comparisons across all levels is bounded |
| **Worst Case** | $\mathcal{O}(n \log n)$ | Strict upper bound; cannot degenerate to $\mathcal{O}(n^2)$ unlike QuickSort |
| **Space Complexity** | $\mathcal{O}(n)$ | Requires auxiliary memory for the merged buffer during recombination |

### Why Merge Sort Over QuickSort in Disaster Evacuation?
1. **Guaranteed Response Time**: QuickSort can degrade to $\mathcal{O}(n^2)$ if pivot selection is poor. In life-critical disaster management, guaranteed $\mathcal{O}(n \log n)$ is non-negotiable.
2. **Stability**: Merge Sort is stable—if two sectors have identical water levels, their original administrative sequence is preserved.
3. **Hierarchical Match**: The Divide and Conquer paradigm directly mirrors multi-tiered emergency command structures.

---

## 7. Faculty Viva Presentation Questions & Answers

**Q1: Why did you sort the data in descending order instead of ascending?**  
*Answer:* In flood disaster triage, the most endangered areas (highest water depth) require immediate rescue intervention. Sorting in descending order places the highest risk sectors at index 0, allowing emergency commanders to dispatch resources to Rank #1 immediately.

**Q2: Did you use built-in sorting libraries?**  
*Answer:* No. Both the Python engine (`merge_sort.py`) and the C++ backend (`merge_sort.cpp`) are written 100% from scratch with recursive divide and merge functions. Zero calls to `sort()`, `sorted()`, or `std::sort()` exist.

**Q3: How does the step-by-step Demonstration Mode work?**  
*Answer:* The engine records an immutable timeline of 191 discrete algorithm snapshots. In Demo Mode, pressing **`NEXT`** or **`PREV`** steps through each divide, comparison, pointer update, selection, and merge, allowing the presenter to pause and explain each algorithmic choice to faculty.

**Q4: How does the visual pointer HUD work during merging?**  
*Answer:* Two pointer variables `i` and `j` index into the Left and Right sorted subarrays. The UI renders pointers `L-PTR` and `R-PTR`, draws arrows connecting the pointed elements into the Comparison Arena, evaluates `left_val >= right_val`, and animates the chosen element dropping into the merged buffer.
