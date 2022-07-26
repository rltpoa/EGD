#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
from datetime import datetime
from checaPastas import Checador
from portalRequests import (expCadastraSeloDigital, isDigital, expedientesBusca, etapasEUseitit, buscaPortalRaw,
                            listaTarefas, verificaTarefasSEI, verificaVS0400SEI, verificaAP0900SEI)
from EGDtools import (pegaEUformatado, pega_opcao, enviarDeQualquerUnidade, copy2clip, escreve_log)
from SEItools import operadorSEI
import winsound
from getpass import getuser, getpass


# - alterar responde_solicit_digit e responde_vistas para processar mais de 1 EU relacionado

# In[ ]:


fase3versao = '30/06/2022'
ACERVO_FISICO = 'ACERVO FISICO-SMAMUS'
ACERVO_EU = 'ACERVO-EU'
EGD_DEL = 'EGD-SMAMUS'
SD_DEL = 'SD-SMAMUS'
STD_DEL = 'STD-SMAMUS'
UVP_DEL = 'UVP-SMAMUS'
CEVEA_DEL = 'CEVEA-DEL'
VISTAS_PS = 'VISTAS-PS'
tags_BPM = ['VS0200', 'AP0500'] # para verificar no SEI se é BPM


# In[ ]:


logfile1 = 'Fase3.txt'
logfile2 = 'Fase3 lista de EUs.txt'
delimitador = '------------------------------------------------------------------------------'


# In[ ]:


def fase3(eu):
    print('Atualizando pastas',end='... ')
    checador = Checador(atualiza=True)
    print('ok')
    print('Localizando EU',eu,end=': ')
    caminhos = checador.pegaCaminhoEU(eu)
    print(caminhos)
    if input('Continuar? ').lower().startswith('n'): return
    
    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    escreve_log(f'[{dh}] {eu} pastas: {caminhos}', logfile1)
    escreve_log(f'[{dh}] {eu}', log = logfile2)
    
    if caminhos == []:
        print('EU não encontrado em nenhuma pasta. Verificar no SEI se foi realmente digitalizado.')
        op = input('Deseja revisar a Fase 3 mesmo assim? Digite "S" para continuar ou [ENTER] para cancelar: ')
        if not op.lower().startswith('s'):
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - operação cancelada pelo usuário - sem pasta de digitalização', logfile1)
            return
        print('Iniciando Fase 3 - REVISÃO')
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Iniciando Fase 3 sem arquivos de digitalização: REVISÃO', logfile1)
        if not isDigital(eu):
            print('Cadastrando selo 100% Digital no Expedientes',end='... ')
            res = expCadastraSeloDigital(eu)
            print('ok')
        else: print('100% Digital já cadastrado!')
        return 'ok'
    
    if len(caminhos)>1:
        while True:
            print('EU encontrado em mais de uma pasta. Escolha qual deseja executar:')
            print('0 - cancelar')
            if 'p1' in caminhos: print('1 - pasta 1 (iniciar fase 2)')
            if 'p2' in caminhos: print('2 - pasta 2 (revisar fase 2 e aguardar robô)')
            if 'p3' in caminhos: print('3 - pasta 3 (iniciar fase 3)')
            if 'digi' in caminhos: print('4 - pasta 100% Digital (revisar digitalizado)')
            op = input('Opção: ')
            if op == '0': return
            if op == '1' and 'p1' in caminhos : caminhos = ['p1']
            if op == '2' and 'p2' in caminhos : caminhos = ['p2']
            if op == '3' and 'p3' in caminhos : caminhos = ['p3']
            if op == '4' and 'digi' in caminhos : caminhos = ['digi']
            if len(caminhos)==1: break
    
    if caminhos == ['p1']:
        print('')
        print('*********************************************************************')
        print('*** ATENÇÃO: expediente na Pasta 1, ainda não passou pela fase 2. ***')
        print('*********************************************************************')
        if not input('Digite "SIM" para fazer Fase1 ou [ENTER] para cancelar... ').lower().startswith('s'): return None
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Pasta 1 para Pasta 2', logfile1)
        print('INICIANDO FASE 2')
        pasta = checador.pegaCaminhoEU(eu,'p1')
        print(f'Movendo pasta do EU {eu}', end='... ')
        checador.movePasta(eu,'p1','p2')
        print('ok')
        return ('fase1')
    
    if caminhos == ['p2']:
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Pasta 2', logfile1)
        print('Processo aguardando robô (fase 2)')
        return 'fase2'
    
    if caminhos == ['p3']:
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Pasta 3', logfile1)
        #input('iniciando Fase 3... [ENTER para continuar]')
        print('INICIANDO FASE 3...')
        print('movendo para 100% Digital',end='... ')
        checador.movePasta(eu,'p3','digi')
        print('ok')
        #print('Verificando 100% Digital...')
        if not isDigital(eu):
            print('Cadastrando selo 100% Digital no Expedientes',end='... ')
            res = expCadastraSeloDigital(eu)
            print('ok')
        else: print('100% Digital já cadastrado!')
        return 'ok'
    
    if caminhos == ['digi']:
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Pasta 100% Digital', logfile1)
        if not isDigital(eu):
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - criado selo 100% Digital', logfile1)
            print('Cadastrando selo 100% Digital no Expedientes',end='... ')
            res = expCadastraSeloDigital(eu)
            print('ok')
        else: print('100% Digital já cadastrado!')
        return 'digi'


