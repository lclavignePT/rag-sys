import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from src.database.database_operations import obter_metadados_por_nome_arquivo

load_dotenv()

DATABASE_DIR = os.environ.get("RAG_DATABASE_DIR", "data")

def criar_indice_chromadb(documentos, embeddings, index_name="documentos_index"):
    """Cria um índice ChromaDB com os documentos e embeddings fornecidos."""

    # Garante que o diretório de dados exista
    os.makedirs(DATABASE_DIR, exist_ok=True)

    # Cria um cliente ChromaDB persistente (salva os dados em disco)
    client = chromadb.PersistentClient(path=os.path.join(DATABASE_DIR, "chroma_db"))

    # Cria uma coleção (se já existir, ele a reutiliza, para foi adicionado o get_or_create_collection)
    collection = client.get_or_create_collection(name=index_name)

    # Prepara os dados para inserção no ChromaDB
    ids = list(documentos.keys())  # Usa os nomes dos arquivos como IDs
    textos = list(documentos.values())  # Conteúdo dos documentos

    # Adiciona os documentos e embeddings à coleção
    collection.add(
        embeddings=embeddings.tolist(),  # Converte embeddings para lista (se forem tensores)
        documents=textos,
        ids=ids,
    )
    print(f"Índice ChromaDB '{index_name}' criado/atualizado com sucesso.")

def buscar_documentos_chromadb(query, model_name, index_name="documentos_index", n_results=30, tipo_documento_filtro=None): # Adicionado tipo_documento_filtro
    """Busca documentos no índice ChromaDB com base em uma query, com filtro opcional por tipo de documento."""

    # Carrega o modelo de embedding
    model = SentenceTransformer(model_name)
    query_embedding = model.encode(query, convert_to_tensor=True).tolist()

    # Cria um cliente ChromaDB persistente
    client = chromadb.PersistentClient(path=os.path.join(DATABASE_DIR, "chroma_db"))

    # Obtém a coleção
    collection = client.get_collection(name=index_name)
    if collection is None:
        print(f"Erro: Coleção ChromaDB '{index_name}' não encontrada.")
        return []

    # Realiza a busca por similaridade
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances"] # Pega documentos e distâncias
    )

    resultados_formatados = []
    if results and results['ids'][0]:
        for i, doc_id in enumerate(results['ids'][0]):
            nome_arquivo = doc_id # doc_id é o nome do arquivo
            metadados = obter_metadados_por_nome_arquivo(nome_arquivo) # Busca metadados no SQLite

            if metadados:
                tipo_doc_resultado = metadados.get("tipo_documento") # Obtém o tipo de documento dos metadados
            else:
                tipo_doc_resultado = None

            # Aplica o filtro por tipo de documento (se especificado)
            print(f"Debug: tipo_documento_filtro = '{tipo_documento_filtro}', tipo_doc_resultado = '{tipo_doc_resultado}'")
            if tipo_documento_filtro is None or tipo_doc_resultado.lower().lstrip('.') == tipo_documento_filtro.lower(): # Filtro
                resultados_formatados.append(
                    {
                        "nome_arquivo": nome_arquivo,
                        "score": results['distances'][0][i],
                        "trecho": results['documents'][0][i],
                        "tipo_documento": tipo_doc_resultado, # Adiciona tipo de documento aos resultados
                    }
                )
            else:
                print(f"Documento '{nome_arquivo}' filtrado por tipo: {tipo_doc_resultado}. Filtro: {tipo_documento_filtro}") # Mensagem de filtro

    return resultados_formatados
