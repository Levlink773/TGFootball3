from .base_item import ITEM

import random

class OpenBox:
    length_of_line: int = 25
    target_index: int = 5
    pointer_index: int = 0 

    def __init__(self, items: list[ITEM]):
        self.items = items
        self.pointer_index: int = 0
        self.is_active: bool = True

    def generate_scroll_line(self) -> str:
        return " | ".join(
            f"{item.name[:3].ljust(3)} x{str(item.count_item).rjust(3)}"
            for item in self.items
        )

    @property
    def winner_item(self) -> ITEM:
        return self.items[self.target_index]

    def generate_text_line(self) -> str:
        scroll_line = self.generate_scroll_line()
        return f"{scroll_line} | {scroll_line}"

    def get_next_frame(self):
        if not self.is_active:
            return

        scroll_line = self.generate_text_line()
        visible_window = self.length_of_line - 4

        total_items = len(self.items)

        while self.is_active:
            start_index = self.pointer_index
            end_index = start_index + visible_window
            visible_text = scroll_line[start_index:end_index]
            visible_line = f"| {visible_text.ljust(visible_window)} |"
            center_position = visible_window // 2

            current_index_in_list = (self.pointer_index // (self.length_of_line // total_items)) % total_items

            if current_index_in_list == self.target_index:
                winner_text = f"{self.winner_item.name[:3].ljust(3)} x{str(self.winner_item.count_item).rjust(3)}"

                winner_start = visible_text.find(winner_text)
                if winner_start != -1:
                    winner_center_position = winner_start + len(winner_text) // 2
                    if abs(winner_center_position - center_position) <= 1:
                        self.is_active = False

            pointer_line = " " * center_position + "🔼"

            yield f"<code>{visible_line}</code>\n<code>{pointer_line}</code>"
            if self.is_active:
                self.pointer_index = (self.pointer_index + 1) % len(scroll_line)