"""Configurações centralizadas e setup de logging para a aplicação."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, TomlConfigSettingsSource


class Settings(BaseSettings):
    """Carrega e valida as configurações da aplicação."""

    OUTPUT_DIR: Path = Path("data")
    LOG_DIR: Path = Path("logs")

    URL_ANBIMA_FERIADOS: str

    EXPORT_FORMATS: list[str]

    model_config = SettingsConfigDict(toml_file="config.toml", toml_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configura o pydantic settings para ler confi.toml corretamente."""
        return (TomlConfigSettingsSource(settings_cls),)

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Cria a instânica de settings e garante a exsitencia das pastas de output e log."""
        super().__init__(**kwargs)

        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.LOG_DIR.mkdir(exist_ok=True)


settings = Settings()


def setup_logging() -> None:
    """Configura o sistema de logging para stdout e arquivo."""
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Handler para o console (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(stream_handler)

    # Handler para arquivo com rotação (5MB por arquivo, mantém 3 backups)
    log_file = settings.LOG_DIR / "data_update.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(log_formatter)
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
