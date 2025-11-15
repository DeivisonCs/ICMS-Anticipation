import requests

class FetchHandler:

    @staticmethod
    def fetch_data(cnpj:str):
        url = f"https://open.cnpja.com/office/{cnpj}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: Failed to ask data."