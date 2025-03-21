import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")  # Usa variável de ambiente ou 'data' como padrão
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db") # Usa variável de ambiente ou 'metadados.db' como padrão
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE) # Caminho completo do banco

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
