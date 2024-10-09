# Sistema Eureka®

## Introdução
O **Eureka®** é um sistema inovador desenvolvido para integrar quatro áreas cruciais da gestão industrial: Engenharia, PCP (Planejamento e Controle da Produção), Compras e Comercial. O objetivo do sistema é centralizar informações e automatizar processos, promovendo uma colaboração mais eficiente entre setores e decisões estratégicas mais ágeis, baseadas em dados confiáveis.

O sistema tem como principal fonte de dados o **TOTVS** e busca aprimorar a experiência do usuário, tornando a interface mais intuitiva e dinâmica. Além disso, o Eureka® proporciona uma redução no uso de licenças do TOTVS, melhorando a eficiência das operações e eliminando disputas por licenças entre os usuários.

## Benefícios
- **Automação de Processos:** Centraliza informações de diferentes setores, promovendo maior colaboração.
- **Redução no uso de licenças TOTVS:** Menor concorrência entre usuários do SmartClient.
- **Substituição de Planilhas Excel:** Elimina os riscos associados a conflitos de revisão de arquivos em nuvem, garantindo maior integridade e confiabilidade dos dados.
- **Agilidade nas Consultas:** Interface melhorada para consultas mais rápidas e pontuais, substituindo o uso do ERP Protheus.

## Módulos do Sistema
### 1. Módulo Engenharia
- **Consulta de Produtos:** Permite pesquisar produtos por código, descrição, tipo, unidade de medida, armazém, grupo, entre outros.
- **Cadastro de Produto:** Permite criar novos produtos ou copiar dados de produtos existentes para agilizar o cadastro.
- **Alteração de Cadastro de Produto:** Realiza modificações em produtos já cadastrados.
- **Consulta de Estrutura de Produtos:** Permite visualizar e alterar as quantidades de itens de uma estrutura.
- **Saldo em Estoque:** Informa o saldo atual de um produto, incluindo quantidade disponível, empenhada e prevista.
- **Últimos Fornecedores:** Mostra os últimos fornecedores de um determinado item.
- **Histórico de Compras:** Exibe as últimas notas fiscais de entrada de um item.

### 2. Módulo PCP
- **Gestão de Ordens de Produção:** Facilita a consulta e o gerenciamento de Ordens de Produção (OPs), com funcionalidades futuras para impressão e fechamento das OPs.
- **Desenvolvimento em PyQt5.**

### 3. Módulo Compras
- **Acompanhamento de SCs e PCs:** Facilita o acompanhamento de Solicitações de Compra (SCs) e Pedidos de Compra (PCs).
- **Follow-up e Consultas:** Acesso a notas fiscais e histórico de compras.
- **Filtros de Pesquisa:** Possibilidade de criar filtros nas tabelas para refinar as pesquisas.

### 4. Módulo Comercial
- **Cálculo de Custos:** Auxilia os profissionais da área comercial no cálculo e análise de custos de matérias-primas e itens comerciais.
- **Relatórios de Custo:** Gera relatórios detalhados de custos, com exportação para Excel e PDF.
- **Análises Simultâneas:** Permite abrir várias janelas para comparar custos de diferentes produtos.

## Como Usar
### Módulo Comercial:
1. Acesse a tela inicial e clique em "COMERCIAL" para abrir a aplicação.
2. Insira o código do produto e clique em "Calcular Custo ($)".
3. Visualize os custos detalhados e exporte os relatórios em Excel ou PDF.
4. Para comparar produtos diferentes, abra novas janelas com o botão "Nova Janela".

## Suporte
Caso encontre **bugs** ou tenha **dúvidas**, entre em contato com a equipe de suporte. Estamos disponíveis para esclarecimentos e contamos com sua colaboração para reportar eventuais problemas.

Para sugestões e melhoria, envie um [e-mail](eliezer.moraes@outlook.com.br).


# Consulta de QPs - EUREKA® PCP (Portuguese)

## Descrição

Este projeto é uma aplicação desktop desenvolvida em Python que utiliza a biblioteca PyQt5 para criar uma interface gráfica de usuário (GUI) para consultar, atualizar e exportar dados de QPs (Quadros de Projetos). A aplicação se conecta a um banco de dados MSSQL para realizar operações de consulta e manipulação de dados. A interface é intuitiva e foi projetada para facilitar a navegação e a manipulação de informações importantes.

### Funcionalidades

- **Consulta de QPs:** A aplicação permite consultar QPs com diferentes status (abertos, concluídos, todos).
- **Atualização de Tabela:** Possibilidade de atualizar dados de QPs diretamente pela interface.
- **Exportação para Excel:** Dados da tabela podem ser exportados para um arquivo Excel.
- **Filtragem por Descrição e QP:** Filtragem avançada com múltiplas opções para localizar QPs específicos.
- **Interface de Usuário Personalizada:** Estilo moderno e visual atraente, projetado para melhorar a experiência do usuário.

### Instalação

1. **Clone o repositório:**
    ```bash
    git clone <URL-do-repositório>
    ```

2. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configuração do Banco de Dados:**
   - Certifique-se de que o arquivo de configuração `USER_PASSWORD_MSSQL_PROD.txt` esteja no caminho especificado com as credenciais corretas.
   - Ajuste o caminho no código, se necessário.

4. **Execute a aplicação:**
    ```bash
    python main.pyw
    ```

### Dependências

- Python 3.x
- PyQt5
- Pandas
- Requests
- SQLAlchemy
- Pyperclip

### Estrutura do Projeto

- `main.py`: Arquivo principal contendo a lógica da aplicação.
- `resources/`: Diretório contendo imagens e outros recursos.
- `libs-python/`: Diretório contendo bibliotecas e arquivos de configuração, como as credenciais do banco de dados.

