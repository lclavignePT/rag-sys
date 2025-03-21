### 2.1. Modelos de Embeddings e Processamento de Linguagem Natural

- **Decisão sobre o Modelo de Embeddings:**

  Após a avaliação de diferentes modelos de embeddings, incluindo `sentence-transformers/all-MiniLM-L6-v2`, `sentence-transformers/all-mpnet-base-v2` e `intfloat/e5-large-v2`, **decidimos selecionar o modelo `intfloat/e5-large-v2` para a prova de conceito do sistema de gestão de documentos.**

- **Justificativa:**

  A escolha do `intfloat/e5-large-v2` foi baseada nos seguintes fatores:

  - **Priorização da Qualidade da Busca:** Para a prova de conceito, priorizamos demonstrar a **mais alta qualidade de busca e relevância dos resultados**. Os testes realizados indicaram que o `intfloat/e5-large-v2` oferece, em geral, **maior precisão semântica** e pontuações de similaridade mais elevadas em comparação com modelos mais leves como o `sentence-transformers/all-mpnet-base-v2`.

  - **Trade-off Desempenho vs. Precisão:** Embora o `intfloat/e5-large-v2` seja um pouco mais lento na geração de embeddings em comparação com o `all-mpnet-base-v2`, o tempo de processamento adicional (em torno de poucos segundos para o conjunto de testes) é considerado **aceitável para a fase de prova de conceito**. Acreditamos que o ganho em qualidade da busca compensa essa pequena diferença em velocidade, especialmente para demonstrar o potencial do sistema.

  - **Flexibilidade para Otimizações Futuras:** Caso a performance se torne um gargalo em cenários de uso com maior volume de documentos ou em produção, otimizações de desempenho (como batching, quantização ou destilação de modelo) poderão ser exploradas no futuro, mantendo o `e5-large-v2` como base pela sua qualidade superior.

- **Alternativas Consideradas (e Razões para Não Escolher):**

  - **`sentence-transformers/all-MiniLM-L6-v2`:** Embora seja o modelo mais leve e rápido, foi considerado **menos robusto em termos de precisão semântica** para as necessidades da prova de conceito.

  - **`sentence-transformers/all-mpnet-base-v2`:** Apresentou um **bom equilíbrio entre velocidade e precisão**, sendo significativamente mais rápido que o `e5-large-v2`. No entanto, em termos de **qualidade geral da busca e pontuações de similaridade**, o `e5-large-v2` demonstrou ser superior nos testes iniciais.

Ao documentar essas decisões e justificativas, garantimos que o processo de desenvolvimento seja transparente, rastreável e alinhado com os objetivos do projeto.

### Seção 5. Autenticação e Segurança

#### 5.1. Estratégia de Autenticação

- **Mecanismo de Proteção do `codigo_autenticacao`:**

  Para garantir a segurança dos documentos restritos e confidenciais, o `codigo_autenticacao` **nunca será armazenado em texto puro** no banco de dados SQLite. Em vez disso, utilizaremos **hashing criptográfico com sal** para armazenar uma representação segura do código de autenticação.

  - **Algoritmo de Hashing:** Será utilizada a biblioteca `bcrypt` em Python, empregando um algoritmo de hashing forte e seguro (bcrypt) juntamente com a geração automática de "sal" (salt) para cada `codigo_autenticacao`.

  - **Fluxo de Autenticação:**

    1.  **Geração do Hash:** Ao definir um `codigo_autenticacao` para um documento restrito, o sistema utilizará a biblioteca `bcrypt` para gerar um hash seguro do código, incluindo um sal aleatório.
    2.  **Armazenamento do Hash:** Apenas o hash gerado (e não o código original) será armazenado na coluna `codigo_autenticacao` da tabela `metadados` no banco de dados SQLite.
    3.  **Verificação de Autenticação:** Quando um usuário fornecer um código de autenticação para acessar um documento restrito:
        - O sistema irá gerar um novo hash do código fornecido pelo usuário, utilizando a mesma biblioteca `bcrypt` e o sal (que é armazenado implicitamente ou explicitamente junto com o hash, dependendo da implementação do `bcrypt`).
        - O sistema irá comparar o hash recém-gerado com o hash armazenado no banco de dados.
        - Se os hashes coincidirem, a autenticação será bem-sucedida e o acesso ao documento será concedido. Caso contrário, o acesso será negado.

  Essa abordagem garante que, mesmo que o arquivo do banco de dados SQLite seja comprometido, os códigos de autenticação originais permanecerão protegidos, pois apenas os hashes (que são computacionalmente difíceis de reverter) estarão armazenados.
