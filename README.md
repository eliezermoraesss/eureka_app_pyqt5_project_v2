# EUREKA!® Sistema integrado de gestão industrial

<p align="center">
<img loading="lazy" src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=for-the-badge"/>
</p>

## 📑 Índice 

- [EUREKA!® Sistema integrado de gestão industrial](#eureka-sistema-integrado-de-gestão-industrial)
  - [📑 Índice](#-índice)
  - [🚀 Introdução](#-introdução)
  - [🎯 Benefícios](#-benefícios)
  - [🛠️ Módulos do Sistema](#️-módulos-do-sistema)
    - [1. Módulo Engenharia 🏗️](#1-módulo-engenharia-️)
    - [2. Módulo PCP 🏭](#2-módulo-pcp-)
    - [3. Módulo Compras 🛒](#3-módulo-compras-)
    - [4. Módulo Comercial 📊](#4-módulo-comercial-)
    - [5. Módulo Vendas 💼](#5-módulo-vendas-)
    - [6. Recursos Adicionais ⚙️](#6-recursos-adicionais-️)
    - [6.1. Autocomplete e Histórico de Pesquisa 🔍](#61-autocomplete-e-histórico-de-pesquisa-)
    - [6.2. Estrutura Explodida de Produtos 🌳](#62-estrutura-explodida-de-produtos-)
  - [📞 Suporte](#-suporte)
  - [💻 Tecnologias Utilizadas](#-tecnologias-utilizadas)
  - [📁 Acesso ao Projeto](#-acesso-ao-projeto)
  - [👥 Autores](#-autores)
  - [📝 Licença](#-licença)

## 🚀 Introdução
O **Eureka!®** é uma aplicação desktop com o objetivo de 
proporcionar ao usuário uma experiência de usabilidade fácil, dinâmica e limpa.

Seu design foi pensado para ser agradável e fácil de usar.
Ele centraliza e integra dados de diferentes departamentos, Engenharia, PCP, Compras, Comercial e Vendas, proporcionando uma visão 
integrada, limpa e centralizada.

Sua fonte de dados é a base de dados SQL Server do ERP TOTVS Protheus, garantindo 
confiabilidade e precisão nas informações, além de automatizar processos manuais, reduzindo 
erros e aumentando a produtividade. 

Com uma interface moderna e intuitiva o Eureka!® agiliza consultas e cadastros, reduzindo tempo e aumentando a produtividade do usuário. 
Sua flexibilidade permite exportação de relatórios nos formatos Excel e PDF.
Além disso, a solução reduz a concorrência por licenças TOTVS, gerando economia sem 
comprometer a produtividade.

Ele não substitui o uso do SmartClient TOTVS, mas para determinadas tarefa tem sido uma ferramenta 
indispensável na empresa, pois economiza muito tempo de análise, consulta, cadastros, geração de relatórios e 
informações que antes demandavam muito tempo para serem obtidas e consolidadas, devido a algumas limitações de 
usabilidade que o SmartClient tem, que de certa forma 'engessam', atrapalham e atrasam o fluxo do trabalho.

O Eureka!® vem para suprir essas necessidades, oferecendo uma solução mais ágil e eficiente de interação.

![intro](images/eureka_main.gif)

![Login](images/login.png)

![Home](images/home.png)

## 🎯 Benefícios
- **👁️ Visão Integrada:** Centraliza informações críticas de diferentes departamentos, promovendo colaboração e eficiência na tomada de decisões.
- **⚡ Agilidade e Produtividade:** Automatiza processos manuais, liberando tempo para atividades estratégicas e reduzindo erros.
- **📊 Confiabilidade dos Dados:** Obtém dados diretamente do ERP Protheus, garantindo informações precisas e atualizadas.
- **🔄 Flexibilidade:** Permite exportação de relatórios em diferentes formatos e oferece opções de personalização por usuário/departamento.
- **💡 Suporte à Decisão:** Fornece informações estratégicas e análises detalhadas para apoiar decisões em todas as áreas.
- **🖥️ Interface Intuitiva:** Design moderno e amigável que supera a experiência do SmartClient TOTVS, facilitando o uso diário.
- **💰 Economia em Licenças:** Reduz a concorrência por licenças TOTVS ao oferecer uma interface mais eficiente para consultas e operações rotineiras.
- **🔗 Complementar ao TOTVS:** Potencializa a produtividade mantendo integração total com o Protheus, que permanece como núcleo essencial para gestão.

## 🛠️ Módulos do Sistema

### 1. Módulo Engenharia 🏗️
![Engenharia](images/eng_01.png)

![Engenharia](images/eng_02.png)

![Engenharia](images/eng_03.png)

![Engenharia](images/eng_04.png)

![Engenharia](images/eng_05.png)

![Engenharia](images/eng_06.png)

- **🔍 Consulta de Produtos:** Permite pesquisar produtos por código, descrição, tipo, unidade de medida, armazém, grupo, entre outros.
- **➕ Cadastro de Produto:** Permite criar novos produtos ou copiar dados de produtos existentes para agilizar o cadastro.
- **✏️ Alteração de Cadastro de Produto:** Realiza modificações em produtos já cadastrados.
- **🔗 Consulta de Estrutura de Produtos:** Permite visualizar e alterar as quantidades de itens de uma estrutura.
- **📦 Saldo em Estoque:** Informa o saldo atual de um produto, incluindo quantidade disponível, empenhada e prevista.
- **🏷️ Últimos Fornecedores:** Mostra os últimos fornecedores de um determinado item.
- **📜 Histórico de Compras:** Exibe as últimas notas fiscais de entrada de um item.

### 2. Módulo PCP 🏭
![PCP](images/pcp_gif_01.gif)  

O módulo PCP do **EUREKA®** é uma ferramenta robusta para gestão de produção, oferecendo funcionalidades como:  
🔹 **Consultar estrutura** (original ou explodida)  
🔹 **Rastrear uso de componentes** ("Onde é usado?")  
🔹 **Monitorar saldo em estoque**  
🔹 **Abrir ferramentas auxiliares** (ImageComparator®, Tabela de Pesos)  
🔹 **Gerenciar documentos** (abrir, imprimir, visualizar desenhos)  

---

#### 🖨️ Novidade: Novo template de Ordens de Produção  
**Destaque da última atualização:**  
![PCP](images/pcp_05.png)  

Implementei uma **melhoria significativa** na geração de Ordens de Produção (OP), elevando o padrão de rastreabilidade e controle. Confira as mudanças:  

✅ **Antes vs. Agora:**  
| **Versão Anterior**         | **Nova Versão**                          |
|-----------------------------|------------------------------------------|
| Informações básicas da OP    | **Dados críticos adicionados:**          |
|                              | ➞ Data de abertura da OP no TOTVS       |
|                              | ➞ Data de impressão da OP               |
|                              | ➞ Detalhamento ampliado para conferência rápida |
|                              | ➞ Lista de itens pais (onde usado)      |
|                              | ➞ Quantidade necessária em cada pai      |

💡 **Novo: Rastreabilidade de Uso**
- Visualize todos os produtos onde o item será utilizado
- Identifique as quantidades necessárias em cada aplicação
- Planeje a produção com base na demanda dos itens pais

🔍 **Impacto da melhoria:**  
- **Transparência:** Rastreie o ciclo completo da OP (da criação à impressão).  
- **Eficiência:** Redução de erros com informações detalhadas e acesso rápido.  
- **Conformidade:** Documentação alinhada a padrões de gestão industrial.  
📊 **Barra de Status: Indicadores de Produção**
- **📈 Indicadores em Tempo Real:**
  - Quantidade de OPs Abertas
  - Quantidade de OPs Fechadas
  ![PCP](images/pcp_06.png) 
- **🔄 Atualização:** Dados sincronizados automaticamente com o TOTVS

*"Essa atualização reflete meu compromisso em transformar o EUREKA® em uma ferramenta cada vez mais estratégica para sua operação!"*  

---

**Próximos passos:**  
Explore outras funcionalidades do módulo PCP através do menu de contexto:

![Menu de contexto](images/pcp_03.png)
![Menu de contexto](images/pcp_07.png)

*Sugestão de uso:* Utilize a opção **"Visualizar"** para checar a OP antes de imprimir e garantir que todos os campos estão preenchidos corretamente.

---

### 📸 Interface do Módulo PCP  
Confira abaixo as telas principais do sistema:  

![PCP](images/pcp_00.png)  
![PCP](images/pcp_01.png)  
![PCP](images/pcp_02.png)  
![PCP](images/pcp_02a.png)  
![PCP](images/pcp_04.png) 


### 3. Módulo Compras 🛒
![Compras](images/compras_gif_01.gif)
![Compras](images/compras_01.png)
![Compras](images/compras_02.png)
![Compras](images/compras_03.png)
![Compras](images/compras_04.png)
![Compras](images/compras_05.png)
![Compras](images/compras_06.png)
![Compras](images/compras_07.png)


- **🔄 Acompanhamento de SCs e PCs:** Facilita o acompanhamento de Solicitações de Compra (SCs) e Pedidos de Compra (PCs).
- **📝 Follow-up e Consultas:** Acesso a notas fiscais e histórico de compras.
- **🔍 Filtros de Pesquisa:** Possibilidade de criar filtros nas tabelas para refinar as pesquisas.


### 4. Módulo Comercial 📊
![Comercial](images/comercial_gif_01.gif)

- **💲 Cálculo de Custos:** Auxilia os profissionais da área comercial no cálculo e análise de custos de matérias-primas e itens comerciais.
- **📑 Relatórios de Custo:** Gera relatórios detalhados de custos, com exportação para Excel e PDF.
- **📊 Análises Simultâneas:** Permite abrir várias janelas para comparar custos de diferentes produtos.

### 5. Módulo Vendas 💼
![Vendas](images/vendas_04.png)

![Vendas](images/vendas_01.png)

![Vendas](images/vendas_03.png)

![Vendas](images/vendas_02.png)

![Vendas](images/vendas_05.png)

![Vendas](images/vendas_06.png)

### 6. Recursos Adicionais ⚙️
### 6.1. Autocomplete e Histórico de Pesquisa 🔍
![Autocomplete](images/autocomplete_eng_01.gif)

O recurso de autocompletar e histórico de pesquisa foi implementado utilizando um banco de dados SQLite local, armazenado no diretório AppData do Windows. Este recurso traz diversos benefícios:

- **🚀 Agilidade nas Consultas:** Reduz significativamente o tempo gasto em pesquisas ao sugerir termos já utilizados anteriormente
- **📝 Histórico Personalizado:** Mantém um registro das pesquisas mais frequentes de cada usuário
- **🔄 Persistência de Dados:** As sugestões são mantidas mesmo após fechar e reabrir o sistema
- **💡 Sugestões Inteligentes:** Apresenta sugestões baseadas no histórico de uso, priorizando as pesquisas mais recentes
- **⚡ Produtividade:** Minimiza erros de digitação e acelera o processo de busca de informações
- **🎯 Precisão:** Ajuda a encontrar termos exatos já utilizados anteriormente

### 6.2. Estrutura Explodida de Produtos 🌳
![Hierarquia](images/hierarquia_produtos_01.gif)

A funcionalidade de explosão hierárquica de estruturas permite visualizar todos os componentes de um produto de forma recursiva, oferecendo:

- **🔍 Busca Avançada:**
  - Pesquisa por código do item
  - Pesquisa por descrição (da esquerda para direita)
  - Pesquisa por termos contidos na descrição

- **🔗 Exploração Dinâmica:**
  - Visualização hierárquica de itens filhos na árvore de estrutura
  - Localização de itens específicos dentro da estrutura
  - Destaque e navegação automática após pesquisa

- **📄 Recursos Adicionais:**
  - Cópia de dados da tabela e árvore hierárquica
  - Acesso rápido aos desenhos via menu de contexto
  - Exportação completa para Excel
  - Alternância entre temas claro e escuro

- **✨ Benefícios:**
  - Pesquisa eficiente em estruturas complexas
  - Decisões mais assertivas com integração de desenhos PDF
  - Visualização completa da hierarquia do produto
  - Centralização de funcionalidades importantes
  - Personalização visual para maior conforto

### 6.3. Rastreabilidade e Consultas Integradas 🔍

O sistema oferece um conjunto robusto de funcionalidades para rastreabilidade e consultas:

- **🔗 Onde é Usado:**
  - Rastreamento completo de utilização do item
  - Visualização de todas as estruturas onde o componente é aplicado
  - Quantidade necessária em cada aplicação
  - Navegação direta para estruturas relacionadas

- **📦 Saldo em Estoque:**
  - Saldo atual disponível
  - Quantidade empenhada em OPs
  - Quantidade prevista (pedidos de compra)
  - Ponto de ressuprimento
  - Estoque mínimo e máximo

- **🏢 Últimos Fornecedores:**
  - Lista dos fornecedores recentes
  - Preços praticados
  - Condições de pagamento
  - Prazos de entrega históricos
  - Ranking de performance

- **📋 Histórico de Compras:**
  - Últimas notas fiscais de entrada
  - Valores e quantidades
  - Comparativo de preços
  - Visualização da NF-e em PDF
  - Exportação de dados para análise

## 📞 Suporte
Caso encontre **bugs** ou tenha **dúvidas**, entre em contato com a equipe de suporte. Estamos disponíveis para esclarecimentos e contamos com sua colaboração para reportar eventuais problemas.

Para sugestões e/ou melhorias, envie um e-mail clicando aqui: [e-mail](mailto:eliezer.moraes@outlook.com.br).

---

## 💻 Tecnologias Utilizadas
```
- Python 3.x
- PyQt5
- CSS
- SQL Server
- SQLite
- TOTVS Protheus (Integração)
- Git/GitHub
- Pandas
- SQLAlchemy
- pyodbc
- requests
- XlsxWriter
- openpyxl
- reportlab
- PyPDF2
- PyMuPDF
- pyinstaller (gerar o executável)
```

## 📁 Acesso ao Projeto

Para ter acesso ao projeto, siga os passos abaixo:

1. Clone o repositório:
```bash
git clone https://github.com/eliezer-moraes/eureka.git
```

2. Acesse a pasta do projeto:
```bash
cd eureka
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o sistema:
```bash
python main.py
```

## 👥 Autores

| [<img loading="lazy" src="https://avatars.githubusercontent.com/eliezermoraesss" width=115><br><sub>Eliezer Moraes</sub>](https://github.com/eliezermoraesss) |
| :---: |

## 📝 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

<p align="center">Desenvolvido com 💙 por <a href="https://www.linkedin.com/in/eliezer-moraes-silva-80b68010b/">Eliezer Moraes Silva</a></p>
