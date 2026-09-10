"""
Carga incremental das vendas diárias do ERP para o SQLite.

Uso: executar("vendas_2026-09-02.csv", "vendas.db")
"""
import sqlite3
from pathlib import Path

import pandas as pd

COLUNAS = ["id_venda", "data", "cliente", "produto", "quantidade",
           "valor_unitario", "status", "atualizado_em"]

DDL = """
CREATE TABLE IF NOT EXISTS vendas (
    id_venda       TEXT PRIMARY KEY,
    data_venda     TEXT NOT NULL,
    cliente        TEXT NOT NULL,
    produto        TEXT NOT NULL,
    quantidade     INTEGER NOT NULL,
    valor_unitario REAL NOT NULL,
    valor_total    REAL NOT NULL,
    atualizado_em  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rejeitados (
    arquivo TEXT NOT NULL,
    linha   INTEGER NOT NULL,
    motivo  TEXT NOT NULL
);
"""

# Só sobrescreve se a versão que chega for igual ou mais nova (A5)
UPSERT = """
INSERT INTO vendas VALUES (:id_venda, :data_venda, :cliente, :produto,
    :quantidade, :valor_unitario, :valor_total, :atualizado_em)
ON CONFLICT(id_venda) DO UPDATE SET
    data_venda     = excluded.data_venda,
    cliente        = excluded.cliente,
    produto        = excluded.produto,
    quantidade     = excluded.quantidade,
    valor_unitario = excluded.valor_unitario,
    valor_total    = excluded.valor_total,
    atualizado_em  = excluded.atualizado_em
WHERE excluded.atualizado_em >= vendas.atualizado_em
"""

APAGAR_CANCELADA = (
    "DELETE FROM vendas WHERE id_venda = ? AND atualizado_em <= ?"
)


def numero_br(texto):
    """'1.234,56' -> 1234.56"""
    return float(texto.replace(".", "").replace(",", "."))


def extrair(caminho_csv):
    # tudo como texto: a conversão acontece na transformação, linha a linha
    df = pd.read_csv(caminho_csv, sep=";", encoding="latin-1",
                     dtype=str, keep_default_na=False)
    df["linha"] = df.index + 2  # linha no arquivo (cabeçalho é a 1)
    return df


def transformar(df, arquivo):
    resumo = {"lidas": len(df), "rodape": 0, "rejeitadas": 0,
              "canceladas": 0, "duplicatas": 0, "carregadas": 0}
    rejeitados, validas = [], []

    for reg in df.to_dict("records"):
        if reg["id_venda"].strip().lower().startswith("total de registros"):
            resumo["rodape"] += 1
            continue

        vazios = [c for c in COLUNAS if not str(reg.get(c) or "").strip()]
        if vazios:
            rejeitados.append(
                (arquivo, reg["linha"], "campo vazio: " + ", ".join(vazios))
            )
            continue

        try:
            quantidade = int(reg["quantidade"])
            valor_unitario = numero_br(reg["valor_unitario"])
            data_venda = pd.to_datetime(reg["data"], format="%d/%m/%Y")
            atualizado_em = pd.to_datetime(
                reg["atualizado_em"], format="%d/%m/%Y %H:%M"
            )
        except ValueError:
            rejeitados.append((arquivo, reg["linha"], "formato inválido"))
            continue

        if not reg["id_venda"].strip().isdigit() or quantidade <= 0:
            rejeitados.append(
                (arquivo, reg["linha"], "id_venda ou quantidade inválidos")
            )
            continue

        validas.append({
            "id_venda": reg["id_venda"].strip(),
            "data_venda": data_venda.strftime("%Y-%m-%d"),
            "cliente": reg["cliente"].strip(),
            "produto": reg["produto"].strip(),
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": round(quantidade * valor_unitario, 2),
            "atualizado_em": atualizado_em.strftime("%Y-%m-%d %H:%M:%S"),
            "cancelada": reg["status"].strip().upper() == "CANCELADA",
        })

    resumo["rejeitadas"] = len(rejeitados)

    # R2: por id_venda, vale o atualizado_em mais recente
    validas.sort(key=lambda v: v["atualizado_em"])
    ultima = {v["id_venda"]: v for v in validas}
    resumo["duplicatas"] = len(validas) - len(ultima)

    vendas, cancelar = [], []
    for v in ultima.values():
        if v.pop("cancelada"):
            cancelar.append((v["id_venda"], v["atualizado_em"]))
        else:
            vendas.append(v)
    resumo["canceladas"] = len(cancelar)
    resumo["carregadas"] = len(vendas)
    return vendas, cancelar, rejeitados, resumo


def carregar(vendas, cancelar, rejeitados, arquivo, caminho_banco):
    conn = sqlite3.connect(caminho_banco)
    try:
        conn.executescript(DDL)
        with conn:  # uma transação: commit no fim ou rollback se algo falhar
            conn.execute(
                "DELETE FROM rejeitados WHERE arquivo = ?", (arquivo,)
            )
            conn.executemany(
                "INSERT INTO rejeitados VALUES (?, ?, ?)", rejeitados
            )
            conn.executemany(UPSERT, vendas)
            # R1: canceladas saem, inclusive as de dias anteriores
            conn.executemany(APAGAR_CANCELADA, cancelar)
    finally:
        conn.close()


def executar(caminho_csv, caminho_banco):
    arquivo = Path(caminho_csv).name
    df = extrair(caminho_csv)
    vendas, cancelar, rejeitados, resumo = transformar(df, arquivo)
    carregar(vendas, cancelar, rejeitados, arquivo, caminho_banco)
    return resumo
