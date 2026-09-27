"""
ui_components.py
Clean, modern, professional LIGHT THEME design system, reusable widgets,
fonts, colors, and layout components for the Flood Evacuation Priority System Pygame desktop simulation.
"""

import pygame
import math
from typing import Tuple, Optional, Callable, List
from merge_sort import AreaRecord, AlgorithmState

# -------------------------------------------------------------
# LIGHT THEME COLOR PALETTE (Professional Desktop Software System)
# -------------------------------------------------------------
COLOR_BG = (248, 250, 252)              # Slate-50 (clean off-white window background)
COLOR_PANEL = (255, 255, 255)           # Pure White primary panels
COLOR_PANEL_ALT = (241, 245, 249)       # Slate-100 secondary cards
COLOR_PANEL_SUBTLE = (248, 250, 252)    # Slate-50 subtle fills
COLOR_BORDER = (203, 213, 225)          # Slate-300 clean subtle borders
COLOR_BORDER_LIGHT = (226, 232, 240)    # Slate-200 card outlines
COLOR_BORDER_STRONG = (148, 163, 184)   # Slate-400 focus borders

# High-contrast typography
COLOR_TEXT_PRIMARY = (15, 23, 42)       # Slate-900 (deep navy/charcoal)
COLOR_TEXT_SECONDARY = (51, 65, 85)     # Slate-700
COLOR_TEXT_MUTED = (100, 116, 139)      # Slate-500

# Blue primary accents
COLOR_ACCENT = (37, 99, 235)            # Blue-600
COLOR_ACCENT_HOVER = (29, 78, 216)      # Blue-700
COLOR_ACCENT_LIGHT = (219, 234, 254)    # Blue-100
COLOR_ACCENT_BORDER = (147, 197, 253)   # Blue-300

# Priority & Algorithm status colors (Tuned for light background)
COLOR_CRITICAL = (220, 38, 38)          # Red-600 (Water Level >= 7.5m)
COLOR_CRITICAL_BG = (254, 226, 226)     # Red-100
COLOR_CRITICAL_BORDER = (252, 165, 165)

COLOR_HIGH = (234, 88, 12)              # Orange-600 (6.0m - 7.4m)
COLOR_HIGH_BG = (255, 237, 213)         # Orange-100
COLOR_HIGH_BORDER = (253, 186, 116)

COLOR_MEDIUM = (217, 119, 6)            # Amber-600 (4.0m - 5.9m)
COLOR_MEDIUM_BG = (254, 243, 199)       # Amber-100
COLOR_MEDIUM_BORDER = (252, 211, 77)

COLOR_LOW = (5, 150, 105)               # Emerald-600 (< 4.0m)
COLOR_LOW_BG = (209, 250, 229)          # Emerald-100
COLOR_LOW_BORDER = (110, 231, 183)

# Comparison & Selection Highlights
COLOR_COMPARE = (217, 119, 6)           # Amber-600 (active comparison)
COLOR_COMPARE_BG = (254, 243, 199)      # Amber-100
COLOR_COMPARE_BORDER = (245, 158, 11)   # Amber-500

COLOR_SELECTED = (5, 150, 105)          # Emerald-600 (selected/merged item)
COLOR_SELECTED_BG = (209, 250, 229)     # Emerald-100
COLOR_SELECTED_BORDER = (16, 185, 129)  # Emerald-500

COLOR_DIMMED = (148, 163, 184)          # Muted/inactive items
COLOR_DIMMED_BG = (241, 245, 249)

# Buttons
COLOR_BUTTON_BG = (255, 255, 255)
COLOR_BUTTON_HOVER = (241, 245, 249)
COLOR_BUTTON_BORDER = (203, 213, 225)
COLOR_BUTTON_ACTIVE = (37, 99, 235)


def get_priority_color(priority: str) -> Tuple[int, int, int]:
    p = priority.upper()
    if p == "CRITICAL":
        return COLOR_CRITICAL
    elif p == "HIGH":
        return COLOR_HIGH
    elif p == "MEDIUM":
        return COLOR_MEDIUM
    else:
        return COLOR_LOW


def get_priority_bg_color(priority: str) -> Tuple[int, int, int]:
    p = priority.upper()
    if p == "CRITICAL":
        return COLOR_CRITICAL_BG
    elif p == "HIGH":
        return COLOR_HIGH_BG
    elif p == "MEDIUM":
        return COLOR_MEDIUM_BG
    else:
        return COLOR_LOW_BG


