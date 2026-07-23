import flet as ft
import random
import asyncio

# UI CONSTANTS - MATCHING REFERENCE
BACKGROUND_COLOR = "#0D1117"  # Deep dark navy/black
GLASS_COLOR = ft.Colors.with_opacity(0.12, ft.Colors.WHITE)
GLASS_BORDER_COLOR = ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
ACCENT_COLOR = "#38BDF8"       # Soft blue
SUCCESS_COLOR = "#A5C9FF"      # Light blue for buttons from image
DANGER_COLOR = "#EF4444"       # Red for trash/reset
SECONDARY_TEXT = "#8B949E"     # Muted gray

# GLASS STYLE FOR CARDS - APPLE INSPIRED
GLASS_STYLE = {
    "bgcolor": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
    "border": ft.Border.all(0.5, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
    "border_radius": 20,
    "blur": ft.Blur(20, 20, ft.BlurStyle.NORMAL),
}

class AnimatedBackground(ft.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blobs = []
        self.expand = True

    def did_mount(self):
        self.page.run_task(self.animate_blobs)

    def change_accent(self, color):
        """Update blob colors to match the new accent."""
        # Create a palette based on the chosen color
        # In a real HSV case we'd shift hue, but for simplicity we'll use opacity/shades
        for blob in self.blobs:
            blob.bgcolor = color
            blob.update()

    async def animate_blobs(self):
        colors = ["#1E293B", "#0F172A", "#1E3A8A", "#172554"]
        for _ in range(4):
            blob = ft.Container(
                width=600,
                height=600,
                bgcolor=random.choice(colors),
                border_radius=300,
                blur=ft.Blur(150, 150, ft.BlurStyle.NORMAL),
                opacity=0.08,
                offset=ft.Offset(random.uniform(-0.5, 1.5), random.uniform(-0.5, 1.5)),
                animate_offset=ft.Animation(40000, ft.AnimationCurve.EASE_IN_OUT),
            )
            self.blobs.append(blob)
            self.controls.append(blob)
        
        self.update()

        while True:
            for blob in self.blobs:
                blob.offset = ft.Offset(random.uniform(-0.5, 1.5), random.uniform(-0.5, 1.5))
            if self.page:
                self.update()
            await asyncio.sleep(40)

def glass_card(content, padding=20):
    return ft.Container(
        content=content,
        padding=padding,
        **GLASS_STYLE
    )
