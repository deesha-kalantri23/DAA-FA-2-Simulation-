"""
simulation_state.py
Global state manager and controller for the Flood Evacuation Priority System simulation.
Coordinates scenes, playback controls, stepping, and synchronization with MergeSortTracer.
"""

import csv
import os
from typing import List, Optional
from merge_sort import AreaRecord, MergeSortTracer, AlgorithmState


class SceneId:
    INTRO = 0
    FLOOD_MAP = 1
    SCAN_DETECT = 2
    INPUT_DATA = 3
    DIVIDE_TREE = 4
    COMPARE_MERGE = 5
    SORTED_RESULT = 6
    EVACUATION = 7
    ANALYSIS = 8

    NAMES = [
        "INTRO",
        "FLOOD DATA",
        "DETECTION SCAN",
        "INPUT ARRAY",
        "DIVIDE & CONQUER",
        "COMPARE & MERGE",
        "FINAL RANKING",
        "EVACUATION",
        "ANALYSIS",
    ]


class PlaybackSpeed:
    SLOW = "SLOW"
    MEDIUM = "MEDIUM"
    FAST = "FAST"

    DURATIONS = {
        "SLOW": 1.2,      # seconds per algorithmic action
        "MEDIUM": 0.55,
        "FAST": 0.15,
    }


