import xml.etree.ElementTree as ET
import zipfile
from typing import List, Dict
import streamlit as st
from datetime import datetime
from models.nfe import Nfe
from models.nfe_item import NFEItem

from config.settings import NFE_NAMESPACE
from utils.helpers import safe_decimal_converter

class XMLProcessor:

    @staticmethod
    def extract_nfe_data(xml_content: bytes, filename: str) -> Nfe:
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
            emitter_uf = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:enderEmit//nfe:UF', NFE_NAMESPACE)
            v_freight = XMLProcessor._get_text_safe(item, './/nfe:total/nfe:ICMSTot//nfe:vFrete', NFE_NAMESPACE)
            ie = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:IE', NFE_NAMESPACE)

            # Get items data
            items_data:List[NFEItem] = []
            for item in root.findall('.//nfe:det', NFE_NAMESPACE):
                item_data:NFEItem = XMLProcessor._extract_item_data(item)
                items_data.append(item_data)

            nfe: Nfe = Nfe(
                ie=ie,
                number=nfe_number,
                key=nfe_key,
                series=nfe_series,
                emitter_name=emitter_name,
                emitter_cnpj=emitter_cnpj,
                emission_date=emission_date,
                emitter_uf=emitter_uf,
                filename=filename,
                items=items_data,
                freight=v_freight
            )

            return nfe

        except Exception as e:
            st.error(f"Erro ao processar XML {filename}: {str(e)}")
            return {'nfe_key': filename, 'items': [], 'error': str(e)}

    @staticmethod
    def _extract_item_data(item) -> NFEItem:
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

        v_ipi = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vIPI', ns)
        v_insurance = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vSeg', ns)
        v_others = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vOutro', ns)

        # Calcular MVA ajustado
        from services.tax_calculator import TaxCalculator
        mva_adjusted = TaxCalculator.calculate_adjusted_mva(safe_decimal_converter(mva_st))

        nfe_item = NFEItem(
            c_prod=cProd,
            ncm=ncm,
            uf_origin=None,
            o_cst=o_cst,
            red_base_cal=safe_decimal_converter(pRedBC),
            cfop=cfop,
            v_total=v_total,
            bc_icms=bc_icms,
            v_icms=v_icms,
            a_icms=a_icms,
            mva_st=mva_st,
            cest=cest,
            mva_adjusted=mva_adjusted,
            freight=None,
            ipi=v_ipi,
            others=v_others,
            insurance=v_insurance
        )

        return nfe_item

    @staticmethod
    def _get_text_safe(element, xpath: str, namespace: Dict) -> str:
         
        found = element.find(xpath, namespace)
        return found.text if found is not None else ''

    @staticmethod
    def process_zip_file(uploaded_file) -> List[Nfe]:

        all_nfes: List[Nfe] = []

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
                        nfe_data: Nfe = XMLProcessor.extract_nfe_data(xml_data, xml_file)
                        all_nfes.append(nfe_data)

                    progress_bar.progress((i + 1) / len(xml_files))

                status_text.text('Processamento concluído!')

        except Exception as e:
            st.error(f"Erro ao processar arquivo ZIP: {str(e)}")
            return []

        return all_nfes
