import xml.etree.ElementTree as ET
import zipfile
from typing import List, Dict
import streamlit as st
from datetime import datetime

from config.settings import NFE_NAMESPACE
from utils.helpers import safe_decimal_converter


class XMLProcessor: 
    
    @staticmethod
    def extract_nfe_data(xml_content: bytes, filename: str) -> Dict:
         
        try:
            root = ET.fromstring(xml_content)
            
            # Extract NF-e header information
            nfe_key = XMLProcessor._get_text_safe(root, './/nfe:chNFe', NFE_NAMESPACE)
            nfe_number = XMLProcessor._get_text_safe(root, './/nfe:nNF', NFE_NAMESPACE)
            nfe_series = XMLProcessor._get_text_safe(root, './/nfe:serie', NFE_NAMESPACE)
            emission_date = XMLProcessor._get_text_safe(root, './/nfe:dhEmi', NFE_NAMESPACE)
            
            # Format emission date if exists
            if emission_date:
                try:
                    date_obj = datetime.fromisoformat(emission_date.split('T')[0])
                    emission_date = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            
            # Get emitter info
            emitter_name = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:xNome', NFE_NAMESPACE)
            emitter_cnpj = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:CNPJ', NFE_NAMESPACE)
            uf = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:enderEmit//nfe:UF', NFE_NAMESPACE)
            ie = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:IE', NFE_NAMESPACE)

            # Get items data
            items_data = []
            for item in root.findall('.//nfe:det', NFE_NAMESPACE):
                item_data = XMLProcessor._extract_item_data(item)
                items_data.append(item_data)

            return {
                'nfe_key': nfe_key or filename,
                'nfe_number': nfe_number,
                'nfe_series': nfe_series,
                'uf': uf,
                'ie': ie,
                'emission_date': emission_date,
                'emitter_name': emitter_name,
                'emitter_cnpj': emitter_cnpj,
                'filename': filename,
                'items': items_data
            }

        except Exception as e:
            st.error(f"Erro ao processar XML {filename}: {str(e)}")
            return {'nfe_key': filename, 'items': [], 'error': str(e)}
    
    @staticmethod
    def _extract_item_data(item) -> Dict:
        ns = NFE_NAMESPACE
        
        # Extrair dados básicos do produto
        cProd = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:cProd', ns)
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
        pRedBC = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:pRedBC', ns)
        
        # Calcular MVA ajustado
        from services.tax_calculator import TaxCalculator
        mva_adjusted = TaxCalculator.calculate_adjusted_mva(safe_decimal_converter(mva_st))
        
        return {
            'CPROD': cProd,
            'NCM/SH': ncm,
            'O/CST': o_cst,
            'RED_BASE_CAL': str(safe_decimal_converter(pRedBC)),
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
         
        all_nfes = []
        
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
                        nfe_data = XMLProcessor.extract_nfe_data(xml_data, xml_file)
                        all_nfes.append(nfe_data)
                    
                    progress_bar.progress((i + 1) / len(xml_files))
                
                status_text.text('Processamento concluído!')
                
        except Exception as e:
            st.error(f"Erro ao processar arquivo ZIP: {str(e)}")
            return []
        
        return all_nfes