def get_water_level_color(level: float) -> Tuple[int, int, int]:
    if level >= 7.5:
        return COLOR_CRITICAL
    elif level >= 6.0:
        return COLOR_HIGH
    elif level >= 4.0:
        return COLOR_MEDIUM
    else:
        return COLOR_LOW


class FontManager:
    """Manages clean system fonts with fallback."""
    _fonts = {}

    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in cls._fonts:
            preferred = ["segoeui", "tahoma", "arial", "dejavusans", "helvetica"]
            font = None
            for font_name in preferred:
                try:
                    font = pygame.font.SysFont(font_name, size, bold=bold)
                    if font:
                        break
                except Exception:
                    continue
            if not font:
                font = pygame.font.Font(None, size)
            cls._fonts[key] = font
        return cls._fonts[key]


def draw_rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Tuple[int, int, int] = COLOR_PANEL,
    border_color: Optional[Tuple[int, int, int]] = COLOR_BORDER,
    border_width: int = 1,
    radius: int = 6,
):
    """Draws a clean modern panel with subtle border in light theme."""
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)


def draw_badge(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    color: Tuple[int, int, int],
    bg_color: Optional[Tuple[int, int, int]] = None,
    size: int = 11,
) -> pygame.Rect:
    """Draws a refined pill badge with soft background and crisp colored text."""
    font = FontManager.get(size, bold=True)
    txt_surf = font.render(text, True, color)
    padding_x = 8
    padding_y = 3
    rect = pygame.Rect(x, y, txt_surf.get_width() + padding_x * 2, txt_surf.get_height() + padding_y * 2)

    if bg_color is None:
        # Default to a gentle tint
        bg_color = (color[0], color[1], color[2], 25)

    pygame.draw.rect(surface, bg_color, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, color, rect, width=1, border_radius=rect.height // 2)
    surface.blit(txt_surf, (x + padding_x, y + padding_y))
    return rect


def draw_arrow(
    surface: pygame.Surface,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Tuple[int, int, int] = COLOR_ACCENT,
    width: int = 2,
    head_size: int = 7,
):
    """Draws a clean directional arrow from start to end with arrowhead."""
    pygame.draw.line(surface, color, start, end, width)

    # Calculate angle for arrowhead
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)

    # Arrowhead points
    p1 = (
        end[0] - head_size * math.cos(angle - math.pi / 6),
        end[1] - head_size * math.sin(angle - math.pi / 6),
    )
    p2 = (
        end[0] - head_size * math.cos(angle + math.pi / 6),
        end[1] - head_size * math.sin(angle + math.pi / 6),
    )
    pygame.draw.polygon(surface, color, [end, p1, p2])


class Button:
    """Modern interactive push button with crisp vector icon rendering for light UI."""
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable] = None,
        icon_type: Optional[str] = None,  # "play", "pause", "prev", "next", "reset", "exit"
        font_size: int = 12,
        bg_color: Tuple[int, int, int] = COLOR_BUTTON_BG,
        hover_color: Tuple[int, int, int] = COLOR_BUTTON_HOVER,
        active_color: Tuple[int, int, int] = COLOR_BUTTON_ACTIVE,
        text_color: Tuple[int, int, int] = COLOR_TEXT_PRIMARY,
        is_active: bool = False,
        disabled: bool = False,
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.icon_type = icon_type
        self.font_size = font_size
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.is_active = is_active
        self.disabled = disabled
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        if self.disabled:
            bg = (241, 245, 249)
            border = (226, 232, 240)
            txt_col = COLOR_TEXT_MUTED
        elif self.is_active:
            bg = self.active_color
            border = COLOR_ACCENT
            txt_col = (255, 255, 255)
        elif self.is_hovered:
            bg = self.hover_color
            border = COLOR_BORDER_STRONG
            txt_col = COLOR_TEXT_PRIMARY
        else:
            bg = self.bg_color
            border = COLOR_BUTTON_BORDER
            txt_col = self.text_color

        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=6)

        font = FontManager.get(self.font_size, bold=True)
        text_surf = font.render(self.text, True, txt_col)

        # Draw icon + text centered
        if self.icon_type:
            icon_w = 12
            gap = 6
            total_w = icon_w + gap + text_surf.get_width()
            start_x = self.rect.centerx - total_w // 2
            icon_rect = pygame.Rect(start_x, self.rect.centery - 6, icon_w, 12)
            self._draw_vector_icon(surface, self.icon_type, icon_rect, txt_col)
            surface.blit(text_surf, (start_x + icon_w + gap, self.rect.centery - text_surf.get_height() // 2))
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def _draw_vector_icon(self, surface: pygame.Surface, icon: str, rect: pygame.Rect, color: Tuple[int, int, int]):
        cx, cy = rect.center
        if icon == "play":
            pts = [(rect.left + 2, rect.top + 1), (rect.right - 1, cy), (rect.left + 2, rect.bottom - 1)]
            pygame.draw.polygon(surface, color, pts)
        elif icon == "pause":
            w = 3
            pygame.draw.rect(surface, color, pygame.Rect(rect.left + 2, rect.top + 1, w, rect.height - 2))
            pygame.draw.rect(surface, color, pygame.Rect(rect.right - 2 - w, rect.top + 1, w, rect.height - 2))
        elif icon == "prev":
            pts = [(rect.right - 1, rect.top + 1), (rect.left + 1, cy), (rect.right - 1, rect.bottom - 1)]
            pygame.draw.polygon(surface, color, pts)
        elif icon == "next":
            pts = [(rect.left + 1, rect.top + 1), (rect.right - 1, cy), (rect.left + 1, rect.bottom - 1)]
            pygame.draw.polygon(surface, color, pts)
        elif icon == "reset":
            pygame.draw.arc(surface, color, pygame.Rect(rect.left + 1, rect.top + 1, rect.width - 2, rect.height - 2), 0.7, 5.8, width=2)
            pts = [(rect.right - 2, cy - 4), (rect.right + 2, cy + 1), (rect.centerx + 1, cy)]
            pygame.draw.polygon(surface, color, pts)
        elif icon == "exit":
            pygame.draw.line(surface, color, (rect.left + 2, rect.top + 2), (rect.right - 2, rect.bottom - 2), 2)
            pygame.draw.line(surface, color, (rect.left + 2, rect.bottom - 2), (rect.right - 2, rect.top + 2), 2)


# -------------------------------------------------------------
# GRAPHICS HELPERS: HOUSES, SHELTERS, BOATS, WATER GAUGES
# -------------------------------------------------------------
def draw_house_icon(surface: pygame.Surface, x: int, y: int, width: int = 24, height: int = 20, color=(148, 163, 184)):
    roof_height = height // 2
    body_height = height - roof_height

    # Roof
    p1 = (x + width // 2, y)
    p2 = (x, y + roof_height)
    p3 = (x + width, y + roof_height)
    pygame.draw.polygon(surface, (239, 68, 68), [p1, p2, p3])

    # Body
    body_rect = pygame.Rect(x + 2, y + roof_height, width - 4, body_height)
    pygame.draw.rect(surface, color, body_rect)
    pygame.draw.rect(surface, COLOR_BORDER, body_rect, width=1)

    # Door
    door_w = max(4, width // 5)
    door_h = max(6, body_height - 2)
    door_rect = pygame.Rect(x + (width - door_w) // 2, y + height - door_h, door_w, door_h)
    pygame.draw.rect(surface, (51, 65, 85), door_rect)


def draw_shelter_icon(surface: pygame.Surface, x: int, y: int, size: int = 32):
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, (16, 185, 129), rect, border_radius=6)
    pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=6)

    cx, cy = rect.center
    arm = size // 5
    span = size // 3
    pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(cx - span, cy - arm // 2, span * 2, arm))
    pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(cx - arm // 2, cy - span, arm, span * 2))


def draw_rescue_boat(surface: pygame.Surface, x: int, y: int, size: int = 24):
    rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
    p1 = (rect.left, rect.centery + 2)
    p2 = (rect.right, rect.centery + 2)
    p3 = (rect.right - 4, rect.bottom - 2)
    p4 = (rect.left + 4, rect.bottom - 2)
    pygame.draw.polygon(surface, (234, 88, 12), [p1, p2, p3, p4])
    pygame.draw.polygon(surface, (194, 65, 12), [p1, p2, p3, p4], width=1)

    cabin_rect = pygame.Rect(rect.centerx - 5, rect.centery - 6, 10, 8)
    pygame.draw.rect(surface, (255, 255, 255), cabin_rect)
    pygame.draw.circle(surface, (220, 38, 38), (rect.centerx, rect.centery - 8), 3)


def draw_water_gauge(
    surface: pygame.Surface,
    rect: pygame.Rect,
    level_m: float,
    max_level: float = 10.0,
    show_text: bool = True,
):
    """Renders a clean water level gauge bar with depth indicator for light theme."""
    pygame.draw.rect(surface, (241, 245, 249), rect, border_radius=4)
    pygame.draw.rect(surface, COLOR_BORDER_LIGHT, rect, width=1, border_radius=4)

    ratio = min(1.0, max(0.0, level_m / max_level))
    fill_w = int((rect.width - 2) * ratio)
    if fill_w > 0:
        fill_rect = pygame.Rect(rect.left + 1, rect.top + 1, fill_w, rect.height - 2)
        color = get_water_level_color(level_m)
        pygame.draw.rect(surface, color, fill_rect, border_radius=3)

    if show_text:
        font = FontManager.get(11, bold=True)
        txt = f"{level_m:.1f} m"
        txt_surf = font.render(txt, True, COLOR_TEXT_PRIMARY)
        txt_rect = txt_surf.get_rect(midleft=(rect.right + 6, rect.centery))
        surface.blit(txt_surf, txt_rect)


# -------------------------------------------------------------
# TOP BAR: APPLICATION TITLE, STAGE TRACKER, PROGRESS, STATUS
# -------------------------------------------------------------
class TopBar:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.short_labels = [
            "INTRO", "DATA", "SCAN", "INPUT", "DIVIDE", "MERGE", "RANK", "EVAC", "ANALYSIS"
        ]

    def draw(
        self,
        surface: pygame.Surface,
        scene_id: int,
        scene_names: List[str],
        is_playing: bool,
        is_demo_mode: bool,
        progress_pct: int,
    ):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=0)

        # 1. Left: Title & Subtitle
        f_title = FontManager.get(15, bold=True)
        f_sub = FontManager.get(11, bold=False)

        title_surf = f_title.render("FLOOD EVACUATION PRIORITY SYSTEM", True, COLOR_TEXT_PRIMARY)
        sub_surf = f_sub.render("DAA FA-2 • MERGE SORT SIMULATION (LIGHT EDITION)", True, COLOR_ACCENT)

        surface.blit(title_surf, (self.rect.left + 16, self.rect.top + 8))
        surface.blit(sub_surf, (self.rect.left + 16, self.rect.top + 28))

        # 2. Middle: Clean Spaced Stage Breadcrumbs
        bc_start_x = self.rect.left + 420
        total_bc_w = 460
        n_stages = len(self.short_labels)
        step_spacing = total_bc_w // (n_stages - 1)
        y_pos = self.rect.centery

        bc_font = FontManager.get(9, bold=True)

        for i, s_label in enumerate(self.short_labels):
            dot_x = bc_start_x + i * step_spacing
            is_curr = (i == scene_id)
            is_past = (i < scene_id)

            # Node circle
            node_r = 4 if is_curr else 3
            node_col = COLOR_ACCENT if is_curr else (COLOR_SELECTED if is_past else COLOR_BORDER)
            pygame.draw.circle(surface, node_col, (dot_x, y_pos - 10), node_r)
            if is_curr:
                pygame.draw.circle(surface, COLOR_ACCENT, (dot_x, y_pos - 10), 6, width=1)

            # Stage label
            col = COLOR_ACCENT if is_curr else (COLOR_TEXT_PRIMARY if is_past else COLOR_TEXT_MUTED)
            txt_surf = bc_font.render(s_label, True, col)
            txt_rect = txt_surf.get_rect(center=(dot_x, y_pos + 8))
            surface.blit(txt_surf, txt_rect)

            # Connector line
            if i < n_stages - 1:
                next_x = bc_start_x + (i + 1) * step_spacing
                line_col = COLOR_ACCENT if is_past else COLOR_BORDER_LIGHT
                pygame.draw.line(surface, line_col, (dot_x + 8, y_pos - 10), (next_x - 8, y_pos - 10), 1)

        # 3. Right: Current Stage Name & Status Badges
        right_panel_x = self.rect.right - 270

        curr_stage_name = scene_names[scene_id] if scene_id < len(scene_names) else ""
        f_st = FontManager.get(10, bold=True)
        surface.blit(f_st.render(f"STAGE: {curr_stage_name}", True, COLOR_ACCENT), (right_panel_x, self.rect.top + 9))

        p_txt = f_st.render(f"PROGRESS: {progress_pct}%", True, COLOR_TEXT_SECONDARY)
        surface.blit(p_txt, (right_panel_x, self.rect.top + 28))

        # Status badge
        badge_x = self.rect.right - 110
        if is_demo_mode:
            draw_badge(surface, "DEMO (STEP)", badge_x - 15, self.rect.top + 14, COLOR_MEDIUM, COLOR_MEDIUM_BG, size=10)
        elif is_playing:
            draw_badge(surface, "RUNNING", badge_x, self.rect.top + 14, COLOR_LOW, COLOR_LOW_BG, size=11)
        else:
            draw_badge(surface, "PAUSED", badge_x + 8, self.rect.top + 14, COLOR_MEDIUM, COLOR_MEDIUM_BG, size=11)


# -------------------------------------------------------------
# BOTTOM CONTROL BAR
# -------------------------------------------------------------
class BottomBar:
    def __init__(self, rect: pygame.Rect, state_controller):
        self.rect = rect
        self.controller = state_controller
        self.buttons: List[Button] = []
        self._build_buttons()

    def _build_buttons(self):
        y = self.rect.top + 12
        h = 36

        # Primary controls with vector icons
        self.btn_play_pause = Button(
            pygame.Rect(self.rect.left + 16, y, 92, h),
            text="PAUSE" if self.controller.is_playing else "PLAY",
            icon_type="pause" if self.controller.is_playing else "play",
            callback=self.controller.toggle_play,
            bg_color=COLOR_BUTTON_BG,
        )

        self.btn_prev = Button(
            pygame.Rect(self.rect.left + 116, y, 84, h),
            text="PREV",
            icon_type="prev",
            callback=self.controller.prev_step,
        )

        self.btn_next = Button(
            pygame.Rect(self.rect.left + 208, y, 86, h),
            text="NEXT",
            icon_type="next",
            callback=self.controller.next_step,
            active_color=COLOR_ACCENT,
        )

        self.btn_reset = Button(
            pygame.Rect(self.rect.left + 302, y, 86, h),
            text="RESET",
            icon_type="reset",
            callback=self.controller.reset_all,
            hover_color=COLOR_CRITICAL_BG,
        )

        # Demo Mode switch
        self.btn_demo_mode = Button(
            pygame.Rect(self.rect.left + 396, y, 138, h),
            text="DAA DEMO MODE",
            callback=self.controller.toggle_demo_mode,
            is_active=self.controller.is_demo_mode,
        )

        # Speed toggles
        speed_x = self.rect.left + 544
        self.btn_speed_slow = Button(
            pygame.Rect(speed_x, y, 52, h),
            text="SLOW",
            callback=lambda: self.controller.set_speed("SLOW"),
        )
        self.btn_speed_med = Button(
            pygame.Rect(speed_x + 58, y, 52, h),
            text="MED",
            callback=lambda: self.controller.set_speed("MEDIUM"),
        )
        self.btn_speed_fast = Button(
            pygame.Rect(speed_x + 116, y, 52, h),
            text="FAST",
            callback=lambda: self.controller.set_speed("FAST"),
        )

        # Exit
        self.btn_exit = Button(
            pygame.Rect(self.rect.right - 90, y, 76, h),
            text="EXIT",
            icon_type="exit",
            callback=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
            hover_color=COLOR_CRITICAL_BG,
        )

        self.buttons = [
            self.btn_play_pause,
            self.btn_prev,
            self.btn_next,
            self.btn_reset,
            self.btn_demo_mode,
            self.btn_speed_slow,
            self.btn_speed_med,
            self.btn_speed_fast,
            self.btn_exit,
        ]

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=0)

        # Update button text & active states dynamically
        self.btn_play_pause.text = "PAUSE" if self.controller.is_playing else "PLAY"
        self.btn_play_pause.icon_type = "pause" if self.controller.is_playing else "play"
        self.btn_demo_mode.is_active = self.controller.is_demo_mode

        self.btn_speed_slow.is_active = (self.controller.speed == "SLOW")
        self.btn_speed_med.is_active = (self.controller.speed == "MEDIUM")
        self.btn_speed_fast.is_active = (self.controller.speed == "FAST")

        for btn in self.buttons:
            btn.draw(surface)

        # Keyboard helper caption
        kb_font = FontManager.get(10)
        kb_text = "KEYS: [SPACE] Pause/Play | [->] Next | [<-] Prev | [R] Reset | [ESC] Exit"
        kb_surf = kb_font.render(kb_text, True, COLOR_TEXT_MUTED)
        surface.blit(kb_surf, (self.rect.left + 725, self.rect.top + 22))


# -------------------------------------------------------------
# RIGHT SIDE INFORMATION PANEL (DAA ACADEMIC HUD - LIGHT THEME)
# -------------------------------------------------------------
class RightPanel:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    def draw(
        self,
        surface: pygame.Surface,
        scene_id: int,
        state: Optional[AlgorithmState],
        total_comps: int,
        total_merges: int,
        areas_count: int = 20,
    ):
        draw_rounded_panel(surface, self.rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8)

        # Section 1: Header
        h_font = FontManager.get(13, bold=True)
        header_surf = h_font.render("ALGORITHM EXPLANATION & HUD", True, COLOR_TEXT_PRIMARY)
        surface.blit(header_surf, (self.rect.left + 16, self.rect.top + 14))
        pygame.draw.line(
            surface,
            COLOR_BORDER_LIGHT,
            (self.rect.left + 14, self.rect.top + 36),
            (self.rect.right - 14, self.rect.top + 36),
            1,
        )

        y = self.rect.top + 46

        # Section 2: Current Operation Box
        op_rect = pygame.Rect(self.rect.left + 14, y, self.rect.width - 28, 64)
        draw_rounded_panel(surface, op_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        lbl_font = FontManager.get(10, bold=True)
        lbl_surf = lbl_font.render("CURRENT OPERATION", True, COLOR_TEXT_SECONDARY)
        surface.blit(lbl_surf, (op_rect.left + 10, op_rect.top + 8))

        # Context-aware operation title and color
        if scene_id == 0:  # INTRO
            op_name = "SYSTEM INITIALIZATION"
            op_color = COLOR_ACCENT
            op_bg = COLOR_ACCENT_LIGHT
        elif scene_id == 1:  # FLOOD MAP
            op_name = "TELEMETRY MONITORING"
            op_color = COLOR_ACCENT
            op_bg = COLOR_ACCENT_LIGHT
        elif scene_id == 2:  # SCAN
            op_name = "SENSOR TELEMETRY SCAN"
            op_color = COLOR_ACCENT
            op_bg = COLOR_ACCENT_LIGHT
        elif scene_id == 3:  # INPUT
            op_name = "ARRAY INITIALIZATION"
            op_color = COLOR_ACCENT
            op_bg = COLOR_ACCENT_LIGHT
        elif scene_id == 4:  # DIVIDE
            op_name = "DIVIDE AND CONQUER"
            op_color = (124, 58, 237)
            op_bg = (237, 233, 254)
        elif scene_id == 5:  # COMPARE & MERGE
            if state and state.op_type == "COMPARE":
                op_name = "COMPARING WATER LEVELS"
                op_color = COLOR_COMPARE
                op_bg = COLOR_COMPARE_BG
            elif state and state.op_type == "SELECT":
                op_name = "SELECTING HIGHER LEVEL"
                op_color = COLOR_SELECTED
                op_bg = COLOR_SELECTED_BG
            elif state and "MERGE" in state.op_type:
                op_name = "MERGING INTO BUFFER"
                op_color = COLOR_ACCENT
                op_bg = COLOR_ACCENT_LIGHT
            else:
                op_name = "MERGE SORT OPERATIONS"
                op_color = COLOR_ACCENT
                op_bg = COLOR_ACCENT_LIGHT
        elif scene_id == 6:  # SORTED RESULT
            op_name = "MERGE SORT COMPLETE"
            op_color = COLOR_LOW
            op_bg = COLOR_LOW_BG
        elif scene_id == 7:  # EVACUATION
            op_name = "PRIORITY RESCUE DISPATCH"
            op_color = COLOR_CRITICAL
            op_bg = COLOR_CRITICAL_BG
        else:  # ANALYSIS
            op_name = "COMPLEXITY VALIDATION"
            op_color = COLOR_ACCENT
            op_bg = COLOR_ACCENT_LIGHT

        draw_badge(surface, op_name, op_rect.left + 10, op_rect.top + 28, op_color, op_bg, size=11)
        y += 76

        # Section 3: Pointer HUD & Active Comparison Box
        comp_rect = pygame.Rect(self.rect.left + 14, y, self.rect.width - 28, 126)
        draw_rounded_panel(surface, comp_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        c_lbl = lbl_font.render("MERGE OPERATION & POINTERS" if scene_id == 5 else "STAGE METRICS & STATUS", True, COLOR_TEXT_SECONDARY)
        surface.blit(c_lbl, (comp_rect.left + 10, comp_rect.top + 8))

        f_val = FontManager.get(11, bold=True)
        f_norm = FontManager.get(11)

        if scene_id == 5 and state and state.comp_left_val is not None and state.comp_right_val is not None:
            l_item = state.left_sub[state.curr_left_idx] if state.curr_left_idx is not None and state.curr_left_idx < len(state.left_sub) else None
            r_item = state.right_sub[state.curr_right_idx] if state.curr_right_idx is not None and state.curr_right_idx < len(state.right_sub) else None

            # Left pointer
            l_str = f"Left pointer:   {l_item.area_id} -> {state.comp_left_val:.1f} m" if l_item else "Left pointer:  -"
            surface.blit(f_norm.render(l_str, True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 30))

            # Right pointer
            r_str = f"Right pointer: {r_item.area_id} -> {state.comp_right_val:.1f} m" if r_item else "Right pointer: -"
            surface.blit(f_norm.render(r_str, True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 50))

            # Inequality decision
            op_sym = ">=" if state.comp_left_val >= state.comp_right_val else "<"
            ineq_str = f"Comparison: {state.comp_left_val:.1f} m {op_sym} {state.comp_right_val:.1f} m"
            surface.blit(f_val.render(ineq_str, True, COLOR_COMPARE), (comp_rect.left + 10, comp_rect.top + 72))

            # Selected result
            if state.selected_item:
                sel_str = f"Selected: {state.selected_item.name} ({state.selected_item.water_level:.1f} m)"
                surface.blit(f_val.render(sel_str, True, COLOR_SELECTED), (comp_rect.left + 10, comp_rect.top + 94))
        else:
            if scene_id == 4:
                surface.blit(f_norm.render("Divide Phase: Splitting array", True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 30))
                surface.blit(f_val.render("20 -> 10,10 -> 5,5,5,5 -> Base", True, COLOR_ACCENT), (comp_rect.left + 10, comp_rect.top + 52))
                surface.blit(f_norm.render("Recursing to 1-element arrays", True, COLOR_TEXT_MUTED), (comp_rect.left + 10, comp_rect.top + 74))
            elif scene_id == 6:
                surface.blit(f_val.render("All 20 sectors sorted descending", True, COLOR_SELECTED), (comp_rect.left + 10, comp_rect.top + 30))
                surface.blit(f_norm.render("Highest water level at Rank #1", True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 52))
                surface.blit(f_val.render("Triage categories: Critical -> Low", True, COLOR_CRITICAL), (comp_rect.left + 10, comp_rect.top + 74))
            elif scene_id == 7:
                surface.blit(f_val.render("Active Rescue Fleet: Dispatched", True, COLOR_CRITICAL), (comp_rect.left + 10, comp_rect.top + 30))
                surface.blit(f_norm.render("Target: Central Relief Shelter", True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 52))
                surface.blit(f_val.render("Order: Priority #1 to #5", True, COLOR_LOW), (comp_rect.left + 10, comp_rect.top + 74))
            elif scene_id == 8:
                surface.blit(f_val.render("Master Theorem: Case 2 Applied", True, COLOR_SELECTED), (comp_rect.left + 10, comp_rect.top + 30))
                surface.blit(f_norm.render("T(n) = 2T(n/2) + O(n) => Θ(n log n)", True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 52))
                surface.blit(f_val.render("Auxiliary Space: O(n) Buffer", True, COLOR_ACCENT), (comp_rect.left + 10, comp_rect.top + 74))
            else:
                surface.blit(f_norm.render(f"Monitored sectors: {areas_count} areas", True, COLOR_TEXT_PRIMARY), (comp_rect.left + 10, comp_rect.top + 30))
                surface.blit(f_val.render("Data Source: flood_areas.csv", True, COLOR_ACCENT), (comp_rect.left + 10, comp_rect.top + 52))
                surface.blit(f_norm.render("Status: Telemetry Ready", True, COLOR_TEXT_MUTED), (comp_rect.left + 10, comp_rect.top + 74))

        y += 138

        # Section 4: "WHY THIS HAPPENS?" Academic Explanation Box
        why_rect = pygame.Rect(self.rect.left + 14, y, self.rect.width - 28, 120)
        draw_rounded_panel(surface, why_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        w_lbl = lbl_font.render("WHY THIS HAPPENS (DAA INSIGHT)", True, COLOR_ACCENT)
        surface.blit(w_lbl, (why_rect.left + 10, why_rect.top + 8))

        if scene_id == 4:
            why_text = "Merge Sort divides the array into smaller subarrays before sorting them. Halving continues until single-element arrays remain."
        elif scene_id == 5 and state and state.why_text:
            why_text = state.why_text
        elif scene_id == 6:
            why_text = "Descending sort places sectors with the deepest water levels first so rescue authorities can prioritize the most critical lives first."
        elif scene_id == 7:
            why_text = "Evacuation vehicles are dispatched strictly according to the sorted Merge Sort output to maximize lives saved under resource limits."
        elif scene_id == 8:
            why_text = "Master Theorem: T(n) = 2T(n/2) + O(n). Here a=2, b=2, and f(n)=O(n). Since n^(log₂2) = n and f(n) = Θ(n^(log₂2)), Master Theorem Case 2 applies: T(n) = Θ(n log n). Auxiliary space is O(n)."
        else:
            why_text = "In emergency flood triage, algorithm sorting provides an automated, unbiased ranking based on sensor depth readings."

        f_why = FontManager.get(11)
        words = why_text.split()
        lines = []
        cur_line = []
        max_w = why_rect.width - 20

        for word in words:
            cur_line.append(word)
            test_w = f_why.size(" ".join(cur_line))[0]
            if test_w > max_w:
                cur_line.pop()
                lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

        line_y = why_rect.top + 28
        for line in lines[:4]:
            surface.blit(f_why.render(line, True, COLOR_TEXT_PRIMARY), (why_rect.left + 10, line_y))
            line_y += 18

        y += 132

        # Section 5: Phase Progress Indicator
        pipe_rect = pygame.Rect(self.rect.left + 14, y, self.rect.width - 28, 52)
        draw_rounded_panel(surface, pipe_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        steps = ["DIVIDE", "COMPARE", "SELECT", "MERGE"]
        if scene_id == 4:
            cur_step = "DIVIDE"
        elif scene_id == 5 and state:
            if state.op_type == "DIVIDE":
                cur_step = "DIVIDE"
            elif state.op_type == "COMPARE":
                cur_step = "COMPARE"
            elif state.op_type == "SELECT":
                cur_step = "SELECT"
            else:
                cur_step = "MERGE"
        elif scene_id >= 6:
            cur_step = "MERGE"
        else:
            cur_step = "DIVIDE"

        p_font = FontManager.get(10, bold=True)
        step_w = (pipe_rect.width - 20) // 4

        for idx, s_name in enumerate(steps):
            sx = pipe_rect.left + 10 + idx * step_w
            is_active_step = (s_name == cur_step)
            pill_rect = pygame.Rect(sx, pipe_rect.top + 14, step_w - 4, 24)

            if is_active_step:
                pygame.draw.rect(surface, COLOR_ACCENT, pill_rect, border_radius=4)
                surface.blit(p_font.render(s_name, True, (255, 255, 255)), (sx + 4, pipe_rect.top + 18))
            else:
                pygame.draw.rect(surface, (255, 255, 255), pill_rect, border_radius=4)
                pygame.draw.rect(surface, COLOR_BORDER_LIGHT, pill_rect, width=1, border_radius=4)
                surface.blit(p_font.render(s_name, True, COLOR_TEXT_MUTED), (sx + 4, pipe_rect.top + 18))

        y += 62

        # Section 6: Live Algorithm Statistics
        stat_rect = pygame.Rect(self.rect.left + 14, y, self.rect.width - 28, 86)
        draw_rounded_panel(surface, stat_rect, bg_color=COLOR_PANEL_ALT, border_color=COLOR_BORDER_LIGHT, radius=6)

        stat_lbl = lbl_font.render("LIVE RUNTIME METRICS", True, COLOR_TEXT_SECONDARY)
        surface.blit(stat_lbl, (stat_rect.left + 10, stat_rect.top + 6))

        s_font = FontManager.get(11)
        val_font = FontManager.get(11, bold=True)

        curr_comps = state.comparisons_so_far if state else 0
        curr_merges = state.merges_so_far if state else 0
        depth = state.depth if state else 0

        surface.blit(s_font.render("Comparisons Done:", True, COLOR_TEXT_PRIMARY), (stat_rect.left + 10, stat_rect.top + 24))
        surface.blit(val_font.render(f"{curr_comps} / {total_comps}", True, COLOR_COMPARE), (stat_rect.right - 70, stat_rect.top + 24))

        surface.blit(s_font.render("Merges Completed:", True, COLOR_TEXT_PRIMARY), (stat_rect.left + 10, stat_rect.top + 42))
        surface.blit(val_font.render(f"{curr_merges} / {total_merges}", True, COLOR_ACCENT), (stat_rect.right - 70, stat_rect.top + 42))

        surface.blit(s_font.render("Recursion Tree Depth:", True, COLOR_TEXT_PRIMARY), (stat_rect.left + 10, stat_rect.top + 60))
        surface.blit(val_font.render(f"Level {depth}", True, COLOR_SELECTED), (stat_rect.right - 70, stat_rect.top + 60))
