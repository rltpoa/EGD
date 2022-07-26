#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
from datetime import datetime
from checaPastas import Checador
from SEItools import operadorSEI
from EGDtools import (pegaEUformatado, pega_opcao, enviarDeQualquerUnidade, copy2clip, escreve_log)
from subprocess import check_call
import winsound
from portalRequests import expedientesBusca, etapasEUseitit
from getpass import getpass, getuser


# In[ ]:


fase2versao = '30/06/2022'
SD_DEL = 'SD-SMAMUS'
logfile = 'Fase2.txt'
delimitador = '------------------------------------------------------------------------------'


# In[ ]:


print(f'Automatização Fase2 atualizada em: {fase2versao}')
print('Inicializando...', end=' ')

try:
    user = getuser()
except:
    user = None
if not user is None:
    c = input(f'Entrar no SEI como {user}? [S/n] ')
    if c.lower().startswith('n'): user = None

headless_option = not '-b' in sys.argv[1:]
#headless_option = False
sei = operadorSEI(usuario=user, headless=headless_option)
print('ok')


# In[ ]:



dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
escreve_log('\n\n\n' + delimitador, logfile)
escreve_log(f'[{dh}] Iniciando Fase 2... usuário {sei.username}', logfile)
escreve_log(delimitador, logfile)

while True:
    
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    print('\n====================================================')
    euRaw = input('\nDigite o EU: ')
    if euRaw == '':
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(delimitador, logfile)
        escreve_log(f'[{dh}] Fim.', logfile)
        escreve_log(delimitador + '\n', logfile)
        break
    if len(euRaw) <7: euRaw = '002' + euRaw.zfill(6)
    
    eu = pegaEUformatado(euRaw)
    escreve_log(f'Verificando {eu}', logfile)
    copy2clip(eu)
    
    print('Atualizando pastas',end='... ')
    checador = Checador(atualiza=True)
    print('ok')
    
    print('Localizando EU',eu,end=': ')
    caminhos = checador.pegaCaminhoEU(eu)
    print(caminhos)
    if input('Continuar? [S/n] ').lower().startswith('n'):
        escreve_log('cancelado', logfile)
        escreve_log(delimitador, logfile)
        continue
    
    if not any(x in caminhos for x in ['p1','p2']):
        print(f'{eu} Não consta na Pasta 1 nem na Pasta 2\n')
        escreve_log(f'{eu} não consta na pasta 1 nem na pasta 2', logfile)
        escreve_log(delimitador, logfile)
        continue
    
    if 'p1' in caminhos: # verifica PDFs e move da P1 para P2
        
        print('---------')
        print('CONFERIR ARQUIVOS:')
        print('---------')
        escreve_log(f'{eu}: analisando arquivos...', logfile)
        p1 = checador.pegaCaminhoEU(eu,'p1')[0]
        subpastas, files = checador.listaPasta(eu,p1)
        if subpastas:
            for subpasta in subpastas:
                print(subpasta)
        pdfs = sorted([x for x in files if x.lower().endswith('.pdf')], reverse=True)
        for f in pdfs:
            print(f)
        winsound.MessageBeep()
        print('---------')
        if not input('[ENTER] para continuar ou qualquer outra tecla para cancelar...')=="":
            escreve_log(f'{eu}: usuário cancelou ao analisar os arquivos PDF', logfile)
            escreve_log(delimitador, logfile)
            continue
        escreve_log(f'{eu}: usuário considerou corretos os arquivos PDF', logfile)
        print('---------')
        
        escreve_log(f'{eu}: movendo da P1 para P2', logfile)
        print('Verificando Pasta 1:')
        pasta = checador.pegaCaminhoEU(eu,'p1')
        print(f'Movendo EU {eu} para Pasta 2', end='... ')
        checador.movePasta(eu,'p1','p2')
        print('ok')
    
    escreve_log(f'{eu}: verificando local do EU no SEI', logfile)
    print('\nVerificando locais abertos do EU',eu,end='... ')
    locais = sei.pegaLocaisAbertos(eu)
    print('ok')
    if not SD_DEL in locais:
        escreve_log(f'{eu}: movendo para {SD_DEL}', logfile)
        print(f'Movendo EU para {SD_DEL}...')
        res = enviarDeQualquerUnidade(sei, eu,SD_DEL)
        print('Enviado para:',res['destino'])
    else:
        escreve_log(f'{eu}: já estava em {SD_DEL}', logfile)
        print(f'EU já está em {SD_DEL}.')
    
    escreve_log(f'{eu}: verificando relacionados no SEI', logfile)
    print('Verificando relacionados que foram digitalizados',end='... ')
    checador = Checador(atualiza=True)
    relDigitalizados = checador.subpastasRelacionados(eu,'p2')
    print('ok')
    for r in relDigitalizados:
        print(f'Pesquisando {r}', end='... ', flush=True)
        if SD_DEL in sei.pegaLocaisAbertos(r):
            escreve_log(f'{eu}: relacionado {r} já estava em {SD_DEL}', logfile)
            continue
        escreve_log(f'{eu}: movendo relacionado {r} para {SD_DEL}', logfile)
        print(f'Movendo {r} para {SD_DEL}...')
        res = enviarDeQualquerUnidade(sei, r, SD_DEL)
        print('Enviado para:', res['destino'])

            
    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    escreve_log(f'[{dh}] {eu}', logfile)
    print(f'\n{eu}: fim')
    


# In[ ]:


print('Finalizando processos...',end=' ')
try:
    sei.driver.quit()
except:
    pass
# ! taskkill /im chrome.exe /f 2> NUL
# ! taskkill /im chromedriver.exe /f 2> NUL
print('ok')


# In[ ]:





# In[ ]:





# In[ ]:




