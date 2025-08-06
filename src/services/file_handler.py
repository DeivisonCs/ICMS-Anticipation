import io
import pandas as pd
from typing import List, Dict
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

from models.nfe_item import NFEItem


class FileHandler: 
    
    @staticmethod
    def generate_excel_file(items: List[NFEItem]) -> bytes: 
        # Converter itens para DataFrame
        data = [item.to_dict() for item in items]
        df = pd.DataFrame(data)
        
        return FileHandler.dataframe_to_excel(df)
    
    @staticmethod
    def dataframe_to_excel(df: pd.DataFrame) -> bytes:
         
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ICMS_Calculado', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['ICMS_Calculado']
            
            # Define styles
            header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            border = Border(
                left=Side(border_style='thin', color='000000'),
                right=Side(border_style='thin', color='000000'),
                top=Side(border_style='thin', color='000000'),
                bottom=Side(border_style='thin', color='000000')
            )
            
            # Format headers
            for col_idx, column in enumerate(df.columns, 1):
                cell = worksheet.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Format data cells
            for row_idx in range(2, len(df) + 2):
                for col_idx in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.border = border
                    
                    # Set currency format for value columns
                    column_name = df.columns[col_idx-1]
                    if any(val in column_name for val in ['TOTAL', 'ICMS', 'ANTECIPACAO']):
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0.00'
                            cell.alignment = Alignment(horizontal='right')
            
            # Adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Add padding
                adjusted_width = max_length + 2
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def validate_zip_file(uploaded_file) -> bool:
         
        try:
            # Verifica se o arquivo tem extensão .zip
            if not uploaded_file.name.lower().endswith('.zip'):
                return False
            
            # Tenta abrir como ZIP (validação básica)
            import zipfile
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                # Verifica se há pelo menos um arquivo XML
                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                return len(xml_files) > 0
                
        except Exception:
            return False
