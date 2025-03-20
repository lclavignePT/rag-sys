import sqlite3
import os
import sys

# Adiciona o diretório 'src' ao PYTHONPATH para permitir imports relativos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Pega o diretório do script atual (src/database)
ROOT_DIR = os.path.dirname(SCRIPT_DIR) # Sobe um nível para chegar à pasta 'src'
SRC_DIR = os.path.dirname(ROOT_DIR) # Sobe mais um nível para chegar à raiz do projeto
sys.path.insert(0, ROOT_DIR) # Adiciona o diretório 'src' ao início do sys.path
print("sys.path after modification:")
for path in sys.path:
    print(f"- {path}")

from dotenv import load_dotenv

load_dotenv()


DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")  # Usa variável de ambiente ou 'data' como padrão
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db") # Usa variável de ambiente ou 'metadados.db' como padrão
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE) # Caminho completo do banco

import src.utils.dummy_module

def inserir_metadados(nome_arquivo, autor, data_criacao, data_modificacao, usuario_modificacao, linguagem, tipo_documento, tags, nivel_acesso, codigo_autenticacao):
    """
    Insere um novo registro de metadados na tabela 'metadados'.

    Args:
        nome_arquivo (str): Nome do arquivo do documento.
        autor (str, optional): Autor do documento.
        data_criacao (str, optional): Data de criação do documento (formato ISO 8601: YYYY-MM-DD HH:MM:SS).
        data_modificacao (str, optional): Data da última modificação (formato ISO 8601).
        usuario_modificacao (str, optional): Usuário da última modificação.
        linguagem (str, optional): Linguagem do documento (ex: 'pt-BR', 'en').
        tipo_documento (str): Tipo do documento (ex: 'relatório', 'email').
        tags (str, optional): Tags/palavras-chave (separadas por vírgula).
        nivel_acesso (str): Nível de acesso ('publico', 'restrito', 'confidencial').
        codigo_autenticacao (str, optional): Código de autenticação (hash bcrypt).

    Returns:
        bool: True se a inserção for bem-sucedida, False em caso de erro. # Vamos simplificar para printar mensagem de sucesso por enquanto
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = """
        INSERT INTO metadados (
            nome_arquivo, autor, data_criacao, data_modificacao, usuario_modificacao,
            linguagem, tipo_documento, tags, nivel_acesso, codigo_autenticacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        valores = (
            nome_arquivo, autor, data_criacao, data_modificacao, usuario_modificacao,
            linguagem, tipo_documento, tags, nivel_acesso, codigo_autenticacao
        )

        cursor.execute(sql, valores)
        conn.commit()
        print(f"Metadados para '{nome_arquivo}' inseridos com sucesso no banco de dados.")
        return True # Por enquanto, vamos retornar True em caso de sucesso (podemos refinar depois)


    except sqlite3.Error as e:
        print(f"Erro ao inserir metadados para '{nome_arquivo}': {e}")
        return False # Retorna False em caso de erro

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Pasta onde estão os documentos de teste (a mesma que usamos em test_models.py)
    DATA_DIR_TEST_DOCUMENTS = "data/test_documents"

    # Carrega os nomes dos arquivos de teste da pasta
    documentos_teste = load_test_documents(DATA_DIR_TEST_DOCUMENTS)

    if not documentos_teste:
        print(f"Nenhum documento de teste encontrado na pasta '{DATA_DIR_TEST_DOCUMENTS}'. Adicione arquivos lá para testar a inserção de metadados.")
    else:
        print(f"Iniciando teste de inserção de metadados para documentos em '{DATA_DIR_TEST_DOCUMENTS}':")
        for nome_arquivo_teste in documentos_teste.keys(): # Itera sobre os nomes dos arquivos carregados
            insercao_sucesso = inserir_metadados(
                nome_arquivo=nome_arquivo_teste,
                autor="Autor Desconhecido", # Metadados de exemplo genéricos
                data_criacao="2024-01-01 00:00:00", # Metadados de exemplo genéricos
                data_modificacao="2024-01-01 00:00:00", # Metadados de exemplo genéricos
                usuario_modificacao="sistema", # Metadados de exemplo genéricos
                linguagem="desconhecido", # Metadados de exemplo genéricos
                tipo_documento="desconhecido", # Metadados de exemplo genéricos
                tags="teste,inicial,exemplo", # Metadados de exemplo genéricos
                nivel_acesso="publico", # Metadados de exemplo genéricos
                codigo_autenticacao=None  # Metadados de exemplo genéricos
            )

            if insercao_sucesso:
                print(f"  - Metadados para '{nome_arquivo_teste}' inseridos com sucesso.")
            else:
                print(f"  - Falha ao inserir metadados para '{nome_arquivo_teste}'. Verifique os erros acima.")

        print("Teste de inserção de metadados para documentos de teste concluído.")