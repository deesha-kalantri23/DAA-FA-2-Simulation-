"""
scenes.py
Rendering and animation logic for all 9 simulation stages in the
Flood Evacuation Priority System Pygame desktop simulation.
Designed with a clean, modern, professional LIGHT THEME.
"""

import pygame
import math
from typing import List, Optional, Tuple
from merge_sort import AreaRecord, AlgorithmState
from simulation_state import SimulationState, SceneId
from ui_components import (
    COLOR_BG,
    COLOR_PANEL,
    COLOR_PANEL_ALT,
    COLOR_PANEL_SUBTLE,
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_ACCENT_LIGHT,
    COLOR_CRITICAL,
    COLOR_CRITICAL_BG,
    COLOR_HIGH,
    COLOR_HIGH_BG,
    COLOR_MEDIUM,
    COLOR_MEDIUM_BG,
    COLOR_LOW,
    COLOR_LOW_BG,
    COLOR_COMPARE,
    COLOR_COMPARE_BG,
    COLOR_COMPARE_BORDER,
    COLOR_SELECTED,
    COLOR_SELECTED_BG,
    COLOR_SELECTED_BORDER,
    COLOR_DIMMED,
    COLOR_DIMMED_BG,
    FontManager,
    draw_rounded_panel,
    draw_badge,
    draw_arrow,
    draw_house_icon,
    draw_shelter_icon,
    draw_rescue_boat,
    draw_water_gauge,
    get_priority_color,
    get_priority_bg_color,
    get_water_level_color,
    Button,
)


