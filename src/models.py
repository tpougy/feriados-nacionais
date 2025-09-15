"""Esquema de validação pandera."""

from __future__ import annotations

from typing import ClassVar

import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame, DateTime, Object, Series


class FeriadosModel(pa.DataFrameModel):
    """Esquema de validação para o DataFrame de feriados."""

    dt: Series[DateTime] = pa.Field(alias="Data", nullable=False)
    dia_semana: Series[Object] = pa.Field(alias="Dia da Semana", nullable=False)
    feriado: Series[Object] = pa.Field(alias="Feriado", nullable=False)

    class Config:
        """Configuração para o esquema."""

        strict = True
        coerce = True

    # Dicionário para mapear os nomes das colunas para cada versão
    _versoes: ClassVar[dict[str, dict | None]] = {
        "pt_br": {"Data": "dt", "Dia da Semana": "dia_semana", "Feriado": "feriado"},
        "en": {"Data": "dt", "Dia da Semana": "weekday", "Feriado": "holiday"},
    }

    # Dicionário para tradução dos dias da semana
    _en_weekday: ClassVar[dict[str, str]] = {
        "segunda-feira": "monday",
        "terça-feira": "tuesday",
        "quarta-feira": "wednesday",
        "quinta-feira": "thursday",
        "sexta-feira": "friday",
        "sábado": "saturday",
        "domingo": "sunday",
    }

    @classmethod
    def _dia_semana_en(cls, df: DataFrame[FeriadosModel]) -> pd.DataFrame:
        """Aplica a tradução na coluna do dia da semana."""
        df = df.copy()

        df["weekday"] = df["weekday"].str.lower().map(cls._en_weekday).fillna(df["weekday"])
        return df

    @classmethod
    def exportar_versoes(cls, df: DataFrame[FeriadosModel]) -> dict[str, pd.DataFrame]:
        """Cria um dicionário com as diferentes versões do DataFrame (pt_br, en).

        A versão 'en' tem os dias da semana traduzidos.
        """
        dataframes_processados = {}

        for v_name, v_cols in cls._versoes.items():
            # Renomeia as colunas conforme a versão
            df_renomeado = df.rename(columns=v_cols)

            # Se for a versão em inglês, aplica a tradução
            df_final = cls._dia_semana_en(df_renomeado) if v_name == "en" else df_renomeado

            dataframes_processados[f"feriados_{v_name}"] = df_final

        return dataframes_processados
