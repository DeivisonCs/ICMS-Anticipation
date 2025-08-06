"""
Serviço para processamento de arquivos XML da NF-E
"""
import xml.etree.ElementTree as ET
import zipfile
from typing import List, Dict
import streamlit as st

from config.settings import NFE_NAMESPACE
from utils.helpers import safe_decimal_converter


class XMLProcessor:
     
    
    @staticmethod
    def extract_nfe_data(xml_content: bytes) -> List[Dict]:
         
        try:
            root = ET.fromstring(xml_content)
            data = []

            for item in root.findall('.//nfe:det', NFE_NAMESPACE):
                item_data = XMLProcessor._extract_item_data(item)
                data.append(item_data)

            return data
        except Exception as e:
            st.error(f"Erro ao processar XML: {str(e)}")
            return []
    
    @staticmethod
    def _extract_item_data(item) -> Dict:
        ns = NFE_NAMESPACE
        
        # Extrair dados básicos do produto
        cod = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:cProd', ns)
        ncm = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:NCM', ns)
        cfop = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:CFOP', ns)
        v_total = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:vProd', ns)
        cest = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:CEST', ns)
        
        # Extrair dados do ICMS
        orig = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:orig', ns)
        cst = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:CST', ns)
        o_cst = f"{orig}{cst}"
        
        bc_icms = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vBC', ns)
        v_icms = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vICMS', ns)
        a_icms = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:pICMS', ns)
        mva_st = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:pMVAST', ns)
        
        # Calcular MVA ajustado
        from services.tax_calculator import TaxCalculator
        mva_adjusted = TaxCalculator.calculate_adjusted_mva(safe_decimal_converter(mva_st))
        
        return {
            'COD': cod,
            'NCM/SH': ncm,
            'O/CST': o_cst,
            'CFOP': cfop,
            'V TOTAL': v_total,
            'BC ICMS': bc_icms,
            'V ICMS': v_icms,
            'A ICMS': a_icms,
            'MVA-ST': mva_st,
            'CEST': cest,
            'MVA': str(mva_adjusted)
        }
    
    @staticmethod
    def _get_text_safe(element, xpath: str, namespace: Dict) -> str:
         
        found = element.find(xpath, namespace)
        return found.text if found is not None else ''
    
    @staticmethod
    def process_zip_file(uploaded_file) -> List[Dict]:
         
        all_data = []
        
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                
                if not xml_files:
                    st.error("Nenhum arquivo XML encontrado no ZIP.")
                    return []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, xml_file in enumerate(xml_files):
                    status_text.text(f'Processando {xml_file}...')
                    
                    with zip_ref.open(xml_file) as xml_content:
                        xml_data = xml_content.read()
                        nfe_data = XMLProcessor.extract_nfe_data(xml_data)
                        all_data.extend(nfe_data)
                    
                    progress_bar.progress((i + 1) / len(xml_files))
                
                status_text.text('Processamento concluído!')
                
        except Exception as e:
            st.error(f"Erro ao processar arquivo ZIP: {str(e)}")
            return []
        
        return all_data
