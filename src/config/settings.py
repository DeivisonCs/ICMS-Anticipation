from decimal import Decimal
from services.taxed_items_extractor import TaxedItemsExtractor
from typing import List

# Taxas de imposto
INTERNAL_TAX_RATE_BA = Decimal('0.205')
INTERSTATE_TAX_RATE = Decimal('0.07')

# NCMs com substituição tributária
taxed_items_extractor = TaxedItemsExtractor()
taxed_items_extractor.process_data_from_pdf()
NCM_SUBSTITUICAO_TRIBUTARIA:List[TaxedItemsExtractor] = taxed_items_extractor.process_taxed_items()

# Configurações de antecipação (percentuais)
ANTECIPACAO_TOTAL_RATE = Decimal('0.02')  # 2% do valor total
ANTECIPACAO_PARCIAL_RATE = Decimal('0.01')  # 1% da base de cálculo

# Lista de CST com isentos
EXEMPTED_CST_LIST = {"40", "41", "50"}

# Lista de CST com redução da base de cálculo
REDUCTION_CST_LIST = {"20"}

# Lista de CST com cobrança de ST ou ST cobrada anteriormente
ALREADY_CHARGED_CST_LIST = {"10", "30", "60"}

# Namespace XML da NF-E
NFE_NAMESPACE = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    'page_title': "Calculadora ICMS - NF-E",
    'page_icon': "📊",
    'layout': "wide"
}
