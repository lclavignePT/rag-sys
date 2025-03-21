import torch
from src.database.database_operations import inserir_metadados, obter_metadados_por_nome_arquivo, buscar_metadados_por_tags
from src.tests.test_models import load_test_documents, generate_embeddings, MODEL_NAMES

# if torch.cuda.is_available():
#     device = torch.device("cuda")
#     print(f"GPU está disponível! Dispositivo: {device}")
#     print(f"Nome da GPU: {torch.cuda.get_device_name(0)}") # Pega o nome da primeira GPU
# else:
#     device = torch.device("cpu")
#     print("GPU não está disponível, usando CPU.")
# 
# print(f"Dispositivo atual: {device}")

if __name__ == "__main__":
    DATA_DIR_TEST_DOCUMENTS = "data/test_documents"
    documentos_teste = load_test_documents(DATA_DIR_TEST_DOCUMENTS)

    if not documentos_teste:
        print(f"Nenhum documento de teste encontrado em {DATA_DIR_TEST_DOCUMENTS}.")
        exit() # Sai do script se não houver documentos

    print(f"Iniciando inserção de metadados e geração de embeddings para documentos em '{DATA_DIR_TEST_DOCUMENTS}':")
    for nome_arquivo_teste in documentos_teste.keys():
        insercao_sucesso = inserir_metadados(nome_arquivo_teste)
        if not insercao_sucesso:
            print(f"  - Falha ao inserir metadados para '{nome_arquivo_teste}'. Abortando.")
            exit() # Sai do script se houver falha na inserção
        else:
            print(f"  - Metadados para '{nome_arquivo_teste}' inseridos com sucesso.")

    print("Inserção de metadados concluída. Gerando embeddings...")

    # Geração de Embeddings
    for model_name in MODEL_NAMES:
        print(f"Gerando embeddings com modelo: {model_name}")
        embeddings_docs, _, _, _ = generate_embeddings(
            model_name, documentos_teste, [], device="cpu"
        )  # Passando lista de queries vazia, pois não estamos usando aqui
        print(f"Embeddings gerados para o modelo {model_name}.")

    print("Teste de inserção de metadados, geração de embeddings e busca por tags concluído.")