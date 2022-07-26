#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os,sys,stat
from datetime import datetime # para o log
from shutil import move
import winsound
import functools, multiprocessing.pool
from shutil import rmtree
from portalRequests import expedientesBusca
from EGDtools import copy2clip
from PyPDF2 import PdfFileReader
from checaPastas import Checador
import configparser


# In[ ]:


# P1: verifica arquivos acima de 200 MB nas pastas EU na raiz P1 (que nao estao na Boomerangs diarias)
# P2: verifica se houve erros do robô, através do log e alerta


# In[ ]:


print('atualizado em 06/07/2022')


# In[ ]:


unidade = 'z:\\'
configfile = 'configpastas.ini'
if os.path.isfile(configfile):
    conf = configparser.ConfigParser()
    conf.read(configfile)
    if 'unidades' in conf:
        unidade = conf['unidades']['0']
p1 = unidade + r'@_parte_1_copia_processo_aqui'
p2 = unidade + r'@_parte_2_move_processo_aqui'
logs = unidade + r'logs'
erro1 = 'não está aberto em nenhuma unidade'
ajustar = unidade + r'_Ajustar_Boomerang'
logfile = ajustar + '\\' + 'ajustar.log'


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


# conta páginas de um PDF, retorna None se demorar 5 segundos
def contaPaginas(file):
    
    @timeout(1)
    def contaPaginas1(file):
        #print(file)
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        #print('ok')
        return pdf.getNumPages()
    
    @timeout(5)
    def contaPaginas5(file):
        #print(file)
        pdf = PdfFileReader(open(file,'rb'), strict=False) # strict=False desliga avisos na leitura de PDFs fora da formatação padrão
        #print('ok')
        return pdf.getNumPages()
    
    r = contaPaginas1(file)
    if r is None:
        r = contaPaginas5(file)
    
    return r
    


# In[ ]:


# lista todos os arquivos PDF na pasta e subpastas
def listaPDFs(caminho):
    tamanhomaximo = 200000000 # 200 MB em bytes
    lista = []
    for (dirpath, dirnames, filenames) in os.walk(caminho):
        lista += [os.path.join(dirpath, file) for file in filenames if file.lower().endswith('.pdf')]
    return lista


# In[ ]:


def escreve_log(frase):
    frase = frase + '\n'
    with open(logfile, 'a') as lf:
        lf.write(frase)


# In[ ]:


# conta as páginas de todos os PDFs da pasta (EU) e subpastas (protocolo SEI)
def contaPasta(path, tamanhomaximo=200000000):
    contador = 0
    lista = listaPDFs(path)
    pasta = path.split('\\')[-1]
    #sys.stdout.flush()
    for f in lista:
        tam = os.path.getsize(f)
        if tam > tamanhomaximo:
            winsound.MessageBeep()
            print('\nATENÇÃO! Arquivo grande:',f)
            #input('[ENTER] para continuar...')
            escreve_log(f'Arquivo grande: {f}')
            return None
        try:
            pags = contaPaginas(f)
        except:
            pags = None
            
        if pags == None:
            winsound.MessageBeep()
            print('\nATENÇÃO! Erro ao contar páginas do arquivo abaixo:\n',f)
            input('[ENTER] para continuar a contagem...')
            escreve_log(f'PDF erro ao contar: {f}')
            continue
            
        contador += pags
            
    #print(f'{contador} páginas')
    return contador


# In[ ]:


def verificaPDFs(caminho):
    
    def achaNovoNome(nome, destino):
        # acrescenta V0, V1, V2, etc... ao final do nome da pasta caso já exista no destino
        novo_nome = nome
        i=0
        while os.path.exists(os.path.join(destino, novo_nome)):
            #novo_nome = nome + f' V{i}'
            novo_nome = nome + f'-A{i}'
            i += 1
        return novo_nome
    
    lista=[]
    pasta=''
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    pastas = [x for x in dirnames if x.replace('.','').isdigit()]
    print(f'Verificando arquivos PDF em {len(pastas)} pastas:')
    escreve_log('----------------------------------------------------------------')
    escreve_log(f"'Iniciando processamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    escreve_log('----------------------------------------------------------------')
    c=0
    movidas = []
    for p in pastas:
        c+=1
        print(f'{c} - {p}',end='... ')
        conta = contaPasta(os.path.join(caminho,p))
        if conta is None:
            r = input(f'Mover pasta {p} para {ajustar}? [s/N] ')
            if r.lower().startswith('s'):
                pasta_destino = p
                if os.path.exists(os.path.join(ajustar,pasta_destino)):
                    pasta_destino = achaNovoNome(p, ajustar)
                    os.rename(os.path.join(caminho,p), os.path.join(caminho,pasta_destino))
                    #p=novonome
                move(os.path.join(caminho,pasta_destino), ajustar)
                movidas.append(pasta_destino)
                escreve_log(f'Pasta movida para {ajustar}: {pasta_destino}')
            continue
        print(conta)
    
    escreve_log('FIM --------------------------------')
    escreve_log('\n')
    if movidas:
        winsound.MessageBeep()
        print('\n*** Pastas movidas:')
        for p in movidas:
            print(p)
        input('[ENTER] para continuar... ')
    print('fim')


# In[ ]:


def temEU(texto):
    lista = texto.split(' ')
    retorno = []
    for palavra in lista:
        if not palavra.replace('.','').replace(',','').isdigit(): continue
        if palavra.startswith('002.'):
            retorno += [palavra]
    return retorno


# In[ ]:


def analisaLogs(caminho):
    
    print('\nAnalisando logs:')
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    serverLog = [x for x in filenames if x.lower().endswith('.log') and x.lower().startswith('server-')]
    if not serverLog: return False
    serverLog.sort()
    lastLog = serverLog[-1]
    data = lastLog[7:17]
    caminho = os.path.join(caminho,lastLog)
    
    errorLog = [x for x in filenames if x.lower().endswith('.log') and x.lower().startswith('error-') and x[7:17]==data]
    if errorLog:
        winsound.MessageBeep()
        print('*** LOG DE ERROS ENCONTRADO:',errorlog)
        input('[ENTER] para continuar... ')
    
    with open(caminho, 'r', encoding="utf-8") as f:
        lines = f.read().splitlines()

    outrosErros = []
    for idx, l in enumerate(lines):
        if 'INICIANDO PROCESSAMENTO' in l:
            outrosErros = []
        if erro1 in l:
            if not temEU(l):
                for ii in range(idx,1,-1):
                    ll = lines[ii]
                    listaEU = temEU(ll)
                    if listaEU: break
            outrosErros += [f'{listaEU}: {l}']

    if outrosErros:
        winsound.MessageBeep()
        print('Outros erros encontrados:')
    for l in outrosErros:
        print(l)
        
    if errorLog or outrosErros: return True
    print('ok')
    
    return False


# In[ ]:


def pegaEUformatado(eu):
    #print('Buscando EU',eu,end='... ')
    eu = eu.replace(' ','')
    if eu.startswith('002.'):
        miolo = eu[4:10]
    elif eu.startswith('002') and eu[3:4].isdigit():
        miolo = eu[3:9]
    else: miolo = eu[:6]
    #r = expedientesBusca('002'+miolo+final)
    r = expedientesBusca(eu)
    euFormatado = False
    euLista = r['data']['ExpedientesExpedienteUnicoList']
    for euAchado in euLista:
        c = euAchado['codigo']
        if c[3:9] == miolo:
            euFormatado = c[:3] + '.' + c[3:9] + '.' + c[9:11] + '.' + c[11:12] + '.' + c[12:]
            break
    if not euFormatado:
        return False
    return euFormatado

def validaEUs(caminho):
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    dirnames = [x for x in dirnames if x.replace('.','').isdigit()]
    if not dirnames:
        print('Pastas de EU não localizadas em:',caminho)
        return
    print(f'Validando {len(dirnames)} nomes de pastas contendo EU:')
    c=0
    for eu in dirnames:
        c+=1
        print(c,'-',eu,end='... ')
        if eu == pegaEUformatado(eu):
            print('ok')
            continue
        winsound.MessageBeep()
        copy2clip(eu)
        print('ERRO! Nome da pasta contém EU inválido.')
        novoeu = input('Digite o novo nome ou apenas [ENTER] para manter o atual: ')
        if novoeu:
            try:
                os.rename(caminho+'\\'+eu, caminho+'\\'+novoeu)
            except Exception as e:
                print(e)
                print()
                input('Ocorreu algum erro ao tentar renomear a pasta. Anote o nome e tente renomear manualmente. [ENTER] para continuar... ')
    input('[ENTER] para copiar a lista para a área de transferência (CTRL+C)... ')
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    dirnames = sorted([x for x in dirnames if x.replace('.','').isdigit()])
    copy2clip('\n'.join(dirnames))
    print('ok')
        


# In[ ]:


def on_rm_error(func, path, exc_info):
    # tenta desmarcar "somente leitura"
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

def hasFiles(caminho):
    ignorar = ['thumbs.db', 'desktop.ini', 'np.xlsx']
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    filenames = [x for x in filenames if not x.lower() in ignorar]
    if filenames: return True
    for subfolder in dirnames:
        if hasFiles(caminho+'\\'+subfolder): return True
    return False

def limpaPasta(caminho):
    dirpath, dirnames, filenames = os.walk(caminho).__next__()
    if not dirnames: print('ok')
    for pasta in dirnames:
        if hasFiles(caminho+'\\'+pasta):
            print(f'{pasta} contém arquivos')
        else:
            print(f'deletando pasta {pasta}',end='... ')
            rmtree(caminho+'\\'+pasta, onerror=on_rm_error)
            print('ok')
    return
    


# In[ ]:


def pega_opcao(opcoes):
    for idx, op in enumerate(opcoes):
        print(f'{idx} - {op}')
    while True:
        r = input('Escolha uma das opções acima: ')
        if r in [str(x) for x in range(len(opcoes))]: break
    return opcoes[int(r)]


# In[ ]:


def pegaDataMaisRecenteNaP1():
    global p1
    path, pastas, files = os.walk(p1).__next__()
    pastas = [x for x in pastas if x.startswith('Boomerang')]
    pastas.sort()
    return pastas[-1]


# In[ ]:


def validaPDFporEU():
    euRaw = input('\nDigite o EU: ')
    if euRaw == '': return
    if len(euRaw) <7: euRaw = '002' + euRaw.zfill(6)
    print('Validando...')
    eu = pegaEUformatado(euRaw)
    if eu is False: return
    print(f'Localizando EU {eu}...')
    checador = Checador(atualiza=True)
    caminhos = checador.pegaCaminhoEU(eu)
    p = 0
    if len(caminhos)>1:
        print('EU encontrado em mais de uma pasta:')
        o = pega_opcao(caminhos)
        p = caminhos.index(o)
    pasta = checador.pegaCaminhoEU(eu,caminhos[p])[0]
    caminho = os.path.join(pasta,eu)
    contagem = contaPasta(caminho)
    print('Pasta:',caminho)
    print('Total de páginas:',contagem)


# In[ ]:


while True:
    opcoes = [
        'Verificação de rotina: verifica PDFs em P1-raiz, limpa P1 e P2, analisa logs',
        'Validar EU em nomes de pastas na Pasta 1',
        'Verificar PDFs na P1 (raiz)',
        'Verificar PDFs na P1 (dia mais recente)',
        'Verificar PDFs na pasta de um EU',
        'Remover pastas vazias na Pasta 1',
        'Remover pastas vazias na Pasta 2',
        'Analisar logs',
        'Sair',
    ]
    
    print('\n\n------------------------------------------\n')
    r = pega_opcao(opcoes)
    print('')

    if r == opcoes[0]: # rodar todas
        validaEUs(p1)
        verificaPDFs(p1)
        #verificaPDFs(pegaDataMaisRecenteNaP1())
        limpaPasta(p1)
        analisaLogs(logs)
        limpaPasta(p2)
    if r == opcoes[1]: validaEUs(p1)
    if r == opcoes[2]: verificaPDFs(p1)
    if r == opcoes[3]: verificaPDFs(os.path.join(p1,pegaDataMaisRecenteNaP1()))
    if r == opcoes[4]: validaPDFporEU()
    if r == opcoes[5]: limpaPasta(p1)
    if r == opcoes[6]: limpaPasta(p2)
    if r == opcoes[7]: analisaLogs(logs)
    if r == opcoes[8]: break # cancelar
    


# In[ ]:




