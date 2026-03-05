from models.nfe import Nfe
from models.nfe_item import NFEItem

from config.settings import (
    INTERNAL_TAX_RATE_BA,
    INTERSTATE_TAX_RATE,
)

def log_anticipation_calculated(nfe:Nfe, item: NFEItem):
    print("-------------- Anticipation Properties --------------")
    print("Item: ", nfe.number)
    print("Alíquota BA: ", INTERNAL_TAX_RATE_BA)
    print("Alíquota Interestadual: ", INTERSTATE_TAX_RATE)
    print("ICMS origem: ", item.v_icms)

    if item.antecipacao_total != 0:
        print("Antecipação Total: ", item.antecipacao_total)
    else:
        print("Antecipação Parcial: ", item.antecipacao_parcial)

    print("-----------------------------------------------------")