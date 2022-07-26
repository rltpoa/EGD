#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from portalRequests import (isDigital, expedientesBusca, PortalRequests)
import os
import pdfplumber
from io import BytesIO
from time import sleep


# In[ ]:


# VERSÃO 11/07/2022

# pegaDadosVistas
# fazer Try para capturar erros do Portal e informar ao usuário
# informar "falha ao pegar dados do Portal" ou retornar {'erro': motivo }


# In[ ]:


EGD_DEL = 'EGD-SMAMUS'


# In[ ]:


def copy2clip(txt):
    import win32clipboard as clip
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardText(str(txt))
    clip.CloseClipboard()
    return


# In[ ]:


def escreve_log(frase, log):
    frase = frase + '\n'
    with open(log, 'a') as lf:
        lf.write(frase)


# In[ ]:


def pegaLista(sei, unidade=EGD_DEL, coluna = 'recebidos'):
    #global sei
    listaResumida = sei.pegaListaResumida(unidade,coluna)
    return listaResumida


# In[ ]:


def pegaDoc(sei, nomeDoc):
    #global sei
    
    ifr = sei.iframe('iframe#ifrArvore')
    arvore = sei.css1('div[id="divArvore"] div[class="infraArvore"]')
    arquivos = arvore.find_elements(sei.bycss,'a[target="ifrVisualizacao"]')
    
    clicou = False
    docOk = [x for x in arquivos if x.text.startswith(nomeDoc)]
    if docOk: docOk[0].click()
    else: return {'erro':'documento não encontrado', 'nomedoc':nomeDoc}
    
    #pega nome do documento selecionado
    sei.iframe('iframe#ifrArvore')
    documento = sei.css('div#divArvore div.infraArvore a span.infraArvoreNoSelecionado')
    if not documento: return {'erro':'sem documento aberto', 'nomedoc':nomeDoc} # sem documento aberto
    documento = documento[0].text
    
    sei.iframe('iframe#ifrVisualizacao')
    ifArv = sei.css1('iframe#ifrArvoreHtml')
    src = ifArv.get_attribute('src')
    
    if 'acao=documento_download_anexo' in src:
        #PDF
        cookiejar = sei.driver.get_cookies()
        cookies = {x['name']:x['value'] for x in cookiejar}
        return {'link':src, 'cookies':cookies}
    
    sei.iframe('iframe#ifrArvoreHtml', reseta=False)
    conteudo = sei.css1('div#conteudo')
    conteudo.text
    txtlinhas = conteudo.text.split('\n')
    txtlinhas
    for idx, el in enumerate(txtlinhas):
        if not el=='Nº do Expediente Único (Processo Físico):': continue
        eu = txtlinhas[idx+1].strip(' ')
        break
    return {'eu':eu}
    


# In[ ]:


def pegaDadosSolicit(sei, p, unidade=EGD_DEL):
    #global sei
    r = sei.listaArquivos(p,unidade)
    doc = pegaDoc(sei, 'Solicitação de digitalização')
    if not 'eu' in doc: return doc
    eu = doc['eu']
    eu = pegaEUformatado(eu)
    return {'eu':eu}


# In[ ]:


def pegaDadosVistasSEI_OLD(driver, p, unidade='VISTAS-PS'):
    #global sei
    
    print('Verificando arquivos no SEI',end='... ')
    r = driver.listaArquivos(p,unidade)
    print('ok')
    
    print('Verificando documento 0',end='... ')
    downloadFolder = driver.download + '\\Downloads'
    doc = pegaDoc(driver, 'Documento 0 - Cópia digital de Expediente Único')
    print('ok')
    
    print('Baixando documento 0',end='...', flush=True)
    r = requests.get(doc['link'], cookies=doc['cookies'])
    pdfstream = BytesIO(r.content)
    print(' ok')
    
    print('Pegando dados',end='... ', flush=True)
    with pdfplumber.open(pdfstream) as pdf:
        conteudo = pdf.pages[0].extract_text()
    print('ok')
    
    linhas = conteudo.split('\n')
    nome = None
    email = None
    eu = None
    for l in linhas:
        if l.startswith('Requerente  '): nome = l.split('  ')[1]
        if l.startswith('e-mail Requerente  '): email = l.split('  ')[1]
        if l.startswith('Expediente único / Área Privativa  '): eu = l.split('  ')[1]
    if any(x==None for x in [nome,email,eu]):
        return {'erro':'dados não localizados no PDF','requerente':nome,'email':email,'eu':eu}
    if eu.endswith(' / 0'): eu = eu.split(' ')[0] + '00000'
    else: eu = eu.split(' ')[0] + eu.split(' ')[-1].zfill(5)
    eu = eu.replace('.', '')
    
    return {'requerente':nome,'email':email,'eu':eu}


# In[ ]:


def pegaDadosVistasSEI(driver, p, unidade='VISTAS-PS'):
    
    docVistas = '0 - Cópia digital de Expediente Único (digitalizaç'
    
    print('Listando documentos',end='... ', flush=True)
    portal = PortalRequests(usuario=driver.username, senha=driver.password)
    dados = portal.apiSEIgetDocs(p)
    #dados = dados.json()
    docVistas = '0 - Cópia digital de Expediente Único (digitalizaç'
    docs = [x for x in dados['documentos'] if x['tituloDocumento']==docVistas]
    if not docs: return {'erro': f'sem documento Vistas','proc':p}
    print('ok')

    print('Baixando documento 0',end='... ', flush=True)
    r = portal.get(docs[0]['linkAcesso'])
    pdfstream = BytesIO(r.content)
    print('ok')

    print('Pegando dados',end='... ', flush=True)
    with pdfplumber.open(pdfstream) as pdf:
        conteudo = pdf.pages[0].extract_text()
    print('ok')
    
    linhas = conteudo.split('\n')
    nome = None
    email = None
    eu = None
    for l in linhas:
        if l.startswith('Requerente  '): nome = l.split('  ')[1]
        if l.startswith('e-mail Requerente  '): email = l.split('  ')[1]
        if l.startswith('Expediente único / Área Privativa  '): eu = l.split('  ')[1]
    if any(x==None for x in [nome,email,eu]):
        return {'erro':'dados não localizados no PDF','requerente':nome,'email':email,'eu':eu}
    if eu.endswith(' / 0'): eu = eu.split(' ')[0] + '00000'
    else: eu = eu.split(' ')[0] + eu.split(' ')[-1].zfill(5)
    eu = eu.replace('.', '')
    
    return {'requerente':nome,'email':email,'eu':eu}


# In[ ]:


def pegaDadosVistas(driver, proc, unidade='VISTAS-PS'):
    
    portal = PortalRequests(usuario=driver.username, senha=driver.password)
    dados = portal.buscaPortalRaw2(proc)
    if not dados['data']['LicenciamentoFormDataList']: return {'erro':'sem resultados'}
    tipo = dados['data']['LicenciamentoFormDataList'][0]['formulario']['nome']
    if not tipo=='Cópia digital de Expediente Único (digitalização/vistas/cópias)': return {'erro': 'protocolo não é do tipo Vistas', 'tipo': tipo}
    if dados['data']['count'] <1: return {'erro': 'processo não encontrado no Portal Licenciamento'}
    nome = dados['data']['LicenciamentoFormDataList'][0]['data'].get('nomeRequerente','')
    email = dados['data']['LicenciamentoFormDataList'][0]['data'].get('emailRequerente','')
    usuario = dados['data']['LicenciamentoFormDataList'][0]['usuario']
    if 'expediente' in dados['data']['LicenciamentoFormDataList'][0]['data']:
        eu = dados['data']['LicenciamentoFormDataList'][0]['data']['expediente']['codigo']
    else: eu = []
    
    return {'requerente':nome,'email':email,'eu':eu, 'usuario':usuario}


# In[ ]:


def disponibilizaVistas(sei, unidade='VISTAS-PS'):
    #global sei
    processos = []
    processos += list(pegaLista(unidade,'recebidos').keys())
    processos += list(pegaLista(unidade,'gerados').keys())
    processos.reverse()
    
    print(f'Verificando {len(processos)} processos:')
    for idx, proc in enumerate(processos):
        
        print(f'{idx+1} - {proc}', end='... ')
        dados = pegaDadosVistas(proc)
        eu0 = dados['eu']
        if eu0 == None: # se não achou EU no Documento0, tenta pegar o primeiro que estiver relacionado
            rel0 = sei.listaRelacionados(proc,unidade)
            if rel0:
                rel = [list(rel0[x].keys())[0] for x in rel0]
                rel = [x for x in rel if x.startswith('002.') and len(x)==21]
                if rel: eu0 = rel[0]
        
        if 'erro' in dados and eu0==None:
            input('Não foi possível pegar dados do Documento 0. [ENTER] para continuar... ')
            continue
        
        nome = dados['requerente']
        email = dados['email']
        motivo = f'Vistas {proc}'
        eu = pegaEUformatado(eu0)
        if not eu:
            input(f'erro ao verificar EU {eu0}. [ENTER] para continuar... ')
            continue
        print(eu,end='... ')
        if not isDigital(eu):
            print('NÃO DIGITALIZADO.')
            continue
        
        relacionados = sei.listaRelacionados(eu,ACERVO_EU)
        relacionados_lista = [list(relacionados[x].keys())[0] for x in relacionados]
        
        etapas = etapasEUseitit(eu)
        etapasOnAtivas = [x['sei'] for x in etapas['etapasOn'] if 'andamento' in x['situacao'].lower()]
        
        etapas_disponibilizar = []
        for tipo in relacionados:
            if tipo.startswith('URBANISMO - Vista e Cópias de Expediente Único'): continue
            for p in relacionados[tipo]:
                if p in etapasOnAtivas: continue
                etapas_disponibilizar += [p]
        
        if not ACERVO_EU in sei.locais:
            r = enviarDeQualquerUnidadeAberta(sei, eu, ACERVO_EU)
            if not ACERVO_EU in r:
                print('\n\nEU não está em ACERVO-EU')
                return
        
        if not proc in relacionados_lista:
            print('relacionando',end='... ')
            sei.relacionaProcessos(eu, proc, ACERVO_EU)
        
        print('disponibilizando EU',end='... ')
        sei.disponibilizaAcessoExterno(eu, nome, email, motivo, unidade=ACERVO_EU, prazo=90)
        
        if etapas_disponibilizar: print('\nrelacionados',end='... ')
        for p in etapas_disponibilizar:
            print(p, end='... ')
            locs = sei.pegaLocaisAbertos(p, ACERVO_FISICO)
            if not ACERVO_FISICO in locs:
                r = enviarDeQualquerUnidadeAberta(sei, p, ACERVO_FISICO)
                if not ACERVO_FISICO in r:
                    input(f'não foi possível abrir em {ACERVO_FISICO}! [ENTER] para continuar... ')
                    continue
            r = sei.disponibilizaAcessoExterno(p, nome, email, motivo, unidade=ACERVO_FISICO, prazo=90)
            if not r.startswith('Disponibilização de Acesso Externo enviada.'):
                input('Erro! [ENTER] para continuar', end='... ')
            else:
                print('ok')
        
        print(f'concluindo {proc} em {unidade}',end='... ')
        sei.concluiProcesso(proc, unidade)
        copy2clip(proc)
        input('DEFERIR NO PORTAL. [ENTER] para continuar... ')
    
    print('fim')


# In[ ]:


def disponibilizaVistas1(sei, unidade='VISTAS-PS'):
    #global sei
    
    proc = input('Digite o protocolo: ')
    
    dados = pegaDadosVistas(proc)
    eu0 = dados['eu']
    if eu0 == None: # se não achou EU no Documento0, tenta pegar o primeiro que estiver relacionado
        rel0 = sei.listaRelacionados(proc,unidade)
        if rel0:
            rel = [list(rel0[x].keys())[0] for x in rel0]
            rel = [x for x in rel if x.startswith('002.') and len(x)==21]
            if rel: eu0 = rel[0]

    if 'erro' in dados and eu0==None:
        input('Não foi possível pegar dados do Documento 0. [ENTER] para continuar... ')
        return

    nome = dados['requerente']
    email = dados['email']
    motivo = f'Vistas {proc}'
    eu = pegaEUformatado(eu0)
    if not eu:
        input(f'erro ao verificar EU {eu0}. [ENTER] para continuar... ')
        return
    print(eu,end='... ')
    if not isDigital(eu):
        print('NÃO DIGITALIZADO.')
        return

    relacionados = sei.listaRelacionados(eu,ACERVO_EU)
    relacionados_lista = [list(relacionados[x].keys())[0] for x in relacionados]

    etapas = etapasEUseitit(eu)
    etapasOnAtivas = [x['sei'] for x in etapas['etapasOn'] if 'andamento' in x['situacao'].lower()]

    etapas_disponibilizar = []
    for tipo in relacionados:
        if tipo.startswith('URBANISMO - Vista e Cópias de Expediente Único'): continue
        for p in relacionados[tipo]:
            if p in etapasOnAtivas: continue
            etapas_disponibilizar += [p]

    if not ACERVO_EU in sei.locais:
        r = enviarDeQualquerUnidadeAberta(sei, eu, ACERVO_EU)
        if not ACERVO_EU in r:
            print('\n\nEU não está em ACERVO-EU')
            return

    if not proc in relacionados_lista:
        print('relacionando',end='... ')
        sei.relacionaProcessos(eu, proc, ACERVO_EU)

    print('disponibilizando EU',end='... ')
    sei.disponibilizaAcessoExterno(eu, nome, email, motivo, unidade=ACERVO_EU, prazo=90)

    if etapas_disponibilizar: print('\nrelacionados',end='... ')
    for p in etapas_disponibilizar:
        print(p, end='... ')
        locs = sei.pegaLocaisAbertos(p, ACERVO_FISICO)
        if not ACERVO_FISICO in locs:
            r = enviarDeQualquerUnidadeAberta(sei, p, ACERVO_FISICO)
            if not ACERVO_FISICO in r:
                input(f'não foi possível abrir em {ACERVO_FISICO}! [ENTER] para continuar... ')
                continue
        r = sei.disponibilizaAcessoExterno(p, nome, email, motivo, unidade=ACERVO_FISICO, prazo=90)
        if not r.startswith('Disponibilização de Acesso Externo enviada.'):
            input('Erro! [ENTER] para continuar', end='... ')
        else:
            print('ok')

    print(f'concluindo {proc} em {unidade}',end='... ')
    sei.concluiProcesso(proc, unidade)
    copy2clip(proc)
    input('DEFERIR NO PORTAL. [ENTER] para continuar... ')
    
    print('fim')


# In[ ]:


def disponibilizaGeral(sei, proc=None, nome=None, email=None, motivo=None, prazo='90', unidade='ACERVO-EU'):
    #global sei
    if not proc: proc = input('Digite o processo: ')
    vistas = input('Pegar dados de Vistas: ')
    if vistas:
        dados = pegaDadosVistas(vistas)
        nome = dados['requerente']
        email = dados['email']
        motivo = f'Vistas {proc}'
    if not nome: nome = input('Nome da pessoa: ')
    if not email: email = input('Email para acesso: ')
    if not motivo: motivo = input('Motivo: ')
    locs = sei.pegaLocaisAbertos(proc, unidade)
    aberto = True
    if not unidade in locs:
        aberto = False
        r = enviarDeQualquerUnidadeAberta(sei, proc, unidade)
        if not unidade in r:
            input(f'erro: não foi possível abrir {proc} em {unidade}. [ENTER] para continuar... ')
            return
    disp = sei.disponibilizaAcessoExterno(proc, nome, email, motivo, unidade=unidade, prazo=prazo)
    if not aberto:
        r = sei.concluiProcesso(proc, unidade)
    print(disp.split('\n')[0])


# In[ ]:


def pegaEUformatado(eu):
    eu = eu.replace(' ','')
    eu = eu.replace(',','.')
    if eu.startswith('002.'):
        miolo = eu[4:10]
    elif eu.startswith('002') and eu[3:4].isdigit():
        miolo = eu[3:9]
    else: miolo = eu[:6]
    final = '00000'
    if eu.count('.'):
        tail = eu[eu.find(miolo)+6:]
        if eu.startswith('002'): tail = eu[eu.find(miolo,3)+6:]
        if tail.count('.') == 1: final = eu.split('.')[-1].zfill(5)
        if tail.count('.') == 2 and not tail.startswith('.00.'): final = eu.split('.')[-1].zfill(5)
        if tail.count('.') == 3: final = eu.split('.')[-1].zfill(5)
    r = expedientesBusca(eu)
    euFormatado = False
    euLista = [x['codigo'] for x in r['data']['ExpedientesExpedienteUnicoList']]
    for euAchado in euLista:
        c = euAchado
        if not euAchado.startswith('002'+miolo): continue
        if not euAchado[-5:] == final: continue
        if c[3:9] == miolo:
            euFormatado = c[:3] + '.' + c[3:9] + '.' + c[9:11] + '.' + c[11:12] + '.' + c[12:]
            break
    if not euFormatado:
        return None # FALHOU
    return euFormatado


# In[ ]:


def pega_opcao(opcoes):
    for idx, op in enumerate(opcoes):
        print(f'{idx} - {op}')
    while True:
        r = input('Escolha uma das opções acima: ')
        if r in [str(x) for x in range(len(opcoes))]: break
    return opcoes[int(r)]


# In[ ]:


def enviarDeQualquerUnidadeAberta(driver, eu, destino):
    #global sei
    unidadesDisponiveis = driver.unidadesDisponiveis()
    locaisAbertos = driver.pegaLocaisAbertos(eu)
    unid = [x for x in unidadesDisponiveis if x in locaisAbertos]
    if len(unid)==0:
        # tentar reabrir em uma unidade disponível
        for u in unidadesDisponiveis:
            r = driver.reabreProcesso(eu,u)
            if r == True:
                if u == destino: return [destino]
                res = driver.enviarProcesso(eu,destino,origem=u)
                res = list(res.keys())
                return res
        winsound.MessageBeep()
        print('\n*** ERRO! Usuário sem acesso às unidades do EU:', locaisAbertos)
        return False
    r = driver.enviarProcesso(eu,destino,origem=unid[0])
    r = list(r.keys())
    return r

def enviarDeQualquerUnidade(sei, proc, destino):
    
    # 1) se já está no destino, return OK (return {'destino':destino})
    locaisAbertos = sei.pegaLocaisAbertos(proc, destino)
    if destino in locaisAbertos: return {'destino':destino}
    
    # 2) verifica unidades possíveis: minhas unidades - unidades tramitadas
    minhasUnidades = sei.unidadesDisponiveis()
    andamentos = sei.pegaAndamentos(proc, destino)
    tabela = sei.css1('tbody')
    linhas = tabela.find_elements(sei.bycss, 'tr')

    def unique(lista, reverse=True):
        if reverse: lista.reverse()
        r = []
        for x in lista:
            if not x in r: r+=[x]
        return r
    
    # 3) se não tem unidades possíveis: return FAIL (return {'destino':None})
    unidadesTramitadas = unique([x.find_elements(sei.bycss,'td')[1].text for x in linhas if len(x.find_elements(sei.bycss,'td'))>1])
    unidadesPossiveis = [x for x in unidadesTramitadas if x in minhasUnidades]
    if not unidadesPossiveis:
        #print(f'Sem acesso para enviar {proc} a {destino}. Fazer manualmente.')
        #input('[ENTER] para continuar... ')
        return {'destino': '', 'unidadesTramitadas':unidadesTramitadas}
    
    # 4) se destino é unidade possível: reabrir (return destino + fechar)
    if destino in unidadesPossiveis:
        sei.reabreProcesso(proc, destino)
        sei.atribuir(proc, destino, '')
        return {'destino':destino, 'fechar':destino}
    
    # 5) ver se está aberto em uma unidade possível: enviar (return destino + origem)
    aberto = [x for x in unidadesPossiveis if x in locaisAbertos]
    if aberto:
        sei.enviarProcesso(proc, destino, aberto[0])
        return {'destino':destino, 'origem':aberto[0]}
    
    # 6) se não está aberto em unidade possível: reabrir e enviar (return destino + fechar)
    if not aberto:
        sei.reabreProcesso(proc, unidadesPossiveis[0])
        sei.enviarProcesso(proc, destino, unidadesPossiveis[0])
        return {'destino':destino, 'fechar':unidadesPossiveis[0]}


# In[ ]:


# # ### TESTES
# from SEItools import operadorSEI
# from getpass import getuser
# sei = operadorSEI(headless=False, usuario=getuser())


# In[ ]:


# p = '22.0.000068694-1'
# r = pegaDadosVistas(sei, p)
# r


# In[ ]:


# portal = PortalRequests(usuario=sei.username, senha=sei.password)
# dados = portal.buscaPortalRaw2(p)


# In[ ]:





# In[ ]:


#sei.quit()


# In[ ]:





# In[ ]:




