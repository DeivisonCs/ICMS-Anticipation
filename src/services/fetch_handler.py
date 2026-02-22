import requests

class FetchHandler:

    @staticmethod
    def fetch_cnpj_data_on_cnpja(cnpj:str):
        url = f"https://open.cnpja.com/office/{cnpj}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                message = error_data.get("message")
            except Exception:
                message = response.text  # fallback caso não seja JSON

            print(f'ERROR - Failed fetch by CNPJ with CnpJá [CNPJ: {cnpj}, statusCode: {response.status_code}, message: {message}].')
            return None
    
    def fetch_cnpj_data_on_open_cnpj(cnpj:str):
        url = f"https://api.opencnpj.org/{cnpj}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                message = error_data.get("message")
            except Exception:
                message = response.text  # fallback caso não seja JSON

            print(f'ERROR - Failed fetch by CNPJ with OpenCNPJ [CNPJ: {cnpj}, statusCode: {response.status_code}, message: {message}].')
            return None