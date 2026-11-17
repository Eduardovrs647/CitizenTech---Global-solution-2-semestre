# Citizen Assist AI

## 1. Sobre o projeto

O Citizen Assist AI é um protótipo de assistente digital de orientação cidadã desenvolvido em Python. Seu objetivo é facilitar o acesso a informações sobre documentos, serviços públicos e orientações comunitárias por meio de uma base de conhecimento organizada e de um sistema de busca textual.

O sistema recebe perguntas dos usuários, identifica orientações relacionadas, apresenta respostas resumidas e disponibiliza referências para consulta. Quando não encontra informações suficientes, informa suas limitações em vez de inventar respostas.

## 2. Público e escopo

O projeto é destinado a cidadãos que precisam encontrar informações introdutórias sobre serviços públicos, documentação e orientações comunitárias.

Os principais temas contemplados são:

- **Documentação:** conta gov.br, CPF, Carteira de Identidade Nacional, passaporte e título de eleitor.
- **Serviços:** Cadastro Único, Bolsa Família, seguro-desemprego, Cartão SUS, INSS e defesa do consumidor.
- **Orientações comunitárias:** CRAS, emergências policiais e médicas, violência contra a mulher e violações de direitos humanos.

O protótipo não representa um canal oficial do governo e não substitui o atendimento dos órgãos responsáveis.

## 3. Arquitetura do sistema

O projeto utiliza Python para executar a aplicação e JSON para armazenar as informações.

Estrutura dos arquivos:

```text
Citizen-Assist-AI/
│
├── src/
│   └── sistema.py
│
├── data/
│   └── base.json
│
├── docs/
│   ├── relatorio.pdf
│   ├── link_video.txt
│   └── uso_ia.md
│
└── README.md
```

O arquivo `sistema.py` contém as funções de carregamento, validação, normalização, busca, apresentação das respostas e execução dos testes.

O arquivo `base.json` armazena as orientações, palavras-chave, fontes, datas de verificação, navegação temática, modelos de prompts e perguntas de teste.

## 4. Fontes consultadas

A base utiliza referências de portais institucionais e serviços públicos:

- Governo Federal: https://www.gov.br/
- Conta gov.br: https://www.gov.br/pt-br/servicos/criar-sua-conta-gov.br
- Receita Federal: https://www.gov.br/pt-br/servicos/inscrever-no-cpf
- Carteira de Identidade Nacional: https://www.gov.br/governodigital/pt-br/identidade/cin
- Polícia Federal: https://www.gov.br/pf/pt-br/assuntos/passaporte/documentacao/lista-brasileiro
- Tribunal Superior Eleitoral: https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral
- Cadastro Único: https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico/Cadastro-unico/
- Bolsa Família: https://www.gov.br/mds/pt-br/acoes-e-programas/bolsa-familia/paginas/conheca-as-regras
- Seguro-desemprego: https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego
- Meu SUS Digital: https://www.gov.br/saude/
- Meu INSS: https://meu.inss.gov.br/
- Consumidor.gov.br: https://www.consumidor.gov.br/
- CRAS: https://www.gov.br/mds/
- SAMU: https://www.gov.br/saude/
- Ministério das Mulheres: https://www.gov.br/mulheres/pt-br/ligue180
- Ministério dos Direitos Humanos: https://www.gov.br/mdh/

As referências devem ser consultadas periodicamente para verificar alterações nas informações e nos procedimentos.

## 5. Base de conhecimento

A base de conhecimento está organizada no arquivo `data/base.json` e contém 17 orientações distribuídas em três categorias principais.

Cada registro possui:

- Identificador único;
- Tema e subtema;
- Pergunta de referência;
- Palavras-chave;
- Orientação resumida;
- Nome da fonte;
- Endereço eletrônico da referência;
- Data de verificação;
- Indicação de necessidade de confirmação adicional.

A estrutura utiliza listas e dicionários para facilitar a organização, a leitura e a inclusão de novas informações sem alterações nas regras principais do programa.

## 6. Estratégia de busca

A pesquisa é realizada por comparação textual entre a pergunta do usuário e os campos de identificação dos registros.

O algoritmo executa as seguintes etapas:

