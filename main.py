from src.database.database_operations import inserir_metadados
from src.tests.test_models import load_test_documents
import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"GPU está disponível! Dispositivo: {device}")
    print(f"Nome da GPU: {torch.cuda.get_device_name(0)}") # Pega o nome da primeira GPU
else:
    device = torch.device("cpu")
    print("GPU não está disponível, usando CPU.")

print(f"Dispositivo atual: {device}")

if __name__ == "__main__":
    # Pasta onde estão os documentos de teste (a mesma que usamos em test_models.py)
    DATA_DIR_TEST_DOCUMENTS = "data/test_documents"

    # Carrega os nomes dos arquivos de teste da pasta
    documentos_teste = load_test_documents(DATA_DIR_TEST_DOCUMENTS)

    if not documentos_teste:
        print(f"Nenhum documento de teste encontrado na pasta '{DATA_DIR_TEST_DOCUMENTS}'. Adicione arquivos lá para testar a inserção de metadados.")
    else:
        print(f"Iniciando teste de inserção de metadados para documentos em '{DATA_DIR_TEST_DOCUMENTS}':")
        for nome_arquivo_teste in documentos_teste.keys(): # Itera sobre os nomes dos arquivos carregados
            insercao_sucesso = inserir_metadados(
                nome_arquivo=nome_arquivo_teste,
                autor="Autor Desconhecido", # Metadados de exemplo genéricos
                data_criacao="2024-01-01 00:00:00", # Metadados de exemplo genéricos
                data_modificacao="2024-01-01 00:00:00", # Metadados de exemplo genéricos
                usuario_modificacao="sistema", # Metadados de exemplo genéricos
                linguagem="desconhecido", # Metadados de exemplo genéricos
                tipo_documento="desconhecido", # Metadados de exemplo genéricos
                tags="teste,inicial,exemplo", # Metadados de exemplo genéricos
                nivel_acesso="publico", # Metadados de exemplo genéricos
                codigo_autenticacao=None  # Metadados de exemplo genéricos
            )

            if insercao_sucesso:
                print(f"  - Metadados para '{nome_arquivo_teste}' inseridos com sucesso.")
            else:
                print(f"  - Falha ao inserir metadados para '{nome_arquivo_teste}'. Verifique os erros acima.")

        print("Teste de inserção de metadados para documentos de teste concluído.")