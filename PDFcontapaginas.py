#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os, sys, time, winsound
from datetime import date
import functools, multiprocessing.pool
from PyPDF2 import PdfFileReader
import configparser
import xlsxwriter
from shutil import move
from EGDtools import copy2clip


# In[ ]:


print('atualizado em 08/07/2022')

# automatizar parte de criar nova pasta com data do último dia útil e mover todos para dentro


# In[ ]:


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            # retorna None quando acabar o tempo
            try:
                x = async_result.get(max_timeout)
            except multiprocessing.TimeoutError:
                x = None
            return x
        return func_wrapper
    return timeout_decorator


# In[ ]:


# verifica se a string é um EU
def padraoEU(eu):
    eu = eu.replace(' ','')
    if not eu.replace('.','').isdigit() and len(eu)>=9: return False
    if not eu.startswith(('002','001')): return False
    return True


# In[ ]:


# lista todos os arquivos PDF na pasta e subpastas
def listaPDFs(caminho):
    tamanhomaximo = 200000000 # 200 MB em bytes
    lista = []
    for (dirpath, dirnames, filenames) in os.walk(caminho):
        lista += [os.path.join(dirpath, file) for file in filenames if file.lower().endswith('.pdf')]
    for f in lista:
        tam = os.path.getsize(f)
        if not tam > tamanhomaximo: continue
        winsound.MessageBeep()
        print(f'\n*** ATENÇÃO! Arquivo com mais de {int(tamanhomaximo/1000/1000)} MB:\n')
        print(f)
        o = input('\nContinuar? ')
        if o.lower().startswith('s'): continue
        sys.exit()
    return lista


# In[ ]:


# conta páginas de um PDF, retorna None se demorar 3 segundos
def contaPaginas(file, modo=None):
    
    def contaPaginas0(file):
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        return pdf.getNumPages()
    
    @timeout(1)
    def contaPaginas1(file):
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        return pdf.getNumPages()
    
    @timeout(5)
    def contaPaginas5(file):
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        return pdf.getNumPages()
    
    @timeout(10)
    def contaPaginas10(file):
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        return pdf.getNumPages()
    
    r = contaPaginas1(file)
    if r is None:
        r = contaPaginas5(file)
    if r is None:
        r = contaPaginas10(file)
    if r is None:
        print('O computador está demorando para ler este PDF.')
        print('Se permanecer muito tempo parado, você pode fechar esta janela e tentar novamente.')
        r = contaPaginas0(file)
    
    return r
    


# In[ ]:


# conta as páginas de todos os PDFs da pasta (EU) e subpastas (protocolo SEI)
def contaPasta(i, path, tamanhomaximo=200000000):
    contador = 0
    lista = listaPDFs(path)
    pasta = path.split('\\')[-1]
    print(f'{i} - {pasta}: {len(lista)} PDFs', end='... ')
    sys.stdout.flush()
    for f in lista:
        try:
            pags = contaPaginas(f)
        except:
            pags = None
        if pags == None:
            winsound.MessageBeep()
            print('\nATENÇÃO! Erro ao contar páginas do arquivo abaixo:\n',f)
            input('[ENTER] para continuar a contagem...')
            continue
        contador += pags
            
    print(f'{contador} páginas')
    return contador


# In[ ]:


# conta as páginas dos PDFs de cada subpasta (EU) na pasta raiz (Boomerang do dia)
def contaTodas(root='.'):
    listagem = {}
    path, pastas, files=os.walk(root).__next__()
    pastas = [x for x in pastas if padraoEU(x)]
    print(f'Processando {len(pastas)} subpastas:')
    for i, p in enumerate(pastas):
        if not p in listagem: listagem[p]=0
        listagem[p] = contaPasta(i+1, root+'\\'+p)
        if listagem[p] == False: return False
    return listagem


# In[ ]:


def salvar(caminho,dados):
    print('Salvando arquivos', end='... ')
    hoje = date.today().strftime("%Y-%m-%d")
    hoje2 = date.today().strftime("%d/%m/%Y")
    outpath = 'Z:\\_Relatórios_Digitalização_Boomerang\\relatorio_pdf_'+hoje+'.xlsx'
    workbook = xlsxwriter.Workbook(outpath)
    worksheet = workbook.add_worksheet()
    cabecalho = ['Processo_E_U','Protocolo_Etapa','Total_Páginas', 'Data_Relatório','ANO','MÊS','DIA','SEMANA']
    linhas = [cabecalho]
    for idx, txt in enumerate(cabecalho): worksheet.write(0,idx,txt)
    for idx, txt in enumerate(list(dados.keys())):
        linhas.append([
            txt,
            '00.0.000000000-0', 
            str(dados[txt]), 
            hoje2, 
            f'=YEAR(D{idx+2})', 
            f'=MONTH(D{idx+2})', 
            f'=DAY(D{idx+2})', 
            f'=WEEKNUM(D{idx+2})'])
        for linha in linhas[1:]:
            for col, cel in enumerate(linha):
                worksheet.write(idx+1, col, cel)
    linhas.append(['', '', f'=SUM(C2:C{len(dados)+1})'])
    worksheet.write(len(dados)+1,2,linhas[-1][-1])
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 1, 17)
    worksheet.set_column(2, 2, 13)
    worksheet.set_column(3, 3, 13)
    while True:
        try:
            workbook.close()
        except:
            print('Erro ao salvar. Feche a planilha:',outpath)
            input('[ENTER] para tentar novamente...')
        else: break
    print('ok\n')
    return linhas


# In[ ]:


def pegaconfig(configfile):
    conf = configparser.ConfigParser()
    conf.read(configfile)
    unidades = []
    if 'unidades' in conf:
        for u in conf['unidades']:
            unidades.append(conf['unidades'][u])
    else:
        unidades = ['z:\\']
    caminho = os.path.join(unidades[0],'@_parte_1_copia_processo_aqui')
    return caminho


# In[ ]:


def acha_novo_nome(nome, destino):
    # acrescenta sufixo ao final do nome caso já exista no destino
    novo_nome = nome
    i=1
    while os.path.exists(os.path.join(destino, novo_nome)):
        novo_nome = f'{nome} ({i})'
        i += 1
    return novo_nome


# In[ ]:


def principal():
    p1 = '@_parte_1_copia_processo_aqui'
    root=r'Z:\@_parte_1_copia_processo_aqui'
    configfile = 'configpastas.ini'
    if os.path.isfile(configfile):
        root = pegaconfig(configfile)
    path, pastas, files = os.walk(root).__next__()
    pastasDia = [x for x in pastas if x.startswith('Boomerang')]
    pastasDia.sort()
    pastasEus = [x for x in pastas if padraoEU(x)]
    
    subpasta=''
    escolha='n'
    if pastasEus:
        escolha = input('Gerar relatório na raiz de P1? ')
    
    if escolha.lower().startswith('n'):
        if not pastasDia:
            print('Sem pastas do dia.')
            input('[ENTER] para finalizar. ')
            return
        subpasta=pastasDia[-1]
        op = input(f'Gerar relatório para a pasta {pastasDia[-1]}? ')
        if op.lower().startswith('n'):
            print('0 - Sair')
            print('1 - raiz de P1')
            for i,o in enumerate(pastasDia):
                print(i+2,'-',o)
            op = input('Número da pasta: ')
            if not op.isdigit(): return
            if not (0 < int(op) <= len(pastasDia)+1): return
            if op=='1': subpasta=''
            else: subpasta=pastasDia[int(op)-2]
    if not pastasEus and subpasta=='':
        print('Pastas de EU ou de entregas do dia não encontradas em P1')
        input('[ENTER] para finalizar. ')
        return
    
    
    caminho = root+'\\'+subpasta
    print(caminho)
    dados = contaTodas(caminho)
    if dados == False:
        return False
    totalPaginas = sum(dados.values())
    print('Total de páginas:',totalPaginas)
    linhas = salvar(caminho, dados)
    if subpasta=='':
        hoje = date.today().strftime("%Y-%m-%d")
        novapasta = f'Boomerang {hoje}'
        if os.path.exists(os.path.join(root,novapasta)): novapasta = acha_novo_nome(novapasta, root)
        fulldir = os.path.join(root,novapasta)
        print('criando pasta:',fulldir)
        os.mkdir(fulldir)
        path, pastas, files=os.walk(root).__next__()
        pastas = [x for x in pastas if padraoEU(x)]
        print(f'movendo {len(pastas)} pastas para {fulldir}:')
        c=0
        for pasta in pastas:
            c+=1
            print(f'{c} {pasta}')
            move(os.path.join(root,pasta),fulldir)
        print('pronto.')
    input('[ENTER] para copiar os dados da planilha... ')
    stringona = '\r\n'.join(['\t'.join(linha) for linha in linhas[1:-1]])
    copy2clip(stringona)
    

principal()


# In[ ]:





# In[ ]:





# In[ ]:




