import flet as ft
import asyncio
import math
import colorsys
from database import Database
from theme import AnimatedBackground, BACKGROUND_COLOR, GLASS_COLOR, SUCCESS_COLOR, SECONDARY_TEXT, DANGER_COLOR, ACCENT_COLOR
from item_card import ItemCard

class PriceSaverApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Smart Price Saver"
        self.page.bgcolor = BACKGROUND_COLOR
        self.page.padding = 0
        self.db = Database()
        self.page.snack_bar = ft.SnackBar(ft.Text(""))
        
        # State
        self.items = []
        self.is_history_view = False
        self.is_dark_mode = True
        self.current_accent_color = ACCENT_COLOR  # Track current theme color
        
        # Scrollable View
        self.content_column = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # UI Components
        self.setup_ui()

    def setup_ui(self):
        # Header (Top Bar)
        self.header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(ft.Icons.PALETTE_OUTLINED, icon_color=ft.Colors.WHITE, on_click=self.open_theme_menu, icon_size=22),
                ], spacing=0),
                ft.Text("Smart Price Saver", size=20, weight="bold", color=ft.Colors.WHITE, expand=True, text_align="center"),
                ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED if not self.is_dark_mode else ft.Icons.DARK_MODE_OUTLINED, 
                            icon_color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE), 
                            icon_size=22,
                            on_click=self.toggle_theme_mode),
            ], alignment="spaceBetween"),
            padding=ft.Padding.only(left=10, top=10, right=20, bottom=10),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            blur=ft.Blur(10, 10, ft.BlurStyle.NORMAL),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)))
        )

        # Global Controls Row (Unit, Currency, Reset)
        self.unit_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("g"), ft.dropdown.Option("kg"), ft.dropdown.Option("ml"), ft.dropdown.Option("L")],
            value="g",
            width=80, height=35,
            text_size=12,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_radius=8,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.Padding.only(left=10, top=0, right=10, bottom=0),
            on_select=self.on_global_change
        )
        self.currency_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("Rs"), ft.dropdown.Option("$"), ft.dropdown.Option("€")],
            value="Rs",
            width=80, height=35,
            text_size=12,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_radius=8,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.Padding.only(left=10, top=0, right=10, bottom=0),
            on_select=self.on_global_change
        )
        self.reset_btn = ft.Container(
            content=ft.IconButton(ft.Icons.RESTART_ALT_ROUNDED, icon_color=ft.Colors.WHITE, on_click=self.reset_app, icon_size=18),
            width=35, height=35,
            bgcolor="#EF4444", # Red reset button
            border_radius=18,
            alignment=ft.Alignment(0, 0)
        )

        self.sub_header = ft.Container(
            content=ft.Row([
                ft.Text("Compare Deals", size=16, weight="bold", color="#A5C9FF"),
                ft.Row([
                    ft.Column([ft.Text("Unit", size=10, color=SECONDARY_TEXT), self.unit_dropdown], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([ft.Text("Currency", size=10, color=SECONDARY_TEXT), self.currency_dropdown], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    self.reset_btn
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding.only(left=15, top=10, right=15, bottom=10),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            blur=ft.Blur(10, 10, ft.BlurStyle.NORMAL),
            border_radius=12,
            margin=ft.Margin.symmetric(horizontal=10, vertical=5)
        )

        # Footer (Bottom Bar)
        self.add_btn = ft.TextButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD, size=18, color="#A5C9FF"), ft.Text("Add New Item", color=ft.Colors.WHITE, size=14)], spacing=5),
            on_click=self.add_item
        )
        
        self.compare_btn_inner = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=18, color="white"), ft.Text("Compare Prices", size=14, weight="bold", color="white")], alignment="center"),
            padding=ft.Padding.only(left=20, top=10, right=20, bottom=10),
            bgcolor="#7EA7FF",
            border_radius=12,
            on_click=self.compare_action
        )

        self.footer = ft.Container(
            content=ft.Row([
                self.add_btn,
                self.compare_btn_inner,
                ft.Container(width=50) # Spacer
            ], alignment="spaceBetween"),
            padding=ft.Padding.only(left=20, top=15, right=20, bottom=15),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            blur=ft.Blur(15, 15, ft.BlurStyle.NORMAL),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)))
        )

        # Empty State
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SHOPPING_BASKET_OUTLINED, size=64, color=SECONDARY_TEXT, opacity=0.3),
                ft.Text("Add products to compare\nand find the best value.", 
                        color=SECONDARY_TEXT, text_align="center"),
            ], horizontal_alignment="center"),
            expand=True,
            alignment=ft.Alignment(0, 0),
            visible=True
        )

        # Theme Menu Layer (Visible/Hidden)
        self.theme_menu_presets = [
            ("#38BDF8", "#38BDF8", "Ocean"),
            ("#A855F7", "#A855F7", "Royal"),
            ("#10B981", "#10B981", "Nature"),
            ("#F59E0B", "#F59E0B", "Sunny"),
            ("#F43F5E", "#F43F5E", "Love"),
            ("#6366F1", "#6366F1", "Indigo"),
            ("#EF4444", "#EF4444", "Fire"),
            ("#F97316", "#F97316", "Orange"),
            ("#E9D5FF", "#E9D5FF", "Lavender"),
            ("#14B8A6", "#14B8A6", "Teal"),
            ("#EC4899", "#EC4899", "Pink"),
            ("#8B5CF6", "#8B5CF6", "Violet"),
            ("#06B6D4", "#06B6D4", "Cyan"),
            ("#84CC16", "#84CC16", "Lime"),
            ("#FBBF24", "#FBBF24", "Amber"),
            ("#EAB308", "#EAB308", "Yellow"),
            ("#22C55E", "#22C55E", "Green"),
            ("#3B82F6", "#3B82F6", "Blue"),
            ("#000000", "black", "Midnight"),
            ("#FFFFFF", "white", "Bright"),
        ]
        
        def on_preset_click(c, n):
            print(f"[SmartPriceSaver] CLICKED: {n} ({c})")
            self.set_app_accent(c)
            self.theme_menu_layer.visible = False
            self.page.update()

        self.theme_menu_box = ft.Container(
            content=ft.Column([
                ft.Text("Theme Presets", weight="bold", size=16, color=ft.Colors.WHITE),
                ft.Row([
                    ft.GestureDetector(
                        content=ft.Container(
                            width=35, height=35,
                            bgcolor=color[1],
                            border_radius=18,
                            border=ft.Border.all(2, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                            tooltip=color[2],
                            animate=ft.Animation(200, "bounceOut")
                        ),
                        on_tap=lambda _, c=color[0], n=color[2]: on_preset_click(c, n)
                    ) for color in self.theme_menu_presets
                ], spacing=12, wrap=True),
            ], tight=True, spacing=20),
            padding=25,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            blur=ft.Blur(15, 15, ft.BlurStyle.NORMAL),
            border_radius=25,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            width=320,
            shadow=ft.BoxShadow(blur_radius=50, color=ft.Colors.BLACK)
        )

        self.theme_menu_layer = ft.Container(
            content=ft.Stack([
                ft.GestureDetector(
                    content=ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                    on_tap=lambda _: (setattr(self.theme_menu_layer, 'visible', False), self.page.update())
                ),
                ft.Container(
                    content=self.theme_menu_box,
                    alignment=ft.Alignment(-1, -1), # top_left
                    padding=ft.Padding.only(left=20, top=70)
                )
            ]),
            visible=False,
            expand=True
        )

        # Main Layout
        self.bg = AnimatedBackground(expand=True)
        self.page.add(
            ft.Stack([
                self.bg,
                ft.Column([
                    self.header,
                    self.sub_header,
                    ft.Container(
                        content=ft.Stack([
                            self.content_column,
                            self.empty_state
                        ]),
                        expand=True,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=0) 
                    ),
                    self.footer
                ], expand=True, spacing=0),
                self.theme_menu_layer,
                # Floating History Button (Bottom Right)
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.HISTORY_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        icon_size=28,
                        on_click=self.toggle_history,
                        tooltip="View History"
                    ),
                    width=60, height=60,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                    blur=ft.Blur(15, 15, ft.BlurStyle.NORMAL),
                    border_radius=30,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        spread_radius=0,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                        offset=ft.Offset(0, 4)
                    ),
                    right=20,
                    bottom=100,
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
                ),
            ], expand=True)
        )
        
        # Initial Item
        self.add_item(None)

    def add_item(self, e):
        if self.is_history_view:
            self.toggle_history(None)
            
        new_item = ItemCard(
            index=len(self.items),
            on_delete=self.delete_item,
            on_change=self.on_item_change,
            initial_unit=self.unit_dropdown.value,
            initial_currency=self.currency_dropdown.value
        )
        
        self.items.append(new_item)
        self.content_column.controls.append(new_item)
        self.update_states()
        self.page.update()
        
        # Apply current accent color to the new item after it's on the page
        new_item.update_accent(self.current_accent_color)

    def delete_item(self, item_to_delete):
        """Ultra-stable deletion using page.overlay instead of page.dialog."""
        print(f"[SmartPriceSaver] START delete_item for index {item_to_delete.index}")
        
        # 1. Clear any existing overlays to prevent "stuck" dialogs
        self.page.overlay.clear()

        def confirm_delete(e):
            print("[SmartPriceSaver] confirm_delete callback triggered")
            try:
                # Remove from tracking lists
                if item_to_delete in self.items:
                    self.items.remove(item_to_delete)
                
                # Re-build content column to be 100% sure the UI is in sync
                self.content_column.controls.clear()
                for i, itm in enumerate(self.items):
                    itm.update_index(i)
                    self.content_column.controls.append(itm)
                
                self.update_states()
                self.page.overlay.clear() # Close dialog
                
                # Success Indicator
                self.page.snack_bar = ft.SnackBar(ft.Text("Successfully Removed"), bgcolor=ft.Colors.GREEN_400)
                self.page.snack_bar.open = True
                self.page.update()
                print("[SmartPriceSaver] Deletion successful and UI refreshed")
            except Exception as ex:
                print(f"[SmartPriceSaver] Error in confirm_delete: {ex}")

        # Create dialog manually as a Container to be in overlay
        dialog_box = ft.Container(
            content=ft.Column([
                ft.Text("Remove Item?", size=18, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Are you sure you want to delete this product?", color=SECONDARY_TEXT),
                ft.Row([
                    ft.TextButton("No", on_click=lambda _: (self.page.overlay.clear(), self.page.update())),
                    ft.ElevatedButton("Yes, Remove", on_click=confirm_delete, bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ], tight=True, spacing=20),
            padding=20,
            bgcolor="#1C1F26",
            border_radius=15,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            width=300,
        )
        
        overlay_mask = ft.Container(
            content=dialog_box,
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
            expand=True,
            on_click=lambda _: (self.page.overlay.clear(), self.page.update()) # Dismiss on click outside
        )
        
        self.page.overlay.append(overlay_mask)
        self.page.update()
        print("[SmartPriceSaver] Custom Overlay Dialog shown")

    async def on_item_change(self, e):
        # Reset ranking when input changes
        for itm in self.items:
            await itm.set_rank(itm.index + 1, False)
        self.page.update()

    def update_states(self):
        self.empty_state.visible = len(self.items) == 0 and not self.is_history_view
        self.footer.visible = not self.is_history_view
        
    def reset_app(self, e):
        self.items.clear()
        self.content_column.controls.clear()
        self.add_item(None)
        self.page.update()

    def on_global_change(self, e):
        # Update symbols on all existing items
        for itm in self.items:
            itm.update_symbols(self.unit_dropdown.value, self.currency_dropdown.value)
        self.page.update()

    def toggle_history(self, e):
        self.is_history_view = not self.is_history_view
        # Clear any active overlays when switching views
        self.page.overlay.clear()
        if self.is_history_view:
            self.show_history()
        else:
            self.show_calculator()
        self.page.update()

    def show_calculator(self):
        self.content_column.controls.clear()
        for itm in self.items:
            self.content_column.controls.append(itm)
        
        self.header.content.controls[1].value = "Smart Price Saver"
        self.header.content.controls[2].visible = True # Theme icon
        self.sub_header.visible = True
        self.update_states()
        
    def show_history(self):
        self.content_column.controls.clear()
        self.header.content.controls[1].value = "History"
        
        # Replace Palette icon with Clear All in history view
        self.header.content.controls[2] = ft.IconButton(
            ft.Icons.DELETE_SWEEP, 
            icon_color=DANGER_COLOR, 
            on_click=self.clear_history_ui,
            tooltip="Clear All History"
        )
        
        self.sub_header.visible = False
        self.footer.visible = False
        self.empty_state.visible = False
        
        history_entries = self.db.get_history()
        if not history_entries:
            self.content_column.controls.append(
                ft.Container(
                    content=ft.Text("No comparisons yet.", color=SECONDARY_TEXT),
                    margin=ft.Margin.only(top=100)
                )
            )
        else:
            for entry in history_entries:
                self.content_column.controls.append(self.create_history_tile(entry))
        
    def create_history_tile(self, entry):
        # Simplified tile to avoid event conflicts or ListTile issues in 0.80.x
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Comparison: {entry['timestamp']}", color=ft.Colors.WHITE, size=14, weight="bold"),
                        ft.Text(f"{entry['item_count']} items", color=SECONDARY_TEXT, size=12),
                    ], spacing=2),
                    on_click=lambda _: self.show_history_detail(entry['id'], entry['timestamp']),
                    expand=True,
                    padding=10
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_300,
                    on_click=lambda _: self.delete_history_entry_ui(entry['id']),
                    icon_size=20,
                )
            ], alignment="spaceBetween"),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=12,
            margin=ft.Margin.only(bottom=5)
        )

    def show_history_detail(self, history_id, timestamp):
        details = self.db.get_history_details(history_id)
        
        # Ensure only one detail view is open
        self.page.overlay.clear()

        def close_detail(_):
            self.page.overlay.clear()
            self.page.update()

        items_list = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10, expand=True)
        for d in details:
            best_mark = "🏆 BEST VALUE" if d['is_best_value'] else ""
            items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Rank {d['rank']}", weight="bold", color=SUCCESS_COLOR if d['is_best_value'] else ft.Colors.WHITE),
                            ft.Text(best_mark, size=10, weight="bold", color=SUCCESS_COLOR)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(d['name'], size=16, weight="w500", color=ft.Colors.WHITE),
                        ft.Row([
                            ft.Column([
                                ft.Text("Weight", size=9, color=SECONDARY_TEXT),
                                ft.Text(f"{d['weight']} {d['unit']}", color=ft.Colors.WHITE, size=12),
                            ], spacing=1),
                            ft.Column([
                                ft.Text("Price", size=9, color=SECONDARY_TEXT),
                                ft.Text(f"{d['currency']}{d['price']}", color=ft.Colors.WHITE, size=12),
                            ], spacing=1),
                            ft.Column([
                                ft.Text("Qty", size=9, color=SECONDARY_TEXT),
                                ft.Text(f"x{d['quantity']}", color=ft.Colors.WHITE, size=12),
                            ], spacing=1),
                        ], spacing=15),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
                        ft.Text(f"Unit Price: {d['currency']}{d['unit_price']:.4f}/{d['unit']}", size=11, color=ACCENT_COLOR, weight="bold")
                    ], spacing=5),
                    padding=12,
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE) if d['is_best_value'] else ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.2, SUCCESS_COLOR)) if d['is_best_value'] else None
                )
            )

        overlay_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=ft.Colors.WHITE, on_click=close_detail, icon_size=18),
                    ft.Text(f"Comparison Details", color=ft.Colors.WHITE, weight="bold", size=16),
                ], alignment="start"),
                ft.Text(f"{timestamp}", color=SECONDARY_TEXT, size=12, margin=ft.Margin.only(left=45, top=-10, bottom=10)),
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                ft.Container(content=items_list, expand=True, padding=ft.Padding.only(top=10))
            ], expand=True),
            bgcolor=BACKGROUND_COLOR,
            padding=15,
            expand=True,
            top=0, left=0, right=0, bottom=0,
        )
        
        self.page.overlay.append(overlay_container)
        self.page.update()

    def delete_history_entry_ui(self, history_id):
        print(f"[SmartPriceSaver] History delete for ID: {history_id}")
        self.page.overlay.clear()

        def confirm_h_delete(e):
            self.db.delete_history_entry(history_id)
            self.show_history()
            self.page.overlay.clear()
            self.page.update()

        h_dialog = ft.Container(
            content=ft.Column([
                ft.Text("Delete Entry?", size=18, color=ft.Colors.WHITE, weight="bold"),
                ft.Row([
                    ft.TextButton("No", on_click=lambda _: (self.page.overlay.clear(), self.page.update())),
                    ft.ElevatedButton("Delete", on_click=confirm_h_delete, bgcolor=ft.Colors.RED_400),
                ], alignment="end")
            ], tight=True),
            padding=20, bgcolor="#1C1F26", border_radius=15, width=300
        )
        
        self.page.overlay.append(ft.Container(content=h_dialog, alignment=ft.Alignment(0,0), expand=True, bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK), on_click=lambda _: (self.page.overlay.clear(), self.page.update())))
        self.page.update()

    def clear_history_ui(self, e):
        print("[SmartPriceSaver] Clear all history requested")
        self.page.overlay.clear()

        def confirm_clear_all(e):
            self.db.clear_history()
            self.show_history()
            self.page.overlay.clear()
            self.page.update()

        c_dialog = ft.Container(
            content=ft.Column([
                ft.Text("Clear All?", size=18, color=ft.Colors.WHITE, weight="bold"),
                ft.Text("This will wipe your entire history.", color=SECONDARY_TEXT),
                ft.Row([
                    ft.TextButton("Cancel", on_click=lambda _: (self.page.overlay.clear(), self.page.update())),
                    ft.ElevatedButton("Clear All", on_click=confirm_clear_all, bgcolor="red400"),
                ], alignment="end")
            ], tight=True),
            padding=20, bgcolor="#1C1F26", border_radius=15, width=300
        )
        
        self.page.overlay.append(ft.Container(content=c_dialog, alignment=ft.Alignment(0,0), expand=True, bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK), on_click=lambda _: (self.page.overlay.clear(), self.page.update())))
        self.page.update()

    def open_theme_menu(self, e):
        """Toggles the direct Stack-based theme menu."""
        print("[SmartPriceSaver] open_theme_menu TOGGLE")
        self.theme_menu_layer.visible = not self.theme_menu_layer.visible
        self.page.update()

    def set_app_accent(self, color):
        """Core sync engine with explicit component updates."""
        print(f"[SmartPriceSaver] APPLYING ACCENT: {color}")
        try:
            if color == "white": color = "#FFFFFF"
            if color == "black": color = "#000000"

            # 1. Background
            if self.bg:
                self.bg.change_accent(color)
            
            # 2. Compare Button
            if self.compare_btn_inner:
                self.compare_btn_inner.bgcolor = color
                # High-contrast auto-tint
                text_color = ft.Colors.BLACK if color.lower() in ["white", "#ffffff", "#fffdd0", "#fefae0"] else ft.Colors.WHITE
                self.compare_btn_inner.content.controls[0].color = text_color
                self.compare_btn_inner.content.controls[1].color = text_color
                self.compare_btn_inner.update()
            
            # 3. Icons and Headlines
            self.add_btn.content.controls[0].color = color
            self.add_btn.update()
            
            self.sub_header.content.controls[0].color = color
            self.sub_header.update()
            
            # 4. Sync all items
            for itm in self.items:
                itm.update_accent(color)
            
            # 5. Save current accent color
            self.current_accent_color = color

            # 5. Feedback
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Vibe set to: {color}"), duration=1000)
            self.page.snack_bar.open = True
            
            self.page.update()
        except Exception as ex:
            print(f"[SmartPriceSaver] set_app_accent ERROR: {ex}")

    def toggle_history(self, e):
        """Toggle between calculator and history view."""
        if self.is_history_view:
            self.show_calculator()
        else:
            self.show_history()

    def show_history(self):
        """Display history page."""
        self.is_history_view = True
        
        # Hide calculator components
        self.sub_header.visible = False
        self.content_column.visible = False
        self.empty_state.visible = False
        self.footer.visible = False
        
        # Create history view
        history_data = self.db.get_history()
        
        if not history_data:
            history_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY, size=80, color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                    ft.Text("No History Yet", size=24, weight="bold", color=ft.Colors.WHITE),
                    ft.Text("Complete comparisons to see them here", size=14, color=SECONDARY_TEXT),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        else:
            history_tiles = [self.create_history_tile(h) for h in history_data]
            
            history_content = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Comparison History", size=20, weight="bold", color=ft.Colors.WHITE),
                            ft.IconButton(
                                ft.Icons.DELETE_SWEEP,
                                icon_color=ft.Colors.with_opacity(0.7, ft.Colors.RED),
                                on_click=self.clear_history_ui,
                                tooltip="Clear All History"
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15
                    ),
                    ft.Column(history_tiles, spacing=10, scroll=ft.ScrollMode.ADAPTIVE),
                ], spacing=0, expand=True),
                padding=ft.Padding.symmetric(horizontal=10, vertical=0),
                expand=True
            )
        
        # Replace content
        self.page.controls[0].controls[1] = ft.Column([
            self.header,
            history_content
        ], expand=True, spacing=0)
        
        self.page.update()

    def show_calculator(self):
        """Return to calculator view."""
        self.is_history_view = False
        
        # Show calculator components
        self.sub_header.visible = True
        self.content_column.visible = True
        self.empty_state.visible = len(self.items) == 0
        self.footer.visible = True
        
        # Restore original layout
        self.page.controls[0].controls[1] = ft.Column([
            self.header,
            self.sub_header,
            ft.Container(
                content=ft.Stack([
                    self.content_column,
                    self.empty_state
                ]),
                expand=True,
                padding=ft.Padding.symmetric(horizontal=10, vertical=0)
            ),
            self.footer
        ], expand=True, spacing=0)
        
        self.page.update()

    def create_history_tile(self, history_entry):
        """Create a tile for a history entry."""
        timestamp = history_entry['timestamp']
        item_count = history_entry['item_count']
        history_id = history_entry['id']
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Compared {item_count} items", size=15, weight="bold", color=ft.Colors.WHITE),
                    ft.Text(timestamp, size=12, color=SECONDARY_TEXT),
                ], spacing=5),
                ft.Row([
                    ft.IconButton(
                        ft.Icons.VISIBILITY,
                        icon_color=ACCENT_COLOR,
                        on_click=lambda _: self.show_history_detail(history_id),
                        tooltip="View Details"
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=ft.Colors.with_opacity(0.6, ft.Colors.RED),
                        on_click=lambda _: self.delete_history_entry_ui(history_id),
                        tooltip="Delete"
                    ),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
            blur=ft.Blur(15, 15, ft.BlurStyle.NORMAL),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            border_radius=12,
            padding=15,
            margin=ft.Margin.symmetric(horizontal=5, vertical=0)
        )

    def show_history_detail(self, history_id):
        """Show detailed view of a specific comparison."""
        items = self.db.get_history_details(history_id)
        
        detail_cards = []
        for item in items:
            rank_color = SUCCESS_COLOR if item['is_best_value'] else ft.Colors.with_opacity(0.5, ft.Colors.WHITE)
            
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"#{item['rank']}", size=12, weight="bold", color=ft.Colors.WHITE),
                            width=30, height=30,
                            bgcolor=rank_color,
                            border_radius=15,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(item['name'], size=15, weight="bold", color=ft.Colors.WHITE, expand=True),
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    ft.Row([
                        ft.Column([
                            ft.Text("Weight", size=10, color=SECONDARY_TEXT),
                            ft.Text(f"{item['weight']} {item['unit']}", size=13, color=ft.Colors.WHITE),
                        ]),
                        ft.Column([
                            ft.Text("Price", size=10, color=SECONDARY_TEXT),
                            ft.Text(f"{item['currency']} {item['price']}", size=13, color=ft.Colors.WHITE),
                        ]),
                        ft.Column([
                            ft.Text("Qty", size=10, color=SECONDARY_TEXT),
                            ft.Text(str(item['quantity']), size=13, color=ft.Colors.WHITE),
                        ]),
                        ft.Column([
                            ft.Text("Unit Price", size=10, color=SECONDARY_TEXT),
                            ft.Text(f"{item['currency']} {item['unit_price']:.2f}", size=13, color=SUCCESS_COLOR if item['is_best_value'] else ft.Colors.WHITE, weight="bold"),
                        ]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
                blur=ft.Blur(15, 15, ft.BlurStyle.NORMAL),
                border=ft.Border.all(2 if item['is_best_value'] else 1, ft.Colors.with_opacity(0.3 if item['is_best_value'] else 0.2, rank_color if item['is_best_value'] else ft.Colors.WHITE)),
                border_radius=12,
                padding=15,
                margin=ft.Margin.only(bottom=10)
            )
            detail_cards.append(card)
        
        # Show detail view
        detail_view = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: self.show_history(),
                            tooltip="Back"
                        ),
                        ft.Text("Comparison Details", size=18, weight="bold", color=ft.Colors.WHITE, expand=True),
                    ]),
                    padding=10
                ),
                ft.Column(detail_cards, spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True),
            ], spacing=5, expand=True),
            padding=ft.Padding.symmetric(horizontal=10, vertical=0),
            expand=True
        )
        
        self.page.controls[0].controls[1] = ft.Column([
            self.header,
            detail_view
        ], expand=True, spacing=0)
        
        self.page.update()

    def delete_history_entry_ui(self, history_id):
        """Delete a history entry with confirmation."""
        self.db.delete_history_entry(history_id)
        self.show_history()  # Refresh

    def clear_history_ui(self, e):
        """Clear all history with confirmation."""
        self.db.clear_history()
        self.show_history()  # Refresh

    def toggle_theme_mode(self, e):
        """Toggles between Dark and Light background themes."""
        self.is_dark_mode = not self.is_dark_mode
        print(f"[SmartPriceSaver] THEME TOGGLE: {'Dark' if self.is_dark_mode else 'Light'}")
        
        # Determine theme colors
        new_accent = "#38BDF8" if self.is_dark_mode else "#2563EB"
        page_bg = "#0D1117" if self.is_dark_mode else "#F8FAFC"
        text_color = ft.Colors.WHITE if self.is_dark_mode else "#1E293B"
        
        # Update Page
        self.page.bgcolor = page_bg
        
        # Update Header/Footer Text
        self.header.content.controls[1].color = text_color
        self.header.update()
        
        # Update app accent
        self.set_app_accent(new_accent if self.is_dark_mode else "#000000")
        
        # Sync all items
        for itm in self.items:
            itm.toggle_theme(self.is_dark_mode)
            
        # Update Empty State
        self.empty_state.content.controls[1].color = text_color
        self.empty_state.update()
        
        # Update Sub Header
        self.sub_header.content.controls[0].color = "#A5C9FF" if self.is_dark_mode else "#2563EB"
        self.sub_header.update()

        # Update toggle icon
        self.header.content.controls[2].icon = ft.Icons.WB_SUNNY_OUTLINED if not self.is_dark_mode else ft.Icons.DARK_MODE_OUTLINED
        self.header.content.controls[2].icon_color = text_color
        
        # Feedback
        mode_text = "Light Vibe" if not self.is_dark_mode else "Midnight Vibe"
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Switched to {mode_text}"), duration=1000)
        self.page.snack_bar.open = True
        
        self.page.update()

    async def compare_action(self, e):
        valid_items_data = []
        item_objects = []
        
        # Validation
        for itm in self.items:
            data = itm.get_data(global_unit=self.unit_dropdown.value, global_currency=self.currency_dropdown.value)
            if data is None or data['weight'] <= 0 or data['price'] <= 0:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please enter valid weight and price > 0 for all items"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            valid_items_data.append(data)
            item_objects.append(itm)

        if not valid_items_data:
            self.page.snack_bar = ft.SnackBar(ft.Text("Add at least one valid item to compare"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Sort
        sorted_indices = sorted(range(len(valid_items_data)), key=lambda i: valid_items_data[i]['unit_price'])
        
        # Reorder objects
        sorted_items = [self.items[i] for i in sorted_indices]
        sorted_data = [valid_items_data[i] for i in sorted_indices]
        
        # Save to DB
        self.db.save_comparison(sorted_data)

        # Animate Reordering
        self.content_column.controls.clear()
        for i, itm in enumerate(sorted_items):
            itm.update_index(i)
            await itm.set_rank(i + 1, is_best=(i == 0))
            self.content_column.controls.append(itm)
        
        self.items = sorted_items # Sync state
        self.page.update()
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Comparison Complete!"), bgcolor="#7EA7FF")
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    PriceSaverApp(page)

if __name__ == "__main__":
    ft.app(target=main)