# In[ ]:


def fase3sei(eu):
    
    global sei
    print('Listando processos relacionados...', flush=True)
    sei.pegaLocaisAbertos(eu,unidade=SD_DEL)
    sei.listaRelacionados(eu)
    locais = sei.locais
    relacionadosSD = sei.relacionados
    etapasTipo = {}
    for tipo in relacionadosSD:
        for p in relacionadosSD[tipo]:
            etapasTipo[p] = tipo.lower()
    print('')
    print('Relacionados:')
    for r in relacionadosSD:
        procs = [x for x in relacionadosSD[r]]
        print(r,': ',procs)
    print('')
    
    etapas = etapasEUseitit(eu)
    etapasOff = etapas['etapasOff']
    etapasOn = etapas['etapasOn']
    etapasOnsei = [x['sei'] for x in etapasOn]
    etapasOnativas = [x['sei'] for x in etapasOn if 'andamento' in x['situacao'].lower()]
    etapasOninativas = [x['sei'] for x in etapasOn if not 'andamento' in x['situacao'].lower()]
    etapasOffativas = [x['sei'] for x in etapasOff if 'andamento' in x['situacao'].lower()]
    
    abertosSD = []
    for tipo in relacionadosSD:
        abertosSD += [(x,tipo) for x in relacionadosSD[tipo] if relacionadosSD[tipo][x]=='protocoloAberto']
    
    # procura tarefas BPM em aberto para avisar o usuário e guarda na lista "temtarefa"
    print('Verificando Tarefas BPM... ',end='',flush=True)
    temtarefa = []
    for tipo in relacionadosSD:
        # procura tarefas AP0900 em aberto
        if tipo.startswith('URBANISMO - Aprovação de Projeto'):
            listaT = listaTarefas('AP0900')
            listaTsei = [x['formData']['procedimentoFormatadoSei'] for x in listaT]
            for proc in relacionadosSD[tipo]:
                if proc in listaTsei: temtarefa += [proc]
        # procura tarefas VS0400 em aberto
        if tipo.startswith('URBANISMO - Habite-se'):
            listaT = listaTarefas('VS0400')
            listaTsei = [x['formData']['procedimentoFormatadoSei'] for x in listaT]
            for proc in relacionadosSD[tipo]:
                if proc in listaTsei: temtarefa += [proc]
    print('ok')
    
    # avisa o usuário sobre tarefas em aberto no BPM
    if temtarefa: print('Listando Tarefas BPM:', flush=True)
    for proc in temtarefa:
        print(proc,end='... ', flush=True)
        copy2clip(proc)
        winsound.MessageBeep()
        print('*** ATENÇÃO: Verificar Portal BPM')
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - Portal BPM - tarefa BPM encontrada: {proc}', logfile1)
        input('[ENTER] para continuar... ')
        print('')
        copy2clip(eu)
    
#     for tipoProc in relacionadosSD:
#         if 'URBANISMO - Aprovação de Projeto Arquitetônico' in tipoProc and not 'Prioritários' in tipoProc:
#             relSei = list(relacionadosSD[tipoProc].keys())[0]
#             copy2clip(relSei)
#             winsound.MessageBeep()
#             print('*** ATENÇÃO! Verificar Portal BPM:',relSei,'\n')
#             input('[ENTER] para continuar... ')
#             copy2clip(eu)
    
    if abertosSD:
        print(f'Verificando relacionados em {SD_DEL}:')
        
        for p, tipo in abertosSD:
            print(p, end = '... ', flush=True)
            
            if p in etapasOffativas:
                trata_etapa_ativa(p, eu, SD_DEL)
                
            if not p in etapasOffativas:
                
                if p in etapasOnativas:
                    trata_etapa_ativa(p, eu, SD_DEL)
                
                elif 'vista' in tipo.lower():
                    responde_vistas(p, SD_DEL)
                    
                elif tipo.startswith('GESTÃO DE INFORMAÇÃO - GESTÃO DOCUMENTAL: Solicitação de Digitalização de Expediente Único')                or tipo.startswith('GESTÃO DE INFORMAÇÃO - GESTÃO DOCUMENTAL: Desarquivamento Processo Físico/Solicitação de Documentos'):
                    responde_solicit_digit(p, eu, SD_DEL)
                
                elif 'habite-se' in tipo.lower():
                    responde_habitese(p, eu, SD_DEL)
                
                else:
                    print(f'concluindo em {ACERVO_FISICO}',end='... ', flush=True)
                    sei.enviarProcesso(p, ACERVO_FISICO, origem=SD_DEL, forcaEnvio=True)
                    sei.concluiProcesso(p, ACERVO_FISICO)
                    
            print('ok')
    else:
        print(f'Nenhum relacionado estava em {SD_DEL}.')
    
    if SD_DEL in locais:
        print(f'\nMovendo EU {eu} para {ACERVO_EU}')
        sei.enviarProcesso(eu,ACERVO_EU,origem=SD_DEL,forcaEnvio=True)
        andamento = 'Transformado em 100% digital. Atualizado'
        sei.insereAndamento(eu,andamento,ACERVO_EU)
    else:
        print(f'EU já está em {ACERVO_EU}.')
    
    # FECHA TODOS OS PROTOCOLOS RELACIONADOS ABERTOS EM ACERVO FISICO
#     print(f'\nVerificando relacionados abertos em {ACERVO_FISICO}...')
#     sei.listaRelacionados(eu,unidade=ACERVO_FISICO)
#     relacionados = sei.relacionados
#     abertos = []
#     for tipo in relacionados:
#         abertos += [x for x in relacionados[tipo] if relacionados[tipo][x]=='protocoloAberto' and not x in etapasOnsei]
#     if abertos:
#         print(f'Fechando relacionados:')
#         for p in abertos:
#             print(p,end='... ')
#             sei.concluiProcesso(p, ACERVO_FISICO)
#             print('ok')
    print('')
        


# In[ ]:


