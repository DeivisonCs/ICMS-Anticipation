from models.taxed_item import TaxedItem
from typing import List
import pandas as pd
import json
import os
import re

class TaxedItemsExtractor():

    def __init__(self):
        self.pdf_to_extract_path = 'resources/anexo_1_mercadorias_sujeitas_st.pdf'
        self.csv_extracted_items_path = 'resources/extracted/taxed_items_extracted.csv'
        self.json_extracted_items_path = 'resources/extracted/taxed_items_json.json'
        self.RE_CEST_RANGE = re.compile(r'(\d{2}\.\d{3}\.\d{2})\s*a\s*(\d{2}\.\d{3}\.\d{2})')

    def process_data_from_pdf(self):
        extracted_path = self.csv_extracted_items_path

        if os.path.exists(extracted_path):
            print("Taxed Items csv already exists.")
            return

        import camelot

        RE_CEST = re.compile(r'\b\d{2}\.\d{3}\.\d{2}\b')

        tables = camelot.read_pdf(self.pdf_to_extract_path, pages="all", flavor="lattice", line_scale=40)

        frames = []

        for table in tables:
            df = table.df
            indexes_to_remove = []

            filtered_df = df.iloc[:, [0, 1, 2, 3, 5, 6]].copy()
            filtered_df.columns = ["ITEM", "CEST", "NCM", "Descrição", "MVA Ajustado", "MVA Original"]
            filtered_df['Descrição'] = filtered_df['Descrição'].str.replace('\n', '', regex=False)

            for index, row in filtered_df.iterrows():
                cest_value = str(row['CEST'])

                if not re.match(RE_CEST, cest_value) or cest_value == '' or cest_value.isalpha():
                    indexes_to_remove.append(index)

            filtered_df = filtered_df.drop(indexes_to_remove)
            filtered_df = filtered_df.reset_index(drop=True)

            frames.append(filtered_df)

        final_table = pd.concat(frames, ignore_index=True)

        final_table.to_csv(self.csv_extracted_items_path, index=False, encoding="utf-8")

        print("Extração de itens tributados concluída!")

    def _get_cest_range(self, cest: str) -> list[str]:
        match = self.RE_CEST_RANGE.search(cest)
        if not match:
            return [cest.strip()]

        cest_start, cest_end = match.groups()

        prefix_start, start_num = cest_start[:-2], int(cest_start[-2:])
        prefix_end, end_num = cest_end[:-2], int(cest_end[-2:])

        if prefix_start != prefix_end:
            return [cest]

        return [f"{prefix_start}{i:02d}" for i in range(start_num, end_num + 1)]


    def _clean_value(self, value):
        if not isinstance(value, str):
            return None

        value = value.strip()
        if not value:
            return None

        match = re.search(r"\d+(?:,\d+)?", value)

        if match:
            return float(match.group().replace(",", "."))

        return None

    def _split_ncm(self, ncm_raw):
        if not isinstance(ncm_raw, str):
            return []
        # Divide por "e" ou vírgulas
        ncms = re.split(r"e|,", ncm_raw)
        return [n.strip() for n in ncms if n.strip()]

    def _parse_mva(self, raw_adjusted_mva, raw_original_mva):
        # Quebra em vários (quando existe 4%, 7% e 12% juntos)
        if isinstance(raw_adjusted_mva, str):
            values = re.findall(r"(\d+,\d+%)", raw_adjusted_mva)
        else:
            values = []

        # Converte para float
        values = [self._clean_value(v) for v in values]

        # Se não achar nada → pode ser só um valor
        if not values and raw_adjusted_mva:
            unique_value = self._clean_value(raw_adjusted_mva)
            if unique_value is not None:
                values = [unique_value]

        # Preenche com cópia se tiver só um valor
        if len(values) == 1:
            values = values * 3

        # Se tiver menos de 3 valores, completa com None
        while len(values) < 3:
            values.append(None)

        # Trata original
        mva_original = self._clean_value(raw_original_mva)

        return {
            "4": values[0],
            "7": values[1],
            "12": values[2],
            "original": mva_original
        }

    # ------------------------------
    # Função principal para converter o DataFrame
    # ------------------------------
    def _dataframe_to_dict(self, df):
        result = []

        for _, row in df.iterrows():
            item_id = str(row["ITEM"])
            cest = str(row["CEST"])
            ncm_raw = row["NCM"]
            description = row["Descrição"]
            raw_adjusted_mva = row["MVA Ajustado"]
            raw_original_mva = row["MVA Original"]
            ncms = self._split_ncm(ncm_raw)

            if not ncms:
                continue

            mva_dict = self._parse_mva(raw_adjusted_mva, raw_original_mva)
            cest_values = self._get_cest_range(cest)

            for c in cest_values:
                result.append({
                    "item": item_id,
                    "cest": c,
                    "descrição": description,
                    "ncm": {ncm: mva_dict for ncm in ncms}
                })

        return result

    def process_taxed_items(self) -> List[TaxedItem]:
        extracted_path = self.json_extracted_items_path

        if os.path.exists(extracted_path):
            print("JSON file already exists.")
            with open(self.json_extracted_items_path, "r", encoding="utf-8") as extracted_items:
                result_json = json.load(extracted_items)
                return [TaxedItem.from_dict(item) for item in result_json]

        df = pd.read_csv(self.csv_extracted_items_path)
        result_json = self._dataframe_to_dict(df)

        with open(self.json_extracted_items_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=4)

        print("Processamento concluído!")
        return [TaxedItem.from_dict(item) for item in result_json]