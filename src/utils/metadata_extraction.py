import os
import datetime
import statx
from PyPDF2 import PdfReader

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
