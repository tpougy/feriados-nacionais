"""Script principal de atualização de dados dos feriados da ANBIMA."""

from __future__ import annotations

import datetime
import logging
from io import BytesIO
from pathlib import Path

import httpx
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from openpyxl.utils import datetime as xl_datetime
from pandera.errors import SchemaError
from pandera.typing import DataFrame  # noqa: TC002

from src.config import settings, setup_logging
from src.models import FeriadosModel


def export_dataframe(df: pd.DataFrame, base_filename: str) -> None:
    """Exporta um DataFrame para múltiplos formatos definidos na configuração."""
    logger = logging.getLogger(__name__)

    logger.info(f"Exportando dados para o prefixo de arquivo: '{base_filename}'...")

    for fmt in settings.EXPORT_FORMATS:
        filepath = settings.OUTPUT_DIR / f"{base_filename}.{fmt}"
        filepath_xl = settings.OUTPUT_DIR / f"{base_filename}_xl.txt"
        try:
            match fmt:
                case "csv":
                    df.to_csv(filepath, index=False, encoding="utf-8", decimal=".", sep=";")
                case "json":
                    df.to_json(filepath, orient="records", date_format="iso", indent=4)
                case "xml":
                    df.to_xml(filepath, index=False, parser="lxml", root_name="feriados")
                case "parquet":
                    df.to_parquet(filepath, index=False)

            # fmt: off
            if "unix" not in base_filename:
                df["dt"].apply(lambda d: int(xl_datetime.to_excel(d))).to_csv( filepath_xl, index=False, encoding="utf-8", lineterminator=";")
            # fmt: on

            logger.info(f">> Arquivo '{filepath}' salvo com sucesso.")

        except Exception:
            logger.exception(f">> Falha ao salvar no formato {fmt}")


def fetch_and_process_holidays() -> int:
    """Busca, valida, processa e salva a tabela de feriados da ANBIMA.

    Returns:
        O ano atual para ser usado na mensagem de commit.
    """
    logger = logging.getLogger(__name__)

    logger.info("Iniciando o processo de atualização de feriados...")

    try:
        # 1. Extrair dados
        logger.info(f"Baixando arquivo de: {settings.URL_ANBIMA_FERIADOS}")
        response = httpx.get(settings.URL_ANBIMA_FERIADOS, verify=False, timeout=30)  # noqa: S501
        response.raise_for_status()

        # 2. Transformar dados com Pandas e validar com Pandera
        raw_df: pd.DataFrame = pd.read_excel(BytesIO(response.content), skipfooter=10)

        logger.info("Validando a estrutura do arquivo Excel...")
        validated_df: DataFrame[FeriadosModel] = FeriadosModel.validate(raw_df)
        logger.info("Validação concluída com sucesso.")

        dataframes_to_export: dict[str, pd.DataFrame] = FeriadosModel.exportar_versoes(validated_df)

        # 3. Exportar para múltiplos formatos e subversões
        for name, df_version in dataframes_to_export.items():
            # Subversão A: Data no formato YYYY-MM-DD
            df_date = df_version.copy()
            date_col_name = df_date.columns[0]  # O nome da coluna de data pode ser 'Data' ou 'dt'
            df_date[date_col_name] = df_date[date_col_name].dt.date
            export_dataframe(df_date, f"{name}_date")

            # Subversão B: Data em formato Unix Timestamp
            df_unix = df_version.copy()
            date_col_name = df_unix.columns[0]

            # Converte para Unix timestamp (segundos desde 1970-01-01) como inteiro
            df_unix[date_col_name] = (df_unix[date_col_name] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
            export_dataframe(df_unix, f"{name}_unix")

        # 4. Gerar o arquivo index.html
        generate_index_html()

        logger.info("Processo concluído com sucesso!")
        return datetime.datetime.now(tz=datetime.UTC).year

    except httpx.RequestError:
        logger.exception("Erro ao baixar o arquivo")
        raise
    except SchemaError:
        logger.exception("Erro de validação do DataFrame")
        raise
    except Exception:
        logger.exception("Ocorreu um erro inesperado")
        raise


def generate_index_html() -> None:
    """Gera um arquivo index.html a partir de um template Jinja2."""
    logger = logging.getLogger(__name__)
    logger.info("Gerando arquivo index.html a partir do template Jinja2...")

    # Configura o ambiente Jinja2 para carregar templates da pasta 'templates'
    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    template = env.get_template("index.html.j2")

    # Lista os arquivos e cria uma estrutura de dados para o template
    files = sorted(settings.OUTPUT_DIR.glob("*"))
    file_list = [
        {"name": file_path.name, "path": f"{settings.OUTPUT_DIR.name}/{file_path.name}"} for file_path in files
    ]

    # Prepara os dados para renderização
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html_content = template.render(files=file_list, timestamp=timestamp)

    # Salva o arquivo na raiz do projeto
    with Path("index.html").open("w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info("Arquivo index.html gerado com sucesso na raiz do projeto.")


def main() -> None:
    """Método principal que executa o script."""
    setup_logging()
    fetch_and_process_holidays()

    dt_exec = datetime.datetime.now(tz=datetime.UTC)

    return dt_exec.year


if __name__ == "__main__":
    main()