class SimulationState:
    """Central state container for the Pygame application."""
    def __init__(self, csv_filepath: str):
        self.csv_filepath = csv_filepath
        self.areas: List[AreaRecord] = []
        self.load_dataset()

        # Initialize manual Merge Sort tracer
        self.tracer = MergeSortTracer(self.areas)
        self.sorted_areas = self.tracer.get_final_sorted()

        # Scene management
        self.current_scene: int = SceneId.INTRO
        self.scene_timer: float = 0.0

        # Playback configuration
        self.is_playing: bool = True
        self.speed: str = PlaybackSpeed.MEDIUM
        self.is_demo_mode: bool = False  # If True, pauses on key events for manual presentation

        # Scene 2 (Scan detection) state
        self.scan_index: int = 0
        self.scan_timer: float = 0.0

        # Scene 4 (Divide Phase) state
        self.divide_step: int = 0
        self.max_divide_steps: int = 4
        self.divide_timer: float = 0.0

        # Scene 5 (Merge Sort timeline) state
        self.timeline_index: int = 0
        self.step_timer: float = 0.0

        # Scene 7 (Evacuation) state
        self.evac_index: int = 0
        self.evac_progress: float = 0.0
        self.evac_completed: List[int] = []

    def load_dataset(self):
        """Reads the exact 20 rows from flood_areas.csv."""
        self.areas.clear()
        if not os.path.exists(self.csv_filepath):
            raise FileNotFoundError(f"Missing CSV file at {self.csv_filepath}")

        with open(self.csv_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.areas.append(
                    AreaRecord(
                        area_id=row["Area_ID"].strip(),
                        name=row["Area_Name"].strip(),
                        water_level=float(row["Water_Level_m"]),
                        population=int(row["Population_Affected"]),
                    )
                )

    def reset_all(self):
        """Resets the simulation to the initial intro state."""
        self.current_scene = SceneId.INTRO
        self.scene_timer = 0.0
        self.is_playing = True
        self.scan_index = 0
        self.scan_timer = 0.0
        self.divide_step = 0
        self.divide_timer = 0.0
        self.timeline_index = 0
        self.step_timer = 0.0
        self.evac_index = 0
        self.evac_progress = 0.0
        self.evac_completed.clear()

    def get_current_timeline_state(self) -> Optional[AlgorithmState]:
        if 0 <= self.timeline_index < len(self.tracer.timeline):
            return self.tracer.timeline[self.timeline_index]
        return self.tracer.timeline[-1] if self.tracer.timeline else None

    def toggle_play(self):
        self.is_playing = not self.is_playing

    def toggle_demo_mode(self):
        self.is_demo_mode = not self.is_demo_mode
        if self.is_demo_mode:
            self.is_playing = False  # Step by step requires manual control

    def set_speed(self, speed_name: str):
        if speed_name in PlaybackSpeed.DURATIONS:
            self.speed = speed_name

    def next_scene(self):
        if self.current_scene < SceneId.ANALYSIS:
            self.current_scene += 1
            self.scene_timer = 0.0
            self.step_timer = 0.0
            self.divide_timer = 0.0

    def prev_scene(self):
        if self.current_scene > SceneId.INTRO:
            self.current_scene -= 1
            self.scene_timer = 0.0
            self.step_timer = 0.0
            self.divide_timer = 0.0

    def next_step(self):
        """Advances one discrete unit depending on current scene."""
        if self.current_scene == SceneId.INTRO:
            self.next_scene()

        elif self.current_scene == SceneId.FLOOD_MAP:
            self.next_scene()

        elif self.current_scene == SceneId.SCAN_DETECT:
            if self.scan_index < len(self.areas) - 1:
                self.scan_index += 1
            else:
                self.next_scene()

        elif self.current_scene == SceneId.INPUT_DATA:
            self.next_scene()

        elif self.current_scene == SceneId.DIVIDE_TREE:
            if self.divide_step < self.max_divide_steps - 1:
                self.divide_step += 1
            else:
                self.next_scene()

        elif self.current_scene == SceneId.COMPARE_MERGE:
            if self.timeline_index < len(self.tracer.timeline) - 1:
                self.timeline_index += 1
            else:
                self.next_scene()

        elif self.current_scene == SceneId.SORTED_RESULT:
            self.next_scene()

        elif self.current_scene == SceneId.EVACUATION:
            if self.evac_index < 5:
                self.evac_completed.append(self.evac_index)
                self.evac_index += 1
                self.evac_progress = 0.0
            else:
                self.next_scene()

        elif self.current_scene == SceneId.ANALYSIS:
            pass

    def prev_step(self):
        """Reverses one discrete unit or returns to previous scene safely."""
        if self.current_scene == SceneId.SCAN_DETECT:
            if self.scan_index > 0:
                self.scan_index -= 1
            else:
                self.prev_scene()

        elif self.current_scene == SceneId.DIVIDE_TREE:
            if self.divide_step > 0:
                self.divide_step -= 1
            else:
                self.prev_scene()

        elif self.current_scene == SceneId.COMPARE_MERGE:
            if self.timeline_index > 0:
                self.timeline_index -= 1
            else:
                self.prev_scene()

        elif self.current_scene == SceneId.EVACUATION:
            if self.evac_index > 0:
                self.evac_index -= 1
                if self.evac_completed:
                    self.evac_completed.pop()
                self.evac_progress = 0.0
            else:
                self.prev_scene()

        else:
            self.prev_scene()

    def update(self, dt: float):
        """Advances continuous auto-play animations if playing."""
        if not self.is_playing:
            return

        step_duration = PlaybackSpeed.DURATIONS.get(self.speed, 0.55)

        if self.current_scene == SceneId.SCAN_DETECT:
            self.scan_timer += dt
            if self.scan_timer >= (step_duration * 0.7):
                self.scan_timer = 0.0
                if self.scan_index < len(self.areas) - 1:
                    self.scan_index += 1
                else:
                    self.scene_timer += dt
                    if self.scene_timer > 1.2:
                        self.next_scene()

        elif self.current_scene == SceneId.DIVIDE_TREE:
            self.divide_timer += dt
            if self.divide_timer >= step_duration * 1.8:
                self.divide_timer = 0.0
                if self.divide_step < self.max_divide_steps - 1:
                    self.divide_step += 1
                else:
                    self.scene_timer += dt
                    if self.scene_timer > 1.5:
                        self.next_scene()

        elif self.current_scene == SceneId.COMPARE_MERGE:
            self.step_timer += dt
            if self.step_timer >= step_duration:
                self.step_timer = 0.0
                if self.timeline_index < len(self.tracer.timeline) - 1:
                    self.timeline_index += 1
                    # In Demo Mode, pause on comparison and selection
                    if self.is_demo_mode:
                        curr = self.get_current_timeline_state()
                        if curr and curr.op_type in ("COMPARE", "SELECT", "MERGE_DONE"):
                            self.is_playing = False
                else:
                    self.scene_timer += dt
                    if self.scene_timer > 1.5:
                        self.next_scene()

        elif self.current_scene == SceneId.EVACUATION:
            self.evac_progress += dt * (1.2 / step_duration)
            if self.evac_progress >= 1.0:
                self.evac_progress = 0.0
                if self.evac_index < 5:
                    self.evac_completed.append(self.evac_index)
                    self.evac_index += 1
                else:
                    self.scene_timer += dt
                    if self.scene_timer > 2.0:
                        self.next_scene()