def trata_etapa_ativa(proc, eu, unid):
    winsound.MessageBeep()
    copy2clip(proc)
    print(f'*** ATENÇÃO: ETAPA ATIVA! {proc} em {unid}')
    opcoes = [
    'ignorar',
    f'concluir em {ACERVO_FISICO}',
    'devolver à unidade remetente com andamento informando 100% Digital',
    'enviar à outra unidade com andamento',
    'enviar à outra unidade sem andamento',
]
    r = pega_opcao(opcoes)
    copy2clip(eu)
    if r==opcoes[1]:
        sei.enviarProcesso(proc, ACERVO_FISICO, origem=unid, forcaEnvio=True)
        sei.concluiProcesso(proc, ACERVO_FISICO)
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - concluído processo {proc} em {ACERVO_FISICO}', logfile1)
    if r==opcoes[2]:
        sei.pegaAndamentos(proc,unid)
        corrente = sei.correntedeunidades
        if len(corrente)==0:
            print('Não foi possível determinar as unidades de origem. Faça a devolução de forma manual.')
            input('[ENTER] para continuar... ')
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - etapa ativa {proc} permaneceu em {unid} - VERIFICAR', logfile1)
            return
        if len(corrente)>1: corrente = corrente[1:]
        destino = corrente[0]
        if len(corrente)>1:
            print('\nSelecione a unidade remetente mais próxima ou anteriores:')
            destino = pega_opcao(corrente)
        print('Devolvendo para:', destino)
        input('[ENTER] para continuar... ')
        andamento = f'EU {eu} 100% digitalizado. Devolvendo para a unidade remetente: {destino}'
        sei.insereAndamento(proc, andamento, unid)
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - inserido andamento em {proc}: {andamento}', logfile1)
        d = sei.enviarProcesso(proc, destino, origem=unid, forcaEnvio=True)
        if not destino.upper() in d:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - ERRO! Processo {proc} NÃO ENVIADO para {destino}. Permanece em {unid}.', logfile1)
            print(f'Atenção! Não foi possível enviar o processo {proc} para {destino}. Verificar manualmente.')
            input('[ENTER] para continuar... ')
        else:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - processo {proc} enviado para {destino}', logfile1)
            print('ok')
    if r==opcoes[3]:
        destino = input('Unidade destino: ')
        andamento = input('Andamento: ')
        sei.insereAndamento(proc, andamento, unid)
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - inserido andamento em {proc}: {andamento}', logfile1)
        r = sei.enviarProcesso(proc, destino, origem=unid, forcaEnvio=True)
        if not destino.upper() in r:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - ERRO! Processo {proc} NÃO ENVIADO para {destino}. Permanece em {unid}.', logfile1)
            print(f'Atenção! Não foi possível enviar o processo {proc} para {destino}. Verificar manualmente.')
            input('[ENTER] para continuar... ')
        else:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - processo {proc} enviado para {destino}', logfile1)
            print('ok')
    if r==opcoes[4]:
        destino = input('Unidade destino: ')
        r = sei.enviarProcesso(proc, destino, origem=unid, forcaEnvio=True)
        if not destino.upper() in r:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - ERRO! Processo {proc} NÃO ENVIADO para {destino}. Permanece em {unid}.', logfile1)
            print(f'Atenção! Não foi possível enviar o processo {proc} para {destino}. Verificar manualmente.')
            input('[ENTER] para continuar... ')
        else:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - processo {proc} enviado para {destino}', logfile1)
            print('ok')


# In[ ]:


def responde_solicit_digit(proc, eu, unidade_origem):
    print(f'Respondendo Solicitação de digitalização {proc}', end='... ', flush=True)
        
    sei.pegaAndamentos(proc,unidade_origem)
    uni = sei.andamento_unidades[0]
    
    if uni in [EGD_DEL, SD_DEL, ACERVO_FISICO, ACERVO_EU]:
        sei.concluiProcesso(proc, unidade_origem)
        print('ok')
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - Processo {proc} concluído em {unidade_origem} - solicitação de digitalização - pedido interno: {uni}', logfile1)
        return
        
    if not uni or uni==unidade_origem:
        print(f'Unidade remetente não localizada. Concluindo em {uni}', end='... ', flush=True)
        sei.concluiProcesso(proc, unidade_origem)
        print('ok')
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - Processo {proc} concluído em {unidade_origem} - solicitação de digitalização - unidade de origem não identificada', logfile1)
    else:
        andamento = f'EU {eu} transformado em 100% digital. Devolvendo para unidade remetente: {uni}'
        sei.insereAndamento(proc, andamento, unidade_origem)
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - inserido andamento em {proc}: {andamento}', logfile1)
        print(f'Enviando para {uni}',end='... ', flush=True)
        res = sei.enviarProcesso(proc, uni, origem=unidade_origem)
        if not uni in res:
            copy2clip(proc)
            winsound.MessageBeep()
            print(f'Erro ao tentar enviar o processo {proc} de {unidade_origem} para {uni}. Verificar a unidade destino e enviar manualmente.')
            input('[ENTER] para continuar... ')
            copy2clip(eu)
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - erro ao tentar enviar {proc} em {unidade_origem} para {uni} - solicitação de digitalização', logfile1)
        else:
            print('ok')
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - enviado {proc} de {unidade_origem} para {uni} - solicitação de digitalização', logfile1)
        
        
def responde_vistas(proc, unidade_origem):
    print('Devolvendo Vistas com andamento',end='...', flush=True)
    sei.enviarProcesso(proc,'VISTAS-PS',origem=unidade_origem, forcaEnvio=True)
    andamento = 'Expediente único digitalizado. Aguardar acesso externo.'
    sei.insereAndamento(proc,andamento, VISTAS_PS)
    print('ok')
    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    escreve_log(f'[{dh}] {eu} - SEI - enviado {proc} para {VISTAS_PS}', logfile1)
    
# def identifica_unidade_remetente(proc, unidade_origem):
#     unidades_ignorar = [EGD_DEL, SD_DEL, ACERVO_FISICO, ACERVO_EU]
#     sei.pegaAndamentos(proc,unidade_origem)
#     andamentos = pd.read_html(sei.andamentos)[0]
#     andamentos = [x for x in andamentos.Unidade.unique().tolist() if not x in unidades_ignorar]
#     corrente = sei.correntedeunidades
#     corrente = [x for x in corrente if not x in unidades_ignorar] 
#     corrente = list(dict.fromkeys(corrente)) # remove duplicados
#     if len(corrente)==0:
#         print(f'Não foi possível determinar a unidades remetente. Processo {proc} em {unidade_origem}.')
#         print('Fazer a devolução manualmente!')
#         input('[ENTER] para continuar... ')
#         return None
#     if len(corrente)>1: corrente = corrente[1:]
#     destino = corrente[0]
#     if not destino in andamentos:
#         u = destino.split('-')[0]
#         for x in andamentos:
#             if u in x: destino = x
#     if len(corrente)>1:
#         print('\nSelecione a unidade remetente mais próxima ou anteriores:')
#         destino = pega_opcao(corrente)
#     return destino

def responde_habitese(proc, eu, unidade_origem=EGD_DEL):
    print('Verificando Habite-se',proc,end='... ', flush=True)
    sei.pegaAndamentos(proc, unidade_origem)
    #andamentos = pd.read_html(sei.andamentos)
    andamentos = sei.andamento_unidades
    andamento = f'Expediente único {eu} digitalizado.'
    sei.insereAndamento(proc,andamento,unidade_origem)
    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    escreve_log(f'[{dh}] {eu} - SEI - inserido andamento em {proc}: {andamento}', logfile1)
    if not STD_DEL in andamentos:
        print(f'enviando para {STD_DEL}',end='... ', flush=True)
        res = sei.enviarProcesso(proc, STD_DEL, origem=unidade_origem)
        return
    opcoes = [
        'ignorar',
        f'concluir em {ACERVO_FISICO}',
        f'enviar à {UVP_DEL} com andamento informando 100% Digital',
        f'enviar à {STD_DEL} com andamento informando 100% Digital',
    ]
    copy2clip(proc)
    winsound.MessageBeep()
    r = pega_opcao(opcoes)
    copy2clip(eu)
    if r==opcoes[0]:
        print('ok')
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - Habite-se {proc} em {unidade_origem} ignorado', logfile1)
        return
    if r==opcoes[1]:
        sei.enviarProcesso(proc, ACERVO_FISICO, origem=unidade_origem, forcaEnvio=True)
        sei.concluiProcesso(proc, ACERVO_FISICO)
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(f'[{dh}] {eu} - SEI - Habite-se {proc}: de {unidade_origem} concluído em {ACERVO_FISICO}', logfile1)
        return
    if r==opcoes[2]: unidade_destino = UVP_DEL
    if r==opcoes[3]: unidade_destino = STD_DEL
    print(f'enviando para {unidade_destino}',end='... ', flush=True)
    res = sei.enviarProcesso(proc, unidade_destino, origem=unidade_origem)
    print('ok')
    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    escreve_log(f'[{dh}] {eu} - SEI - Habite-se {proc}: enviado de {unidade_origem} para {unidade_destino}', logfile1)
    
        


