def relatorio_vendas(vendas):
    total = sum(vendas)
    media = total / len(vendas)
    maior = max(vendas)
    menor = min(vendas)

    print("=== RELATORIO DE VENDAS ===")
    print("Total: R$", total)
    print("Media: R$", media)
    print("Maior venda: R$", maior)
    print("Menor venda: R$", menor)


vendas = [1500, 2300, 800, 4200, 1750]
relatorio_vendas(vendas)
