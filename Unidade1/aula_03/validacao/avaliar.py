"""
Roda os três scripts ETL (respostas dos prompts 1, 2 e 3) contra os
arquivos reais do ERP e confere 10 critérios definidos antes do teste.

Cenário: banco vazio -> carga de 02/09 -> mesma carga de novo -> carga de 03/09.

Uso: pip install pandas && python avaliar.py
"""
import importlib.util
import pathlib
import sqlite3
import tempfile
import traceback

RAIZ = pathlib.Path(__file__).parent
DIA1 = str(RAIZ / "dados" / "vendas_2026-09-02.csv")
DIA2 = str(RAIZ / "dados" / "vendas_2026-09-03.csv")

CRITERIOS = {
    "C1": "Lê o arquivo real sem erro",
    "C2": "Rodapé do ERP não vira venda",
    "C3": "Valores 1.234,56 e total corretos",
    "C4": "02/09 vira 2 de setembro",
    "C5": "Duplicata: fica a versão mais recente",
    "C6": "Cancelada fora (status ' cancelada ')",
    "C7": "Linha inválida vai para rejeitados",
    "C8": "Reprocessar não duplica",
    "C9": "Novo dia não apaga o anterior",
    "C10": "Cancelamento posterior sai da base",
}


def carregar_modulo(nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "respostas" / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "executar", None) or getattr(mod, "executar_etl")


def linhas(db, sql, args=()):
    try:
        with sqlite3.connect(db) as c:
            return c.execute(sql, args).fetchall()
    except sqlite3.Error:
        return None


def vendas(db, id_venda):
    return linhas(db, "SELECT * FROM vendas WHERE CAST(id_venda AS TEXT) = ?", (id_venda,)) or []


def coluna(db, id_venda, col):
    r = linhas(db, f"SELECT {col} FROM vendas WHERE CAST(id_venda AS TEXT) = ?", (id_venda,))
    return r[0][0] if r else None


def total_linhas(db):
    r = linhas(db, "SELECT COUNT(*), ROUND(SUM(valor_total), 2) FROM vendas")
    return r[0] if r else None


def avaliar(nome):
    executar = carregar_modulo(nome)
    db = tempfile.mktemp(suffix=".db")
    ok = dict.fromkeys(CRITERIOS, False)
    erro = None
    try:
        executar(DIA1, db)
        ok["C1"] = True
    except Exception as e:  # noqa: BLE001
        erro = f"{type(e).__name__}: {str(e).splitlines()[0][:90]}"
        return ok, erro

    ids = [str(r[0]) for r in (linhas(db, "SELECT id_venda FROM vendas") or [])]
    ok["C2"] = all(i.strip().isdigit() for i in ids) and len(ids) > 0
    ok["C3"] = (coluna(db, "1003", "valor_unitario") == 1234.56
                and coluna(db, "1003", "valor_total") == 4938.24
                and coluna(db, "1006", "valor_total") == 1799.98)
    ok["C4"] = str(coluna(db, "1001", "data_venda") or "").startswith("2026-09-02")
    r1002 = vendas(db, "1002")
    ok["C5"] = len(r1002) == 1 and coluna(db, "1002", "valor_unitario") == 3299.0
    ok["C6"] = len(ids) > 0 and "1004" not in ids
    outras = [t for (t,) in (linhas(db, "SELECT name FROM sqlite_master WHERE type='table' AND name != 'vendas'") or [])]
    # a venda 1005 (quantidade vazia) está na linha 7 do arquivo
    rejeitado = any(
        any("1005" in str(v) or v == 7 for row in (linhas(db, f"SELECT * FROM {t}") or []) for v in row)
        for t in outras
    )
    ok["C7"] = "1005" not in ids and rejeitado

    antes = total_linhas(db)
    try:
        executar(DIA1, db)
        ok["C8"] = total_linhas(db) == antes
    except Exception:  # noqa: BLE001
        pass

    try:
        executar(DIA2, db)
        ids2 = [str(r[0]) for r in (linhas(db, "SELECT id_venda FROM vendas") or [])]
        ok["C9"] = "1001" in ids2 and "1007" in ids2
        ok["C10"] = "1007" in ids2 and "1003" not in ids2
    except Exception:  # noqa: BLE001
        pass

    # Teste extra, criado depois de ler a resposta 3 (ambiguidade A5):
    # reprocessar o arquivo de 02/09 depois do de 03/09 não pode trazer
    # de volta a venda 1003, que foi cancelada em 03/09.
    try:
        executar(DIA1, db)
        ids3 = [str(r[0]) for r in (linhas(db, "SELECT id_venda FROM vendas") or [])]
        ok["EXTRA"] = ok["C10"] and "1003" not in ids3
    except Exception:  # noqa: BLE001
        ok["EXTRA"] = False
    return ok, erro


if __name__ == "__main__":
    res = {n: avaliar(n) for n in ["etl_r1", "etl_r2", "etl_r3"]}
    print(f"{'':6}" + "".join(f"{n[-2:].upper():>6}" for n in res))
    for c, desc in CRITERIOS.items():
        print(f"{c:<6}" + "".join(f"{'ok' if res[n][0][c] else '--':>6}" for n in res) + f"   {desc}")
    print(f"{'TOTAL':<6}" + "".join(f"{sum(res[n][0].get(c, False) for c in CRITERIOS):>4}/10" for n in res))
    print(f"{'EXTRA':<6}" + "".join(f"{'ok' if res[n][0].get('EXTRA') else '--':>6}" for n in res)
          + "   Reprocessar dia antigo não ressuscita cancelada")
    for n, (_, e) in res.items():
        if e:
            print(f"{n}: {e}")
