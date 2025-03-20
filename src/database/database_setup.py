import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")  # Usa variável de ambiente ou 'data' como padrão
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db") # Usa variável de ambiente ou 'metadados.db' como padrão
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE) # Caminho completo do banco

def create_database_and_tables():
    """Cria o banco de dados SQLite e a tabela 'metadados' se não existirem."""

    # Cria a pasta 'data' se não existir
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)

    conn = None  # Inicializa a conexão fora do bloco try
    try:
        conn = sqlite3.connect(DATABASE_PATH) # Conecta ou cria o banco se não existir
        cursor = conn.cursor()

        # SQL para criar a tabela 'metadados' (ESQUEMA FINAL DEFINIDO)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS metadados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT UNIQUE NOT NULL,
            autor TEXT,
            data_criacao DATETIME,
            data_modificacao DATETIME,
            usuario_modificacao TEXT,
            linguagem TEXT,
            tipo_documento TEXT NOT NULL,
            tags TEXT,
            nivel_acesso TEXT NOT NULL CHECK(nivel_acesso IN ('publico', 'restrito', 'confidencial')),
            codigo_autenticacao TEXT
        );
        """
        cursor.execute(create_table_sql)

        # SQL para criar os índices (ÍNDICES DEFINIDOS)
        create_indices_sql = """
        CREATE INDEX IF NOT EXISTS idx_tipo_documento ON metadados (tipo_documento);
        CREATE INDEX IF NOT EXISTS idx_tags ON metadados (tags);
        CREATE INDEX IF NOT EXISTS idx_nivel_acesso ON metadados (nivel_acesso);
        """
        cursor.executescript(create_indices_sql) # executescript para executar múltiplas instruções SQL de vez

        conn.commit() # Salva as alterações no banco de dados
        print(f"Banco de dados SQLite '{DATABASE_FILE}' e tabela 'metadados' criados/verificados com sucesso em: {DATABASE_PATH}")

    except sqlite3.Error as e:
        print(f"Erro ao criar banco de dados ou tabela: {e}")
    finally:
        if conn:
            conn.close() # Fecha a conexão se estiver aberta


if __name__ == "__main__":
    create_database_and_tables() # Executa a função se o script for rodado diretamente