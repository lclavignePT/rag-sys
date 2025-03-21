import os
import json
from PyPDF2 import PdfReader
import datetime

def inspect_pdf_metadata(pdf_filepath):
    """
    Lê os metadados brutos de um arquivo PDF e retorna um dicionário.

    Args:
        pdf_filepath (str): Caminho completo para o arquivo PDF.

    Returns:
        dict: Um dicionário contendo os metadados brutos do PDF, ou None em caso de erro.
    """
    try:
        with open(pdf_filepath, "rb") as f:
            reader = PdfReader(f)
            metadata = reader.metadata

            if metadata:
                metadata_dict = {}
                for key, value in metadata.items():
                    # Converte datetime para string ISO 8601, se necessário
                    if isinstance(value, datetime.datetime):
                        value = value.isoformat() + "Z"  # Formato ISO 8601 com Z para UTC
                    metadata_dict[key] = value
                return metadata_dict
            else:
                return None  # Nenhum metadado encontrado

    except FileNotFoundError:
        print(f"Erro: Arquivo PDF não encontrado: {pdf_filepath}")
        return None
    except Exception as e:
        print(f"Erro ao ler metadados do PDF: {e}")
        return None

if __name__ == "__main__":
    # --- Configuração ---
    DATA_DIR = "data/test_documents"
    OUTPUT_JSON_FILE = "pdf_metadata.json"  # Nome do arquivo JSON de saída
    # --- Fim da Configuração ---

    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

    all_metadata = {}  # Dicionário para guardar metadados de TODOS os PDFs

    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado na pasta '{DATA_DIR}'.")
    else:
        for pdf_file in pdf_files:
            pdf_filepath = os.path.join(DATA_DIR, pdf_file)
            metadata = inspect_pdf_metadata(pdf_filepath)
            if metadata:
                all_metadata[pdf_file] = metadata  # Salva metadados no dicionário, usando nome do arquivo como chave

        # Salva o dicionário completo em um arquivo JSON
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as json_file:
            json.dump(all_metadata, json_file, indent=4, ensure_ascii=False)  # Salva como JSON formatado

        print(f"Metadados dos PDFs salvos em: {OUTPUT_JSON_FILE}")