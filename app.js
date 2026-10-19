/**
 * app.js
 * Interactive Web Application Controller for Flood Evacuation Priority System
 * Implements full 9-scene state machine, audio synthesizer, and interactive animations.
 */

import { AreaRecord, AlgorithmState, MergeSortTracer, INITIAL_FLOOD_AREAS } from "./mergeSortTracer.js";

// Scene definitions
export const SceneId = {
  INTRO: 0,
  FLOOD_MAP: 1,
  SCAN_DETECT: 2,
  INPUT_DATA: 3,
  DIVIDE_TREE: 4,
  COMPARE_MERGE: 5,
  SORTED_RESULT: 6,
  EVACUATION: 7,
  ANALYSIS: 8,
};

export const SCENE_NAMES = [
  "INTRO",
  "FLOOD DATA",
  "DETECTION SCAN",
  "INPUT ARRAY",
  "DIVIDE & CONQUER",
  "COMPARE & MERGE",
  "FINAL RANKING",
  "EVACUATION",
  "ANALYSIS",
];

export const SCENE_DESCRIPTIONS = [
  "Monsoon flood disaster triage overview and divide & conquer strategy.",
  "Pune metropolitan flood map with real-time water gauges across 20 monitored zones.",
  "Automated sensor telemetry detection scanning water depth levels.",
  "Initial unsorted administrative dataset before Divide & Conquer sorting.",
  "Recursive decomposition tree halving the 20 sectors down to atomic base cases.",
  "Descending Merge Sort comparison arena with directional pointers and buffer placement.",
  "Definitive evacuation priority ranking sorted strictly by descending water depth.",
  "Priority rescue boat fleet dispatch simulation to top 5 critical flood zones.",
  "DAA algorithmic analysis, Master Theorem recurrence proof, and verified runtime telemetry.",
];

// Audio Synthesizer using Web Audio API
class SoundFX {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
  }

  playBeep(freq = 440, duration = 0.06, type = "sine", gainVal = 0.08) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx || this.ctx.state === "suspended") {
      this.ctx?.resume();
    }
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      // Audio autoplay policy fallback
    }
  }

  compareSound() {
    this.playBeep(520, 0.07, "triangle", 0.08);
  }

  selectSound() {
    this.playBeep(780, 0.09, "sine", 0.1);
  }

  mergeDoneSound() {
    this.playBeep(660, 0.12, "sine", 0.09);
    setTimeout(() => this.playBeep(880, 0.15, "sine", 0.09), 80);
  }

  sceneChangeSound() {
    this.playBeep(440, 0.06, "sine", 0.06);
    setTimeout(() => this.playBeep(580, 0.08, "sine", 0.06), 50);
  }
}

// Helpers for color and priority
function getPriorityColor(priority) {
  switch (priority.toUpperCase()) {
    case "CRITICAL": return "var(--critical-color)";
    case "HIGH": return "var(--high-color)";
    case "MEDIUM": return "var(--medium-color)";
    default: return "var(--low-color)";
  }
}

function getPriorityBadgeClass(priority) {
  switch (priority.toUpperCase()) {
    case "CRITICAL": return "badge-critical";
    case "HIGH": return "badge-high";
    case "MEDIUM": return "badge-medium";
    default: return "badge-low";
  }
}

function getWaterLevelColor(level) {
  if (level >= 7.5) return "var(--critical-color)";
  if (level >= 6.0) return "var(--high-color)";
  if (level >= 4.0) return "var(--medium-color)";
  return "var(--low-color)";
}

// Simulation Controller
class SimulationApp {
  constructor() {
    this.areas = INITIAL_FLOOD_AREAS.map(x => x.clone());
    this.tracer = new MergeSortTracer(this.areas);
    this.sortedAreas = this.tracer.getFinalSorted();
    this.sound = new SoundFX();

    // Application state
    this.currentScene = SceneId.INTRO;
    this.isPlaying = true;
    this.isDemoMode = false;
    this.speed = "MEDIUM";
    this.speedDurations = {
      SLOW: 1200,
      MEDIUM: 550,
      FAST: 150,
    };

    // Sub-scene progression states
    this.scanIndex = 0;
    this.divideStep = 0;
    this.timelineIndex = 0;
    this.evacIndex = 0;
    this.evacProgress = 0.0;
    this.evacCompleted = [];

    // Loop interval
    this.stepTimer = null;
    this.animationFrame = null;
    this.boatTimer = null;

    // DOM references
    this.dom = {
      app: document.getElementById("app"),
      stepperNav: document.getElementById("stepperNav"),
      statusBadge: document.getElementById("statusBadge"),
      statusBadgeText: document.getElementById("statusBadgeText"),
      sceneTitle: document.getElementById("sceneTitle"),
      sceneSubtitle: document.getElementById("sceneSubtitle"),
      sceneMetaBadge: document.getElementById("sceneMetaBadge"),
      sceneContainer: document.getElementById("sceneContainer"),
      btnPlayPause: document.getElementById("btnPlayPause"),
      playPauseText: document.getElementById("playPauseText"),
      btnPrev: document.getElementById("btnPrev"),
      btnNext: document.getElementById("btnNext"),
      btnReset: document.getElementById("btnReset"),
      btnDemoMode: document.getElementById("btnDemoMode"),
      btnTheme: document.getElementById("btnTheme"),
      btnSound: document.getElementById("btnSound"),
      hudOpBadge: document.getElementById("hudOpBadge"),
      hudActiveRange: document.getElementById("hudActiveRange"),
      hudTreeDepth: document.getElementById("hudTreeDepth"),
      hudCompsCount: document.getElementById("hudCompsCount"),
      hudMergesCount: document.getElementById("hudMergesCount"),
      hudExplanation: document.getElementById("hudExplanation"),
    };

    this.initUI();
    this.bindEvents();
    this.renderCurrentScene();
    this.startPlaybackLoop();
  }

