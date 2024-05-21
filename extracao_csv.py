
import csv

ano = 1989
item = []

with open('CSV\\Producao.csv', 'r') as ficheiro:
    reader = csv.reader(ficheiro)

    # Lendo a primeira linha para obter os títulos das colunas
    colunas = next(reader)[0].split(';')
    print(colunas)

    # Encontrando a posição do ano nos títulos das colunas
    indice_ano = colunas.index(str(ano))
    print(indice_ano)

    # Iterar sobre as linhas restantes
    for linha in reader:
        # Verificando se a linha não está vazia
        if linha:
            # Adicionando os valores necessários ao item
            linha_v = linha[0].split(';')
            item.append([linha_v[0], linha_v[1], linha_v[2], linha_v[indice_ano]])

    print(item)