1. Recebe a pergunta digitada.
2. Converte o texto para letras minúsculas.
3. Remove acentos e caracteres especiais.
4. Separa os termos relevantes.
5. Compara os termos com perguntas, temas, subtemas e palavras-chave cadastradas.
6. Calcula uma pontuação de correspondência.
7. Seleciona o registro mais adequado, desde que ultrapasse o limite mínimo de confiança.

Quando não existe correspondência suficiente ou há ambiguidade entre resultados, o sistema informa que não encontrou uma orientação confiável.

A navegação temática utiliza uma estrutura de grafo simples, representada por uma lista de adjacência no JSON, permitindo sugerir assuntos relacionados.

## 7. Estratégias de resposta e prompts

O projeto documenta dois modelos de instrução.

**Modelo 1 — Direto**

Define o papel do assistente, determina que as respostas utilizem somente informações presentes na base e exige a apresentação da fonte consultada.

**Modelo 2 — Estruturado**

Organiza a resposta em quatro partes:

- Orientação;
- Próximo passo;
- Fonte;
- Limitações e necessidade de confirmação.

O segundo modelo apresenta maior padronização e facilita a identificação de informações ausentes.

Esses modelos são utilizados como instruções documentadas para a lógica de resposta. O protótipo não realiza chamadas a APIs de inteligência artificial nem utiliza um modelo externo de linguagem.

## 8. Testes e métricas

O arquivo `base.json` contém 15 perguntas de teste, incluindo consultas diretas, reformulações e situações sem resposta prevista.

Os testes contemplam:

- Consultas sobre documentação;
- Consultas sobre serviços públicos;
- Orientações comunitárias;
- Perguntas reformuladas;
- Entrada vazia;
- Perguntas ambíguas;
- Consultas fora dos assuntos cadastrados.

O programa disponibiliza uma função de execução automática dos testes, comparando o identificador esperado com o registro encontrado.

Os indicadores calculados são:

**Taxa de acerto:**

Taxa de acerto = (Quantidade de acertos / Total de perguntas) × 100

**Tempo médio de consulta:**

Tempo médio = Soma dos tempos de consulta / Quantidade de consultas

Os resultados efetivos devem ser obtidos executando a opção 4 do menu. A taxa de acerto mede a correspondência com os resultados esperados cadastrados, não a veracidade completa das orientações.

## 9. Privacidade e limitações

O sistema não solicita CPF, senhas, dados bancários ou outras informações pessoais para realizar consultas.

Entre suas principais limitações estão:

- Base de conhecimento restrita aos assuntos cadastrados;
- Dependência da atualização manual das referências;
- Busca baseada em correspondência textual;
- Possibilidade de não reconhecer perguntas com vocabulário muito diferente;
- Ausência de integração direta com órgãos públicos;
- Ausência de validação automática das informações em tempo real.

O usuário deve confirmar informações importantes diretamente nas fontes oficiais.

## 10. Instruções de execução

**Requisitos:**
- Python 3 instalado;
- Arquivos `src/sistema.py` e `data/base.json` presentes na estrutura do projeto.

Não são necessárias bibliotecas externas, pois o sistema utiliza módulos da biblioteca padrão do Python.

**Execução:**

Abra o terminal na pasta principal do projeto e execute:

```bash
python src/sistema.py
```

O menu disponibiliza as seguintes funcionalidades:

1. Fazer uma pergunta;
2. Consultar por tema;
3. Ver temas disponíveis;
4. Executar testes e métricas;
5. Comparar modelos de prompt;
6. Consultar informações sobre privacidade e limitações;
0. Sair.

## 11. Conclusão

O Citizen Assist AI demonstra como estruturas de dados, manipulação de arquivos JSON, algoritmos de busca e regras lógicas podem ser utilizados para desenvolver uma ferramenta introdutória de orientação cidadã.

A solução organiza informações de diferentes serviços, facilita sua consulta e apresenta referências para que os usuários possam verificar as orientações.

Como melhorias futuras, destacam-se a ampliação da base de conhecimento, a revisão periódica das fontes, o aprimoramento dos algoritmos de busca e a realização de testes com usuários reais.
