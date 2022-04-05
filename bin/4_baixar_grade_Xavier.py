# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 10:22:19 2021

Created by Jocelito B. C. da Cruz
jocelitocastro@gmail.com
__version__: 0.1
Date: 2021/06/25

Objetivos:
    Ler o conteúdo do Dropbox de Xavier, contendo os arquivos climáticos em 
    grid para o Brasil; 
    Após leitura, aplicar expressão regular no conteúdo para extrair os nomes
    dos arquivos *.nc;
    Os links duplicados são eliminados;
    Para cada nome de arquivo, adiciona 1 ao final para possibilitar o 
    download dos dados.
    
        python baixar_arquivos_nc_xavier.py
    
    Caso já exista o arquivo no diretório informado, o arquivo não será baixado,
    encerrando a função o loop segue para o próximo arquivo, até finalizar todos os itens.
    Os arquivos são baixados de forma serial para evitar sobrecarga no servidor
    e no Dropbox de Alexandre Cândido Xavier.
        
"""
__version__ = 0.1
__author__ = "Jocelito Cruz"

import sys, os
import urllib.request
import re
import submodules as sm

# =============================================================================
gridded_path = os.path.join(sm.path_project, "Database", "Weather", "gridded")

def criarDictArquivos(arquivos_raw):
    """
    Extrai os nomes dos arquivos *.nc e monta um dict usando o nome do arquivo
    como chave e o link como valor.
    """
    # Padrão para extrair o nome do arquivo do link
    reNomeArquivo = re.compile("(/\S+.nc)")
    # Adiciona 1 ao final do link
    lista_links = [value.replace('?dl=','?dl=1') for value in arquivos_raw]
    #Extrai o nome dos arquivos
    nomeArquivo = [re.search(reNomeArquivo, i).group(1).split("/")[-1] for i in lista_links]
    return dict(zip(nomeArquivo, lista_links))


def extrairLinks(dropbox_text):
    """
    Usando a regex, extrair todos os links de variáveis climáticas (*.nc). 
    Após extrair os links, elimina as duplicatas, cria um dicionário com o 
    nome do arquivo na chave e com o link no valor.
    """
     # Compilar o padrão de extração dos nomes de arquivos *.nc do Dropbox de Xavier
    ncRegExpression = re.compile("(https:\/\/www\.dropbox\.com\/sh\/kz57win77tbecu9\/[A-Za-z0-9-_]+\/[A-Za-z0-9-_.]+.nc\?dl=)")
    # Extrai os links dos arquivos de dropbox_text usando um padrão regex
    arquivos_raw = set_arquivos_nc_raw = set(re.findall(ncRegExpression, dropbox_text))
    #Chama função para extrair nome dos arquivos e criar dicionário
    return criarDictArquivos(set_arquivos_nc_raw)


def baixarArquivos(nomeArquivo, linkArquivo):
    """
    Função para baixar os arquivos.
    Primeiro testa se o diretório existe;
    Em seguida, testa se o arquivo existe. Em caso afirmativo, encerra a
    função retornando para o loop.    
    """
    # Testa se o arquivo existe. Caso não exista, cria conforme caminho disponibilizado
    if not os.path.exists(gridded_path):
        os.makedirs(gridded_path)
    # Testa se o arquivo existe no diretório. Se existir, baixa, caso contrário, sai da função.
    if not os.path.isfile(os.path.join(gridded_path, nomeArquivo)):
        print('\nBaixando arquivo: {0}'.format(nomeArquivo))
        urllib.request.urlretrieve(linkArquivo, os.path.join(gridded_path, nomeArquivo))
    else:
        print("Arquivo {0} já existe e não será baixado\n".format(nomeArquivo))


def main():
    """
    Rotina principal para baixar os arquivos grid climáticos do Dropbox 
    de Alexandre Cândido Xavier.
    """
    # print(gridded_path)
        
    # url do Dropbox de Xavier contendo os arquivos climáticos *.nc
    URL = "https://www.dropbox.com/sh/kz57win77tbecu9/AADF5eV_JbJwy4hq5vXytKSPa"

    # Carregar o conteúdo da página selecionada
    page = urllib.request.urlopen(URL)
    dropbox_text = page.read().decode("utf8")

    #Chama função para extrair nome dos arquivos e criar dicionário
    dict_arquivos_nc = extrairLinks(dropbox_text)
   
    print("\nArquivos disponíveis para download: ", len(dict_arquivos_nc), "\n")
   
    for key in dict_arquivos_nc:
        print("\nNome arquivo: ", key, "\nLink do arquivo: ", dict_arquivos_nc[key])
        baixarArquivos(key, dict_arquivos_nc[key])
    

# Inicialização para rodar o módulo em linha de comando   
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("[ ERROR ] This program needs no arguments")
        sys.exit(1)

    main()
