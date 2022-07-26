#!/usr/bin/env python
# coding: utf-8

# In[ ]:


ACERVO_EU = 'ACERVO-EU'
EGD_DEL = 'EGD-SMAMUS'
SD_DEL = 'SD-SMAMUS'
ACERVO_FISICO = 'ACERVO FISICO-SMAMUS'
VISTAS_PS = 'VISTAS-PS'


# In[ ]:


versao = '14/07/2022'


# In[ ]:


def disponibilizaVistas(proc, unidade=VISTAS_PS):
    
    # pega EUs relacionados ou tenta pegar do documento
    # disponibiliza um por um
    # se não estiver relacionado, relaciona
    # disponibiliza as etapas relacionadas que não sejam etapa ONLINE ativas
    
    from EGDtools import (pegaDadosVistas, pegaDadosVistasSEI, enviarDeQualquerUnidade, pegaEUformatado, copy2clip, pega_opcao)
    from portalRequests import isDigital, etapasEUseitit, PortalRequests
    
    print('pegando dados do Portal',end='... ')
    dados = pegaDadosVistas(sei, proc)
    if 'erro' in dados:
        if 'tipo' in dados:
            print(f'Processo não é do tipo Vistas: {dados["tipo"]}')
            input('[ENTER] para continuar... ')
            return
        print('erro.')
        print('Tentando pegar dados de Documento 0:')
        dados = pegaDadosVistasSEI(sei, proc)
        if 'erro' in dados:
            print(f'Não foi possível pegar dados do processo {proc} em {unidade}.')
            input('[ENTER] para continuar... ')
            return
        print('ok')
    nome = dados['requerente']
    email = dados['email']
    motivo = f'Vistas {proc}'
    e = dados['eu']
    if e: e = e[:3] + '.' + e[3:9] + '.' + e[9:11] + '.' + e[11:12] + '.' + e[12:]
    print(nome, email)
    
    print('pegando EUs',end='... ')
    sei.processo=''
    listaEU = sei.listaEU(proc,unidade)
    if e and not e in listaEU: listaEU += [e]
    print(listaEU)
    tab = ' ' * 4
    
    eus_nao_digitalizados = []
    for eu in listaEU:
        
        print(f'Processando {eu}:')
        print(tab+f'verificando se é 100% Digital',end='... ')
        if not isDigital(eu):
            print(f'{eu}: EU não digitalizado.')
            #print('REVISAR MANUALMENTE.')
            input('[ENTER] para continuar... ')
            eus_nao_digitalizados += [eu]
            continue
        print('ok')
        
        print(tab+'verificando relacionados',end='... ')
        relacionados = sei.listaRelacionados(eu,ACERVO_EU)
        relacionados_lista = [list(relacionados[t].keys()) for t in relacionados]
        relacionados_lista = [p for x in relacionados_lista for p in x]
        print('ok')
        
        print(tab+'verificando etapas online ativas',end='... ')
        etapas = etapasEUseitit(eu)
        etapasOnAtivas = [x['sei'] for x in etapas['etapasOn'] if 'andamento' in x['situacao'].lower()]
        etapas_disponibilizar = []
        for tipo in relacionados:
            if tipo.startswith('URBANISMO - Vista e Cópias de Expediente Único'): continue
            for p in relacionados[tipo]:
                if p in etapasOnAtivas: continue
                etapas_disponibilizar += [p]
        print('ok')

        if not ACERVO_EU in sei.locais:
            print(tab+f'enviando para {ACERVO_EU}',end='... ')
            envio = enviarDeQualquerUnidade(sei, eu, ACERVO_EU)
            if not ACERVO_EU in envio['destino']:
                print(f'\n\nNão foi possível abrir {eu} em {ACERVO_EU}. Fazer manualmente.')
                input('[ENTER] para continuar... ')
                return
            print('ok')

        if not proc in relacionados_lista:
            print(tab+'relacionando',end='... ')
            sei.relacionaProcessos(eu, proc, ACERVO_EU)
            print('ok')

        print(tab+'disponibilizando EU',end='... ')
        sei.disponibilizaAcessoExterno(eu, nome, email, motivo, unidade=ACERVO_EU, prazo=90)
        print('ok')

        if etapas_disponibilizar: print(f'Disponibilizando {len(etapas_disponibilizar)} processos relacionados:')
        for idx, p in enumerate(etapas_disponibilizar):
            print(f'{idx+1}) {p}', end='... ', flush=True)
            locs = sei.pegaLocaisAbertos(p, ACERVO_FISICO)
            arqs = sei.listaArquivos(p, ACERVO_FISICO)
            pdfs = [arqs[x] for x in arqs if 'pdf.gif' in arqs[x]['icone']]
            if not pdfs:
                print('sem PDFs.')
                continue
            if not ACERVO_FISICO in locs:
                envio = enviarDeQualquerUnidade(sei, p, ACERVO_FISICO)
                if not ACERVO_FISICO in envio['destino']:
                    print(f'Não foi possível abrir {p} em {ACERVO_FISICO}. Fazer manualmente.')
                    input('[ENTER] para continuar... ')
                    continue
            r = sei.disponibilizaAcessoExterno(p, nome, email, motivo, unidade=ACERVO_FISICO, prazo=90)
            if not r.startswith('Disponibilização de Acesso Externo enviada.'):
                input('Erro! [ENTER] para continuar', end='... ')
            else:
                print('disponibilizado.')
    
    if eus_nao_digitalizados:
        print('\nATENÇÃO:')
        print(f'Os seguintes EUs ainda não estão digitalizados: {eus_nao_digitalizados}')
        print('Estes podem ser EUs relacionados ou o EU solicitado pelo requerente no Portal.')
        o = input('Deseja finalizar o protocolo mesmo assim? [S/n] ')
        if o.lower().startswith('n'):
            print(f'O protocolo {proc} permanecerá aberto em {VISTAS_PS}.')
            input('[ENTER] para continuar.')
            return
        
    print(f'concluindo {proc} em {unidade}',end='... ')
    sei.concluiProcesso(proc, unidade)
    copy2clip(proc)
    print('ok')
    print('deferindo no Portal',end='... ')
    portal = PortalRequests(usuario=sei.username,senha=sei.password)
    r = portal.baixaVistas(proc,'deferido')
    if not 'ok' in r: input('ERRO: verificar este protocolo no Portal.')
    else: print('ok')
    
    print('')


# In[ ]:


if __name__ == "__main__":
    
    import sys
    from SEItools import operadorSEI
    from getpass import getuser
    
    print(f'atualizado em: {versao}')
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
    
    while True:
        print('-------------------------------------------------------------------------------------')
        proc = input('Digite o protocolo: ')
        if proc == '': break
        disponibilizaVistas(proc)
        print('fim.\n\n')
    
    sei.quit()


# In[ ]:


# ## TESTES
# from EGDtools import (pegaDadosVistas, enviarDeQualquerUnidade, pegaEUformatado, copy2clip)
# from portalRequests import isDigital, etapasEUseitit, PortalRequests
# from SEItools import operadorSEI
# from getpass import getuser

# sei = operadorSEI(usuario=getuser(), headless=False)


# In[ ]:


# proc = '22.0.000077555-3'
# disponibilizaVistas(proc)


# In[ ]:


# portal = PortalRequests(usuario=sei.username,senha=sei.password)
# r = portal.baixaVistas(proc,'deferido')
# r


# In[ ]:


# docs = portal.apiSEIgetDocs(proc)
# docs


# In[ ]:


# docs.text


# In[ ]:


#dados['data']['count'] < 1


# In[ ]:





# In[ ]:


#sei.quit()


# In[ ]:





# In[ ]:




