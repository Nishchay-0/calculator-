import flet as ft
import asyncio
from theme import GLASS_STYLE, SECONDARY_TEXT, SUCCESS_COLOR, DANGER_COLOR

class ItemCard(ft.Container):
    def __init__(self, index, on_delete, on_change, initial_unit="g", initial_currency="Rs", **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.on_delete = on_delete
        self.on_change = on_change
        
        # Symbols for internal display
        self.unit_label = ft.Text(initial_unit, color=SECONDARY_TEXT, size=12, weight="bold")
        self.currency_label = ft.Text(initial_currency, color=SECONDARY_TEXT, size=12, weight="bold")
        
        # UI Attributes
        self.name_field = ft.TextField(
            hint_text="Product Name",
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
            text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
            hint_style=ft.TextStyle(color=SECONDARY_TEXT, size=14),
            on_change=self.on_change,
            height=35,
            content_padding=ft.Padding.only(left=10, top=0, right=10, bottom=0),
            expand=True
        )
        
        self.weight_field = ft.TextField(
            hint_text="Weight",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""),
            border_radius=8,
            bgcolor=ft.Colors.TRANSPARENT,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.TRANSPARENT,
            text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
            hint_style=ft.TextStyle(color=SECONDARY_TEXT, size=14),
            on_change=self.on_change,
            height=35,
            # content_padding=ft.Padding.only(left=10, top=0, right=10, bottom=0),
            expand=True
        )
        
        self.price_field = ft.TextField(
            hint_text="Price",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""),
            border_radius=8,
            bgcolor=ft.Colors.TRANSPARENT,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.TRANSPARENT,
            text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
            hint_style=ft.TextStyle(color=SECONDARY_TEXT, size=14),
            on_change=self.on_change,
            height=35,
            # content_padding=ft.Padding.only(left=10, top=0, right=10, bottom=0),
            expand=True
        )
        
        self.quantity_text = ft.Text("1", color=ft.Colors.WHITE, size=14, weight="bold")
        self.qty = 1
        
        # Quantity Selector UI Container
        self.qty_selector = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.REMOVE, on_click=self.decrease_qty, icon_color=ft.Colors.WHITE, icon_size=14),
                self.quantity_text,
                ft.IconButton(ft.Icons.ADD, on_click=self.increase_qty, icon_color=ft.Colors.WHITE, icon_size=14),
            ], spacing=5, alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_radius=8,
            padding=ft.Padding.only(left=5, top=0, right=5, bottom=0),
            height=35
        )

        # Style matches GLASS_STYLE
        for k, v in GLASS_STYLE.items():
            setattr(self, k, v)
        
        # Apply enhanced blur and transparency for Apple-like glassmorphism
        self.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE))
        self.border_radius = 16
        self.blur = ft.Blur(12, 12, ft.BlurStyle.NORMAL)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 5)
        )
        
        self.padding = ft.Padding.all(12)
        self.margin = ft.Margin.only(bottom=10)
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT)

        self.content = ft.Column([
            # Row 1: Index, Name, Trash
            ft.Row([
                ft.Container(
                    content=ft.Text(str(self.index + 1), color=ft.Colors.WHITE, size=11, weight="bold"),
                    width=22, height=22,
                    bgcolor=SUCCESS_COLOR,
                    border_radius=11,
                    alignment=ft.Alignment(0, 0),
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.3, SUCCESS_COLOR))
                ),
                self.name_field,
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                    on_click=self.handle_delete,
                    icon_size=20,
                    tooltip="Remove item"
                )
            ], alignment="spaceBetween", vertical_alignment="center"),
            
            # Row 2: Weight, Price, Qty Selector (with Professional Suffixes)
            ft.Row([
                # Weight Input with Suffix Box
                ft.Container(
                    content=ft.Row([
                        self.weight_field,
                        ft.Container(
                            content=self.unit_label,
                            width=30,
                            height=35,
                            # bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), # Slightly different shade
                            alignment=ft.Alignment(0, 0),
                            border=ft.Border(left=ft.BorderSide(0.5, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)))
                        )
                    ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    border_radius=8,
                    height=35,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                ),
                
                # Price Input with Suffix Box
                ft.Container(
                    content=ft.Row([
                        self.price_field,
                        ft.Container(
                            content=self.currency_label,
                            width=30,
                            height=35,
                            # bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                            alignment=ft.Alignment(0, 0),
                            border=ft.Border(left=ft.BorderSide(0.5, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)))
                        )
                    ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    border_radius=8,
                    height=35,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                ),
                self.qty_selector
            ], alignment="spaceBetween", vertical_alignment="center", spacing=10)
        ], spacing=10)

    async def increase_qty(self, e):
        if self.qty < 999:
            self.qty += 1
            self.quantity_text.value = str(self.qty)
            self.update()
            await self.on_change(e)

    async def decrease_qty(self, e):
        if self.qty > 1:
            self.qty -= 1
            self.quantity_text.value = str(self.qty)
            self.update()
            await self.on_change(e)

    def update_index(self, index):
        self.index = index
        self.content.controls[0].controls[0].content.value = str(index + 1)
        self.update()

    def update_symbols(self, unit, currency):
        self.unit_label.value = unit
        self.currency_label.value = currency
        self.update()

    async def set_rank(self, rank, is_best=False):
        if is_best:
            self.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, success_color if 'success_color' in locals() else "#7EA7FF"))
            self.scale = 1.01
            self.update()
            await asyncio.sleep(0.3)
            self.scale = 1.0
            self.update()
        else:
            self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        self.update()

    def update_accent(self, color):
        """Update the rank circle and border colors dynamically."""
        self.content.controls[0].controls[0].bgcolor = color
        # Shadow color sync
        self.content.controls[0].controls[0].shadow.color = ft.Colors.with_opacity(0.3, color)
        self.update()

    def toggle_theme(self, is_dark):
        """Update colors based on Dark/Light mode."""
        text_color = ft.Colors.WHITE if is_dark else "#1E293B"
        sub_text = SECONDARY_TEXT if is_dark else "#64748B"
        card_bg = "#1C1F26" if is_dark else "#FFFFFF"
        field_bg = ft.Colors.with_opacity(0.1, ft.Colors.BLACK) if is_dark else ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
        
        self.bgcolor = card_bg
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE if is_dark else ft.Colors.BLACK))
        
        # Update Fields
        for field in [self.name_field, self.weight_field, self.price_field]:
            field.text_style.color = text_color
            field.hint_style.color = sub_text
            if field == self.name_field:
                field.bgcolor = field_bg
        
        self.unit_label.color = sub_text
        self.currency_label.color = sub_text
        self.quantity_text.color = text_color
        
        self.update()

    def handle_delete(self, e):
        if self.on_delete:
            self.on_delete(self)

    def get_data(self, global_unit="g", global_currency="Rs"):
        try:
            w = float(self.weight_field.value) if self.weight_field.value else 0
            p = float(self.price_field.value) if self.price_field.value else 0
            
            # Normalize to base (g/ml)
            norm_factor = 1000 if global_unit in ["kg", "L"] else 1
            total_weight = (w * norm_factor)
            
            unit_price = (p * self.qty) / total_weight if total_weight > 0 else 0
            
            return {
                "name": self.name_field.value or f"Item {self.index + 1}",
                "weight": w,
                "unit": global_unit,
                "price": p,
                "currency": global_currency,
                "quantity": self.qty,
                "unit_price": unit_price
            }
        except ValueError:
            return None
