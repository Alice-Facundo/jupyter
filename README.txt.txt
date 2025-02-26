Sistema de Gestão de Voluntários e Animais

Este projeto é uma aplicação web desenvolvida em Python utilizando o Streamlit. 
A aplicação possibilita o gerenciamento de informações de voluntários e animais por meio 
de uma interface interativa, permitindo as operações de cadastro, edição, listagem e exclusão 
de registros armazenados em um banco de dados PostgreSQL.

------------------------------------------------------------
Funcionalidades:

Gerenciamento de Voluntários:
- Cadastro: Inserção de ID, nome, CPF, contato e área de atuação.
- Listagem: Exibição de todos os voluntários com opção de filtrar por nome ou CPF.
- Edição: Atualização dos dados dos voluntários.
- Exclusão: Remoção de registros, com deleção de dados dependentes em tabelas relacionadas.

Gerenciamento de Animais:
- Cadastro: Inserção de ID, ID do Lar Temporário, nome, porte, raça, idade e sexo.
- Listagem: Exibição de todos os animais com opção de filtrar por nome ou ID.
- Edição: Atualização dos dados dos animais.
- Exclusão: Remoção de registros, incluindo a deleção de dados dependentes em tabelas relacionadas 
  (como registros de saúde, testes de convívio, feedbacks e adoções).

------------------------------------------------------------
Tecnologias Utilizadas:

- Python 3.x
- Streamlit
- SQLAlchemy
- psycopg2
- PIL (Pillow)

------------------------------------------------------------
Pré-requisitos:

- Python 3.7 ou superior
- PostgreSQL instalado e configurado
- As tabelas "voluntario" e "animal" devem existir no banco de dados
- Dependências Python instaladas 

------------------------------------------------------------
Configuração do Banco de Dados:

- Atualize as variáveis DATABASE_URL e DATABASE_URL2 no código com as credenciais corretas do seu PostgreSQL.
  Exemplo:
    DATABASE_URL = "postgresql://usuario:senha@localhost/nome_do_banco"
    DATABASE_URL2 = "dbname=nome_do_banco user=usuario password=senha host=localhost"
- Certifique-se de que as tabelas "voluntario" e "animal" estejam criadas no banco de dados.

------------------------------------------------------------
Execução da Aplicação:

Para iniciar a aplicação, execute o comando abaixo na raiz do projeto:
    streamlit run adocaoanimais.py

------------------------------------------------------------
Estrutura do Código:

- Conexão e configuração do banco de dados utilizando SQLAlchemy e psycopg2.
- Função "executar_query" para centralizar as consultas de leitura com psycopg2, retornando resultados como dicionários.
- Interface interativa construída com Streamlit, que exibe:
  - Uma logo centralizada.
  - Um menu lateral para alternar entre "Gerenciar Voluntários" e "Gerenciar Animais".
  - Formulários para cadastro, edição e deleção dos registros.
- Operações CRUD (Create, Read, Update, Delete) para voluntários e animais, garantindo a integridade dos dados com transações e rollback em caso de erro.

------------------------------------------------------------
Considerações Finais:

- A aplicação utiliza transações para garantir a integridade do banco de dados.
- O layout e as funcionalidades podem ser customizados conforme necessário.
- Mensagens de sucesso e erro são exibidas para fornecer feedback ao usuário.

