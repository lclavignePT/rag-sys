import torch
from src.database.database_operations import inserir_metadados, obter_metadados_por_nome_arquivo
from src.tests.test_models import load_test_documents, generate_embeddings, MODEL_NAMES
from src.utils.db_vectores import criar_indice_chromadb, buscar_documentos_chromadb

if __name__ == "__main__":
    DATA_DIR_TEST_DOCUMENTS = "data/test_documents"
    documentos_teste = load_test_documents(DATA_DIR_TEST_DOCUMENTS)

    if not documentos_teste:
        print(f"Nenhum documento de teste encontrado em {DATA_DIR_TEST_DOCUMENTS}.")
        exit()

#    print(f"Iniciando inserção de metadados para documentos em '{DATA_DIR_TEST_DOCUMENTS}':")
#    for nome_arquivo_teste in documentos_teste.keys():
#        insercao_sucesso = inserir_metadados(nome_arquivo_teste)
#        if not insercao_sucesso:
#            print(f"  - Falha ao inserir metadados para '{nome_arquivo_teste}'. Abortando.")
#            exit()
#        else:
#            print(f"  - Metadados para '{nome_arquivo_teste}' inseridos com sucesso.")
#
#    print("Inserção de metadados concluída.")

    # --- Geração de Embeddings e Criação do Índice ChromaDB ---
    model_name = MODEL_NAMES[2]  # Usar o primeiro modelo da lista por enquanto
    print(f"Gerando embeddings com modelo: {model_name}")
    embeddings_docs, document_filenames, embedding_time = generate_embeddings(
    model_name, documentos_teste, device="cpu"
)  # Passando lista de queries vazia
    print(f"Embeddings gerados para o modelo {model_name}.")

    print("Criando índice ChromaDB...")
    criar_indice_chromadb(documentos_teste, embeddings_docs)
    print("Índice ChromaDB criado.")

    # --- Loop de Busca (Simulação de Produção) - Redirecionando Saída ---
    print("\n--- Simulando Busca em Produção ---")

    with open("resultados_busca.txt", "w", encoding="utf-8") as output_file:
        while True:
            query = input("Digite sua pergunta (ou deixe em branco para sair): ")
            if not query:
                break

            tipo_documento_filtro = input("Filtrar por tipo de documento (pdf, txt, md, ou deixe em branco para todos): ").strip().lower() # Pede o tipo de documento para filtro

            resultados = buscar_documentos_chromadb(query, model_name, tipo_documento_filtro=tipo_documento_filtro) # Passa o filtro para a função de busca

            if resultados:
                print("\nResultados da busca:", file=output_file)
                for resultado in resultados:
                    print(f"  - Nome do arquivo: {resultado['nome_arquivo']} (Tipo: {resultado['tipo_documento']})", file=output_file) # Mostra o tipo de documento nos resultados
                    print(f"    Trecho: {resultado['trecho']}", file=output_file)
                    print(f"    Score: {resultado['score']:.4f}", file=output_file)
                    print("-" * 20, file=output_file)
            else:
                print("Nenhum documento encontrado para a sua busca.", file=output_file)

    print("Programa encerrado. Resultados da busca salvos em 'resultados_busca.txt'.")