import os
import datetime
import statx
import sqlite3
from PyPDF2 import PdfReader
from dateutil import parser
from dotenv import load_dotenv

load_dotenv()

DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db")
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE)

def _obter_metadados_fs(filepath):
    """Obtém metadados do sistema de arquivos para um arquivo (versão simplificada)."""

    try:
        # Tenta usar statx para obter informações, incluindo stx_btime
        stx_info = statx.statx(filepath)
        stat_info = os.stat(filepath)

        # Dicionário para armazenar os metadados
        metadata = {}

        # --- Informações Básicas ---
        metadata['nome_arquivo'] = os.path.basename(filepath)
        metadata['tamanho_bytes'] = stat_info.st_size
        metadata['autor'] = "Autor Desconhecido"  # Valor padrão
        metadata['linguagem'] = "desconhecido"  # Valor padrão
        metadata['codigo_autenticacao'] = None  # Valor padrão por enquanto
        metadata['nivel_acesso'] = "publico"   # Valor padrão por enquanto
        metadata['titulo'] = None
        metadata['usuario_modificacao'] = "sistema"
        metadata['tags'] = os.path.splitext(metadata['nome_arquivo'])[0]

        # --- Datas ---
        metadata['data_modificacao'] = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat() + "Z"

        # Data de Criação (tentando usar stx_btime, fallback para stx_ctime)
        if hasattr(stx_info, 'btime'):  # Verifica se stx_btime está disponível
            metadata['data_criacao'] = datetime.datetime.fromtimestamp(stx_info.btime).isoformat() + "Z"
        else:
            print(f"Aviso: stx_btime não suportado neste sistema. Usando stx_ctime para data de criação de {filepath}.")
            metadata['data_criacao'] = datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat() + "Z"
        
        return metadata

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {filepath}")
        return None
    except Exception as e:
        print(f"Erro ao obter metadados do sistema de arquivos: {e} - {type(e)}")
        return None

def _extrair_metadados_txt(filepath):
    """Extrai metadados de um arquivo .txt."""
    metadados = _obter_metadados_fs(filepath)
    if metadados:
        metadados["tipo_documento"] = ".txt"
        metadados["tags"] = os.path.splitext(metadados['nome_arquivo'])[0]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                primeira_linha = f.readline().strip()
                if primeira_linha:
                    metadados["titulo"] = primeira_linha
        except Exception as e:
            print(f"Erro ao ler arquivo TXT: {e}")
    return metadados

def _extrair_metadados_pdf(filepath):
    """Extrai metadados de um arquivo .pdf."""
    metadados = _obter_metadados_fs(filepath)
    if metadados:
        metadados["tipo_documento"] = ".pdf"
        try:
            with open(filepath, "rb") as f:
                reader = PdfReader(f)
                metadata = reader.metadata
                if metadata:
                    metadados["autor"] = metadata.author or "Autor Desconhecido"
                    metadados["titulo"] = metadata.title
                    # Remove a lógica de data daqui! Já está em _obter_metadados_fs()
                    if hasattr(metadata, 'keywords') and metadata.keywords:
                        metadados["tags"] = metadata.keywords

        except Exception as e:
            print(f"Erro ao ler metadados do PDF: {e}")
    return metadados

def _extrair_metadados_md(filepath):
    """Extrai metadados de um arquivo .md."""
    metadados = _obter_metadados_fs(filepath)
    if metadados:
        metadados["tipo_documento"] = ".md"
        metadados["tags"] = os.path.splitext(metadados['nome_arquivo'])[0]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                primeira_linha = f.readline().strip()
                if primeira_linha.startswith("# "):
                    metadados["titulo"] = primeira_linha[2:]
        except Exception as e:
            print(f"Erro ao ler arquivo MD: {e}")
    return metadados

def extrair_metadados(filepath):
    """Extrai metadados de um arquivo, independentemente do tipo (TXT, MD, PDF)."""
    try:
        if filepath.lower().endswith(".txt"):
            return _extrair_metadados_txt(filepath)
        elif filepath.lower().endswith(".pdf"):
            return _extrair_metadados_pdf(filepath)
        elif filepath.lower().endswith(".md"):
            return _extrair_metadados_md(filepath)
        else:
            print(f"Tipo de arquivo não suportado para extração de metadados: {filepath}")
            return None  # Tipo de arquivo não suportado
    except Exception as e:
        print(f"Erro ao extrair metadados de {filepath}: {e} - {type(e)}")
        return None

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