import io
import pandas as pd
from typing import List, Dict
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

from models.nfe_item import NFEItem


class FileHandler: 
    
    @staticmethod
    def dataframe_to_excel(df: pd.DataFrame, emitter_name: str, period: str, ie: str) -> bytes:
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Check if DataFrame is empty or has no rows
            if df.empty:
                # Create a simple DataFrame with headers for empty case
                df = pd.DataFrame({'Notas': [], 'Antecip.': [], '%': [], 'UF': [], 'Observações': []})
            else:
                # Prepare the custom table with required columns
                table_df = pd.DataFrame()

                # Prepare the columns according to the required mapping
                table_df['Notas'] = df['NF-e']

                # Calculate the sum of ANTECIPACAO_TOTAL and ANTECIPACAO_PARCIAL
                table_df['Antecip.'] = df['ANTECIPACAO_TOTAL'] + df['ANTECIPACAO_PARCIAL']

                table_df['%'] = df['A ICMS']

                # UF column
                table_df['UF'] = df['UF']

                # Observations based on RED_BASE_CAL (leave empty if no value)
                table_df['Observações'] = ''
                table_df.loc[df['RED_BASE_CAL'] > 0, 'Observações'] = df.loc[df['RED_BASE_CAL'] > 0, 'RED_BASE_CAL'].astype(str)

                # Replace any NaN values with empty strings
                table_df = table_df.fillna('')
                df = table_df

            # Write data to Excel
            df.to_excel(writer, sheet_name='ICMS_Calculado', index=False, startrow=4)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['ICMS_Calculado']

            # Add header information
            worksheet.cell(row=1, column=1, value=f"Empresa: {emitter_name}")
            worksheet.cell(row=2, column=1, value=f"Período: {period}")
            worksheet.cell(row=3, column=1, value=f"Inscrição: {ie}")

            # Format headers
            header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            border = Border(
                left=Side(border_style='thin', color='000000'),
                right=Side(border_style='thin', color='000000'),
                top=Side(border_style='thin', color='000000'),
                bottom=Side(border_style='thin', color='000000')
            )

            for col_idx, column in enumerate(df.columns, 1):
                cell = worksheet.cell(row=4, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center')

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