class SceneRenderer:
    """Renders the active simulation scene inside the main viewport (916 x 592)."""
    def __init__(self, viewport_rect: pygame.Rect, sim_state: SimulationState):
        self.rect = viewport_rect
        self.sim = sim_state

        # Interactive Start Button for Intro Scene
        self.btn_start = Button(
            pygame.Rect(self.rect.centerx - 110, self.rect.bottom - 80, 220, 46),
            text="START SIMULATION",
            icon_type="play",
            font_size=13,
            bg_color=COLOR_ACCENT,
            hover_color=(29, 78, 216),
            active_color=COLOR_ACCENT,
            text_color=(255, 255, 255),
            callback=self.sim.next_scene,
        )

    def handle_event(self, event: pygame.event.Event):
        if self.sim.current_scene == SceneId.INTRO:
            self.btn_start.handle_event(event)

    def render(self, surface: pygame.Surface):
        scene_id = self.sim.current_scene

        if scene_id == SceneId.INTRO:
            self._render_scene_intro(surface)
        elif scene_id == SceneId.FLOOD_MAP:
            self._render_scene_flood_map(surface)
        elif scene_id == SceneId.SCAN_DETECT:
            self._render_scene_scan(surface)
        elif scene_id == SceneId.INPUT_DATA:
            self._render_scene_input_data(surface)
        elif scene_id == SceneId.DIVIDE_TREE:
            self._render_scene_divide_tree(surface)
        elif scene_id == SceneId.COMPARE_MERGE:
            self._render_scene_compare_merge(surface)
        elif scene_id == SceneId.SORTED_RESULT:
            self._render_scene_sorted_result(surface)
        elif scene_id == SceneId.EVACUATION:
            self._render_scene_evacuation(surface)
        elif scene_id == SceneId.ANALYSIS:
            self._render_scene_analysis(surface)

    # ------------------------------------------------------------------
    # SCENE 1: PROFESSIONAL INTRO SCREEN (Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_intro(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Title block
        f_hero = FontManager.get(24, bold=True)
        f_sub = FontManager.get(14, bold=True)
        f_desc = FontManager.get(12)

        title_surf = f_hero.render("FLOOD EVACUATION PRIORITY SYSTEM", True, COLOR_TEXT_PRIMARY)
        sub_surf = f_sub.render("Using Merge Sort • Divide and Conquer Paradigm", True, COLOR_ACCENT)

        surface.blit(title_surf, (self.rect.left + 36, self.rect.top + 32))
        surface.blit(sub_surf, (self.rect.left + 36, self.rect.top + 68))

        # Problem statement card
        card_rect = pygame.Rect(self.rect.left + 36, self.rect.top + 104, self.rect.width - 72, 126)
        draw_rounded_panel(surface, card_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        lbl = FontManager.get(11, bold=True).render("REAL-WORLD PROBLEM CONTEXT", True, COLOR_ACCENT)
        surface.blit(lbl, (card_rect.left + 16, card_rect.top + 14))

        desc_text = (
            "During severe monsoon flooding in urban Pune, emergency response teams face resource scarcity. "
            "Authorities must rapidly triage flood-affected zones to evacuate high-risk citizens first.\n\n"
            "This software demonstrates how Merge Sort systematically organizes affected regions in descending "
            "order of water levels with a guaranteed O(n log n) efficiency, establishing instant evacuation priority."
        )
        self._render_multiline_text(surface, desc_text, card_rect.left + 16, card_rect.top + 38, card_rect.width - 32, f_desc, COLOR_TEXT_PRIMARY)

        # Three key pillars cards
        pillars = [
            ("ALGORITHM", "Merge Sort", "Guaranteed O(n log n)\nRecursive Divide & Conquer\nStable sorting behaviour"),
            ("INPUT DATA", "20 Flood Zones", "Pune Municipal Dataset\nWater level metric (m)\nPopulation at risk"),
            ("OUTPUT GOAL", "Priority Evacuation", "Descending Water Level\nCritical to Low Triage\nDirect Rescue Dispatch"),
        ]

        card_w = (self.rect.width - 72 - 32) // 3
        card_h = 145
        top_y = card_rect.bottom + 20

        for idx, (head, sub, desc) in enumerate(pillars):
            p_rect = pygame.Rect(self.rect.left + 36 + idx * (card_w + 16), top_y, card_w, card_h)
            draw_rounded_panel(surface, p_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

            h_s = FontManager.get(10, bold=True).render(head, True, COLOR_TEXT_MUTED)
            s_s = FontManager.get(14, bold=True).render(sub, True, COLOR_ACCENT)

            surface.blit(h_s, (p_rect.left + 14, p_rect.top + 14))
            surface.blit(s_s, (p_rect.left + 14, p_rect.top + 32))

            self._render_multiline_text(surface, desc, p_rect.left + 14, p_rect.top + 62, p_rect.width - 28, FontManager.get(11), COLOR_TEXT_SECONDARY)

        # Start simulation button
        self.btn_start.draw(surface)

    # ------------------------------------------------------------------
    # SCENE 2: FLOOD AREA VISUALIZATION (Clean Map Grid Layout)
    # ------------------------------------------------------------------
    def _render_scene_flood_map(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("PUNE METROPOLITAN FLOOD MAP — 20 MONITORED ZONES", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))
        surface.blit(f_sub.render("Real-time telemetry showing water depth gauges and population density across monitored sectors.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        # 5 columns x 4 rows grid
        cols = 5
        rows = 4
        margin_x = 24
        margin_y = 62
        spacing_x = 10
        spacing_y = 10

        grid_w = self.rect.width - margin_x * 2
        grid_h = self.rect.height - margin_y - 20
        cell_w = (grid_w - (cols - 1) * spacing_x) // cols
        cell_h = (grid_h - (rows - 1) * spacing_y) // rows

        f_id = FontManager.get(11, bold=True)
        f_name = FontManager.get(10, bold=True)
        f_num = FontManager.get(10)

        for i, area in enumerate(self.sim.areas):
            c = i % cols
            r = i // cols
            cx = self.rect.left + margin_x + c * (cell_w + spacing_x)
            cy = self.rect.top + margin_y + r * (cell_h + spacing_y)

            card_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            draw_rounded_panel(surface, card_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

            # Water level tint background at bottom
            water_ratio = min(1.0, area.water_level / 10.0)
            water_h = int(cell_h * 0.40 * water_ratio)
            if water_h > 0:
                water_rect = pygame.Rect(cx + 1, cy + cell_h - water_h - 1, cell_w - 2, water_h)
                pygame.draw.rect(surface, (219, 234, 254), water_rect, border_bottom_left_radius=5, border_bottom_right_radius=5)

            # Area ID badge & house icon
            draw_badge(surface, area.area_id, cx + 8, cy + 8, COLOR_ACCENT, COLOR_ACCENT_LIGHT, size=9)
            draw_house_icon(surface, cx + cell_w - 26, cy + 8, width=18, height=16)

            # Area Name
            surface.blit(f_name.render(area.name[:14], True, COLOR_TEXT_PRIMARY), (cx + 8, cy + 30))

            # Water Level Gauge Bar
            gauge_rect = pygame.Rect(cx + 8, cy + 54, cell_w - 48, 8)
            draw_water_gauge(surface, gauge_rect, area.water_level, max_level=10.0, show_text=True)

            # Population indicator
            pop_txt = f"Pop: {area.population:,}"
            surface.blit(f_num.render(pop_txt, True, COLOR_TEXT_MUTED), (cx + 8, cy + cell_h - 18))

            # Priority dot
            p_col = get_priority_color(area.get_priority())
            pygame.draw.circle(surface, p_col, (cx + cell_w - 12, cy + cell_h - 12), 4)

    # ------------------------------------------------------------------
    # SCENE 3: WATER LEVEL DETECTION (Animated Scan - Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_scan(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        surface.blit(f_head.render("ANALYZING FLOOD AREAS — TELEMETRY SCANNING", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))

        curr_idx = self.sim.scan_index
        active_area = self.sim.areas[curr_idx]

        # 5x4 mini grid on left side
        cols = 5
        rows = 4
        margin_x = 24
        margin_y = 54
        spacing_x = 8
        spacing_y = 8
        grid_w = 520
        grid_h = 510
        cell_w = (grid_w - (cols - 1) * spacing_x) // cols
        cell_h = (grid_h - (rows - 1) * spacing_y) // rows

        f_sm = FontManager.get(9, bold=True)
        f_val = FontManager.get(9)

        for i, area in enumerate(self.sim.areas):
            c = i % cols
            r = i // cols
            cx = self.rect.left + margin_x + c * (cell_w + spacing_x)
            cy = self.rect.top + margin_y + r * (cell_h + spacing_y)

            card_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            is_active = (i == curr_idx)
            is_scanned = (i < curr_idx)

            if is_active:
                bg_col = COLOR_ACCENT_LIGHT
                border_col = COLOR_ACCENT
                border_w = 2
            elif is_scanned:
                bg_col = COLOR_PANEL_ALT
                border_col = COLOR_LOW
                border_w = 1
            else:
                bg_col = (255, 255, 255)
                border_col = COLOR_BORDER_LIGHT
                border_w = 1

            draw_rounded_panel(surface, card_rect, bg_color=bg_col, border_color=border_col, border_width=border_w, radius=4)

            # Details inside card
            id_col = COLOR_ACCENT if is_active else (COLOR_TEXT_PRIMARY if is_scanned else COLOR_TEXT_MUTED)
            surface.blit(f_sm.render(area.area_id, True, id_col), (cx + 6, cy + 6))
            surface.blit(f_sm.render(area.name[:9], True, COLOR_TEXT_PRIMARY), (cx + 6, cy + 22))

            # Water level bar
            g_rect = pygame.Rect(cx + 6, cy + 40, cell_w - 12, 6)
            draw_water_gauge(surface, g_rect, area.water_level, max_level=10.0, show_text=False)

            lvl_str = f"{area.water_level:.1f}m"
            surface.blit(f_val.render(lvl_str, True, get_water_level_color(area.water_level)), (cx + 6, cy + 52))

        # Spotlight HUD on right side of viewport
        hud_rect = pygame.Rect(self.rect.left + 565, margin_y, 330, grid_h)
        draw_rounded_panel(surface, hud_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_ACCENT, border_width=2, radius=8)

        f_hud_title = FontManager.get(14, bold=True)
        f_hud_lbl = FontManager.get(11, bold=True)

        surface.blit(f_hud_title.render("TELEMETRY SENSOR FEED", True, COLOR_ACCENT), (hud_rect.left + 20, hud_rect.top + 20))
        draw_badge(surface, f"SCANNING {curr_idx + 1} OF 20", hud_rect.left + 20, hud_rect.top + 50, COLOR_ACCENT, COLOR_ACCENT_LIGHT, size=11)

        # Target Area Spotlight
        box_y = hud_rect.top + 90
        spot_rect = pygame.Rect(hud_rect.left + 20, box_y, hud_rect.width - 40, 240)
        draw_rounded_panel(surface, spot_rect, bg_color=(255, 255, 255), border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(f_hud_lbl.render("CURRENTLY CHECKING", True, COLOR_TEXT_SECONDARY), (spot_rect.left + 16, spot_rect.top + 16))
        surface.blit(FontManager.get(19, bold=True).render(f"{active_area.area_id} — {active_area.name.upper()}", True, COLOR_TEXT_PRIMARY), (spot_rect.left + 16, spot_rect.top + 38))

        # Water level readout
        surface.blit(f_hud_lbl.render("MEASURED WATER LEVEL:", True, COLOR_TEXT_SECONDARY), (spot_rect.left + 16, spot_rect.top + 80))
        lvl_col = get_water_level_color(active_area.water_level)
        surface.blit(FontManager.get(26, bold=True).render(f"{active_area.water_level:.1f} METERS", True, lvl_col), (spot_rect.left + 16, spot_rect.top + 100))

        # Priority tag
        draw_badge(surface, f"PRIORITY: {active_area.get_priority()}", spot_rect.left + 16, spot_rect.top + 144, get_priority_color(active_area.get_priority()), get_priority_bg_color(active_area.get_priority()), size=11)

        # Population
        surface.blit(f_hud_lbl.render("AFFECTED POPULATION:", True, COLOR_TEXT_SECONDARY), (spot_rect.left + 16, spot_rect.top + 180))
        surface.blit(FontManager.get(15, bold=True).render(f"{active_area.population:,} RESIDENTS", True, COLOR_TEXT_PRIMARY), (spot_rect.left + 16, spot_rect.top + 200))

        # Bottom transition note
        note_y = spot_rect.bottom + 20
        if curr_idx >= len(self.sim.areas) - 1:
            draw_badge(surface, "ALL 20 FLOOD ZONES DETECTED", hud_rect.left + 20, note_y, COLOR_LOW, COLOR_LOW_BG, size=12)
            surface.blit(FontManager.get(11).render("Preparing dataset for Merge Sort algorithm...", True, COLOR_ACCENT), (hud_rect.left + 20, note_y + 36))
        else:
            pct = int(((curr_idx + 1) / 20) * 100)
            p_bar = pygame.Rect(hud_rect.left + 20, note_y, hud_rect.width - 40, 10)
            pygame.draw.rect(surface, (226, 232, 240), p_bar, border_radius=5)
            fill_w = int((hud_rect.width - 40) * (pct / 100.0))
            pygame.draw.rect(surface, COLOR_ACCENT, pygame.Rect(p_bar.left, p_bar.top, fill_w, p_bar.height), border_radius=5)
            surface.blit(FontManager.get(11).render(f"Scan progress: {pct}% complete", True, COLOR_TEXT_SECONDARY), (hud_rect.left + 20, note_y + 18))

    # ------------------------------------------------------------------
    # SCENE 4: INPUT DATA ARRAY (5x4 Unsorted Grid - Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_input_data(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("INPUT DATA ARRAY — ORIGINAL UNSORTED ORDER", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))
        surface.blit(f_sub.render("Initial array arrangement as read from flood_areas.csv before Divide and Conquer sorting.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        # 5 columns x 4 rows
        cols = 5
        rows = 4
        margin_x = 24
        margin_y = 66
        spacing_x = 12
        spacing_y = 12

        grid_w = self.rect.width - margin_x * 2
        grid_h = self.rect.height - margin_y - 20
        cell_w = (grid_w - (cols - 1) * spacing_x) // cols
        cell_h = (grid_h - (rows - 1) * spacing_y) // rows

        f_idx = FontManager.get(10, bold=True)
        f_id = FontManager.get(12, bold=True)
        f_name = FontManager.get(11, bold=True)
        f_val = FontManager.get(13, bold=True)

        for i, area in enumerate(self.sim.areas):
            c = i % cols
            r = i // cols
            cx = self.rect.left + margin_x + c * (cell_w + spacing_x)
            cy = self.rect.top + margin_y + r * (cell_h + spacing_y)

            card_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            draw_rounded_panel(surface, card_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

            # Index badge in top left (e.g. [0], [1]...)
            surface.blit(f_idx.render(f"[{i}]", True, COLOR_TEXT_MUTED), (cx + 8, cy + 6))

            # Area ID
            draw_badge(surface, area.area_id, cx + cell_w - 38, cy + 6, COLOR_ACCENT, COLOR_ACCENT_LIGHT, size=9)

            # Area Name
            surface.blit(f_name.render(area.name, True, COLOR_TEXT_PRIMARY), (cx + 8, cy + 28))

            # Water level highlight box
            w_box = pygame.Rect(cx + 8, cy + 50, cell_w - 16, 26)
            pygame.draw.rect(surface, (255, 255, 255), w_box, border_radius=4)
            pygame.draw.rect(surface, COLOR_BORDER_LIGHT, w_box, width=1, border_radius=4)
            surface.blit(FontManager.get(10).render("Water Level:", True, COLOR_TEXT_SECONDARY), (w_box.left + 6, w_box.top + 6))

            lvl_col = get_water_level_color(area.water_level)
            surface.blit(f_val.render(f"{area.water_level:.1f} m", True, lvl_col), (w_box.right - 50, w_box.top + 4))

            # Water gauge line
            g_rect = pygame.Rect(cx + 8, cy + cell_h - 14, cell_w - 16, 6)
            draw_water_gauge(surface, g_rect, area.water_level, max_level=10.0, show_text=False)

    # ------------------------------------------------------------------
    # SCENE 5: DIVIDE & CONQUER (Step-by-Step Divide & Tree Visualization)
    # ------------------------------------------------------------------
    def _render_scene_divide_tree(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("MERGE SORT — DIVIDE AND CONQUER PHASE", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))

        curr_divide_step = self.sim.divide_step  # 0 to 3
        step_descriptions = [
            ("STEP 1 / 4: ORIGINAL ARRAY (20 ELEMENTS)", "Initial 20-sector flood dataset awaiting recursive division."),
            ("STEP 2 / 4: FIRST DIVISION (TWO 10-ELEMENT HALVES)", "Array split at midpoint mid=9 into Left [A01..A10] and Right [A11..A20]."),
            ("STEP 3 / 4: SECOND DIVISION (FOUR 5-ELEMENT QUARTERS)", "Each half divided recursively into four 5-element subarrays."),
            ("STEP 4 / 4: ATOMIC SUBARRAYS (BASE CASE REACHED)", "Continued recursion down to 2-3 elements and atomic 1-element arrays ready for merging."),
        ]
        step_title, step_desc = step_descriptions[curr_divide_step]
        surface.blit(f_sub.render(step_desc, True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        # Current Divide Operation Badge
        draw_badge(surface, step_title, self.rect.right - 350, self.rect.top + 14, COLOR_ACCENT, COLOR_ACCENT_LIGHT, size=11)

        # Top section: Visual Tree (Height 210px)
        tree_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 60, self.rect.width - 48, 200)
        draw_rounded_panel(surface, tree_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        # Draw visual tree nodes
        tree_levels = [
            [(0, 19, "Root [20]")] ,
            [(0, 9, "Left [10]"), (10, 19, "Right [10]")],
            [(0, 4, "[5]"), (5, 9, "[5]"), (10, 14, "[5]"), (15, 19, "[5]")],
            [(0, 2, "[3]"), (3, 4, "[2]"), (5, 7, "[3]"), (8, 9, "[2]"), (10, 12, "[3]"), (13, 14, "[2]"), (15, 17, "[3]"), (18, 19, "[2]")],
        ]

        y_positions = [tree_rect.top + 14, tree_rect.top + 62, tree_rect.top + 110, tree_rect.top + 158]
        tree_node_centers = []

        f_node = FontManager.get(10, bold=True)
        for lvl_idx, ranges in enumerate(tree_levels):
            y = y_positions[lvl_idx]
            n_count = len(ranges)
            slot_w = (tree_rect.width - 40) / n_count
            lvl_pts = []

            for r_idx, (st, en, lbl) in enumerate(ranges):
                box_w = min(slot_w - 8, 86)
                box_h = 32
                cx = tree_rect.left + 20 + r_idx * slot_w + (slot_w - box_w) / 2
                node_box = pygame.Rect(cx, y, box_w, box_h)
                lvl_pts.append(node_box.center)

                is_active_lvl = (lvl_idx <= curr_divide_step)
                is_curr_lvl = (lvl_idx == curr_divide_step)

                if is_curr_lvl:
                    bg = COLOR_ACCENT_LIGHT
                    border = COLOR_ACCENT
                    bw = 2
                    tc = COLOR_ACCENT
                elif is_active_lvl:
                    bg = (255, 255, 255)
                    border = COLOR_BORDER
                    bw = 1
                    tc = COLOR_TEXT_PRIMARY
                else:
                    bg = COLOR_PANEL_SUBTLE
                    border = COLOR_BORDER_LIGHT
                    bw = 1
                    tc = COLOR_TEXT_MUTED

                draw_rounded_panel(surface, node_box, bg_color=bg, border_color=border, border_width=bw, radius=4)
                surface.blit(f_node.render(lbl, True, tc), (node_box.left + 6, node_box.top + 8))

            tree_node_centers.append(lvl_pts)

        # Connecting branch lines
        for lvl in range(len(tree_node_centers) - 1):
            if lvl < curr_divide_step:
                for p_idx, p_pt in enumerate(tree_node_centers[lvl]):
                    c1_idx = p_idx * 2
                    c2_idx = p_idx * 2 + 1
                    if c1_idx < len(tree_node_centers[lvl + 1]):
                        c1_pt = tree_node_centers[lvl + 1][c1_idx]
                        pygame.draw.line(surface, COLOR_ACCENT, (p_pt[0], p_pt[1] + 16), (c1_pt[0], c1_pt[1] - 16), 1)
                    if c2_idx < len(tree_node_centers[lvl + 1]):
                        c2_pt = tree_node_centers[lvl + 1][c2_idx]
                        pygame.draw.line(surface, COLOR_ACCENT, (p_pt[0], p_pt[1] + 16), (c2_pt[0], c2_pt[1] - 16), 1)

        # Bottom section: DYNAMIC CARD SIZING & PHYSICAL DIVISION DISPLAY (Height 300px)
        display_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 270, self.rect.width - 48, 305)
        draw_rounded_panel(surface, display_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(f_head.render("PHYSICAL SUBARRAY PARTITIONS & CARD SIZING", True, COLOR_TEXT_PRIMARY), (display_rect.left + 16, display_rect.top + 12))

        # Dynamic card scaling and groups based on current_divide_step
        if curr_divide_step == 0:
            # 20 elements -> Compact cards
            surface.blit(FontManager.get(11).render("Complete Unbroken Array [0..19] (20 Sectors):", True, COLOR_TEXT_SECONDARY), (display_rect.left + 16, display_rect.top + 36))
            self._render_divide_group(surface, self.sim.areas, display_rect.left + 16, display_rect.top + 60, display_rect.width - 32, card_size="compact")

        elif curr_divide_step == 1:
            # Two 10-element halves -> Medium cards
            half_w = (display_rect.width - 48) // 2
            surface.blit(FontManager.get(12, bold=True).render("LEFT HALF: Sectors [A01..A10] (10 Areas)", True, COLOR_ACCENT), (display_rect.left + 16, display_rect.top + 36))
            self._render_divide_group(surface, self.sim.areas[0:10], display_rect.left + 16, display_rect.top + 60, half_w, card_size="medium")

            surface.blit(FontManager.get(12, bold=True).render("RIGHT HALF: Sectors [A11..A20] (10 Areas)", True, COLOR_ACCENT), (display_rect.left + 16 + half_w + 16, display_rect.top + 36))
            self._render_divide_group(surface, self.sim.areas[10:20], display_rect.left + 16 + half_w + 16, display_rect.top + 60, half_w, card_size="medium")

        elif curr_divide_step == 2:
            # Four 5-element quarters -> Large cards
            quarter_w = (display_rect.width - 64) // 2
            quarters = [
                ("[A01..A05] (5 Areas)", self.sim.areas[0:5], display_rect.left + 16, display_rect.top + 50),
                ("[A06..A10] (5 Areas)", self.sim.areas[5:10], display_rect.left + 16 + quarter_w + 16, display_rect.top + 50),
                ("[A11..A15] (5 Areas)", self.sim.areas[10:15], display_rect.left + 16, display_rect.top + 175),
                ("[A16..A20] (5 Areas)", self.sim.areas[15:20], display_rect.left + 16 + quarter_w + 16, display_rect.top + 175),
            ]
            for q_title, q_items, qx, qy in quarters:
                surface.blit(FontManager.get(11, bold=True).render(q_title, True, COLOR_ACCENT), (qx, qy - 18))
                self._render_divide_group(surface, q_items, qx, qy, quarter_w, card_size="large")

        elif curr_divide_step >= 3:
            # Base case: 2-3 element subarrays -> Extra Large readable cards
            surface.blit(FontManager.get(12, bold=True).render("RECURSION BASE CASES (Subarrays of 2-3 Elements down to Atomic Arrays)", True, COLOR_ACCENT), (display_rect.left + 16, display_rect.top + 36))
            sub_groups = [
                ("Subarray [A01 A02 A03]", self.sim.areas[0:3]),
                ("Subarray [A04 A05]", self.sim.areas[3:5]),
                ("Subarray [A06 A07 A08]", self.sim.areas[5:8]),
            ]
            grp_w = (display_rect.width - 48) // 3
            for g_idx, (g_title, g_items) in enumerate(sub_groups):
                gx = display_rect.left + 16 + g_idx * (grp_w + 8)
                surface.blit(FontManager.get(11, bold=True).render(g_title, True, COLOR_TEXT_PRIMARY), (gx, display_rect.top + 65))
                self._render_divide_group(surface, g_items, gx, display_rect.top + 88, grp_w, card_size="xlarge")

    def _render_divide_group(self, surface: pygame.Surface, items: List[AreaRecord], x: int, y: int, max_w: int, card_size: str):
        n = len(items)
        if n == 0:
            return

        if card_size == "compact":
            cw = min(38, (max_w - (n - 1) * 4) // n)
            ch = 64
        elif card_size == "medium":
            cw = min(72, (max_w - (n - 1) * 6) // n)
            ch = 82
        elif card_size == "large":
            cw = min(88, (max_w - (n - 1) * 6) // n)
            ch = 86
        else:  # xlarge
            cw = min(105, (max_w - (n - 1) * 8) // n)
            ch = 110

        f_id = FontManager.get(10 if card_size != "compact" else 8, bold=True)
        f_name = FontManager.get(9 if card_size != "compact" else 7)
        f_val = FontManager.get(11 if card_size != "compact" else 9, bold=True)

        for idx, item in enumerate(items):
            cx = x + idx * (cw + 4)
            c_box = pygame.Rect(cx, y, cw, ch)
            draw_rounded_panel(surface, c_box, bg_color=(255, 255, 255), border_color=COLOR_BORDER, radius=4)

            surface.blit(f_id.render(item.area_id, True, COLOR_ACCENT), (cx + 4, y + 4))
            if card_size != "compact":
                surface.blit(f_name.render(item.name[:8], True, COLOR_TEXT_PRIMARY), (cx + 4, y + 18))
                lvl_col = get_water_level_color(item.water_level)
                surface.blit(f_val.render(f"{item.water_level:.1f}m", True, lvl_col), (cx + 4, y + 36))
                # Water gauge
                g_rect = pygame.Rect(cx + 4, y + ch - 12, cw - 8, 5)
                draw_water_gauge(surface, g_rect, item.water_level, max_level=10.0, show_text=False)
            else:
                surface.blit(f_val.render(f"{item.water_level:.1f}", True, get_water_level_color(item.water_level)), (cx + 4, y + 20))

    # ------------------------------------------------------------------
    # SCENE 6 & 7: STEP-BY-STEP MERGE WITH ARROWS & POINTERS (Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_compare_merge(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("MERGE SORT — STEP-BY-STEP MERGING WITH DIRECTIONAL ARROWS", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))

        state = self.sim.get_current_timeline_state()
        if not state:
            return

        left_sub = state.left_sub
        right_sub = state.right_sub
        curr_l = state.curr_left_idx
        curr_r = state.curr_right_idx
        merged = state.merged_buffer

        is_final_merge = (state.active_range == (0, 19))
        if is_final_merge:
            sub_txt = "FINAL MERGE: Combining the two 10-element sorted halves [A01..A10] and [A11..A20] into the final 20-element sorted array!"
            surface.blit(f_sub.render(sub_txt, True, COLOR_CRITICAL), (self.rect.left + 24, self.rect.top + 36))
        else:
            surface.blit(f_sub.render("Comparing head elements of Left and Right sorted subarrays to construct merged descending order.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        half_w = (self.rect.width - 72) // 2

        # 1. LEFT SUBARRAY PANEL (Top-Left)
        left_panel_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 60, half_w, 140)
        draw_rounded_panel(surface, left_panel_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render(f"LEFT SORTED SUBARRAY ({len(left_sub)} Elements)", True, COLOR_ACCENT), (left_panel_rect.left + 14, left_panel_rect.top + 10))

        # Render Left Subarray cards
        left_head_pt = self._render_merge_subarray_row(
            surface=surface,
            items=left_sub,
            start_x=left_panel_rect.left + 14,
            start_y=left_panel_rect.top + 34,
            max_w=left_panel_rect.width - 28,
            active_idx=curr_l,
            is_selected_side=(state.selected_item in left_sub if state.selected_item else False),
            pointer_label="L-PTR",
        )

        # 2. RIGHT SUBARRAY PANEL (Top-Right)
        right_panel_rect = pygame.Rect(self.rect.left + 24 + half_w + 24, self.rect.top + 60, half_w, 140)
        draw_rounded_panel(surface, right_panel_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render(f"RIGHT SORTED SUBARRAY ({len(right_sub)} Elements)", True, COLOR_ACCENT), (right_panel_rect.left + 14, right_panel_rect.top + 10))

        # Render Right Subarray cards
        right_head_pt = self._render_merge_subarray_row(
            surface=surface,
            items=right_sub,
            start_x=right_panel_rect.left + 14,
            start_y=right_panel_rect.top + 34,
            max_w=right_panel_rect.width - 28,
            active_idx=curr_r,
            is_selected_side=(state.selected_item in right_sub if state.selected_item else False),
            pointer_label="R-PTR",
        )

        # 3. COMPARISON ARENA (Center Spotlight with Directional Arrows)
        arena_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 214, self.rect.width - 48, 140)
        draw_rounded_panel(surface, arena_rect, bg_color=(255, 255, 255), border_color=COLOR_ACCENT, border_width=2, radius=6)

        f_arena_lbl = FontManager.get(11, bold=True)
        surface.blit(f_arena_lbl.render("ACTIVE COMPARISON SPOTLIGHT", True, COLOR_COMPARE), (arena_rect.left + 16, arena_rect.top + 10))

        has_comparison = (state.comp_left_val is not None and state.comp_right_val is not None)

        if has_comparison:
            l_item = left_sub[curr_l] if curr_l is not None and curr_l < len(left_sub) else None
            r_item = right_sub[curr_r] if curr_r is not None and curr_r < len(right_sub) else None

            box_w = 200
            box_h = 72
            box_l_x = arena_rect.centerx - box_w - 70
            box_r_x = arena_rect.centerx + 70
            box_y = arena_rect.top + 38

            # Left Compared Box
            l_box = pygame.Rect(box_l_x, box_y, box_w, box_h)
            draw_rounded_panel(surface, l_box, bg_color=COLOR_COMPARE_BG, border_color=COLOR_COMPARE_BORDER, border_width=2, radius=6)
            if l_item:
                surface.blit(FontManager.get(11, bold=True).render(f"{l_item.area_id} — {l_item.name}", True, COLOR_TEXT_PRIMARY), (l_box.left + 10, l_box.top + 8))
                surface.blit(FontManager.get(20, bold=True).render(f"{l_item.water_level:.1f} m", True, COLOR_COMPARE), (l_box.left + 10, l_box.top + 28))

            # VS text in center
            vs_font = FontManager.get(18, bold=True)
            op_sym = ">=" if state.comp_left_val >= state.comp_right_val else "<"
            surface.blit(vs_font.render("VS", True, COLOR_TEXT_MUTED), (arena_rect.centerx - 12, box_y + 8))
            surface.blit(FontManager.get(22, bold=True).render(f"{op_sym}", True, COLOR_COMPARE), (arena_rect.centerx - 8, box_y + 34))

            # Right Compared Box
            r_box = pygame.Rect(box_r_x, box_y, box_w, box_h)
            draw_rounded_panel(surface, r_box, bg_color=COLOR_COMPARE_BG, border_color=COLOR_COMPARE_BORDER, border_width=2, radius=6)
            if r_item:
                surface.blit(FontManager.get(11, bold=True).render(f"{r_item.area_id} — {r_item.name}", True, COLOR_TEXT_PRIMARY), (r_box.left + 10, r_box.top + 8))
                surface.blit(FontManager.get(20, bold=True).render(f"{r_item.water_level:.1f} m", True, COLOR_COMPARE), (r_box.left + 10, r_box.top + 28))

            # Draw directional arrows from subarray pointer heads into compared boxes
            if left_head_pt:
                draw_arrow(surface, left_head_pt, (l_box.centerx, l_box.top), color=COLOR_COMPARE, width=2)
            if right_head_pt:
                draw_arrow(surface, right_head_pt, (r_box.centerx, r_box.top), color=COLOR_COMPARE, width=2)

            # Decision banner
            if state.selected_item:
                banner_str = f"SELECTED FOR HIGHEST EVACUATION PRIORITY: {state.selected_item.name} ({state.selected_item.water_level:.1f} m)"
                draw_badge(surface, banner_str, arena_rect.left + 16, arena_rect.bottom - 26, COLOR_SELECTED, COLOR_SELECTED_BG, size=11)
        else:
            info_txt = state.comparison_text or "Merging subarrays in descending order..."
            surface.blit(FontManager.get(14, bold=True).render(info_txt, True, COLOR_ACCENT), (arena_rect.left + 20, arena_rect.top + 45))
            surface.blit(FontManager.get(11).render(state.why_text, True, COLOR_TEXT_SECONDARY), (arena_rect.left + 20, arena_rect.top + 75))

        # 4. MERGED RESULT BUFFER (Bottom Panel: Building Step-by-Step)
        merged_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 368, self.rect.width - 48, 205)
        draw_rounded_panel(surface, merged_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render(f"MERGED RESULT BUFFER — BUILDING STEP-BY-STEP ({len(merged)} Elements Placed)", True, COLOR_SELECTED), (merged_rect.left + 14, merged_rect.top + 10))

        # Render cards inside merged buffer
        target_slot_pt = self._render_merged_building_row(
            surface=surface,
            items=merged,
            start_x=merged_rect.left + 14,
            start_y=merged_rect.top + 36,
            max_w=merged_rect.width - 28,
        )

        # Draw downward arrow from active comparison arena into the latest merged slot
        if has_comparison and state.selected_item and target_slot_pt:
            draw_arrow(surface, (arena_rect.centerx, arena_rect.bottom), target_slot_pt, color=COLOR_SELECTED, width=2)

    def _render_merge_subarray_row(
        self,
        surface: pygame.Surface,
        items: List[AreaRecord],
        start_x: int,
        start_y: int,
        max_w: int,
        active_idx: Optional[int],
        is_selected_side: bool,
        pointer_label: str,
    ) -> Optional[Tuple[int, int]]:
        """Renders subarray elements and returns bottom-center point of active pointer element for arrow attachment."""
        if not items:
            surface.blit(FontManager.get(11).render("(Empty subarray)", True, COLOR_TEXT_MUTED), (start_x, start_y + 20))
            return None

        n = len(items)
        card_w = min(84, max(44, (max_w - (n - 1) * 6) // n))
        card_h = 86
        active_bottom_center = None

        for idx, item in enumerate(items):
            cx = start_x + idx * (card_w + 6)
            cy = start_y
            c_box = pygame.Rect(cx, cy, card_w, card_h)

            is_active = (idx == active_idx)
            is_already_merged = (active_idx is not None and idx < active_idx)

            if is_active:
                bg = COLOR_COMPARE_BG if not is_selected_side else COLOR_SELECTED_BG
                border = COLOR_COMPARE_BORDER if not is_selected_side else COLOR_SELECTED_BORDER
                bw = 2
                active_bottom_center = (c_box.centerx, c_box.bottom)
            elif is_already_merged:
                bg = COLOR_DIMMED_BG
                border = COLOR_BORDER_LIGHT
                bw = 1
            else:
                bg = (255, 255, 255)
                border = COLOR_BORDER
                bw = 1

            draw_rounded_panel(surface, c_box, bg_color=bg, border_color=border, border_width=bw, radius=4)

            # Pointer indicator above active element
            if is_active:
                p_rect = pygame.Rect(cx + (card_w - 44) // 2, cy - 14, 44, 14)
                pygame.draw.rect(surface, COLOR_ACCENT, p_rect, border_radius=3)
                surface.blit(FontManager.get(8, bold=True).render(pointer_label, True, (255, 255, 255)), (p_rect.left + 4, p_rect.top + 2))

            # Text inside card
            id_col = COLOR_ACCENT if is_active else (COLOR_TEXT_MUTED if is_already_merged else COLOR_TEXT_PRIMARY)
            surface.blit(FontManager.get(10, bold=True).render(item.area_id, True, id_col), (cx + 4, cy + 6))
            surface.blit(FontManager.get(9).render(item.name[:7], True, COLOR_TEXT_SECONDARY), (cx + 4, cy + 22))

            lvl_col = get_water_level_color(item.water_level)
            surface.blit(FontManager.get(11, bold=True).render(f"{item.water_level:.1f}m", True, lvl_col), (cx + 4, cy + 38))

            g_rect = pygame.Rect(cx + 4, cy + card_h - 10, card_w - 8, 4)
            draw_water_gauge(surface, g_rect, item.water_level, max_level=10.0, show_text=False)

        return active_bottom_center

    def _render_merged_building_row(
        self,
        surface: pygame.Surface,
        items: List[AreaRecord],
        start_x: int,
        start_y: int,
        max_w: int,
    ) -> Optional[Tuple[int, int]]:
        """Renders building merged array and returns the top-center point of the latest placed item."""
        if not items:
            surface.blit(FontManager.get(11).render("[ Empty Buffer — awaiting first comparison selection ]", True, COLOR_TEXT_MUTED), (start_x, start_y + 24))
            return None

        n = len(items)
        card_w = min(80, max(40, (max_w - (n - 1) * 6) // n))
        card_h = 92
        latest_top_center = None

        for idx, item in enumerate(items):
            cx = start_x + idx * (card_w + 6)
            cy = start_y
            c_box = pygame.Rect(cx, cy, card_w, card_h)

            is_latest = (idx == len(items) - 1)
            if is_latest:
                bg = COLOR_SELECTED_BG
                border = COLOR_SELECTED_BORDER
                bw = 2
                latest_top_center = (c_box.centerx, c_box.top)
            else:
                bg = (255, 255, 255)
                border = COLOR_BORDER
                bw = 1

            draw_rounded_panel(surface, c_box, bg_color=bg, border_color=border, border_width=bw, radius=4)

            # Rank indicator
            surface.blit(FontManager.get(9, bold=True).render(f"#{idx + 1}", True, COLOR_ACCENT), (cx + 4, cy + 4))

            surface.blit(FontManager.get(10, bold=True).render(item.area_id, True, COLOR_TEXT_PRIMARY), (cx + 4, cy + 18))
            surface.blit(FontManager.get(9).render(item.name[:7], True, COLOR_TEXT_SECONDARY), (cx + 4, cy + 32))

            lvl_col = get_water_level_color(item.water_level)
            surface.blit(FontManager.get(11, bold=True).render(f"{item.water_level:.1f}m", True, lvl_col), (cx + 4, cy + 48))

            g_rect = pygame.Rect(cx + 4, cy + card_h - 12, card_w - 8, 4)
            draw_water_gauge(surface, g_rect, item.water_level, max_level=10.0, show_text=False)

        return latest_top_center

    # ------------------------------------------------------------------
    # SCENE 8: FINAL SORTED RESULT (Evacuation Ranking Table - Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_sorted_result(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header banner
        draw_badge(surface, "✓ MERGE SORT COMPLETE", self.rect.left + 24, self.rect.top + 14, COLOR_LOW, COLOR_LOW_BG, size=12)

        f_head = FontManager.get(16, bold=True)
        surface.blit(f_head.render("FINAL EVACUATION PRIORITY RANKING (DESCENDING WATER LEVEL)", True, COLOR_TEXT_PRIMARY), (self.rect.left + 220, self.rect.top + 14))

        # Note
        f_note = FontManager.get(10)
        surface.blit(f_note.render("Educational simulation — evacuation priority is strictly determined by sorted flood water level.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 40))

        # Parallel tables of 10 items each
        table_y = self.rect.top + 64
        col_w = (self.rect.width - 64) // 2

        self._render_priority_subtable(surface, self.sim.sorted_areas[:10], self.rect.left + 24, table_y, col_w, start_rank=1)
        self._render_priority_subtable(surface, self.sim.sorted_areas[10:], self.rect.left + 24 + col_w + 16, table_y, col_w, start_rank=11)

    def _render_priority_subtable(self, surface: pygame.Surface, items: List[AreaRecord], x: int, y: int, width: int, start_rank: int):
        t_rect = pygame.Rect(x, y, width, 505)
        draw_rounded_panel(surface, t_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        th_font = FontManager.get(10, bold=True)
        surface.blit(th_font.render("RANK", True, COLOR_TEXT_MUTED), (x + 12, y + 10))
        surface.blit(th_font.render("ID", True, COLOR_TEXT_MUTED), (x + 55, y + 10))
        surface.blit(th_font.render("AREA NAME", True, COLOR_TEXT_MUTED), (x + 95, y + 10))
        surface.blit(th_font.render("WATER LEVEL", True, COLOR_TEXT_MUTED), (x + 220, y + 10))
        surface.blit(th_font.render("PRIORITY", True, COLOR_TEXT_MUTED), (x + width - 78, y + 10))

        pygame.draw.line(surface, COLOR_BORDER_LIGHT, (x + 8, y + 28), (x + width - 8, y + 28), 1)

        row_h = 46
        f_row = FontManager.get(11)
        f_bold = FontManager.get(11, bold=True)

        for i, item in enumerate(items):
            ry = y + 32 + i * row_h
            rank = start_rank + i

            if i % 2 == 1:
                pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(x + 4, ry, width - 8, row_h - 2), border_radius=4)

            # Rank
            r_col = COLOR_CRITICAL if rank <= 3 else (COLOR_ACCENT if rank <= 8 else COLOR_TEXT_MUTED)
            surface.blit(f_bold.render(f"#{rank}", True, r_col), (x + 12, ry + 12))

            # ID
            surface.blit(f_row.render(item.area_id, True, COLOR_TEXT_PRIMARY), (x + 55, ry + 12))

            # Name
            surface.blit(f_bold.render(item.name[:14], True, COLOR_TEXT_PRIMARY), (x + 95, ry + 12))

            # Water level & gauge
            lvl_col = get_water_level_color(item.water_level)
            surface.blit(f_bold.render(f"{item.water_level:.1f} m", True, lvl_col), (x + 220, ry + 12))

            g_rect = pygame.Rect(x + 270, ry + 16, 45, 6)
            draw_water_gauge(surface, g_rect, item.water_level, max_level=10.0, show_text=False)

            # Priority badge
            draw_badge(surface, item.get_priority(), x + width - 80, ry + 10, get_priority_color(item.get_priority()), get_priority_bg_color(item.get_priority()), size=9)

    # ------------------------------------------------------------------
    # SCENE 9: EVACUATION SIMULATION (Light Blueprint Map Dispatch)
    # ------------------------------------------------------------------
    def _render_scene_evacuation(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("PRIORITY RESCUE DISPATCH — TOP 5 FLOOD CRITICAL ZONES", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))
        surface.blit(f_sub.render("Deploying rescue fleets to highest water level zones in exact Merge Sort priority order.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        top5 = self.sim.sorted_areas[:5]
        active_evac_idx = self.sim.evac_index
        evac_pct = self.sim.evac_progress

        # Visual map container on left (540 x 510)
        map_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 60, 540, 510)
        draw_rounded_panel(surface, map_rect, bg_color=(241, 245, 249), border_color=COLOR_BORDER_LIGHT, radius=6)

        # Water river representation across Pune map
        river_pts = [
            (map_rect.left, map_rect.top + 180),
            (map_rect.left + 150, map_rect.top + 230),
            (map_rect.left + 320, map_rect.top + 210),
            (map_rect.right, map_rect.top + 270),
        ]
        pygame.draw.lines(surface, (147, 197, 253), False, river_pts, width=16)

        # Designated Central Shelter
        shelter_pos = (map_rect.centerx + 40, map_rect.bottom - 80)
        draw_shelter_icon(surface, shelter_pos[0] - 16, shelter_pos[1] - 16, size=32)
        surface.blit(FontManager.get(10, bold=True).render("CENTRAL RELIEF SHELTER", True, COLOR_LOW), (shelter_pos[0] - 65, shelter_pos[1] + 20))

        # Map positions for top 5 areas
        zone_coords = [
            (map_rect.left + 80, map_rect.top + 80),    # Hadapsar
            (map_rect.left + 220, map_rect.top + 110),  # Yerawada
            (map_rect.left + 390, map_rect.top + 70),   # Bhosari
            (map_rect.left + 120, map_rect.top + 340),  # Hinjewadi
            (map_rect.left + 420, map_rect.top + 330),  # Pimpri
        ]

        f_map = FontManager.get(10, bold=True)
        for idx, (area, (zx, zy)) in enumerate(zip(top5, zone_coords)):
            is_active = (idx == active_evac_idx)
            is_done = (idx in self.sim.evac_completed)

            node_col = COLOR_LOW if is_done else (COLOR_COMPARE if is_active else COLOR_CRITICAL)
            pygame.draw.circle(surface, node_col, (zx, zy), 18)
            pygame.draw.circle(surface, (255, 255, 255), (zx, zy), 18, width=2)

            draw_house_icon(surface, zx - 8, zy - 7, width=16, height=14)

            lbl = f"#{idx + 1} {area.name}"
            surface.blit(f_map.render(lbl, True, COLOR_TEXT_PRIMARY), (zx - 30, zy + 22))

            if is_active or is_done:
                pygame.draw.line(surface, COLOR_BORDER_STRONG, (zx, zy), shelter_pos, 1)

            if is_active:
                cur_x = int(zx + (shelter_pos[0] - zx) * evac_pct)
                cur_y = int(zy + (shelter_pos[1] - zy) * evac_pct)
                draw_rescue_boat(surface, cur_x, cur_y, size=24)

        # Right side: Priority Mission Status Log
        log_rect = pygame.Rect(self.rect.left + 580, self.rect.top + 60, 315, 510)
        draw_rounded_panel(surface, log_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render("RESCUE LOG (TRIAGE QUEUE)", True, COLOR_ACCENT), (log_rect.left + 16, log_rect.top + 14))

        card_h = 86
        for idx, area in enumerate(top5):
            cy = log_rect.top + 46 + idx * (card_h + 8)
            c_box = pygame.Rect(log_rect.left + 14, cy, log_rect.width - 28, card_h)

            is_active = (idx == active_evac_idx)
            is_done = (idx in self.sim.evac_completed)

            if is_done:
                bg_col = COLOR_LOW_BG
                b_col = COLOR_LOW
            elif is_active:
                bg_col = COLOR_COMPARE_BG
                b_col = COLOR_COMPARE
            else:
                bg_col = (255, 255, 255)
                b_col = COLOR_BORDER_LIGHT

            draw_rounded_panel(surface, c_box, bg_color=bg_col, border_color=b_col, border_width=2 if is_active else 1, radius=6)

            # Details
            draw_badge(surface, f"PRIORITY #{idx + 1}", c_box.left + 8, c_box.top + 8, COLOR_CRITICAL if idx < 3 else COLOR_HIGH, COLOR_CRITICAL_BG if idx < 3 else COLOR_HIGH_BG, size=9)

            surface.blit(FontManager.get(12, bold=True).render(f"{area.area_id} — {area.name}", True, COLOR_TEXT_PRIMARY), (c_box.left + 8, c_box.top + 32))
            surface.blit(FontManager.get(10).render(f"Water: {area.water_level:.1f}m | Pop: {area.population:,}", True, COLOR_TEXT_SECONDARY), (c_box.left + 8, c_box.top + 52))

            status_txt = "SAFE (EVACUATED)" if is_done else ("IN TRANSIT..." if is_active else "QUEUED")
            s_col = COLOR_LOW if is_done else (COLOR_COMPARE if is_active else COLOR_TEXT_MUTED)
            s_bg = COLOR_LOW_BG if is_done else (COLOR_COMPARE_BG if is_active else (241, 245, 249))
            draw_badge(surface, status_txt, c_box.right - 95, c_box.top + 8, s_col, s_bg, size=9)

    # ------------------------------------------------------------------
    # SCENE 10: ALGORITHM ANALYSIS & MASTER THEOREM PROOF (Light Theme)
    # ------------------------------------------------------------------
    def _render_scene_analysis(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Header
        f_head = FontManager.get(16, bold=True)
        f_sub = FontManager.get(11)
        surface.blit(f_head.render("ALGORITHM ANALYSIS & MASTER THEOREM PROOF", True, COLOR_TEXT_PRIMARY), (self.rect.left + 24, self.rect.top + 14))
        surface.blit(f_sub.render("Academic complexity breakdown, Master Theorem proof, and mathematical validation of Merge Sort.", True, COLOR_TEXT_SECONDARY), (self.rect.left + 24, self.rect.top + 36))

        # 1. Left Card: Time Complexity Using Master Theorem (Step-by-step visual derivation)
        mt_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 60, 496, 235)
        draw_rounded_panel(surface, mt_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render("TIME COMPLEXITY USING MASTER THEOREM", True, COLOR_ACCENT), (mt_rect.left + 16, mt_rect.top + 10))
        surface.blit(FontManager.get(9).render("Standard Form: T(n) = aT(n/b) + f(n)", True, COLOR_TEXT_MUTED), (mt_rect.left + 290, mt_rect.top + 12))

        # Visual step-by-step container
        steps_box = pygame.Rect(mt_rect.left + 12, mt_rect.top + 32, mt_rect.width - 24, 192)
        draw_rounded_panel(surface, steps_box, bg_color=(255, 255, 255), border_color=COLOR_BORDER_LIGHT, radius=4)

        f_step = FontManager.get(11, bold=True)
        f_desc = FontManager.get(10)
        f_arr = FontManager.get(11, bold=True)

        proof_steps = [
            ("T(n) = 2T(n/2) + O(n)", "Merge Sort recursive recurrence relation", COLOR_TEXT_PRIMARY),
            ("a = 2,  b = 2,  f(n) = O(n)", "a: subproblems, b: factor, f(n): linear merge", COLOR_ACCENT),
            ("n^(log_b a) = n^(log₂2) = n", "Critical exponent calculation: n¹ = n", (124, 58, 237)),
            ("f(n) = O(n) = Θ(n^(log₂2))", "Merge cost f(n) matches n^(log_b a)", COLOR_COMPARE),
            ("Master Theorem Case 2", "f(n) = Θ(n^(log_b a))  =>  T(n) = Θ(n^(log_b a) · log n)", COLOR_SELECTED),
            ("T(n) = Θ(n log n)", "Proven: Optimal Θ(n log n) running time", COLOR_SELECTED),
        ]

        sy = steps_box.top + 8
        for idx, (eq, desc, col) in enumerate(proof_steps):
            surface.blit(f_step.render(eq, True, col), (steps_box.left + 14, sy))
            surface.blit(f_desc.render(desc, True, COLOR_TEXT_MUTED), (steps_box.left + 225, sy + 1))

            if idx < len(proof_steps) - 1:
                # Centered downward arrow indicator
                arr_surf = f_arr.render("↓", True, COLOR_ACCENT)
                surface.blit(arr_surf, (steps_box.left + 65, sy + 15))
                sy += 30
            else:
                sy += 24

        # 2. Right Card: Complexity Bounds & Space Complexity
        t_rect = pygame.Rect(self.rect.left + 532, self.rect.top + 60, 360, 235)
        draw_rounded_panel(surface, t_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render("FINAL COMPLEXITY & SPACE ANALYSIS", True, COLOR_ACCENT), (t_rect.left + 16, t_rect.top + 10))

        comp_rows = [
            ("Best Case", "O(n log n)", COLOR_SELECTED, COLOR_SELECTED_BG),
            ("Average Case", "O(n log n)", COLOR_SELECTED, COLOR_SELECTED_BG),
            ("Worst Case", "O(n log n)", COLOR_SELECTED, COLOR_SELECTED_BG),
            ("Space Complexity", "O(n)", COLOR_ACCENT, COLOR_ACCENT_LIGHT),
        ]

        th_f = FontManager.get(11, bold=True)
        for idx, (metric, val, badge_col, badge_bg) in enumerate(comp_rows):
            ry = t_rect.top + 34 + idx * 35
            surface.blit(th_f.render(metric, True, COLOR_TEXT_PRIMARY), (t_rect.left + 16, ry + 4))
            draw_badge(surface, val, t_rect.right - 90, ry + 2, badge_col, badge_bg, size=10)

        # Auxiliary space explanation note
        sp_note_rect = pygame.Rect(t_rect.left + 12, t_rect.top + 176, t_rect.width - 24, 48)
        draw_rounded_panel(surface, sp_note_rect, bg_color=(255, 255, 255), border_color=COLOR_BORDER_LIGHT, radius=4)
        surface.blit(FontManager.get(9, bold=True).render("WHY O(n) AUXILIARY SPACE?", True, COLOR_TEXT_PRIMARY), (sp_note_rect.left + 8, sp_note_rect.top + 6))
        surface.blit(FontManager.get(9).render("Merge Sort requires auxiliary space for merging.", True, COLOR_TEXT_SECONDARY), (sp_note_rect.left + 8, sp_note_rect.top + 20))
        surface.blit(FontManager.get(9).render("Allocates temporary buffers to recombine subarrays.", True, COLOR_TEXT_MUTED), (sp_note_rect.left + 8, sp_note_rect.top + 32))

        # 3. Bottom Card: Full End-to-End Visual Pipeline & Live Telemetry
        pipe_rect = pygame.Rect(self.rect.left + 24, self.rect.top + 305, self.rect.width - 48, 268)
        draw_rounded_panel(surface, pipe_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(12, bold=True).render("COMPLETE DAA ARCHITECTURAL PIPELINE", True, COLOR_ACCENT), (pipe_rect.left + 16, pipe_rect.top + 14))

        stages = [
            ("1. FLOOD SENSORS", "Collect 20 Area Readings"),
            ("2. INPUT ARRAY", "Unsorted Administrative Order"),
            ("3. RECURSIVE DIVIDE", "Split down to 1-element arrays"),
            ("4. COMPARE & SELECT", "Select Higher Water Level"),
            ("5. MERGE SUBARRAYS", "Combine into Descending Order"),
            ("6. EVACUATION QUEUE", "Dispatch Rescue Vehicles"),
        ]

        card_w = (pipe_rect.width - 32 - 5 * 10) // 6
        card_h = 75
        py = pipe_rect.top + 50

        for idx, (st_name, st_desc) in enumerate(stages):
            px = pipe_rect.left + 16 + idx * (card_w + 10)
            p_box = pygame.Rect(px, py, card_w, card_h)
            draw_rounded_panel(surface, p_box, bg_color=(255, 255, 255), border_color=COLOR_BORDER_LIGHT, radius=6)

            surface.blit(FontManager.get(10, bold=True).render(st_name, True, COLOR_ACCENT), (px + 6, py + 10))
            self._render_multiline_text(surface, st_desc, px + 6, py + 30, card_w - 12, FontManager.get(9), COLOR_TEXT_SECONDARY)

            if idx < len(stages) - 1:
                arr_x = px + card_w + 2
                surface.blit(FontManager.get(14, bold=True).render(">", True, COLOR_ACCENT), (arr_x, py + 26))

        # Runtime Execution Stats summary
        stat_box = pygame.Rect(pipe_rect.left + 16, pipe_rect.top + 145, pipe_rect.width - 32, 105)
        draw_rounded_panel(surface, stat_box, bg_color=(255, 255, 255), border_color=COLOR_BORDER_LIGHT, radius=6)

        surface.blit(FontManager.get(11, bold=True).render("ACTUAL RUNTIME SIMULATION TELEMETRY (C++ & PYTHON VERIFIED)", True, COLOR_COMPARE), (stat_box.left + 16, stat_box.top + 10))

        s_font = FontManager.get(11)
        b_font = FontManager.get(11, bold=True)

        surface.blit(s_font.render("Total Elements Sorted:", True, COLOR_TEXT_PRIMARY), (stat_box.left + 16, stat_box.top + 36))
        surface.blit(b_font.render("20 Areas", True, COLOR_ACCENT), (stat_box.left + 170, stat_box.top + 36))

        surface.blit(s_font.render("Total Comparisons Made:", True, COLOR_TEXT_PRIMARY), (stat_box.left + 16, stat_box.top + 56))
        surface.blit(b_font.render(f"{self.sim.tracer.comparisons_count} Comparisons", True, COLOR_COMPARE), (stat_box.left + 170, stat_box.top + 56))

        surface.blit(s_font.render("Total Merges Performed:", True, COLOR_TEXT_PRIMARY), (stat_box.left + 350, stat_box.top + 36))
        surface.blit(b_font.render(f"{self.sim.tracer.merges_count} Merges", True, COLOR_SELECTED), (stat_box.left + 510, stat_box.top + 36))

        surface.blit(s_font.render("Recursion Tree Max Depth:", True, COLOR_TEXT_PRIMARY), (stat_box.left + 350, stat_box.top + 56))
        surface.blit(b_font.render(f"{self.sim.tracer.max_depth} Levels (log₂ 20 ≈ 4.32)", True, COLOR_ACCENT), (stat_box.left + 510, stat_box.top + 56))

        surface.blit(FontManager.get(10, bold=True).render("DAA FA-2 Software Simulation Verified • Zero Built-in Sorting Used", True, COLOR_LOW), (stat_box.left + 16, stat_box.top + 82))

    def _render_multiline_text(self, surface: pygame.Surface, text: str, x: int, y: int, max_width: int, font: pygame.font.Font, color: Tuple[int, int, int]):
        paragraphs = text.split("\n")
        curr_y = y
        line_height = font.get_linesize()

        for para in paragraphs:
            if not para.strip():
                curr_y += line_height // 2
                continue

            words = para.split(" ")
            curr_line = []
            for word in words:
                curr_line.append(word)
                test_str = " ".join(curr_line)
                if font.size(test_str)[0] > max_width:
                    curr_line.pop()
                    line_surf = font.render(" ".join(curr_line), True, color)
                    surface.blit(line_surf, (x, curr_y))
                    curr_y += line_height
                    curr_line = [word]

            if curr_line:
                line_surf = font.render(" ".join(curr_line), True, color)
                surface.blit(line_surf, (x, curr_y))
                curr_y += line_height
