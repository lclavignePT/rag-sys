import os
import sqlite3

from src.utils.metadata_extraction import extrair_metadados

from dotenv import load_dotenv

load_dotenv()

DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db")
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE)


def inserir_metadados(nome_arquivo):
    """
    Insere um novo registro de metadados na tabela 'metadados', extraindo
    informações do arquivo fornecido.

    Args:
        nome_arquivo (str): Nome do arquivo do documento (dentro da pasta de documentos de teste).

    Returns:
        bool: True se a inserção for bem-sucedida, False em caso de erro.
    """

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Constrói o caminho completo do arquivo
        filepath = os.path.join(DATABASE_DIR, "test_documents", nome_arquivo)

        # Extrai metadados usando a função unificada
        metadados = extrair_metadados(filepath)

        if metadados is None:
            print(f"Erro ao extrair metadados para: {nome_arquivo} - Abortando inserção.")
            return False

        sql = """
        INSERT INTO metadados (
            nome_arquivo, autor, data_criacao, data_modificacao, usuario_modificacao,
            linguagem, tipo_documento, tags, nivel_acesso, codigo_autenticacao, titulo, tamanho_bytes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            metadados['nome_arquivo'], metadados['autor'], metadados['data_criacao'], metadados['data_modificacao'], metadados['usuario_modificacao'],
            metadados['linguagem'], metadados['tipo_documento'], metadados['tags'], metadados['nivel_acesso'], metadados['codigo_autenticacao'], metadados['titulo'],
            metadados['tamanho_bytes']
        )

        cursor.execute(sql, valores)
        conn.commit()
        print(f"Metadados para '{nome_arquivo}' inseridos com sucesso no banco de dados.")
        return True

    except sqlite3.Error as e:
        print(f"Erro ao inserir metadados para '{nome_arquivo}': {e}")
        return False

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: '{filepath}'")
        return False

    except Exception as e:
        print(f"Erro inesperado ao inserir metadados para '{nome_arquivo}': {e}")
        return False

    finally:
        if conn:
            conn.close()
def obter_metadados_por_nome_arquivo(nome_arquivo):
    """
    Obtém um registro de metadados da tabela 'metadados' pelo nome do arquivo.

    Args:
        nome_arquivo (str): Nome do arquivo do documento para buscar os metadados.

    Returns:
        dict or None: Um dicionário contendo os metadados se o arquivo for encontrado, None caso contrário.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row # Para retornar resultados como dicionários
        cursor = conn.cursor()

        sql = """
        SELECT * FROM metadados WHERE nome_arquivo = ?
        """
        cursor.execute(sql, (nome_arquivo,)) # Passa o nome_arquivo como parâmetro

        registro = cursor.fetchone() # Busca um único registro (ou None se não encontrar)

        if registro:
            # Se encontrou um registro, retorna como dicionário
            return dict(registro)
        else:
            return None # Retorna None se não encontrou

    except sqlite3.Error as e:
        print(f"Erro ao obter metadados para '{nome_arquivo}': {e}")
        return None # Retorna None em caso de erro

    finally:
        if conn:
            conn.close()

def buscar_metadados_por_tags(tags_busca):
    """
    Busca registros de metadados na tabela 'metadados' que contenham alguma das tags fornecidas.

    Args:
        tags_busca (list de str): Lista de tags a serem buscadas. A busca é do tipo "OR",
                                   retornando documentos que contenham *qualquer uma* dessas tags.

    Returns:
        list de dict: Uma lista de dicionários, onde cada dicionário representa os metadados de um documento
                      que contém pelo menos uma das tags de busca. Retorna uma lista vazia se nenhum documento
                      corresponder às tags.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row # Para retornar resultados como dicionários
        cursor = conn.cursor()

        if not tags_busca: # Se a lista de tags de busca estiver vazia, retorna lista vazia
            return []

        # Constrói a cláusula WHERE dinamicamente para buscar tags usando LIKE e OR
        clausulas_where = []
        parametros = []
        for tag in tags_busca:
            clausulas_where.append("tags LIKE ?") # Adiciona "tags LIKE ?" para cada tag
            parametros.append(f"%{tag}%") # Usa "%tag%" para buscar tag como substring (contém)

        sql = f"""
        SELECT * FROM metadados
        WHERE {' OR '.join(clausulas_where)}
        """
        print(f"Query SQL construída dinamicamente:\n{sql}")

        cursor.execute(sql, parametros) # Executa a query com a lista de parâmetros
        registros = cursor.fetchall() # Busca todos os registros correspondentes

        lista_metadados = []
        for registro in registros:
            lista_metadados.append(dict(registro)) # Converte cada sqlite3.Row para dicionário

        return lista_metadados # Retorna a lista de dicionários de metadados

    except sqlite3.Error as e:
        print(f"Erro ao buscar metadados por tags '{tags_busca}': {e}")
        return [] # Retorna lista vazia em caso de erro

    finally:
        if conn:
            conn.close()