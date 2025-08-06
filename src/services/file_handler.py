 
import io
import pandas as pd
from typing import List

from models.nfe_item import NFEItem


class FileHandler: 
    
    @staticmethod
    def generate_excel_file(items: List[NFEItem]) -> bytes: 
        # Converter itens para DataFrame
        data = [item.to_dict() for item in items]
        df = pd.DataFrame(data)
        
        # Gerar arquivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ICMS_Calculado', index=False)
        
        return output.getvalue()
    
    @staticmethod
    def dataframe_to_excel(df: pd.DataFrame) -> bytes:
         
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ICMS_Calculado', index=False)
        
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
