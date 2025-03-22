from transformers import pipeline

def classificar_query(query):
    """
    Classifica a query do usuário em um tipo (busca semântica, contagem, listagem, etc.)
    usando um modelo de classificação de texto.

    Args:
        query (str): A query do usuário.

    Returns:
        str: O tipo da query (ex: "busca_semantica", "contagem", "listagem").
    """
    # Carrega o modelo de classificação pré-treinado (substitua pelo modelo desejado)
    classifier = pipeline("text-classification", model="distilbert-base-multilingual-cased")

    # Mapeamento de rótulos de classe para nomes de classe (MUITO IMPORTANTE: Ajuste se mudar as classes!)
    label_mapping = {
        "LABEL_0": "busca_semantica",
        "LABEL_1": "contagem",
        "LABEL_2": "listagem",
    }

    # Adiciona um prompt à query
    prompt = "Classifique o tipo da seguinte query de busca de documentos: "
    query_com_prompt = prompt + query

    try:
        result = classifier(query_com_prompt) # Usa a query COM o prompt
        predicted_label = result[0]['label']

        return label_mapping.get(predicted_label, "busca_semantica")

    except Exception as e:
        print(f"Erro ao classificar a query: {e}")
        return "busca_semantica"
    
if __name__ == "__main__":
    queries = [
        "Quantos arquivos PDF eu tenho?",
        "Mostre todos os arquivos TXT",
        "relatório do projeto X",
        "Quero ver os documentos sobre segurança.",
        "Listar os arquivos modificados em 2024",
        "Número de arquivos .md",
        "buscar documentos sobre automação",
        "Existe algum documento sobre backup?",
        "documentos do autor João Silva"
    ]

    for query in queries:
        tipo = classificar_query(query)
        print(f"Query: '{query}' -> Tipo: {tipo}")