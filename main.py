"""
main.py
Main entry point for the Flood Evacuation Priority System Pygame desktop simulation.
College DAA FA-2 Activity: Educational Merge Sort & Divide and Conquer Visualization.
"""

import sys
import os
import pygame

from simulation_state import SimulationState, SceneId
from ui_components import (
    COLOR_BG,
    TopBar,
    BottomBar,
    RightPanel,
)
from scenes import SceneRenderer


def main():
    # Set window title and center position
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    pygame.font.init()

    WIDTH = 1280
    HEIGHT = 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("FLOOD EVACUATION PRIORITY SYSTEM — DAA MERGE SORT SIMULATION")

    # Optional: set clean window icon
    icon_surf = pygame.Surface((32, 32))
    icon_surf.fill((14, 165, 233))
    pygame.draw.rect(icon_surf, (239, 68, 68), pygame.Rect(4, 4, 24, 24), border_radius=4)
    pygame.display.set_icon(icon_surf)

    clock = pygame.time.Clock()

    # Load dataset & simulation controller
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flood_areas.csv")
    sim = SimulationState(csv_path)

    # Layout dimensions
    top_bar_rect = pygame.Rect(0, 0, WIDTH, 54)
    bottom_bar_rect = pygame.Rect(0, HEIGHT - 62, WIDTH, 62)
    main_viewport_rect = pygame.Rect(12, 60, 916, HEIGHT - 54 - 62 - 12)
    right_panel_rect = pygame.Rect(936, 60, 332, HEIGHT - 54 - 62 - 12)

    # Instantiate UI sections
    top_bar = TopBar(top_bar_rect)
    bottom_bar = BottomBar(bottom_bar_rect, sim)
    right_panel = RightPanel(right_panel_rect)
    scene_renderer = SceneRenderer(main_viewport_rect, sim)

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds (60 FPS cap)

        # 1. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_SPACE:
                    sim.toggle_play()
                elif event.key == pygame.K_RIGHT:
                    sim.next_step()
                elif event.key == pygame.K_LEFT:
                    sim.prev_step()
                elif event.key == pygame.K_r:
                    sim.reset_all()
                elif event.key == pygame.K_d:
                    sim.toggle_demo_mode()
                elif event.key == pygame.K_1:
                    sim.set_speed("SLOW")
                elif event.key == pygame.K_2:
                    sim.set_speed("MEDIUM")
                elif event.key == pygame.K_3:
                    sim.set_speed("FAST")

            # Dispatch events to UI components
            bottom_bar.handle_event(event)
            scene_renderer.handle_event(event)

        # 2. STATE UPDATE
        sim.update(dt)

        # Calculate progress percentage for top bar
        progress_pct = 0
        if sim.current_scene == SceneId.INTRO:
            progress_pct = 5
        elif sim.current_scene == SceneId.FLOOD_MAP:
            progress_pct = 15
        elif sim.current_scene == SceneId.SCAN_DETECT:
            progress_pct = 15 + int((sim.scan_index / max(1, len(sim.areas))) * 15)
        elif sim.current_scene == SceneId.INPUT_DATA:
            progress_pct = 35
        elif sim.current_scene == SceneId.DIVIDE_TREE:
            progress_pct = 48
        elif sim.current_scene == SceneId.COMPARE_MERGE:
            timeline_len = max(1, len(sim.tracer.timeline))
            progress_pct = 50 + int((sim.timeline_index / timeline_len) * 30)
        elif sim.current_scene == SceneId.SORTED_RESULT:
            progress_pct = 85
        elif sim.current_scene == SceneId.EVACUATION:
            progress_pct = 88 + int((sim.evac_index / 5) * 8)
        elif sim.current_scene == SceneId.ANALYSIS:
            progress_pct = 100

        # 3. RENDERING
        screen.fill(COLOR_BG)

        # Render active scene in main viewport
        scene_renderer.render(screen)

        # Render right-hand educational HUD
        curr_state = sim.get_current_timeline_state()
        right_panel.draw(
            surface=screen,
            scene_id=sim.current_scene,
            state=curr_state,
            total_comps=sim.tracer.comparisons_count,
            total_merges=sim.tracer.merges_count,
            areas_count=len(sim.areas),
        )

        # Render top bar
        top_bar.draw(
            surface=screen,
            scene_id=sim.current_scene,
            scene_names=SceneId.NAMES,
            is_playing=sim.is_playing,
            is_demo_mode=sim.is_demo_mode,
            progress_pct=progress_pct,
        )

        # Render bottom control bar
        bottom_bar.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
