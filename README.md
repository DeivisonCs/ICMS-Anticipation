# Calculadora ICMS - NF-E

Uma aplicação web desenvolvida em Streamlit para processar Notas Fiscais Eletrônicas (NF-E) e calcular valores de ICMS, MVA ajustado e antecipações tributárias.

## 📋 Funcionalidades

- Upload e processamento de arquivos ZIP contendo XMLs de NF-E
- Extração automática de dados dos XMLs
- Cálculo de MVA (Margem de Valor Agregado) ajustado
- Cálculo de antecipações tributárias (total e parcial)
- Visualização de dados em tabelas interativas
- Exportação dos resultados para Excel
- Interface web intuitiva e responsiva

## 🚀 Como usar

1. Execute a aplicação: `streamlit run app.py`
2. Acesse a interface web no navegador
3. Faça upload de um arquivo ZIP contendo arquivos XML de NF-E
4. Aguarde o processamento dos dados
5. Visualize os resultados e baixe a planilha Excel

## 📁 Estrutura do Projeto

```
ICMS-Anticipation/
├── app.py                    # Aplicação principal Streamlit
├── requirements.txt          # Dependências do projeto
├── README.md                # Documentação
├── config/
│   └── settings.py          # Configurações e constantes
├── src/
│   ├── models/
│   │   └── nfe_item.py      # Modelo de dados para itens NF-E
│   ├── services/
│   │   ├── xml_processor.py  # Processamento de XMLs
│   │   ├── tax_calculator.py # Cálculos tributários
│   │   └── file_handler.py   # Manipulação de arquivos
│   └── utils/
│       └── helpers.py        # Funções auxiliares
```

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd ICMS-Anticipation
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# ou
myenv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
streamlit run app.py
```