# In[ ]:


print(f'Automatização Fase3 atualizada em: {fase3versao}')
print('Inicializando...', end=' ')
try:
    user = getuser()
except:
    user = None
if not user is None:
    c = input(f'Entrar no SEI como {user}? ')
    if c.lower().startswith('n'): user = None
headless_option = not '-b' in sys.argv[1:]
sei = operadorSEI(usuario=user, headless=headless_option)
print('ok')


# In[ ]:


dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
escreve_log('\n\n\n' + delimitador, logfile1)
escreve_log(f'[{dh}] Iniciando Fase 3... usuário {sei.username}', logfile1)
escreve_log(f'[{dh}] automatização da fase3 atualizada em: {fase3versao}', logfile1)
escreve_log(delimitador, logfile1)

escreve_log('\n\n\n' + delimitador, log = logfile2)
escreve_log(f'[{dh}] Iniciando Fase 3... usuário {sei.username}', log = logfile2)
escreve_log(delimitador, log = logfile2)


# In[ ]:


while True:
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    print('\n====================================================')
    euRaw = input('\nDigite o EU: ')
    if euRaw == '':
        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        escreve_log(delimitador, logfile1)
        escreve_log(f'[{dh}] Fim.', logfile1)
        escreve_log(delimitador + '\n', logfile1)
        
        escreve_log(delimitador, log = logfile2)
        escreve_log(f'[{dh}] Fim.', log = logfile2)
        escreve_log(delimitador + '\n', log = logfile2)
        break
    if len(euRaw) <7: euRaw = '002' + euRaw.zfill(6)
        
    eu = pegaEUformatado(euRaw)
    
    copy2clip(eu)

    f = fase3(eu)
    if f == None: continue
    
    if f == 'ok' or f=='digi':
        if not 'sei' in locals() or not type(sei) == operadorSEI: sei = operadorSEI(headless=True)
        
        # While necessário para retomar o uso do SEI após longo tempo de inatividade
        while True:
            try:
                fase3sei(eu)
            except:
                sei.logaSei()
            else:
                break
        
        print(f'\nVerificando processos na {EGD_DEL}...', flush=True)
        sei.listaRelacionados(eu,unidade=EGD_DEL)
        relacionados = sei.relacionados
        
        # AVISO DE VISTAS
#         vistas_abertos = []
#         for tipo in relacionados:
#             if not 'vista' in tipo: continue
#             vistas_abertos = [x for x in relacionados[tipo] if relacionados[tipo][x]=='protocoloAberto']
#         if vistas_abertos:
#             print(f'*** ATENÇÃO! Vistas na {EGD_DEL}:', vistas_abertos, '\n')
#             input('[ENTER] para continuar... ')
        
        for tipo in relacionados:
            
            for proc in relacionados[tipo]:
                
                if relacionados[tipo][proc] == 'protocoloFechado':
                    continue
                print(proc,end='... ', flush=True)
                
                if 'habite-se' in tipo.lower():
                    responde_habitese(proc, eu, EGD_DEL)
                
                elif 'vista' in tipo.lower():
                    responde_vistas(proc, EGD_DEL)
                    
                elif tipo.startswith('URBANISMO - EVU'):
                    unidade_EVU = CEVEA_DEL
                    print(f'Enviando EVU para {unidade_EVU}',end='... ', flush=True)
                    res = sei.enviarProcesso(proc, unidade_EVU, origem=EGD_DEL)
                    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    escreve_log(f'[{dh}] {eu} - SEI - EVU {proc}: enviado para {unidade_EVU}', logfile1)
                    print('ok')
                    
                elif tipo.startswith('GESTÃO DE INFORMAÇÃO - GESTÃO DOCUMENTAL: Solicitação de Digitalização de Expediente Único')                or tipo.startswith('GESTÃO DE INFORMAÇÃO - GESTÃO DOCUMENTAL: Desarquivamento Processo Físico/Solicitação de Documentos'):
                    r = responde_solicit_digit(proc, eu, EGD_DEL)
                
                elif tipo.startswith('URBANISMO - Fracionamento de Solo'):
                    print(f'Fracionamento de solo: enviando para {ACERVO_FISICO}',end='... ', flush=True)
                    sei.enviarProcesso(proc, ACERVO_FISICO, origem=EGD_DEL, forcaEnvio=True)
                    #sei.concluiProcesso(proc, ACERVO_FISICO)
                    print('ok')
                    dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    escreve_log(f'[{dh}] {eu} - SEI - Fracionamento de Solo {proc}: enviado para {ACERVO_FISICO}', logfile1)
                        
                elif tipo.startswith('EXPEDIENTE ÚNICO - Etapa'):
                    
                    # testa se a etapa está ativa no Expedientes (caso que pode ser Orquestra)
                    etapas = etapasEUseitit(eu)
                    etapasOff = etapas['etapasOff']
                    etapasOffativas = [x['sei'] for x in etapasOff if 'andamento' in x['situacao'].lower()]
                    if proc in etapasOffativas:
                        trata_etapa_ativa(proc, eu, EGD_DEL)
                    else:
                        print(f'concluindo em {ACERVO_FISICO}',end='... ')
                        sei.enviarProcesso(proc, ACERVO_FISICO, origem=EGD_DEL, forcaEnvio=True)
                        sei.concluiProcesso(proc, ACERVO_FISICO)
                        dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        escreve_log(f'[{dh}] {eu} - etapa {proc}: concluído em {ACERVO_FISICO}', logfile1)
                    print('ok')
                    
                else:
                    trata_etapa_ativa(proc, eu, EGD_DEL)    
        
