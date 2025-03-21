import sqlite3
import os
from dotenv import load_dotenv

from PyPDF2 import PdfReader
from dateutil import parser
import datetime

load_dotenv()

DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")
DATABASE_FILE = os.environ.get("RAG_DATABASE_FILE", "metadados.db")
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE)

def _extrair_metadados_txt(filepath):
    """Extrai metadados de um arquivo .txt."""
    metadados = {
        "autor": "Autor Desconhecido",
        "data_criacao": None,  # Inicializa como None
        "data_modificacao": None,  # Inicializa como None
        "usuario_modificacao": "sistema",
        "linguagem": "desconhecido",
        "tipo_documento": ".txt",
        "tags": os.path.splitext(os.path.basename(filepath))[0],
        "titulo": None,
        "nivel_acesso": "publico",
        "codigo_autenticacao": None,
    }
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            primeira_linha = f.readline().strip()
            if primeira_linha:
                metadados["titulo"] = primeira_linha

        # Obter timestamp em segundos (UTC) e converter para datetime UTC
        data_criacao_ts = os.path.getctime(filepath)
        data_modificacao_ts = os.path.getmtime(filepath)

        metadados["data_criacao"] = datetime.datetime.utcfromtimestamp(data_criacao_ts).isoformat() + "Z"
        metadados["data_modificacao"] = datetime.datetime.utcfromtimestamp(data_modificacao_ts).isoformat() + "Z"


    except Exception as e:
        print(f"Erro ao ler arquivo TXT: {e}")
        # Mantém valores padrão em caso de erro
    return metadados


    """Extrai metadados de um arquivo .pdf."""
    metadados = {
        "autor": "Autor Desconhecido",
        "data_criacao": None,
        "data_modificacao": None,
        "usuario_modificacao": "sistema",
        "linguagem": "desconhecido",
        "tipo_documento": ".pdf",
        "tags": os.path.splitext(os.path.basename(filepath))[0],
        "titulo": None,
        "nivel_acesso": "publico",
        "codigo_autenticacao": None,
    }
    try:
        with open(filepath, "rb") as f:
            reader = PdfReader(f)
            metadata = reader.metadata
            if metadata:
                metadados["autor"] = metadata.author or "Autor Desconhecido"
                metadados["titulo"] = metadata.title

                # Tratamento de data e hora (verifica tipo antes de converter)
                if metadata.creation_date:
                    try:
                        if isinstance(metadata.creation_date, str): # VERIFICA SE É STRING
                            data_criacao = parser.parse(metadata.creation_date)
                        else:  # Se não for string, assume que já é datetime
                            data_criacao = metadata.creation_date
                        metadados["data_criacao"] = data_criacao.astimezone(datetime.timezone.utc).isoformat() + "Z"
                    except Exception as e:
                        print(f"Erro ao converter data de criação do PDF: {e}")

                if metadata.modification_date:
                    try:
                        if isinstance(metadata.modification_date, str): #VERIFICA SE É STRING
                            data_modificacao = parser.parse(metadata.modification_date)
                        else:  # Se não for string, assume que já é datetime
                            data_modificacao = metadata.modification_date
                        metadados["data_modificacao"] = data_modificacao.astimezone(datetime.timezone.utc).isoformat() + "Z"
                    except Exception as e:
                        print(f"Erro ao converter data de modificação do PDF: {e}")

                if hasattr(metadata, 'keywords') and metadata.keywords:
                    metadados["tags"] = metadata.keywords

    except Exception as e:
        print(f"Erro ao ler metadados do PDF: {e}")
        # Mantém valores padrão em caso de erro
    return metadados

def _extrair_metadados_pdf(filepath):
    """Extrai metadados de um arquivo .pdf."""
    metadados = {
        "autor": "Autor Desconhecido",
        "data_criacao": None,
        "data_modificacao": None,
        "usuario_modificacao": "sistema",
        "linguagem": "desconhecido",
        "tipo_documento": ".pdf",
        "tags": os.path.splitext(os.path.basename(filepath))[0],
        "titulo": None,
        "nivel_acesso": "publico",
        "codigo_autenticacao": None,
    }
    try:
        with open(filepath, "rb") as f:
            reader = PdfReader(f)
            metadata = reader.metadata
            if metadata:
                metadados["autor"] = metadata.author or "Autor Desconhecido"
                metadados["titulo"] = metadata.title

                # Tratamento robusto de data e hora
                for date_field in ["creation_date", "modification_date"]:
                    date_str = getattr(metadata, date_field, None)
                    if date_str:
                        try:
                            # Se já for datetime, converte direto
                            if isinstance(date_str, datetime.datetime):
                                date_obj = date_str
                            else:  # Se for string, tenta analisar
                                # Remove o prefixo "D:" e aspas simples
                                date_str = date_str.replace("D:", "").replace("'", "")
                                # Tenta analisar com e sem fuso horário
                                try:
                                    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S%z")
                                except ValueError:
                                    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S")  # Sem fuso
                                    date_obj = date_obj.replace(tzinfo=datetime.timezone.utc) # Assume UTC
                        except Exception as e:
                            print(f"Erro ao converter data ({date_field}) do PDF: {e} ({type(e)})")
                            date_obj = None # Define como None em caso de erro

                        if date_obj:
                            date_str_iso = date_obj.astimezone(datetime.timezone.utc).isoformat() + "Z"
                            metadados[("data_criacao" if date_field == "creation_date" else "data_modificacao")] = date_str_iso


                if hasattr(metadata, 'keywords') and metadata.keywords:
                    metadados["tags"] = metadata.keywords

    except Exception as e:
        print(f"Erro ao ler metadados do PDF: {e} - {type(e)}")
        # Mantém valores padrão em caso de erro
    return metadados

def _extrair_metadados_md(filepath):
    """Extrai metadados de um arquivo .md."""
    metadados = {
        "autor": "Autor Desconhecido",
        "data_criacao": None,  # Inicializa como None
        "data_modificacao": None,  # Inicializa como None
        "usuario_modificacao": "sistema",
        "linguagem": "desconhecido",
        "tipo_documento": ".md",
        "tags": os.path.splitext(os.path.basename(filepath))[0],
        "titulo": None,
        "nivel_acesso": "publico",
        "codigo_autenticacao": None,
    }
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            primeira_linha = f.readline().strip()
            if primeira_linha.startswith("# "):
                metadados["titulo"] = primeira_linha[2:]
        # Obter timestamp em segundos (UTC) e converter para datetime UTC
        data_criacao_ts = os.path.getctime(filepath)
        data_modificacao_ts = os.path.getmtime(filepath)

        metadados["data_criacao"] = datetime.datetime.utcfromtimestamp(data_criacao_ts).isoformat() + "Z"
        metadados["data_modificacao"] = datetime.datetime.utcfromtimestamp(data_modificacao_ts).isoformat() + "Z"

    except Exception as e:
        print(f"Erro ao ler arquivo MD: {e}")
        # Mantém valores padrão em caso de erro
    return metadados

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

        # Determina o tipo de arquivo e extrai metadados
        if nome_arquivo.lower().endswith(".txt"):
            metadados = _extrair_metadados_txt(filepath)
        elif nome_arquivo.lower().endswith(".pdf"):
            metadados = _extrair_metadados_pdf(filepath)
        elif nome_arquivo.lower().endswith(".md"):
            metadados = _extrair_metadados_md(filepath)
        else:
            print(f"Tipo de arquivo não suportado para extração de metadados: {nome_arquivo}")
            return False

        # Inserir Título
        metadados['nome_arquivo'] = nome_arquivo

        sql = """
        INSERT INTO metadados (
            nome_arquivo, autor, data_criacao, data_modificacao, usuario_modificacao,
            linguagem, tipo_documento, tags, nivel_acesso, codigo_autenticacao, titulo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            metadados['nome_arquivo'], metadados['autor'], metadados['data_criacao'], metadados['data_modificacao'], metadados['usuario_modificacao'],
            metadados['linguagem'], metadados['tipo_documento'], metadados['tags'], metadados['nivel_acesso'], metadados['codigo_autenticacao'], metadados['titulo']
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