  initUI() {
    // Build Stepper Chips
    this.dom.stepperNav.innerHTML = "";
    SCENE_NAMES.forEach((name, idx) => {
      const chip = document.createElement("button");
      chip.className = `step-chip ${idx === this.currentScene ? "active" : ""}`;
      chip.innerHTML = `<span class="step-dot"></span><span>${name}</span>`;
      chip.addEventListener("click", () => {
        this.goToScene(idx);
      });
      this.dom.stepperNav.appendChild(chip);
    });

    // Theme check
    const savedTheme = localStorage.getItem("daa-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
  }

  bindEvents() {
    // Play/Pause
    this.dom.btnPlayPause.addEventListener("click", () => this.togglePlay());

    // Step Forward / Backward
    this.dom.btnNext.addEventListener("click", () => this.nextStep());
    this.dom.btnPrev.addEventListener("click", () => this.prevStep());

    // Reset
    this.dom.btnReset.addEventListener("click", () => this.resetAll());

    // Demo Mode toggle
    this.dom.btnDemoMode.addEventListener("click", () => this.toggleDemoMode());

    // Speed buttons
    document.querySelectorAll(".speed-btn").forEach(btn => {
      btn.addEventListener("click", e => {
        document.querySelectorAll(".speed-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.speed = btn.dataset.speed;
        this.restartPlaybackLoop();
      });
    });

    // Sound toggle
    this.dom.btnSound.addEventListener("click", () => {
      this.sound.enabled = !this.sound.enabled;
      this.dom.btnSound.style.opacity = this.sound.enabled ? "1" : "0.45";
    });

    // Theme toggle
    this.dom.btnTheme.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("daa-theme", next);
    });

    // Keyboard controls
    window.addEventListener("keydown", e => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.code === "Space") {
        e.preventDefault();
        this.togglePlay();
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        this.nextStep();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        this.prevStep();
      } else if (e.key === "r" || e.key === "R") {
        this.resetAll();
      } else if (e.key === "d" || e.key === "D") {
        this.toggleDemoMode();
      } else if (e.key === "1") {
        this.setSpeed("SLOW");
      } else if (e.key === "2") {
        this.setSpeed("MEDIUM");
      } else if (e.key === "3") {
        this.setSpeed("FAST");
      }
    });
  }

  setSpeed(speedName) {
    this.speed = speedName;
    document.querySelectorAll(".speed-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.speed === speedName);
    });
    this.restartPlaybackLoop();
  }

  togglePlay() {
    this.isPlaying = !this.isPlaying;
    this.updateControlsState();
    if (this.isPlaying) {
      this.startPlaybackLoop();
    } else {
      this.stopPlaybackLoop();
    }
  }

  toggleDemoMode() {
    this.isDemoMode = !this.isDemoMode;
    this.dom.btnDemoMode.classList.toggle("active", this.isDemoMode);
    if (this.isDemoMode) {
      this.isPlaying = false;
      this.stopPlaybackLoop();
    }
    this.updateControlsState();
  }

  goToScene(sceneId) {
    if (sceneId === this.currentScene) return;
    this.currentScene = sceneId;
    this.sound.sceneChangeSound();
    this.renderCurrentScene();
    this.updateStepperNav();
  }

  nextScene() {
    if (this.currentScene < SceneId.ANALYSIS) {
      this.goToScene(this.currentScene + 1);
    }
  }

  prevScene() {
    if (this.currentScene > SceneId.INTRO) {
      this.goToScene(this.currentScene - 1);
    }
  }

  nextStep() {
    if (this.currentScene === SceneId.INTRO) {
      this.nextScene();
      return;
    }
    if (this.currentScene === SceneId.FLOOD_MAP) {
      this.nextScene();
      return;
    }
    if (this.currentScene === SceneId.SCAN_DETECT) {
      if (this.scanIndex < this.areas.length - 1) {
        this.scanIndex++;
        this.sound.compareSound();
        this.renderScanScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
      return;
    }
    if (this.currentScene === SceneId.INPUT_DATA) {
      this.nextScene();
      return;
    }
    if (this.currentScene === SceneId.DIVIDE_TREE) {
      if (this.divideStep < 3) {
        this.divideStep++;
        this.sound.compareSound();
        this.renderDivideTreeScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
      return;
    }
    if (this.currentScene === SceneId.COMPARE_MERGE) {
      if (this.timelineIndex < this.tracer.timeline.length - 1) {
        this.timelineIndex++;
        const state = this.getCurrentTimelineState();
        if (state.opType === "COMPARE") this.sound.compareSound();
        else if (state.opType === "SELECT") this.sound.selectSound();
        else if (state.opType === "MERGE_DONE") this.sound.mergeDoneSound();
        this.renderCompareMergeScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
      return;
    }
    if (this.currentScene === SceneId.SORTED_RESULT) {
      this.nextScene();
      return;
    }
    if (this.currentScene === SceneId.EVACUATION) {
      if (this.evacIndex < 5) {
        if (!this.evacCompleted.includes(this.evacIndex)) {
          this.evacCompleted.push(this.evacIndex);
        }
        this.evacIndex++;
        this.evacProgress = 0.0;
        this.sound.selectSound();
        this.renderEvacuationScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
      return;
    }
    if (this.currentScene === SceneId.ANALYSIS) {
      // Loop or pause
      this.isPlaying = false;
      this.updateControlsState();
    }
  }

  prevStep() {
    if (this.currentScene === SceneId.SCAN_DETECT && this.scanIndex > 0) {
      this.scanIndex--;
      this.renderScanScene();
      this.updateHUD();
    } else if (this.currentScene === SceneId.DIVIDE_TREE && this.divideStep > 0) {
      this.divideStep--;
      this.renderDivideTreeScene();
      this.updateHUD();
    } else if (this.currentScene === SceneId.COMPARE_MERGE && this.timelineIndex > 0) {
      this.timelineIndex--;
      this.renderCompareMergeScene();
      this.updateHUD();
    } else if (this.currentScene === SceneId.EVACUATION && this.evacIndex > 0) {
      this.evacIndex--;
      this.evacCompleted = this.evacCompleted.filter(idx => idx < this.evacIndex);
      this.renderEvacuationScene();
      this.updateHUD();
    } else {
      this.prevScene();
    }
  }

  resetAll() {
    this.currentScene = SceneId.INTRO;
    this.isPlaying = true;
    this.scanIndex = 0;
    this.divideStep = 0;
    this.timelineIndex = 0;
    this.evacIndex = 0;
    this.evacProgress = 0.0;
    this.evacCompleted = [];
    this.renderCurrentScene();
    this.updateControlsState();
    this.updateStepperNav();
    this.restartPlaybackLoop();
  }

  startPlaybackLoop() {
    this.stopPlaybackLoop();
    if (!this.isPlaying || this.isDemoMode) return;

    const interval = this.speedDurations[this.speed] || 550;
    this.stepTimer = setInterval(() => {
      this.autoAdvanceStep();
    }, interval);
  }

  stopPlaybackLoop() {
    if (this.stepTimer) {
      clearInterval(this.stepTimer);
      this.stepTimer = null;
    }
  }

  restartPlaybackLoop() {
    this.stopPlaybackLoop();
    this.startPlaybackLoop();
  }

  autoAdvanceStep() {
    if (!this.isPlaying) return;

    if (this.currentScene === SceneId.INTRO) {
      // Wait slightly then go to Scene 1
      this.nextScene();
    } else if (this.currentScene === SceneId.FLOOD_MAP) {
      // Show for 3 intervals then go to scan
      this.nextScene();
    } else if (this.currentScene === SceneId.SCAN_DETECT) {
      if (this.scanIndex < this.areas.length - 1) {
        this.scanIndex++;
        this.sound.compareSound();
        this.renderScanScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
    } else if (this.currentScene === SceneId.INPUT_DATA) {
      this.nextScene();
    } else if (this.currentScene === SceneId.DIVIDE_TREE) {
      if (this.divideStep < 3) {
        this.divideStep++;
        this.sound.compareSound();
        this.renderDivideTreeScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
    } else if (this.currentScene === SceneId.COMPARE_MERGE) {
      if (this.timelineIndex < this.tracer.timeline.length - 1) {
        this.timelineIndex++;
        const state = this.getCurrentTimelineState();
        if (state.opType === "COMPARE") this.sound.compareSound();
        else if (state.opType === "SELECT") this.sound.selectSound();
        else if (state.opType === "MERGE_DONE") this.sound.mergeDoneSound();
        this.renderCompareMergeScene();
        this.updateHUD();
      } else {
        this.nextScene();
      }
    } else if (this.currentScene === SceneId.SORTED_RESULT) {
      this.nextScene();
    } else if (this.currentScene === SceneId.EVACUATION) {
      this.evacProgress += 0.25;
      if (this.evacProgress >= 1.0) {
        if (!this.evacCompleted.includes(this.evacIndex)) {
          this.evacCompleted.push(this.evacIndex);
        }
        if (this.evacIndex < 4) {
          this.evacIndex++;
          this.evacProgress = 0.0;
          this.sound.selectSound();
        } else {
          this.nextScene();
        }
      }
      this.renderEvacuationScene();
      this.updateHUD();
    } else if (this.currentScene === SceneId.ANALYSIS) {
      // At analysis scene, we remain paused
      this.isPlaying = false;
      this.updateControlsState();
      this.stopPlaybackLoop();
    }
  }

  getCurrentTimelineState() {
    return this.tracer.timeline[this.timelineIndex] || null;
  }

  updateControlsState() {
    this.dom.playPauseText.textContent = this.isPlaying ? "PAUSE" : "PLAY";
    this.dom.btnPlayPause.innerHTML = this.isPlaying
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg> <span>PAUSE</span>`
      : `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> <span>PLAY</span>`;

    if (this.isDemoMode) {
      this.dom.statusBadge.className = "badge badge-demo";
      this.dom.statusBadgeText.textContent = "DEMO (STEP)";
    } else if (this.isPlaying) {
      this.dom.statusBadge.className = "badge badge-running";
      this.dom.statusBadgeText.textContent = "RUNNING";
    } else {
      this.dom.statusBadge.className = "badge badge-paused";
      this.dom.statusBadgeText.textContent = "PAUSED";
    }
  }

  updateStepperNav() {
    const chips = this.dom.stepperNav.querySelectorAll(".step-chip");
    chips.forEach((chip, idx) => {
      chip.classList.toggle("active", idx === this.currentScene);
      chip.classList.toggle("completed", idx < this.currentScene);
    });
    // Scroll chip into view
    const activeChip = chips[this.currentScene];
    if (activeChip) {
      activeChip.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }

  updateHUD() {
    const state = this.getCurrentTimelineState();
    const scene = this.currentScene;

    if (scene === SceneId.COMPARE_MERGE && state) {
      this.dom.hudOpBadge.textContent = state.opType;
      this.dom.hudActiveRange.textContent = `[${state.activeRange[0]}..${state.activeRange[1]}]`;
      this.dom.hudTreeDepth.textContent = state.depth;
      this.dom.hudCompsCount.textContent = state.comparisonsSoFar;
      this.dom.hudMergesCount.textContent = state.mergesSoFar;
      this.dom.hudExplanation.innerHTML = `<strong>${state.explanation}</strong>${state.whyText}`;
    } else if (scene === SceneId.SCAN_DETECT) {
      const active = this.areas[this.scanIndex];
      this.dom.hudOpBadge.textContent = "SCANNING";
      this.dom.hudActiveRange.textContent = `[0..19]`;
      this.dom.hudTreeDepth.textContent = "0";
      this.dom.hudCompsCount.textContent = "0";
      this.dom.hudMergesCount.textContent = "0";
      this.dom.hudExplanation.innerHTML = `<strong>Telemetry Scan: Sector ${active.areaId} (${active.name})</strong>Measured depth: ${active.waterLevel.toFixed(1)}m. Population: ${active.population.toLocaleString()}. Priority triage category: ${active.getPriority()}.`;
    } else if (scene === SceneId.DIVIDE_TREE) {
      const stepDescs = [
        "Unbroken 20-element initial array.",
        "Divided at mid=9 into Left [0..9] and Right [10..19].",
        "Divided recursively into four 5-element quarters.",
        "Base cases reached: Subarrays of 2-3 items and atomic 1-item arrays.",
      ];
      this.dom.hudOpBadge.textContent = "DIVIDE";
      this.dom.hudActiveRange.textContent = `Depth ${this.divideStep}`;
      this.dom.hudTreeDepth.textContent = `${this.divideStep} / 4`;
      this.dom.hudCompsCount.textContent = "0";
      this.dom.hudMergesCount.textContent = "0";
      this.dom.hudExplanation.innerHTML = `<strong>Divide Step ${this.divideStep + 1} of 4</strong>${stepDescs[this.divideStep]}`;
    } else if (scene === SceneId.EVACUATION) {
      const top5 = this.sortedAreas.slice(0, 5);
      const target = top5[this.evacIndex] || top5[0];
      this.dom.hudOpBadge.textContent = "EVACUATING";
      this.dom.hudActiveRange.textContent = `Top 5 Zones`;
      this.dom.hudTreeDepth.textContent = `${this.evacIndex + 1} / 5`;
      this.dom.hudCompsCount.textContent = "65 (Done)";
      this.dom.hudMergesCount.textContent = "19 (Done)";
      this.dom.hudExplanation.innerHTML = `<strong>Dispatching Rescue Fleet #${this.evacIndex + 1}</strong>Target: ${target.name} (${target.waterLevel.toFixed(1)}m water level). Evacuating ${target.population.toLocaleString()} citizens to Central Relief Shelter.`;
    } else if (scene === SceneId.ANALYSIS) {
      this.dom.hudOpBadge.textContent = "PROVEN";
      this.dom.hudActiveRange.textContent = "Θ(n log n)";
      this.dom.hudTreeDepth.textContent = `${this.tracer.maxDepth} Levels`;
      this.dom.hudCompsCount.textContent = `${this.tracer.comparisonsCount}`;
      this.dom.hudMergesCount.textContent = `${this.tracer.mergesCount}`;
      this.dom.hudExplanation.innerHTML = `<strong>Complexity Verification Complete</strong>Merge Sort guarantees O(n log n) running time with zero worst-case degradation. Total comparisons made: ${this.tracer.comparisonsCount}, Merges performed: ${this.tracer.mergesCount}.`;
    } else {
      this.dom.hudOpBadge.textContent = "STANDBY";
      this.dom.hudActiveRange.textContent = "[0..19]";
      this.dom.hudTreeDepth.textContent = "0";
      this.dom.hudCompsCount.textContent = "0";
      this.dom.hudMergesCount.textContent = "0";
      this.dom.hudExplanation.innerHTML = `<strong>${SCENE_NAMES[scene]}</strong>${SCENE_DESCRIPTIONS[scene]}`;
    }
  }

  renderCurrentScene() {
    this.dom.sceneTitle.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polygon points="12 8 8 12 12 16 12 8"></polygon>
        <line x1="16" y1="12" x2="12" y2="12"></line>
      </svg>
      ${SCENE_NAMES[this.currentScene]}
    `;
    this.dom.sceneSubtitle.textContent = SCENE_DESCRIPTIONS[this.currentScene];
    this.dom.sceneMetaBadge.textContent = `STAGE ${this.currentScene + 1} / 9`;

    this.updateHUD();

    switch (this.currentScene) {
      case SceneId.INTRO:
        this.renderIntroScene();
        break;
      case SceneId.FLOOD_MAP:
        this.renderFloodMapScene();
        break;
      case SceneId.SCAN_DETECT:
        this.renderScanScene();
        break;
      case SceneId.INPUT_DATA:
        this.renderInputDataScene();
        break;
      case SceneId.DIVIDE_TREE:
        this.renderDivideTreeScene();
        break;
      case SceneId.COMPARE_MERGE:
        this.renderCompareMergeScene();
        break;
      case SceneId.SORTED_RESULT:
        this.renderSortedResultScene();
        break;
      case SceneId.EVACUATION:
        this.renderEvacuationScene();
        break;
      case SceneId.ANALYSIS:
        this.renderAnalysisScene();
        break;
    }
  }

  // -------------------------------------------------------------
  // SCENE 0: INTRO
  // -------------------------------------------------------------
  renderIntroScene() {
    this.dom.sceneContainer.innerHTML = `
      <div class="intro-view">
        <div class="intro-hero-badge">COLLEGE DAA FA-2 EDUCATIONAL SIMULATION</div>
        <h2>Flood Evacuation Priority System<br />Using <span>Merge Sort (Divide & Conquer)</span></h2>
        
        <div class="intro-problem-card">
          <h4>Real-World Problem Context</h4>
          <p>
            During severe monsoon flooding in urban Pune, emergency response resources (rescue boats, ambulances, evacuation personnel) are scarce.
            Authorities must systematically triage affected sectors strictly in <strong>descending order of water levels</strong> so that communities facing catastrophic flooding are evacuated immediately.
          </p>
        </div>

        <div class="pillars-grid">
          <div class="pillar-card">
            <span class="pillar-tag">ALGORITHM</span>
            <h3 class="pillar-title">Merge Sort</h3>
            <p class="pillar-desc">
              Guaranteed optimal <strong>O(n log n)</strong> complexity in best, average, and worst cases with stable triage preservation.
            </p>
          </div>
          <div class="pillar-card">
            <span class="pillar-tag">INPUT DATA</span>
            <h3 class="pillar-title">20 Pune Sectors</h3>
            <p class="pillar-desc">
              Real telemetry tracking water gauge levels (2.5m to 8.2m) and impacted citizen counts across municipal wards.
            </p>
          </div>
          <div class="pillar-card">
            <span class="pillar-tag">OUTPUT GOAL</span>
            <h3 class="pillar-title">Priority Triage</h3>
            <p class="pillar-desc">
              Dynamic rank dispatch queue ordering sectors into Critical, High, Medium, and Low risk evacuation tiers.
            </p>
          </div>
        </div>

        <button id="btnStartSimulation" class="btn btn-primary btn-launch">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          LAUNCH LIVE SIMULATION
        </button>
      </div>
    `;

    document.getElementById("btnStartSimulation")?.addEventListener("click", () => {
      this.nextScene();
    });
  }

  // -------------------------------------------------------------
  // SCENE 1: FLOOD DATA MAP
  // -------------------------------------------------------------
  renderFloodMapScene() {
    let gridHtml = `<div class="flood-grid">`;
    this.areas.forEach(area => {
      const waterPct = Math.min(100, (area.waterLevel / 10.0) * 100);
      const lvlColor = getWaterLevelColor(area.waterLevel);
      const priority = area.getPriority();

      gridHtml += `
        <div class="sector-card">
          <div class="sector-water-fill" style="height: ${waterPct * 0.45}%;"></div>
          <div>
            <div class="sector-header">
              <span class="sector-id">${area.areaId}</span>
              <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${lvlColor};"></span>
            </div>
            <div class="sector-name" title="${area.name}">${area.name}</div>
          </div>
          <div>
            <div class="gauge-container">
              <div class="gauge-fill" style="width: ${waterPct}%; background: ${lvlColor};"></div>
            </div>
            <div class="sector-footer">
              <span class="water-val" style="color: ${lvlColor};">${area.waterLevel.toFixed(1)}m</span>
              <span class="pop-val">Pop: ${area.population.toLocaleString()}</span>
            </div>
          </div>
        </div>
      `;
    });
    gridHtml += `</div>`;
    this.dom.sceneContainer.innerHTML = gridHtml;
  }

  // -------------------------------------------------------------
  // SCENE 2: SCAN DETECTION
  // -------------------------------------------------------------
  renderScanScene() {
    const active = this.areas[this.scanIndex];
    const lvlColor = getWaterLevelColor(active.waterLevel);
    const scanPct = Math.round(((this.scanIndex + 1) / this.areas.length) * 100);

    let miniGridHtml = `<div class="mini-grid">`;
    this.areas.forEach((area, idx) => {
      const isActive = idx === this.scanIndex;
      const isScanned = idx < this.scanIndex;
      const cardClass = isActive ? "active-scan" : (isScanned ? "scanned" : "");
      miniGridHtml += `
        <div class="mini-card ${cardClass}">
          <div style="display:flex; justify-content:space-between; font-size:9.5px; font-weight:700;">
            <span style="color:${isActive ? 'var(--accent-primary)' : 'inherit'};">${area.areaId}</span>
            <span style="font-family:var(--font-mono); color:${getWaterLevelColor(area.waterLevel)};">${area.waterLevel.toFixed(1)}m</span>
          </div>
          <div style="font-size:10px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${area.name}</div>
          <div class="gauge-container" style="height:4px; margin:4px 0 0 0;">
            <div class="gauge-fill" style="width:${(area.waterLevel / 10.0) * 100}%; background:${getWaterLevelColor(area.waterLevel)};"></div>
          </div>
        </div>
      `;
    });
    miniGridHtml += `</div>`;

    this.dom.sceneContainer.innerHTML = `
      <div class="scan-layout">
        ${miniGridHtml}
        <div class="spotlight-hud">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <h4 style="font-size:12px; font-weight:800; color:var(--accent-primary); text-transform:uppercase;">TELEMETRY SENSOR FEED</h4>
            <span class="badge badge-demo">SCANNING ${this.scanIndex + 1} OF 20</span>
          </div>

          <div class="spotlight-card">
            <div style="font-size:10.5px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">CURRENTLY ANALYZING</div>
            <div style="font-size:18px; font-weight:800; color:var(--text-primary); margin:2px 0 12px 0;">${active.areaId} — ${active.name.toUpperCase()}</div>

            <div style="font-size:10px; font-weight:700; color:var(--text-muted);">MEASURED WATER DEPTH</div>
            <div style="font-size:32px; font-weight:900; color:${lvlColor}; font-family:var(--font-mono);">${active.waterLevel.toFixed(1)} <span style="font-size:18px;">METERS</span></div>

            <div style="margin:10px 0;">
              <span class="badge" style="background:${lvlColor}15; color:${lvlColor}; border:1px solid ${lvlColor}40;">
                PRIORITY: ${active.getPriority()}
              </span>
            </div>

            <div style="font-size:10px; font-weight:700; color:var(--text-muted); margin-top:10px;">AFFECTED CITIZENS</div>
            <div style="font-size:15px; font-weight:800; color:var(--text-primary);">${active.population.toLocaleString()} Residents</div>
          </div>

          <div>
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span style="font-weight:700; color:var(--text-muted);">Telemetry Scan Progress</span>
              <span style="font-weight:800; color:var(--accent-primary);">${scanPct}%</span>
            </div>
            <div class="gauge-container" style="height:8px;">
              <div class="gauge-fill" style="width:${scanPct}%; background:var(--accent-primary);"></div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // -------------------------------------------------------------
  // SCENE 3: INPUT DATA ARRAY
  // -------------------------------------------------------------
  renderInputDataScene() {
    let gridHtml = `<div class="flood-grid">`;
    this.areas.forEach((area, idx) => {
      const lvlColor = getWaterLevelColor(area.waterLevel);
      gridHtml += `
        <div class="sector-card" style="padding:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-family:var(--font-mono); font-size:10.5px; font-weight:800; color:var(--text-muted);">[${idx}]</span>
            <span class="sector-id">${area.areaId}</span>
          </div>
          <div class="sector-name" style="font-size:13px; margin:6px 0;">${area.name}</div>
          <div style="background:var(--bg-card-alt); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:6px 8px; margin-bottom:6px;">
            <div style="font-size:9.5px; color:var(--text-muted);">Water Level:</div>
            <div style="font-size:16px; font-weight:800; font-family:var(--font-mono); color:${lvlColor};">${area.waterLevel.toFixed(1)} m</div>
          </div>
          <div class="gauge-container" style="height:5px;">
            <div class="gauge-fill" style="width:${(area.waterLevel / 10.0) * 100}%; background:${lvlColor};"></div>
          </div>
        </div>
      `;
    });
    gridHtml += `</div>`;
    this.dom.sceneContainer.innerHTML = gridHtml;
  }

  // -------------------------------------------------------------
  // SCENE 4: DIVIDE & CONQUER TREE & PARTITIONS
  // -------------------------------------------------------------
  renderDivideTreeScene() {
    // Dynamic Subarrays rendering based on current divideStep
    let partitionHtml = "";
    if (this.divideStep === 0) {
      partitionHtml = `
        <div style="font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:6px;">Complete Unbroken Array [0..19] (20 Sectors):</div>
        <div class="cards-row">
          ${this.areas.map(a => `
            <div class="algo-card" style="min-width:38px; padding:3px;">
              <span style="font-size:8px; font-weight:800; color:var(--accent-primary);">${a.areaId}</span>
              <span style="font-size:9.5px; font-weight:800; font-family:var(--font-mono); color:${getWaterLevelColor(a.waterLevel)};">${a.waterLevel.toFixed(1)}</span>
            </div>
          `).join("")}
        </div>
      `;
    } else if (this.divideStep === 1) {
      const left10 = this.areas.slice(0, 10);
      const right10 = this.areas.slice(10, 20);
      partitionHtml = `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; width:100%;">
          <div class="subgroup-block">
            <span style="font-size:11px; font-weight:800; color:var(--accent-primary);">LEFT HALF: Sectors [A01..A10] (10 Areas)</span>
            <div class="cards-row">
              ${left10.map(a => `
                <div class="algo-card" style="min-width:44px;">
                  <span style="font-size:9px; font-weight:800; color:var(--accent-primary);">${a.areaId}</span>
                  <span style="font-size:10px; font-weight:700;">${a.name.slice(0, 6)}</span>
                  <span style="font-size:11px; font-weight:800; color:${getWaterLevelColor(a.waterLevel)}; font-family:var(--font-mono);">${a.waterLevel.toFixed(1)}m</span>
                </div>
              `).join("")}
            </div>
          </div>
          <div class="subgroup-block">
            <span style="font-size:11px; font-weight:800; color:var(--accent-primary);">RIGHT HALF: Sectors [A11..A20] (10 Areas)</span>
            <div class="cards-row">
              ${right10.map(a => `
                <div class="algo-card" style="min-width:44px;">
                  <span style="font-size:9px; font-weight:800; color:var(--accent-primary);">${a.areaId}</span>
                  <span style="font-size:10px; font-weight:700;">${a.name.slice(0, 6)}</span>
                  <span style="font-size:11px; font-weight:800; color:${getWaterLevelColor(a.waterLevel)}; font-family:var(--font-mono);">${a.waterLevel.toFixed(1)}m</span>
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      `;
    } else if (this.divideStep === 2) {
      const quarters = [
        { title: "[A01..A05] (5 Areas)", items: this.areas.slice(0, 5) },
        { title: "[A06..A10] (5 Areas)", items: this.areas.slice(5, 10) },
        { title: "[A11..A15] (5 Areas)", items: this.areas.slice(10, 15) },
        { title: "[A16..A20] (5 Areas)", items: this.areas.slice(15, 20) },
      ];
      partitionHtml = `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; width:100%;">
          ${quarters.map(q => `
            <div class="subgroup-block">
              <span style="font-size:11px; font-weight:800; color:var(--accent-primary);">${q.title}</span>
              <div class="cards-row">
                ${q.items.map(a => `
                  <div class="algo-card" style="min-width:48px;">
                    <span style="font-size:9px; font-weight:800; color:var(--accent-primary);">${a.areaId}</span>
                    <span style="font-size:10px; font-weight:700;">${a.name.slice(0, 6)}</span>
                    <span style="font-size:11px; font-weight:800; color:${getWaterLevelColor(a.waterLevel)}; font-family:var(--font-mono);">${a.waterLevel.toFixed(1)}m</span>
                  </div>
                `).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      `;
    } else {
      const baseSubgroups = [
        { title: "Subarray [A01 A02 A03]", items: this.areas.slice(0, 3) },
        { title: "Subarray [A04 A05]", items: this.areas.slice(3, 5) },
        { title: "Subarray [A06 A07 A08]", items: this.areas.slice(5, 8) },
        { title: "Subarray [A09 A10]", items: this.areas.slice(8, 10) },
      ];
      partitionHtml = `
        <div style="font-size:12px; font-weight:800; color:var(--accent-primary); margin-bottom:6px;">RECURSION BASE CASES (Subarrays of 2-3 Elements down to Atomic Arrays)</div>
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; width:100%;">
          ${baseSubgroups.map(g => `
            <div class="subgroup-block">
              <span style="font-size:10.5px; font-weight:800; color:var(--text-primary);">${g.title}</span>
              <div class="cards-row">
                ${g.items.map(a => `
                  <div class="algo-card" style="min-width:54px; padding:6px;">
                    <span style="font-size:10px; font-weight:800; color:var(--accent-primary);">${a.areaId}</span>
                    <span style="font-size:10.5px; font-weight:700;">${a.name.slice(0, 7)}</span>
                    <span style="font-size:12px; font-weight:800; color:${getWaterLevelColor(a.waterLevel)}; font-family:var(--font-mono);">${a.waterLevel.toFixed(1)}m</span>
                  </div>
                `).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      `;
    }

    this.dom.sceneContainer.innerHTML = `
      <div class="divide-layout">
        <!-- Visual Tree Section -->
        <div class="tree-canvas-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:12px; font-weight:800; color:var(--text-primary); text-transform:uppercase;">RECURSION DECOMPOSITION TREE (DEPTH 0 TO 3)</span>
            <span class="badge badge-demo">STEP ${this.divideStep + 1} OF 4</span>
          </div>

          <!-- SVG Branching Tree -->
          <svg style="width:100%; height:160px;" viewBox="0 0 800 150">
            <!-- Level 0: Root -->
            <rect x="350" y="5" width="100" height="28" rx="6" fill="${this.divideStep >= 0 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 0 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 0 ? '2' : '1'}"></rect>
            <text x="400" y="24" text-anchor="middle" font-family="var(--font-sans)" font-size="11" font-weight="800" fill="var(--text-primary)">Root [20 Elements]</text>

            <!-- Lines to Level 1 -->
            <line x1="375" y1="33" x2="200" y2="55" stroke="${this.divideStep >= 1 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="2"></line>
            <line x1="425" y1="33" x2="600" y2="55" stroke="${this.divideStep >= 1 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="2"></line>

            <!-- Level 1: Halves -->
            <rect x="150" y="55" width="100" height="28" rx="6" fill="${this.divideStep >= 1 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 1 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 1 ? '2' : '1'}"></rect>
            <text x="200" y="74" text-anchor="middle" font-family="var(--font-sans)" font-size="11" font-weight="800" fill="var(--text-primary)">Left [10 Elements]</text>

            <rect x="550" y="55" width="100" height="28" rx="6" fill="${this.divideStep >= 1 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 1 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 1 ? '2' : '1'}"></rect>
            <text x="600" y="74" text-anchor="middle" font-family="var(--font-sans)" font-size="11" font-weight="800" fill="var(--text-primary)">Right [10 Elements]</text>

            <!-- Lines to Level 2 -->
            <line x1="180" y1="83" x2="100" y2="105" stroke="${this.divideStep >= 2 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="1.5"></line>
            <line x1="220" y1="83" x2="300" y2="105" stroke="${this.divideStep >= 2 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="1.5"></line>
            <line x1="580" y1="83" x2="500" y2="105" stroke="${this.divideStep >= 2 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="1.5"></line>
            <line x1="620" y1="83" x2="700" y2="105" stroke="${this.divideStep >= 2 ? 'var(--accent-primary)' : 'var(--border-subtle)'}" stroke-width="1.5"></line>

            <!-- Level 2: Quarters -->
            <rect x="60" y="105" width="80" height="26" rx="5" fill="${this.divideStep >= 2 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 2 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 2 ? '2' : '1'}"></rect>
            <text x="100" y="122" text-anchor="middle" font-family="var(--font-sans)" font-size="10" font-weight="700" fill="var(--text-primary)">Q1 [5 Areas]</text>

            <rect x="260" y="105" width="80" height="26" rx="5" fill="${this.divideStep >= 2 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 2 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 2 ? '2' : '1'}"></rect>
            <text x="300" y="122" text-anchor="middle" font-family="var(--font-sans)" font-size="10" font-weight="700" fill="var(--text-primary)">Q2 [5 Areas]</text>

            <rect x="460" y="105" width="80" height="26" rx="5" fill="${this.divideStep >= 2 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 2 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 2 ? '2' : '1'}"></rect>
            <text x="500" y="122" text-anchor="middle" font-family="var(--font-sans)" font-size="10" font-weight="700" fill="var(--text-primary)">Q3 [5 Areas]</text>

            <rect x="660" y="105" width="80" height="26" rx="5" fill="${this.divideStep >= 2 ? 'var(--accent-light)' : 'var(--bg-card)'}" stroke="${this.divideStep === 2 ? 'var(--accent-primary)' : 'var(--border-default)'}" stroke-width="${this.divideStep === 2 ? '2' : '1'}"></rect>
            <text x="700" y="122" text-anchor="middle" font-family="var(--font-sans)" font-size="10" font-weight="700" fill="var(--text-primary)">Q4 [5 Areas]</text>
          </svg>
        </div>

        <!-- Partitions display -->
        <div class="partitions-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; font-weight:800; color:var(--text-primary);">PHYSICAL SUBARRAY PARTITIONS & CARD SIZING</span>
            <div style="display:flex; gap:6px;">
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:10px;" id="btnDivideStepPrev" ${this.divideStep === 0 ? 'disabled' : ''}>&larr; Prev Division</button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:10px;" id="btnDivideStepNext" ${this.divideStep === 3 ? 'disabled' : ''}>Next Division &rarr;</button>
            </div>
          </div>
          ${partitionHtml}
        </div>
      </div>
    `;

    document.getElementById("btnDivideStepPrev")?.addEventListener("click", () => {
      if (this.divideStep > 0) {
        this.divideStep--;
        this.renderDivideTreeScene();
        this.updateHUD();
      }
    });
    document.getElementById("btnDivideStepNext")?.addEventListener("click", () => {
      if (this.divideStep < 3) {
        this.divideStep++;
        this.renderDivideTreeScene();
        this.updateHUD();
      }
    });
  }

  // -------------------------------------------------------------
  // SCENE 5: COMPARE & MERGE ARENA
  // -------------------------------------------------------------
  renderCompareMergeScene() {
    const state = this.getCurrentTimelineState();
    if (!state) return;

    const leftSub = state.leftSub;
    const rightSub = state.rightSub;
    const currL = state.currLeftIdx;
    const currR = state.currRightIdx;
    const merged = state.mergedBuffer;
    const isFinalMerge = state.activeRange[0] === 0 && state.activeRange[1] === 19;

    const hasComparison = state.compLeftVal !== null && state.compRightVal !== null;
    const lItem = currL !== null && currL < leftSub.length ? leftSub[currL] : null;
    const rItem = currR !== null && currR < rightSub.length ? rightSub[currR] : null;

    this.dom.sceneContainer.innerHTML = `
      <div class="compare-layout">
        ${isFinalMerge ? `
          <div style="background:var(--critical-bg); border:1px solid var(--critical-border); color:var(--critical-color); padding:6px 14px; border-radius:var(--radius-sm); font-size:11.5px; font-weight:800; display:flex; align-items:center; gap:8px;">
            <span class="pulse-dot"></span>
            FINAL MERGE: Combining the two 10-element sorted halves [A01..A10] and [A11..A20] into the final 20-element evacuation ranking!
          </div>
        ` : ''}

        <!-- Top Row: Left and Right Subarrays -->
        <div class="subarrays-row">
          <div class="subarray-panel">
            <div class="subarray-header">
              <span>LEFT SORTED SUBARRAY (${leftSub.length} Elements)</span>
              <span class="badge badge-demo">L-PTR: ${currL !== null ? `[${currL}]` : 'DONE'}</span>
            </div>
            <div class="cards-row">
              ${leftSub.length === 0 ? '<span style="font-size:11px; color:var(--text-muted);">(Empty)</span>' : ''}
              ${leftSub.map((item, idx) => {
                const isActive = idx === currL;
                const isMerged = currL !== null && idx < currL;
                const cardClass = isActive ? "pointer-active" : (isMerged ? "dimmed" : "");
                return `
                  <div class="algo-card ${cardClass}" style="min-width:52px; padding:6px;">
                    <div style="display:flex; justify-content:space-between; width:100%; font-size:9px; font-weight:800;">
                      <span style="color:var(--accent-primary);">${item.areaId}</span>
                      ${isActive ? '<span style="color:var(--compare-color);">PTR</span>' : ''}
                    </div>
                    <div style="font-size:10px; font-weight:700; margin:2px 0;">${item.name.slice(0, 7)}</div>
                    <div style="font-size:12px; font-weight:800; font-family:var(--font-mono); color:${getWaterLevelColor(item.waterLevel)};">${item.waterLevel.toFixed(1)}m</div>
                  </div>
                `;
              }).join("")}
            </div>
          </div>

          <div class="subarray-panel">
            <div class="subarray-header">
              <span>RIGHT SORTED SUBARRAY (${rightSub.length} Elements)</span>
              <span class="badge badge-demo">R-PTR: ${currR !== null ? `[${currR}]` : 'DONE'}</span>
            </div>
            <div class="cards-row">
              ${rightSub.length === 0 ? '<span style="font-size:11px; color:var(--text-muted);">(Empty)</span>' : ''}
              ${rightSub.map((item, idx) => {
                const isActive = idx === currR;
                const isMerged = currR !== null && idx < currR;
                const cardClass = isActive ? "pointer-active" : (isMerged ? "dimmed" : "");
                return `
                  <div class="algo-card ${cardClass}" style="min-width:52px; padding:6px;">
                    <div style="display:flex; justify-content:space-between; width:100%; font-size:9px; font-weight:800;">
                      <span style="color:var(--accent-primary);">${item.areaId}</span>
                      ${isActive ? '<span style="color:var(--compare-color);">PTR</span>' : ''}
                    </div>
                    <div style="font-size:10px; font-weight:700; margin:2px 0;">${item.name.slice(0, 7)}</div>
                    <div style="font-size:12px; font-weight:800; font-family:var(--font-mono); color:${getWaterLevelColor(item.waterLevel)};">${item.waterLevel.toFixed(1)}m</div>
                  </div>
                `;
              }).join("")}
            </div>
          </div>
        </div>

        <!-- Middle Arena: Comparison Spotlight -->
        <div class="comparison-arena">
          <div style="position:absolute; top:8px; left:14px; font-size:10px; font-weight:800; color:var(--compare-color); text-transform:uppercase;">
            ACTIVE COMPARISON SPOTLIGHT
          </div>

          ${hasComparison && lItem && rItem ? `
            <div class="vs-battle-box">
              <div class="versus-fighter" style="${state.selectedItem?.areaId === lItem.areaId ? 'border-color:var(--selected-border); background:var(--selected-bg);' : ''}">
                <div style="font-size:10px; font-weight:800; color:var(--accent-primary);">${lItem.areaId} — ${lItem.name}</div>
                <div style="font-size:24px; font-weight:900; font-family:var(--font-mono); color:${getWaterLevelColor(lItem.waterLevel)};">${lItem.waterLevel.toFixed(1)} m</div>
              </div>

              <div class="vs-icon-badge">
                ${state.compLeftVal >= state.compRightVal ? '&ge;' : '&lt;'}
              </div>

              <div class="versus-fighter" style="${state.selectedItem?.areaId === rItem.areaId ? 'border-color:var(--selected-border); background:var(--selected-bg);' : ''}">
                <div style="font-size:10px; font-weight:800; color:var(--accent-primary);">${rItem.areaId} — ${rItem.name}</div>
                <div style="font-size:24px; font-weight:900; font-family:var(--font-mono); color:${getWaterLevelColor(rItem.waterLevel)};">${rItem.waterLevel.toFixed(1)} m</div>
              </div>
            </div>

            ${state.selectedItem ? `
              <div style="margin-top:10px;">
                <span class="badge" style="background:var(--selected-bg); color:var(--selected-color); border:1px solid var(--selected-border); font-size:11px;">
                  &check; SELECTED FOR HIGHER PRIORITY: ${state.selectedItem.name} (${state.selectedItem.waterLevel.toFixed(1)}m)
                </span>
              </div>
            ` : ''}
          ` : `
            <div style="text-align:center; padding:10px;">
              <div style="font-size:14px; font-weight:800; color:var(--accent-primary);">${state.comparisonText || "Merging subarrays..."}</div>
              <div style="font-size:11.5px; color:var(--text-secondary); margin-top:4px;">${state.whyText}</div>
            </div>
          `}
        </div>

        <!-- Bottom: Merged Buffer Building Step-by-Step -->
        <div class="merged-buffer-panel">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:11.5px; font-weight:800; color:var(--selected-color);">
              MERGED RESULT BUFFER — BUILDING STEP-BY-STEP (${merged.length} Elements Placed)
            </span>
            <span class="badge badge-demo">ACTIVE BUFFER</span>
          </div>
          <div class="cards-row">
            ${merged.length === 0 ? '<span style="font-size:11px; color:var(--text-muted); padding:10px;">[ Buffer empty — awaiting first element selection ]</span>' : ''}
            ${merged.map((item, idx) => {
              const isLatest = idx === merged.length - 1;
              return `
                <div class="algo-card ${isLatest ? 'chosen-item' : ''}" style="min-width:54px; padding:6px;">
                  <div style="display:flex; justify-content:space-between; width:100%; font-size:9px; font-weight:800;">
                    <span style="color:var(--accent-primary);">#${idx + 1}</span>
                    <span>${item.areaId}</span>
                  </div>
                  <div style="font-size:10px; font-weight:700; margin:2px 0;">${item.name.slice(0, 7)}</div>
                  <div style="font-size:12px; font-weight:800; font-family:var(--font-mono); color:${getWaterLevelColor(item.waterLevel)};">${item.waterLevel.toFixed(1)}m</div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      </div>
    `;
  }

  // -------------------------------------------------------------
  // SCENE 6: FINAL RANKING TABLE
  // -------------------------------------------------------------
  renderSortedResultScene() {
    const col1 = this.sortedAreas.slice(0, 10);
    const col2 = this.sortedAreas.slice(10, 20);

    const renderTable = (items, startRank) => `
      <div class="table-card">
        <table class="custom-table">
          <thead>
            <tr>
              <th>RANK</th>
              <th>ID</th>
              <th>AREA NAME</th>
              <th>WATER DEPTH</th>
              <th>PRIORITY</th>
            </tr>
          </thead>
          <tbody>
            ${items.map((item, idx) => {
              const rank = startRank + idx;
              const lvlColor = getWaterLevelColor(item.waterLevel);
              const rankColor = rank <= 3 ? 'var(--critical-color)' : (rank <= 8 ? 'var(--accent-primary)' : 'var(--text-muted)');
              return `
                <tr>
                  <td style="font-weight:900; color:${rankColor};">#${rank}</td>
                  <td style="font-weight:700; color:var(--text-muted);">${item.areaId}</td>
                  <td style="font-weight:700; color:var(--text-primary);">${item.name}</td>
                  <td>
                    <span style="font-weight:800; font-family:var(--font-mono); color:${lvlColor};">${item.waterLevel.toFixed(1)} m</span>
                  </td>
                  <td>
                    <span class="badge" style="background:${lvlColor}15; color:${lvlColor}; border:1px solid ${lvlColor}40; font-size:9px;">
                      ${item.getPriority()}
                    </span>
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    `;

    this.dom.sceneContainer.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <span class="badge" style="background:var(--selected-bg); color:var(--selected-color); border:1px solid var(--selected-border);">
          &check; MERGE SORT EXECUTION COMPLETE — DESCENDING EVACUATION QUEUE
        </span>
        <button id="btnExportCSV" class="btn btn-secondary" style="font-size:11px; padding:4px 10px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          Export Sorted CSV
        </button>
      </div>
      <div class="ranking-table-layout">
        ${renderTable(col1, 1)}
        ${renderTable(col2, 11)}
      </div>
    `;

    document.getElementById("btnExportCSV")?.addEventListener("click", () => {
      let csv = "Rank,Area_ID,Area_Name,Water_Level_m,Population_Affected,Priority\n";
      this.sortedAreas.forEach((a, i) => {
        csv += `${i + 1},${a.areaId},"${a.name}",${a.waterLevel},${a.population},${a.getPriority()}\n`;
      });
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", "flood_evacuation_priority_ranking.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // -------------------------------------------------------------
  // SCENE 7: EVACUATION DISPATCH MAP SIMULATION
  // -------------------------------------------------------------
  renderEvacuationScene() {
    const top5 = this.sortedAreas.slice(0, 5);
    const shelter = { x: 380, y: 320, name: "Central Relief Shelter" };

    const zones = [
      { id: "A08", name: "Hadapsar", x: 100, y: 80, area: top5[0] },
      { id: "A17", name: "Yerawada", x: 260, y: 110, area: top5[1] },
      { id: "A12", name: "Bhosari", x: 440, y: 70, area: top5[2] },
      { id: "A04", name: "Hinjewadi", x: 140, y: 280, area: top5[3] },
      { id: "A10", name: "Pimpri", x: 480, y: 260, area: top5[4] },
    ];

    let boatSvg = "";
    if (this.evacIndex < 5) {
      const activeZone = zones[this.evacIndex];
      const curX = activeZone.x + (shelter.x - activeZone.x) * this.evacProgress;
      const curY = activeZone.y + (shelter.y - activeZone.y) * this.evacProgress;
      boatSvg = `
        <g transform="translate(${curX - 16}, ${curY - 14})">
          <ellipse cx="16" cy="18" rx="14" ry="5" fill="rgba(37, 99, 235, 0.25)"></ellipse>
          <path d="M4 14 L28 14 L22 22 L10 22 Z" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"></path>
          <line x1="16" y1="4" x2="16" y2="14" stroke="#ffffff" stroke-width="2"></line>
          <polygon points="16 4 23 8 16 11" fill="#f59e0b"></polygon>
        </g>
      `;
    }

    this.dom.sceneContainer.innerHTML = `
      <div class="evacuation-layout">
        <div class="evac-map-container">
          <svg style="width:100%; height:100%; min-height:450px;" viewBox="0 0 600 400">
            <!-- Pune Mula-Mutha River -->
            <path d="M 0 160 Q 150 220 300 180 T 600 240" fill="none" stroke="#93c5fd" stroke-width="28" stroke-linecap="round"></path>
            <path d="M 0 160 Q 150 220 300 180 T 600 240" fill="none" stroke="#60a5fa" stroke-width="6" stroke-linecap="round" stroke-dasharray="6,4"></path>

            <!-- Route Lines -->
            ${zones.map((z, idx) => {
              const isDone = this.evacCompleted.includes(idx);
              const isActive = idx === this.evacIndex;
              const strokeColor = isDone ? 'var(--low-color)' : (isActive ? 'var(--compare-color)' : 'var(--border-default)');
              return `<line x1="${z.x}" y1="${z.y}" x2="${shelter.x}" y2="${shelter.y}" stroke="${strokeColor}" stroke-width="${isActive ? 2.5 : 1.5}" stroke-dasharray="${isActive ? '4,4' : 'none'}"></line>`;
            }).join("")}

            <!-- Central Shelter -->
            <circle cx="${shelter.x}" cy="${shelter.y}" r="22" fill="#ecfdf5" stroke="#059669" stroke-width="3"></circle>
            <text x="${shelter.x}" y="${shelter.y + 5}" text-anchor="middle" font-size="14">🏥</text>
            <text x="${shelter.x}" y="${shelter.y + 36}" text-anchor="middle" font-family="var(--font-sans)" font-size="10.5" font-weight="800" fill="#059669">CENTRAL RELIEF SHELTER</text>

            <!-- Zone Nodes -->
            ${zones.map((z, idx) => {
              const isDone = this.evacCompleted.includes(idx);
              const isActive = idx === this.evacIndex;
              const nodeBg = isDone ? '#10b981' : (isActive ? '#f59e0b' : '#ef4444');
              return `
                <g>
                  <circle cx="${z.x}" cy="${z.y}" r="18" fill="${nodeBg}" stroke="#ffffff" stroke-width="2.5"></circle>
                  <text x="${z.x}" y="${z.y + 4}" text-anchor="middle" font-size="12">🏠</text>
                  <text x="${z.x}" y="${z.y + 30}" text-anchor="middle" font-family="var(--font-sans)" font-size="11" font-weight="800" fill="var(--text-primary)">#${idx + 1} ${z.name}</text>
                  <text x="${z.x}" y="${z.y + 44}" text-anchor="middle" font-family="var(--font-mono)" font-size="9.5" font-weight="700" fill="${nodeBg}">${z.area.waterLevel.toFixed(1)}m</text>
                </g>
              `;
            }).join("")}

            <!-- Active Boat -->
            ${boatSvg}
          </svg>
        </div>

        <!-- Right Side Evacuation Log -->
        <div class="evac-log-container">
          <div style="font-size:12px; font-weight:800; color:var(--accent-primary); text-transform:uppercase;">
            RESCUE MISSION LOG (TOP 5 CRITICAL ZONES)
          </div>
          ${top5.map((area, idx) => {
            const isDone = this.evacCompleted.includes(idx);
            const isActive = idx === this.evacIndex;
            const cardClass = isDone ? "completed-mission" : (isActive ? "active-mission" : "");
            const statusText = isDone ? "SAFE (EVACUATED)" : (isActive ? "IN TRANSIT..." : "QUEUED");
            return `
              <div class="evac-log-card ${cardClass}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span class="badge" style="background:${idx < 3 ? 'var(--critical-bg)' : 'var(--high-bg)'}; color:${idx < 3 ? 'var(--critical-color)' : 'var(--high-color)'}; font-size:9.5px;">
                    PRIORITY #${idx + 1}
                  </span>
                  <span class="badge" style="font-size:9px; ${isDone ? 'background:var(--low-bg); color:var(--low-color);' : (isActive ? 'background:var(--compare-bg); color:var(--compare-color);' : '')}">
                    ${statusText}
                  </span>
                </div>
                <div style="font-size:13px; font-weight:800; color:var(--text-primary); margin:6px 0 2px 0;">${area.areaId} — ${area.name}</div>
                <div style="font-size:10.5px; color:var(--text-secondary);">
                  Water Depth: <strong style="color:${getWaterLevelColor(area.waterLevel)};">${area.waterLevel.toFixed(1)}m</strong> | Pop: <strong>${area.population.toLocaleString()}</strong>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    `;
  }

  // -------------------------------------------------------------
  // SCENE 8: DAA ANALYSIS & MASTER THEOREM PROOF
  // -------------------------------------------------------------
  renderAnalysisScene() {
    const proofSteps = [
      { eq: "T(n) = 2T(n/2) + O(n)", desc: "Recursive recurrence relation for Merge Sort" },
      { eq: "a = 2,  b = 2,  f(n) = O(n)", desc: "a: subproblems, b: division factor, f(n): linear merge" },
      { eq: "n^(log_b a) = n^(log₂2) = n¹ = n", desc: "Critical exponent calculation" },
      { eq: "f(n) = O(n) = Θ(n^(log_b a))", desc: "Merge cost matches critical exponent (Case 2)" },
      { eq: "Master Theorem Case 2 Applies", desc: "T(n) = Θ(n^(log_b a) · log n) = Θ(n log n)" },
      { eq: "Final Solution: Θ(n log n)", desc: "Guaranteed optimal time complexity verified" },
    ];

    this.dom.sceneContainer.innerHTML = `
      <div class="analysis-layout">
        <!-- Card 1: Master Theorem Proof -->
        <div class="analysis-card">
          <div style="font-size:12px; font-weight:800; color:var(--accent-primary); margin-bottom:10px;">
            TIME COMPLEXITY DERIVATION (MASTER THEOREM)
          </div>
          <div>
            ${proofSteps.map((step, idx) => `
              <div class="proof-step">
                <span style="font-weight:700; color:var(--accent-primary);">${step.eq}</span>
                <span class="proof-desc">${step.desc}</span>
              </div>
              ${idx < proofSteps.length - 1 ? '<div style="text-align:center; color:var(--accent-primary); font-size:12px; margin:-3px 0 3px 0;">&darr;</div>' : ''}
            `).join("")}
          </div>
        </div>

        <!-- Card 2: Bounds & Space Complexity -->
        <div class="analysis-card">
          <div style="font-size:12px; font-weight:800; color:var(--accent-primary); margin-bottom:10px;">
            ASYMPTOTIC BOUNDS & AUXILIARY SPACE
          </div>
          <div style="display:flex; flex-direction:column; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-weight:700; font-size:12px;">Best Case Complexity</span>
              <span class="badge" style="background:var(--selected-bg); color:var(--selected-color); font-size:11px;">O(n log n)</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-weight:700; font-size:12px;">Average Case Complexity</span>
              <span class="badge" style="background:var(--selected-bg); color:var(--selected-color); font-size:11px;">O(n log n)</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-weight:700; font-size:12px;">Worst Case Complexity</span>
              <span class="badge" style="background:var(--selected-bg); color:var(--selected-color); font-size:11px;">O(n log n)</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-weight:700; font-size:12px;">Auxiliary Space Complexity</span>
              <span class="badge badge-demo" style="font-size:11px;">O(n)</span>
            </div>
          </div>

          <div style="background:var(--bg-secondary); border-radius:var(--radius-sm); padding:10px; margin-top:10px; border:1px solid var(--border-subtle); font-size:11px; color:var(--text-secondary);">
            <strong style="color:var(--text-primary); display:block; margin-bottom:2px;">Why O(n) Auxiliary Space?</strong>
            Merge Sort requires auxiliary memory buffers to store and recombine disjoint subarrays in sorted order. For 20 flood areas, this requires space for 20 elements during the final merge.
          </div>
        </div>

        <!-- Card 3: Complete DAA Pipeline Flowchart (Spans 2 columns) -->
        <div class="analysis-card" style="grid-column: span 2;">
          <div style="font-size:12px; font-weight:800; color:var(--accent-primary); margin-bottom:10px;">
            COMPLETE DAA ARCHITECTURAL PIPELINE
          </div>
          <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:8px;">
            ${[
              { name: "1. SENSOR FEED", desc: "20 Water depth telemetry gauges collected" },
              { name: "2. INPUT ARRAY", desc: "Administrative initial unsorted array order" },
              { name: "3. RECURSIVE DIVIDE", desc: "Binary split down to 1-element atomic base cases" },
              { name: "4. COMPARE & SELECT", desc: "Pick sector with higher water depth first" },
              { name: "5. MERGE SUBARRAYS", desc: "Combine sorted runs into descending order" },
              { name: "6. EVACUATION QUEUE", desc: "Dispatch rescue fleet to critical zones" },
            ].map(stage => `
              <div style="background:var(--bg-secondary); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:8px 10px;">
                <div style="font-size:10px; font-weight:800; color:var(--accent-primary);">${stage.name}</div>
                <div style="font-size:10px; color:var(--text-secondary); margin-top:4px;">${stage.desc}</div>
              </div>
            `).join("")}
          </div>

          <!-- Live Telemetry Stats Box -->
          <div style="background:var(--bg-secondary); border:1px solid var(--border-subtle); border-radius:var(--radius-sm); padding:12px; margin-top:12px; display:flex; justify-content:space-around; text-align:center;">
            <div>
              <div style="font-size:10px; font-weight:700; color:var(--text-muted);">TOTAL AREAS SORTED</div>
              <div style="font-size:20px; font-weight:900; color:var(--accent-primary); font-family:var(--font-mono);">20 Areas</div>
            </div>
            <div>
              <div style="font-size:10px; font-weight:700; color:var(--text-muted);">COMPARISONS EXECUTED</div>
              <div style="font-size:20px; font-weight:900; color:var(--compare-color); font-family:var(--font-mono);">${this.tracer.comparisonsCount}</div>
            </div>
            <div>
              <div style="font-size:10px; font-weight:700; color:var(--text-muted);">SUBARRAY MERGES</div>
              <div style="font-size:20px; font-weight:900; color:var(--selected-color); font-family:var(--font-mono);">${this.tracer.mergesCount}</div>
            </div>
            <div>
              <div style="font-size:10px; font-weight:700; color:var(--text-muted);">RECURSION TREE DEPTH</div>
              <div style="font-size:20px; font-weight:900; color:var(--accent-primary); font-family:var(--font-mono);">${this.tracer.maxDepth} Levels</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

// Initialize application on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.simApp = new SimulationApp();
});
