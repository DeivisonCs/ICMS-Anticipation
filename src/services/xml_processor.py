from decimal import Decimal
import xml.etree.ElementTree as ET
import zipfile
from typing import List, Dict
import streamlit as st
from datetime import datetime
from models.nfe import Nfe
from models.nfe_item import NFEItem

from services.fetch_handler import FetchHandler

from config.settings import NFE_NAMESPACE
from utils.helpers import safe_decimal_converter

from config.settings import (
    TAXED_ITEMS
)

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
            v_freight = XMLProcessor._get_text_safe(root, './/nfe:total/nfe:ICMSTot//nfe:vFrete', NFE_NAMESPACE)
            v_ipi = XMLProcessor._get_text_safe(root, './/nfe:total/nfe:ICMSTot//nfe:vIPI', NFE_NAMESPACE)
            v_insurance = XMLProcessor._get_text_safe(root, './/nfe:total/nfe:ICMSTot//nfe:vSeg', NFE_NAMESPACE)
            v_others = XMLProcessor._get_text_safe(root, './/nfe:total/nfe:ICMSTot//nfe:vOutro', NFE_NAMESPACE)
            ie = XMLProcessor._get_text_safe(root, './/nfe:emit/nfe:IE', NFE_NAMESPACE)

            # Get items data
            items_data:List[NFEItem] = []
            for item in root.findall('.//nfe:det', NFE_NAMESPACE):
                item_data:NFEItem = XMLProcessor._extract_item_data(item)
                items_data.append(item_data)

            is_simples_optant = XMLProcessor.is_simple_optant(emitter_cnpj)

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
                isSimple=is_simples_optant,
                freight=safe_decimal_converter(v_freight),
                ipi=safe_decimal_converter(v_ipi),
                insurance=safe_decimal_converter(v_insurance),
                others=safe_decimal_converter(v_others)
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

        v_freight = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:vFrete', ns)
        v_insurance = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:vSeg', ns)
        v_others = XMLProcessor._get_text_safe(item, 'nfe:prod/nfe:vOutro', ns)
        v_ipi = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:IPI//nfe:vIPI', ns)
        v_icms_st = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vICMSST', ns)
        v_bc_st = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:vBCST', ns)

        percentage = XMLProcessor._get_text_safe(item, 'nfe:imposto/nfe:ICMS//nfe:pICMS', ns)
        percentage = percentage.split('.')[0]
        mva_adjusted = XMLProcessor.search_mva_adjusted(cest=cest, ncm=ncm, percentage=percentage)
        mva_st = XMLProcessor.search_mva_original(cest=cest, ncm=ncm)

        nfe_item = NFEItem(
            c_prod=cProd,
            ncm=ncm,
            o_cst=o_cst,
            red_base_cal=safe_decimal_converter(pRedBC),
            cfop=cfop,
            v_total=safe_decimal_converter(v_total),
            bc_icms=safe_decimal_converter(bc_icms),
            v_icms=safe_decimal_converter(v_icms),
            a_icms=safe_decimal_converter(a_icms),
            mva_st=safe_decimal_converter(mva_st),
            mva_adjusted=safe_decimal_converter(mva_adjusted),
            cest=cest,
            freight=safe_decimal_converter(v_freight),
            insurance=safe_decimal_converter(v_insurance),
            others_costs=safe_decimal_converter(v_others),
            ipi=safe_decimal_converter(v_ipi),
            icms_st=safe_decimal_converter(v_icms_st),
            bc_st=safe_decimal_converter(v_bc_st)
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

    @staticmethod
    def search_mva_adjusted(cest:str, ncm:str, percentage:str):
        formatted_cest = cest.replace('.', '')
        formatted_ncm = ncm.replace('.', '')

        for taxed_item in TAXED_ITEMS:
            if formatted_cest == taxed_item.cest.replace('.', ''):
                for key in taxed_item.ncm.keys():
                    formatted_key = key.replace('.', '')

                    if formatted_key == formatted_ncm or formatted_ncm.startswith(formatted_key):
                        mva_values = taxed_item.ncm[key]
                        attr_name = f"_{percentage}"
                        
                        return getattr(mva_values, attr_name)

    @staticmethod
    def search_mva_original(cest:str, ncm:str):
        formatted_cest = cest.replace('.', '')
        formatted_ncm = ncm.replace('.', '')

        for taxed_item in TAXED_ITEMS:
            if formatted_cest == taxed_item.cest.replace('.', ''):
                for key in taxed_item.ncm.keys():
                    formatted_key = key.replace('.', '')

                    if formatted_key == formatted_ncm or formatted_ncm.startswith(formatted_key):
                        mva_values = taxed_item.ncm[key]

                        return mva_values.original

    def is_simple_optant(cnpj: str):
        response_data = FetchHandler.fetch_cnpj_data_on_open_cnpj(cnpj)

        if not response_data:
            return None

        return response_data.get("opcao_simples") == "S"