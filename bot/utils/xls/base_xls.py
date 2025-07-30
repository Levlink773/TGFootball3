from abc import ABC, abstractmethod

import openpyxl
from openpyxl.styles import Alignment, Font

from database.models.character import Character


class BaseXLS(ABC):
    
    HEADERS: list[str]
    
    def __init__(self, members: list[Character]):
        self.members = members
        
        self.workbook = openpyxl.Workbook()
        self.current_sheet = self.workbook.active

    def set_base_settings(self) -> None:
        self.adjust_alignment()
        self.adjust_column_widths()

    def header_setings(self) -> None:
        self.current_sheet.append(self.HEADERS)
        for cell in self.current_sheet[1]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(bold=True)

    def adjust_column_widths(self) -> None:
        for column in self.current_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            adjusted_width = max_length + 2 
            self.current_sheet.column_dimensions[column_letter].width = adjusted_width
            
    def adjust_alignment(self) -> None:
        for row in self.current_sheet.iter_rows(min_row=2):  
            for cell in row:
                    cell.alignment = Alignment(horizontal="left", vertical="center")



    @abstractmethod
    async def generate_xls(self):
        pass
    