#         print(f'\nVerificando processos em {VISTAS_PS}...', flush=True)
#         sei.listaRelacionados(eu,unidade=VISTAS_PS)
#         relacionados = sei.relacionados
#         for tipo in relacionados:
#             for proc in relacionados[tipo]:
#                 if relacionados[tipo][proc] == 'protocoloFechado':
#                     continue
#                 if 'vista' in tipo.lower():
#                     print(proc,end='... ', flush=True)
#                     sei.pegaAndamentos(proc, VISTAS_PS)
#                     andamentos = pd.read_html(sei.andamentos)[0]
#                     andamentos = [x for x in andamentos.Unidade.unique().tolist()]
#                     if not EGD_DEL in andamentos:
#                         responde_vistas(proc, VISTAS_PS)
                    
                        
        
    if f=='fase1' or f=='fase2':
        
        print('\nVerificando locais abertos do EU',eu,end='... ')
        # While necessário para retomar o uso do SEI após longo tempo de inatividade
        while True:
            try:
                locais = sei.pegaLocaisAbertos(eu)
            except:
                sei.logaSei()
            else:
                break
        print('ok')
        if not SD_DEL in locais:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - enviado para {SD_DEL}', logfile1)
            print(f'Movendo EU para {SD_DEL}...')
            res = enviarDeQualquerUnidade(sei, eu,SD_DEL)
            print('Enviado para:',res['destino'])
        else:
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - já estava em {SD_DEL}', logfile1)
            print(f'EU já está em {SD_DEL}.')
        
        print('Verificando relacionados que foram digitalizados',end='... ')
        checador = Checador(atualiza=True)
        relDigitalizados = checador.subpastasRelacionados(eu,'p2')
        print('ok')
        for r in relDigitalizados:
            if SD_DEL in sei.pegaLocaisAbertos(r): continue
            print(f'Movendo {r} para {SD_DEL}...')
            res = enviarDeQualquerUnidade(sei, r,SD_DEL)
            print('Enviado para:', res['destino'])
            dh = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            escreve_log(f'[{dh}] {eu} - SEI - enviado {r} para {SD_DEL}', logfile1)
    print('\nFim')
    #continua = input('Checar fase 3 para novo EU?')
    #if continua.lower().startswith('n'): break
    


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


# TESTES
# eu = '002.293437.00.0.00000'
# checador = Checador(atualiza=True)
# p2 = checador.pegaCaminhoEU(eu,'p2')
# p2


# In[ ]:





# In[ ]:




