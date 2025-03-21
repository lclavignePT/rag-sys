#!/usr/bin/env python3

import torch
from sentence_transformers import SentenceTransformer, util
from InstructorEmbedding import INSTRUCTOR
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import time

# Definir o dispositivo: GPU se disponível, senão CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo usado: {device}")

# Pasta onde estão os documentos de teste
DATA_DIR = "data/test_documents"

# Modelos a serem testados
MODEL_NAMES = ["intfloat/e5-large-v2", "intfloat/multilingual-e5-large", "sentence-transformers/sentence-t5-xl"]

# Queries de busca de exemplo
QUERIES = [
    "Encontre o relatório sobre o projeto X",
    "Quais documentos mencionam a data de 2023?",
    "Busque por informações sobre o processo de homologação",
    "Documentos relacionados a segurança da informação"
]

def load_test_documents(data_dir):
    documents = {}
    for filename in os.listdir(data_dir):
        if filename.endswith((".txt", ".pdf", ".docx", ".html", ".md")): # Adicione as extensões relevantes
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f: # Tenta ler como texto
                    documents[filename] = f.read()
            except UnicodeDecodeError: # Se falhar como texto, tenta ler como bytes (pode ser binário)
                try:
                    with open(filepath, "r", encoding="latin-1") as f: # Tenta encoding latin-1 para alguns binários como PDF extraído como texto
                        documents[filename] = f.read()
                except Exception as e:
                    print(f"Erro ao ler arquivo {filename}: {e}")
                    continue # Pula para o próximo arquivo em caso de erro
            except Exception as e:
                print(f"Erro ao ler arquivo {filename}: {e}")
                continue
    return documents

def generate_embeddings(model_name, documents, device): # REMOVED 'queries' parameter
    """
    Gera embeddings para uma lista de documentos usando um modelo Sentence Transformer.

    Args:
        model_name (str): Nome do modelo Sentence Transformer a ser usado.
        documents (dict): Dicionário de documentos (nome_arquivo: conteúdo).
        device (torch.device): Dispositivo (CPU ou GPU) para rodar o modelo.

    Returns:
        tuple: (embeddings_docs, document_filenames, embedding_time)
               - embeddings_docs: Embeddings dos documentos (torch.Tensor).
               - document_filenames: Lista de nomes de arquivos dos documentos.
               - embedding_time: Tempo total para gerar os embeddings.
    """
    start_time = time.time()
    print(f"Carregando modelo: {model_name}")
    model = SentenceTransformer(model_name).to(device)
    corpus = list(documents.values())
    embeddings_docs = model.encode(corpus, convert_to_tensor=True, device=device)
    end_time = time.time()
    embedding_time = end_time - start_time
    print(f"Modelo {model_name} carregado e embeddings gerados em {embedding_time:.2f} segundos.")
    return embeddings_docs, list(documents.keys()), embedding_time

def search_and_evaluate(embeddings_docs, embeddings_queries, document_filenames, model_name):
    print(f"\n--- Resultados para o modelo: {model_name} ---")
    for query_idx, query in enumerate(QUERIES):
        print(f"\nQuery: '{query}'")
        query_embedding = embeddings_queries[query_idx] # Embedding da query atual

        if isinstance(embeddings_docs, np.ndarray): # Para modelos INSTRUCTOR (embeddings numpy)
            similarities = cosine_similarity(query_embedding.reshape(1, -1), embeddings_docs)[0] # Calcula similaridades
            doc_scores = list(zip(document_filenames, similarities)) # Combina filename e similaridade
        elif isinstance(embeddings_docs, torch.Tensor): # Para Sentence Transformers (embeddings torch)
            similarities = util.cos_sim(query_embedding, embeddings_docs).cpu().tolist()[0] # Similaridade de cossenos com Sentence Transformers
            doc_scores = list(zip(document_filenames, similarities)) # Combina filename e similaridade
        else:
            raise TypeError("Tipo de embedding de documentos não suportado. Deve ser numpy.ndarray ou torch.Tensor")


        doc_scores.sort(key=lambda x: x[1], reverse=True) # Ordena por similaridade (descendente)

        print("Documentos mais relevantes:")
        for doc_name, score in doc_scores[:3]: # Mostra os 3 documentos mais relevantes
            print(f"- {doc_name}: (Similaridade: {score:.4f})")

def main():
    documents = load_test_documents(DATA_DIR) # Carrega documentos de teste
    if not documents:
        print(f"Nenhum documento encontrado em {DATA_DIR}. Adicione documentos de teste lá.")
        return

    for model_name in MODEL_NAMES: # Itera sobre os modelos definidos
        embeddings_docs, embeddings_queries, document_filenames, embedding_time = generate_embeddings(
            model_name, documents, QUERIES, device
        )
        search_and_evaluate(embeddings_docs, embeddings_queries, document_filenames, model_name)
        print(f"\nTempo total de embedding para {model_name}: {embedding_time:.2f} segundos.\n")

if __name__ == "__main__":
    main()