### Consultas SQL Utilizadas

Aqui estão todas as consultas SQL utilizadas na aplicação:

#### Consulta de QPs

```sql
SELECT
    cod_qp AS "QP",
    des_qp AS "NOME DO PROJETO",
    status_qp AS "STATUS QP",
    dt_open_qp AS "DATA DE EMISSÃO",
    dt_end_qp AS "PRAZO DE ENTREGA",
    dt_completed_qp AS "DATA DE ENTREGA",
    vl_delay AS "DIAS EM ATRASO",
    status_delivery AS "STATUS ENTREGA"
FROM 
    enaplic_management.dbo.tb_qps
WHERE
    cod_qp LIKE '%{numero_qp}'
    AND des_qp LIKE '{descricao}%'
    AND {clausulas_contem_descricao}
    AND status_qp = '{status_qp}'
ORDER BY id DESC;
```

#### Contagem de Resultados

```sql
SELECT
    COUNT(*) AS count
FROM 
    (
        SELECT
            cod_qp AS "QP",
            des_qp AS "NOME DO PROJETO",
            status_qp AS "STATUS QP",
            dt_open_qp AS "DATA DE EMISSÃO",
            dt_end_qp AS "PRAZO DE ENTREGA",
            dt_completed_qp AS "DATA DE ENTREGA",
            vl_delay AS "DIAS EM ATRASO",
            status_delivery AS "STATUS ENTREGA"
        FROM 
            enaplic_management.dbo.tb_qps
        WHERE
            cod_qp LIKE '%{numero_qp}'
            AND des_qp LIKE '{descricao}%'
            AND {clausulas_contem_descricao}
            AND status_qp = '{status_qp}'
    ) AS results;
```

#### Atualização da Data de Entrega (Data Concluída)

```sql
UPDATE enaplic_management.dbo.tb_qps
SET dt_completed_qp = :selected_date
WHERE cod_qp = :cod_qp;
```

#### Remoção da Data de Entrega

```sql
UPDATE enaplic_management.dbo.tb_qps
SET dt_completed_qp = ''
WHERE cod_qp = :cod_qp;
```

### Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

# QP Inquiry - EUREKA® PCP (English)

## Description

This project is a desktop application developed in Python using the PyQt5 library to create a graphical user interface (GUI) for querying, updating, and exporting QP (Project Frame) data. The application connects to an MSSQL database to perform data query and manipulation operations. The interface is intuitive and designed to facilitate navigation and handling of important information.

### Features

- **QP Query:** The application allows you to query QPs with different statuses (open, closed, all).
- **Table Update:** Ability to update QP data directly from the interface.
- **Export to Excel:** Table data can be exported to an Excel file.
- **Filtering by Description and QP:** Advanced filtering with multiple options to locate specific QPs.
- **Customized User Interface:** Modern style and attractive visuals designed to enhance the user experience.

### Installation

1. **Clone the repository:**
    ```bash
    git clone <repository-URL>
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Database Configuration:**
   - Make sure the configuration file `USER_PASSWORD_MSSQL_PROD.txt` is in the specified path with the correct credentials.
   - Adjust the path in the code if necessary.

4. **Run the application:**
    ```bash
    python main.pyw
    ```

### Dependencies

- Python 3.x
- PyQt5
- Pandas
- Requests
- SQLAlchemy
- Pyperclip

### Project Structure

- `main.py`: Main file containing the application logic.
- `resources/`: Directory containing images and other resources.
- `libs-python/`: Directory containing libraries and configuration files, such as database credentials.

### SQL Queries Used

Here are all the SQL queries used in the application:

#### QP Query

```sql
SELECT
    cod_qp AS "QP",
    des_qp AS "PROJECT NAME",
    status_qp AS "QP STATUS",
    dt_open_qp AS "ISSUE DATE",
    dt_end_qp AS "DELIVERY DEADLINE",
    dt_completed_qp AS "DELIVERY DATE",
    vl_delay AS "DAYS DELAYED",
    status_delivery AS "DELIVERY STATUS"
FROM 
    enaplic_management.dbo.tb_qps
WHERE
    cod_qp LIKE '%{numero_qp}'
    AND des_qp LIKE '{descricao}%'
    AND {clausulas_contem_descricao}
    AND status_qp = '{status_qp}'
ORDER BY id DESC;
```

#### Counting Results

```sql
SELECT
    COUNT(*) AS count
FROM 
    (
        SELECT
            cod_qp AS "QP",
            des_qp AS "PROJECT NAME",
            status_qp AS "QP STATUS",
            dt_open_qp AS "ISSUE DATE",
            dt_end_qp AS "DELIVERY DEADLINE",
            dt_completed_qp AS "DELIVERY DATE",
            vl_delay AS "DAYS DELAYED",
            status_delivery AS "DELIVERY STATUS"
        FROM 
            enaplic_management.dbo.tb_qps
        WHERE
            cod_qp LIKE '%{numero_qp}'
            AND des_qp LIKE '{descricao}%'
            AND {clausulas_contem_descricao}
            AND status_qp = '{status_qp}'
    ) AS results;
```

#### Updating Delivery Date (Completed Date)

```sql
UPDATE enaplic_management.dbo.tb_qps
SET dt_completed_qp = :selected_date
WHERE cod_qp = :cod_qp;
```

#### Removing Delivery Date
```sql
UPDATE enaplic_management.dbo.tb_qps
SET dt_completed_qp = ''
WHERE cod_qp = :cod_qp;
```

### Contributions
Contributions are welcome! Feel free to open issues and pull requests.
