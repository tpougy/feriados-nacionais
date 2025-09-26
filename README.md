# Feriados Nacionais Brasileiros

(Fonte: ANBIMA)

Este repositório serve como uma fonte de dados centralizada, confiável e sempre atualizada para os feriados nacionais brasileiros desde o ano 2000 até 2099, com base na tabela oficial publicada pela ANBIMA.

O objetivo é transformar uma informação que normalmente fica "presa" em um arquivo Excel em um recurso acessível, versionado e disponível em múltiplos formatos para consumo por desenvolvedores, analistas e outras aplicações. O processo é 100% automatizado com GitHub Actions, garantindo que os dados sejam atualizados anualmente.

## 🚀 Como Usar os Dados

Existem duas maneiras principais de acessar os dados:

1. Acesso via UI GitHub Pages
   Uma página web simples foi criada para listar e fornecer links diretos para todos os arquivos de dados disponíveis.

➡️ Acesse o portal de dados em: https://tpougy.blog/feriados-nacionais/

1. Acesso Direto aos Arquivos (Análogo a uma API)
   Você pode usar as URLs dos arquivos brutos diretamente em suas aplicações ou scripts.

URL Base: https://tpougy.blog/feriados-nacionais/data/

Exemplos:

CSV (Português, com data):
https://tpougy.blog/feriados-nacionais/data/feriados_pt_br_date.csv

JSON (Inglês, com timestamp Unix):
https://tpougy.blog/feriados-nacionais/data/feriados_en_unix.json

## 💡 Uso Específico: Microsoft Excel (Funções de Data)

Para otimizar o uso em funções de data do Excel (como WORKDAY.INTL ou NETWORKDAYS.INTL), foi criada uma versão especial dos arquivos de dados: feriados\_<versão>\_date_xl.txt.

**Como Funciona?**
O Microsoft Excel não armazena datas como "25/12/2025". Internamente, ele as trata como um número de série (ex: 46015), que representa o número de dias desde 01/01/1900.

Os arquivos \_xl.txt contêm exatamente isso: uma única linha de texto com todos os números de série dos feriados, separados por ponto e vírgula.

**Exemplo do conteúdo de `feriados_pt_br_date_xl.txt`:**

```
45658;45736;45767;...
```

Esta abordagem é ideal para ser usada com a função WEBSERVICE do Excel, pois o resultado é um texto leve e que o Excel pode interpretar numericamente sem a necessidade de conversões complexas.

**Como Usar com Fórmulas do Excel**

1. Via ExcelLabs

- Opção A: Importe o módulo via gist

`https://gist.github.com/tpougy/eedb782adc59f7977fc439e8030367fa`

- Opção B. Copie e cole o código abaixo na aba "módulo" do Excel Labs

```
// Retorna os feriados brasileiros segundo a ANBIMA
FERIADOS.ANBIMA=LAMBDA([header];
   LET(
      url; "https://tpougy.blog/feriados-nacionais/data/feriados_excel.txt";
      h; IF(ISOMITTED(header); 0; INT(VALUE(header)));
      h_name; "dt";
      feriados; VALUE(TRANSPOSE(TEXTSPLIT(WEBSERVICE(url); ";")));
      IF(h = 1; VSTACK(h_name; feriados); feriados)
   )
)
```

## 🗃️ Formatos Disponíveis

Os dados são disponibilizados nos seguintes formatos para atender a diferentes necessidades:

.csv: Ideal para importação em planilhas (Excel, Google Sheets) e sistemas de análise de dados.

.json: Perfeito para consumo em aplicações web, APIs e scripts (JavaScript, Python, etc.).

.xml: Útil para integração com sistemas legados que utilizam este formato.

.parquet: Formato colunar de alta performance, ideal para análise de dados em larga escala (Big Data, Data Science).

## 📊 Estrutura dos Dados

Para máxima flexibilidade, os dados são oferecidos em diferentes "versões":

1. Versões de Idioma:

- \_pt_br: Colunas e conteúdo em português.

- \_en: Colunas e dias da semana traduzidos para o inglês.

2. Versões de Formato de Data:

- \_date: A coluna de data está no formato AAAA-MM-DD.

- \_unix: A coluna de data está no formato Unix Timestamp (inteiro representando os segundos desde 1970-01-01).

| Versão pt_br | Versão en | Tipo de Dado    | Descrição                                     |
| ------------ | --------- | --------------- | --------------------------------------------- |
| dt           | dt        | Data ou Inteiro | A data do feriado (formato \_date ou \_unix). |
| dia_semana   | weekday   | Texto           | O nome do dia da semana.                      |
| feriado      | holiday   | Texto           | O nome oficial do feriado.                    |

## 🤖 Automação

Este repositório é mantido por um workflow de GitHub Actions localizado em .github/workflows/atualiza_feriados.yml.

- Gatilho: A automação é executada automaticamente uma vez por ano, no dia 1º de Janeiro. Também pode ser acionada manualmente através da aba "Actions".

- Processo: O workflow executa um script Python (src/script.py) que:

1. Baixa o arquivo Excel mais recente do site da ANBIMA.

2. Valida a estrutura dos dados usando pandera para garantir a integridade.

3. Processa e cria as 6 versões diferentes dos DataFrames.

4. Exporta os dados para todos os formatos definidos na configuração (.csv, .json, etc.).

5. Gera o arquivo index.html com a lista de links atualizada.

6. Faz o commit e push dos novos arquivos para o repositório.

## 🔧 Como Executar Localmente

Se você deseja rodar o processo de atualização na sua máquina:

1. Clone o repositório:

Crie um fork e clone o repositório

2. Crie e ative um ambiente virtual:

```bash
uv venv
source .venv/bin/activate # No Windows: .venv\Scripts\activate
```

Instale as dependências:

```bash

uv pip install -r requirements.txt
```

Execute o script:

```bash

python src/script.py
```

Os novos arquivos serão gerados na pasta data/ e o index.html será atualizado na raiz.

## 📜 Licença

MIT
