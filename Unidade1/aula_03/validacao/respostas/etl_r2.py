import sqlite3

import pandas as pd

COLUNAS_DESTINO = ["id_venda", "data_venda", "cliente", "produto",
                   "quantidade", "valor_unitario", "valor_total"]


def extrair(caminho_csv):
    # latin-1 e ";" vêm do ERP; decimal e thousands convertem "1.234,56"
    return pd.read_csv(
        caminho_csv,
        sep=";",
        encoding="latin-1",
        decimal=",",
        thousands=".",
        dtype={"id_venda": str},
    )


def transformar(df):
    df = df.copy()

    # Regra: canceladas ficam de fora (normaliza caixa e espaços)
    df["status"] = df["status"].str.strip().str.upper()
    df = df[df["status"] != "CANCELADA"]

    # Datas em dia/mês/ano
    df["data_venda"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.date
    df["atualizado_em"] = pd.to_datetime(
        df["atualizado_em"], format="%d/%m/%Y %H:%M"
    )

    # Regra: se o id se repete, vale a versão mais recente
    df = df.sort_values("atualizado_em").drop_duplicates(
        "id_venda", keep="last"
    )

    # Regra: valor_total = quantidade x valor_unitario
    df["valor_total"] = (df["quantidade"] * df["valor_unitario"]).round(2)

    return df[COLUNAS_DESTINO]


def carregar(df, caminho_banco):
    with sqlite3.connect(caminho_banco) as conn:
        df.to_sql("vendas", conn, if_exists="append", index=False)


def executar(caminho_csv, caminho_banco):
    df = extrair(caminho_csv)
    df = transformar(df)
    carregar(df, caminho_banco)
    return len(df)
