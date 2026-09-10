import logging
import sqlite3

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extrair(caminho_csv: str) -> pd.DataFrame:
    """Lê o arquivo CSV de vendas."""
    logging.info("Extraindo dados de %s", caminho_csv)
    return pd.read_csv(caminho_csv)


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza os dados."""
    logging.info("Transformando %d linhas", len(df))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()
    df = df.dropna()

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    if {"quantidade", "preco"}.issubset(df.columns):
        df["total"] = df["quantidade"] * df["preco"]

    return df


def carregar(
    df: pd.DataFrame, caminho_banco: str, tabela: str = "vendas"
) -> None:
    """Grava os dados no banco SQLite."""
    logging.info("Carregando %d linhas na tabela %s", len(df), tabela)
    with sqlite3.connect(caminho_banco) as conn:
        df.to_sql(tabela, conn, if_exists="replace", index=False)


def executar_etl(caminho_csv: str, caminho_banco: str) -> None:
    df = extrair(caminho_csv)
    df = transformar(df)
    carregar(df, caminho_banco)
    logging.info("ETL concluído com sucesso")


if __name__ == "__main__":
    executar_etl("vendas.csv", "vendas.db")
