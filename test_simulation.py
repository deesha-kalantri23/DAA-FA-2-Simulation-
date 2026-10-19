"""
test_simulation.py
Automated headless validation script to test all simulation states,
scene transitions, timeline stepping, and UI rendering without crashing.
"""

import os
import sys

# Configure Pygame for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

pygame.init()
pygame.font.init()

from simulation_state import SimulationState, SceneId
from ui_components import (
    COLOR_BG,
    TopBar,
    BottomBar,
    RightPanel,
)
from scenes import SceneRenderer

def run_tests():
    print(">>> 1. Initializing Pygame dummy surface (1280x720)...")
    surface = pygame.display.set_mode((1280, 720))
    
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flood_areas.csv")
    print(f">>> 2. Loading dataset from {csv_path}...")
    sim = SimulationState(csv_path)
    assert len(sim.areas) == 20, f"Expected 20 areas, got {len(sim.areas)}"
    print(f"    Loaded {len(sim.areas)} areas successfully.")
    
    print(">>> 3. Testing MergeSortTracer results...")
    sorted_areas = sim.sorted_areas
    assert len(sorted_areas) == 20
    assert sorted_areas[0].area_id == "A08" and sorted_areas[0].name == "Hadapsar"
    assert sorted_areas[0].water_level == 8.2
    assert sorted_areas[1].area_id == "A17" and sorted_areas[1].name == "Yerawada"
    assert sorted_areas[1].water_level == 7.9
    assert sorted_areas[2].area_id == "A12" and sorted_areas[2].name == "Bhosari"
    assert sorted_areas[2].water_level == 7.6
    print("    First 3 sorted areas match expected priority ranking.")
    
    print(">>> 4. Testing UI component instantiations...")
    top_bar = TopBar(pygame.Rect(0, 0, 1280, 54))
    bottom_bar = BottomBar(pygame.Rect(0, 720 - 62, 1280, 62), sim)
    right_panel = RightPanel(pygame.Rect(936, 60, 332, 592))
    scene_renderer = SceneRenderer(pygame.Rect(12, 60, 916, 592), sim)
    
    print(">>> 5. Testing rendering of every single scene...")
    for scene_id in range(len(SceneId.NAMES)):
        sim.current_scene = scene_id
        surface.fill(COLOR_BG)
        scene_renderer.render(surface)
        
        curr_state = sim.get_current_timeline_state()
        right_panel.draw(
            surface=surface,
            scene_id=sim.current_scene,
            state=curr_state,
            total_comps=sim.tracer.comparisons_count,
            total_merges=sim.tracer.merges_count,
            areas_count=len(sim.areas),
        )
        
        top_bar.draw(
            surface=surface,
            scene_id=sim.current_scene,
            scene_names=SceneId.NAMES,
            is_playing=sim.is_playing,
            is_demo_mode=sim.is_demo_mode,
            progress_pct=50,
        )
        bottom_bar.draw(surface)
        print(f"    Scene {scene_id} ({SceneId.NAMES[scene_id]}): Rendered successfully.")
        
    print(">>> 6. Testing timeline stepping forward and backward...")
    sim.current_scene = SceneId.COMPARE_MERGE
    for i in range(25):
        sim.next_step()
    assert sim.timeline_index > 0
    print(f"    Stepped forward to index {sim.timeline_index}.")
    
    for i in range(10):
        sim.prev_step()
    print(f"    Stepped backward to index {sim.timeline_index}.")
    
    print(">>> 7. Testing playback controls...")
    sim.toggle_play()
    sim.toggle_demo_mode()
    sim.set_speed("SLOW")
    sim.set_speed("FAST")
    sim.reset_all()
    assert sim.current_scene == SceneId.INTRO
    assert sim.timeline_index == 0
    print("    Reset verified.")
    
    print("\n==============================================")
    print("ALL TESTS PASSED WITH ZERO ERRORS!")
    print("==============================================")

if __name__ == "__main__":
    run_tests()
