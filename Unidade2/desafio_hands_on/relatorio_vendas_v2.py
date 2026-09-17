"""Gera um resumo estatistico de uma lista de valores de vendas."""

from typing import Sequence


def validar_vendas(vendas: Sequence[float]) -> list[float]:
    """Valida a lista de vendas e devolve uma copia somente com numeros.

    Levanta ValueError se a lista estiver vazia, se algum item nao for
    numerico ou se algum valor for negativo.
    """
    if not vendas:
        raise ValueError("A lista de vendas esta vazia.")

    validadas: list[float] = []
    for posicao, valor in enumerate(vendas):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(
                f"Valor invalido na posicao {posicao}: {valor!r} nao e numerico."
            )
        if valor < 0:
            raise ValueError(
                f"Valor invalido na posicao {posicao}: venda negativa ({valor})."
            )
        validadas.append(float(valor))

    return validadas


def calcular_resumo(vendas: Sequence[float]) -> dict[str, float]:
    """Calcula total, media, maior e menor valor de uma lista de vendas.

    Exemplo:
        >>> calcular_resumo([100, 200, 300])["total"]
        600.0
    """
    valores = validar_vendas(vendas)
    return {
        "total": sum(valores),
        "media": sum(valores) / len(valores),
        "maior": max(valores),
        "menor": min(valores),
        "quantidade": len(valores),
    }


def formatar_moeda(valor: float) -> str:
    """Formata um numero no padrao monetario brasileiro (R$ 1.234,56)."""
    inteiro, centavos = f"{valor:.2f}".split(".")
    milhares = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {milhares},{centavos}"


def formatar_relatorio(resumo: dict[str, float]) -> str:
    """Monta o texto do relatorio a partir do resumo calculado."""
    linhas = [
        "=== RELATORIO DE VENDAS ===",
        f"Vendas registradas: {int(resumo['quantidade'])}",
        f"Total .......: {formatar_moeda(resumo['total'])}",
        f"Media .......: {formatar_moeda(resumo['media'])}",
        f"Maior venda .: {formatar_moeda(resumo['maior'])}",
        f"Menor venda .: {formatar_moeda(resumo['menor'])}",
    ]
    return "\n".join(linhas)


def main() -> None:
    """Executa o relatorio com uma lista de exemplo."""
    vendas = [1500, 2300, 800, 4200, 1750]
    try:
        print(formatar_relatorio(calcular_resumo(vendas)))
    except ValueError as erro:
        print(f"Nao foi possivel gerar o relatorio: {erro}")


if __name__ == "__main__":
    main()
