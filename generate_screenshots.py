"""
generate_screenshots.py
Renders each scene and saves high-resolution PNG screenshots
into a 'screenshots/' directory for inspection and report inclusion.
"""

import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
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

def capture_scenes():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    
    screen = pygame.display.set_mode((1280, 720))
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flood_areas.csv")
    sim = SimulationState(csv_path)

    top_bar = TopBar(pygame.Rect(0, 0, 1280, 54))
    bottom_bar = BottomBar(pygame.Rect(0, 720 - 62, 1280, 62), sim)
    right_panel = RightPanel(pygame.Rect(936, 60, 332, 592))
    scene_renderer = SceneRenderer(pygame.Rect(12, 60, 916, 592), sim)

    # Specific scenes and custom state setups for showcase
    scenarios = [
        (SceneId.INTRO, 0, "01_intro.png"),
        (SceneId.FLOOD_MAP, 0, "02_flood_map.png"),
        (SceneId.SCAN_DETECT, 7, "03_scan_hadapsar.png"),
        (SceneId.INPUT_DATA, 0, "04_input_data.png"),
        (SceneId.DIVIDE_TREE, 1, "05_divide_tree.png"),
        (SceneId.COMPARE_MERGE, 42, "06_compare_merge.png"),
        (SceneId.SORTED_RESULT, 0, "07_sorted_result.png"),
        (SceneId.EVACUATION, 2, "08_evacuation_dispatch.png"),
        (SceneId.ANALYSIS, 0, "09_algorithm_analysis.png"),
    ]

    for scene_id, step_idx, fname in scenarios:
        sim.current_scene = scene_id
        if scene_id == SceneId.SCAN_DETECT:
            sim.scan_index = step_idx
        elif scene_id == SceneId.DIVIDE_TREE:
            sim.divide_step = step_idx
        elif scene_id == SceneId.COMPARE_MERGE:
            sim.timeline_index = min(step_idx, len(sim.tracer.timeline) - 1)
        elif scene_id == SceneId.EVACUATION:
            sim.evac_index = step_idx
            sim.evac_progress = 0.55
            sim.evac_completed = [0, 1]

        screen.fill(COLOR_BG)
        scene_renderer.render(screen)
        
        curr_state = sim.get_current_timeline_state()
        right_panel.draw(
            surface=screen,
            scene_id=sim.current_scene,
            state=curr_state,
            total_comps=sim.tracer.comparisons_count,
            total_merges=sim.tracer.merges_count,
            areas_count=len(sim.areas),
        )
        
        pct = 10 + scene_id * 10
        top_bar.draw(
            surface=screen,
            scene_id=sim.current_scene,
            scene_names=SceneId.NAMES,
            is_playing=sim.is_playing,
            is_demo_mode=sim.is_demo_mode,
            progress_pct=pct,
        )
        bottom_bar.draw(screen)

        save_path = os.path.join(out_dir, fname)
        pygame.image.save(screen, save_path)
        print(f"Saved screenshot: {save_path}")

if __name__ == "__main__":
    capture_scenes()
