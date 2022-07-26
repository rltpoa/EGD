#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from uuid import uuid4
from urllib.parse import urlparse
from datetime import datetime, timedelta
import time
import hashlib
from getpass import getpass, getuser


# In[ ]:


# versão 11/07/2022


# In[ ]:


usuariosBPM = []
# pegar do Portal


# # NOTAS
# 
# - API para visualizar documentos SEI:
# https://licenciamento-api.procempa.com.br/api/sei-docs?numeroProcesso=22.0.000073625-6
# 
# - API para consultar processos SEI:
# https://licenciamento-api.procempa.com.br/api/consultarProcessoSei?numeroProcesso=22.0.000071752-9
# 
# - pega revisores Portal (função usuariosBPM):
# https://licenciamento-api.procempa.com.br/api/usuarios-autorizados/revisor?ignoreBpm=true
# 
# - pega etapas de EU:
# https://expedientes-api.procempa.com.br/api/eu/ad52b053f86013817724ff4935ce7d01
# 
# 

# In[ ]:





# In[ ]:



def extraiDadosPortal(resultados):
    if not type(resultados) == list: resultados = [resultados]
    dadosEtapa = []
    c = 0
    for r in resultados:
        c+=1
        dados = {}
        tipoForm = r['dadosFormulario']['idTipoFormulario']
        #print(tipoForm)
        if tipoForm in ['habite-se']:
            dados = {
                'titulo':r.get('formulario',{}).get('nome',''),
                'habitese':r['data']['vistoria']['tipoVistoria']['tipo'],
                'sei':r.get('procedimentoFormatadoSei',''),
                'dataEntrada':r.get('dataCriacaoSei',''),
                'pr_nome':r.get('data',{}).get('proprietario',{}).get('nome',''),
                'pr_cpfcnpj':r.get('data',{}).get('proprietario',{}).get('cpfCnpj',''),
                'endereco':r.get('data',{}).get('vistoria',{}).get('enderecoCDL',{}).get('logradouro','') + ', ' + r.get('data',{}).get('vistoria',{}).get('enderecoCDL',{}).get('numero',''),
                'rt_nome':r.get('data',{}).get('rt',{}).get('nome',''),
                'rt_regtipo':r.get('data',{}).get('rt',{}).get('registroProfissional',{}).get('tipo',''),
                'rt_reg':r.get('data',{}).get('rt',{}).get('registroProfissional',{}).get('numeroRegistro',''),
                'rt_email':r.get('data',{}).get('rt',{}).get('email',''),
                'complementado':(True,False)[not r.get('dataComplementacao','')],
                'revisor':r.get('revisor') or '',
                'EUinformado':r.get('data',{}).get('vistoria',{}).get('numeroExpediente',''),
                }
            
        
        if tipoForm in ['form-generico','form-generico-sem-artrrt','aprovacao-projeto-licenciamento-expresso']:
            dados = {
                'titulo':r.get('formulario',{}).get('nome',''),
                'sei':r.get('procedimentoFormatadoSei',''),
                'dataEntrada':r.get('dataCriacaoSei',''),
                'pr_nome':r.get('data',{}).get('nomeProprietario',''),
                'pr_cpfcnpj':r.get('data',{}).get('cpfCnpjProprietario',''),
                'endereco':r.get('data',{}).get('enderecoCdl',{}).get('enderecoFormatadoCurto',''),
                'rt_nome':r.get('data',{}).get('artRespTecnico',{}).get('nome',''),
                'rt_regtipo':'',
                'rt_reg':r.get('data',{}).get('artRespTecnico',{}).get('registro',''),
                'rt_email':r.get('data',{}).get('emailRespTecnico',''),
                'complementado':(True,False)[not r.get('dataComplementacao','')],
                'revisor':r.get('revisor') or '',
                'EUinformado':r.get('data',{}).get('expediente',{}).get('codigo',''),
                }
            
        if tipoForm in ['certidao']:
            dados = {
                'titulo':r.get('formulario',{}).get('nome',''),
                'sei':r.get('procedimentoFormatadoSei',''),
                'dataEntrada':r.get('dataCriacaoSei',''),
                'nome':r.get('data',{}).get('nomeRequerente',''),
                'cpfcnpj':r.get('data',{}).get('cpfCnpjRequerente',''),
                'email':r.get('data',{}).get('emailRequerente',''),
                'complementado':(True,False)[not r.get('dataComplementacao','')],
                'revisor':r.get('revisor') or '',
                'EUinformado':r.get('data',{}).get('expediente',{}).get('codigo',''),
                }
        
        if tipoForm in ['padrao']:
            dados = {
                'titulo':r.get('formulario',{}).get('nome',''),
                'sei':r.get('procedimentoFormatadoSei',''),
                'dataEntrada':r.get('dataCriacaoSei',''),
                'pr_nome':r.get('data',{}).get('interessados',{}).get('proprietario',{}).get('nome',''),
                'pr_cpfcnpj':r.get('data',{}).get('interessados',{}).get('proprietario',{}).get('cpfCnpj',''),
                'endereco':r.get('data',{}).get('local',{}).get('enderecoCdlList',{}).get('enderecosCDL',{})[0].get('logradouro','') + ', ' + r.get('data',{}).get('local',{}).get('enderecoCdlList',{}).get('enderecosCDL',{})[0].get('numero',''),
                'rt_nome':r.get('data',{}).get('interessados',{}).get('rt',{}).get('nome',''),
                'rt_regtipo':r.get('data',{}).get('interessados',{}).get('rt',{}).get('registroProfissional',{}).get('tipo',''),
                'rt_reg':r.get('data',{}).get('interessados',{}).get('rt',{}).get('registroProfissional',{}).get('numeroRegistro',''),
                'rt_email':r.get('data',{}).get('interessados',{}).get('rt',{}).get('email',''),
                'complementado':(True,False)[not r.get('dataComplementacao','')],
                'revisor':r.get('revisor') or '',
                'EUinformado':r.get('data',{}).get('expediente',{}).get('codigo',''),
                }
            
        if dados == {}:
            print('item:',c,' - Tipo de formulário desconhecido:',tipoForm)
            #print(r)
            return False
        
        if dados.get('endereco')==', ': dados['endereco']=''
        
        if type(dados['revisor']) == dict:
            dados['revisor'] = dados['revisor'].get('username','')
        
        if 'dataEntrada' in dados:
            d = int(dados['dataEntrada'])/1000
            dados['dataEntrada'] = datetime.fromtimestamp(d)
        
        dados['fase'] = r['resultado'] or 'Em revisão'
        
        dadosEtapa.append(dados)
    
    return dadosEtapa


# In[ ]:


def buscaPortalRaw(busca, url = 'https://licenciamento-api.procempa.com.br/graphql'):
    graphqlQuery = {"operationName":"formsData",
    "variables":{"skip":0,
    "limit":20,
    "term":"{\"procedimentoFormatadoSei\":{\"$regex\":\".*"+ busca +".*\"},\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1}}"},
    "query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
    x = requests.post(url, json = graphqlQuery)
    resp = x.json()
    return resp

def buscaPortalRaw2(busca,url='https://licenciamento-api.procempa.com.br/graphql'):
    graphqlQuery = {"operationName":"formsData","variables":{"skip":0,"limit":20,"term":"{\"$and\":[{\"procedimentoFormatadoSei\":{\"$exists\":true}},{\"procedimentoFormatadoSei\":{\"$ne\":null}}],\"dadosFormulario.idSetor\":{\"$in\":[\"b83919a5-c7b4-495e-8647-3dc3e20d86ba\",\"fb204548-8a72-452a-906e-f8e641a19abf\",\"7f738961-7f4a-454f-bb2c-05c5eb05c1e3\",\"33732631-c644-4b64-9de4-09d296b4ab36\"]},\"$or\":[{\"procedimentoFormatadoSei\":{\"$regex\":\".*"+busca+".*\"}},{\"dataAsString\":{\"$regex\":\".*"+busca+".*\"}}],\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1}}"},"query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    dataAsString\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    dataUltimaAtualizacaoPortal\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
    while True:
        x = requests.post(url, json = graphqlQuery)
        if not x==None: break
    return x

def buscaPortal(busca):
    resp = buscaPortalRaw(busca)
    res = resp['data']['LicenciamentoFormDataList']
    return extraiDadosPortal(res)

def buscaPortalBPMRaw(busca,url='https://licenciamento-api.procempa.com.br/graphql'):
    graphqlQuery = {"operationName":"formData",
                    "variables":{"id":busca},
                    "query":"query formData($id: String!) {\n  LicenciamentoFormDataById(id: $id) {\n    id\n    idFormulario\n    formulario {\n      id\n      schema\n      uiSchema\n      documentos\n      __typename\n    }\n    dadosFormulario\n    data\n    documentos\n    documentosDados\n    extraInfo\n    idProcedimentoSei\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComparecimento\n    resultado\n    usuario\n    revisor\n    bpmUser\n    bpmProcessDefinition\n    bpmProcessInstance\n    bpmTasks {\n      id\n      taskName\n      contrato\n      checklist {\n        id\n        itens {\n          id\n          descricao\n          obrigatorio\n          ordem\n          done\n          username\n          data\n          __typename\n        }\n        __typename\n      }\n      username\n      data\n      taskData\n      __typename\n    }\n    marcadoresPublicos {\n      id\n      __typename\n    }\n    __typename\n  }\n}\n"}
    x = requests.post(url, json = graphqlQuery)
    resp = x.json()
    return resp

def buscaPortalBPM(busca):
    r = buscaPortalBPMRaw(busca)
    sei = r['data']['LicenciamentoFormDataById']['procedimentoFormatadoSei']
    eu = r['data']['LicenciamentoFormDataById']['data']['expediente']['codigo']
    tarefa = ''
    lindeiros = r['data']['LicenciamentoFormDataById']['data']['dadosTriagem'].get('expedientesLindeiros','')
    dados = {
        'sei':sei,
        'eu':eu,
        'tarefa':tarefa,
        'lindeiros':lindeiros,
    }
    return dados


# In[ ]:


def baixaListaBPM(login):
    url_BPM = 'https://licenciamento-api.procempa.com.br/api/bpm/task/pending/[login]?vars=idLicenciamento&vars=retornoApi&p=[p]&c=[tam]'
    listagem = []
    url = url_BPM.replace('[login]',login).replace('[p]','0').replace('[tam]','0')
    r = requests.get(url)
    total = r.headers['X-CUSTOM-COUNT-TOTAL-ITEMS']
    print(f'Baixando {total} tarefas',end='... ')
    url = url_BPM.replace('[login]',login).replace('[p]','0').replace('[tam]',total)
    r = requests.get(url)
    listagem = r.json()
    print('ok')
    return listagem


# In[ ]:


def baixaListaBPMapi(task='ap0800'):
    #headers={'Authorization':"Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ1ZVp5c3JIelQwS3FHMUpldmc3c19vQkhtYW5HV1ZJWi03MmtTTS0wbXljIn0.eyJqdGkiOiI2NDNlNDY5OC03ZDc0LTQ3ZjYtOWQzOC1iMjU3ZTdiYTVlNDUiLCJleHAiOjE2Mjk4MjY5ODcsIm5iZiI6MCwiaWF0IjoxNjI5ODI2MDg3LCJpc3MiOiJodHRwczovL3Nzby1wbXBhLnByb2NlbXBhLmNvbS5ici9hdXRoL3JlYWxtcy9wbXBhIiwiYXVkIjpbImV4cGVkaWVudGVzIiwiYWNjb3VudCIsImFnZW5kYW1lbnRvIl0sInN1YiI6IjNmY2VjMzNmLTI1ZGMtNGY0MC05NTQ2LWFkZmQxODRjMGJiOSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImxpY2VuY2lhbWVudG8tYWRtaW4iLCJub25jZSI6IjI4NDEzMjNlLTY0OTktNGIyNy1iMzE1LWEyZmRmMGIwMzI2NSIsImF1dGhfdGltZSI6MTYyOTgyNjA4Niwic2Vzc2lvbl9zdGF0ZSI6IjVjNzE2Nzk2LTY5ZGEtNGJiZS05ZjQxLWZhNzU5NWIxYjAzZSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImV4cGVkaWVudGVzIjp7InJvbGVzIjpbInRyYW5zZmVyaXItZXRhcGFzIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWNyaWFyLWV4cGVkaWVudGVzIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWV4Y2x1aXItcmVnaXN0cm9zIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWV4Y2x1aXItbHRpcCIsInVyYmFuaXNtby1leHBlZGllbnRlcy10cmFuc2ZlcmlyLWV0YXBhIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWVkaXRhci1lbmRlcmVjb3MiLCJ0cmlhZ2VtIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWV4Y2x1aXItcGVkIiwiZXhjbHVpci1yZWdpc3Ryb3MiLCJQcm90b2NvbG8iLCJ1cmJhbmlzbW8tZXhwZWRpZW50ZXMtZXhjbHVpci1ldGFwYXMiLCJ1cmJhbmlzbW8tZXhwZWRpZW50ZXMtYXNzb2NpYXItc2VpLWV0YXBhIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLXBlc3F1aXNhIiwiYW51bGFjYW8iLCJ1cmJhbmlzbW8tZXhwZWRpZW50ZXMtZXhjbHVpci1saWNlbmNhcyIsInVyYmFuaXNtby1leHBlZGllbnRlcy1hbnVsYWNhbyIsImVuZGVyZWNvcyIsInVyYmFuaXNtby1leHBlZGllbnRlcy1leGNsdWlyLWVuZGVyZWNvcyIsInVyYmFuaXNtby1leHBlZGllbnRlcy1lZGl0YXItZXRhcGFzIiwiZXRhcGFzIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWV4Y2x1aXItdmlzdG9yaWFzIiwidXJiYW5pc21vLWV4cGVkaWVudGVzLWV4Y2x1aXItcGFyY3NvbG8iLCJ1cmJhbmlzbW8tZXhwZWRpZW50ZXMtZXhjbHVpci1ldnUiXX0sImxpY2VuY2lhbWVudG8tYWRtaW4iOnsicm9sZXMiOlsicmV2aXNvciIsInVyYmFuaXNtby1saWNlbmNpYW1lbnRvLWFycXVpdm8iLCJ1cmJhbmlzbW8tbGljZW5jaWFtZW50by1kaXN0cmlidWlyIiwicHJlVHJpYWdlbSIsImRpZ2l0YWxpemFjYW8iLCJkaXN0cmlidWlkb3IiLCJ1cmJhbmlzbW8tbGljZW5jaWFtZW50by1kaWdpdGFsaXphY2FvIiwidXJiYW5pc21vLWxpY2VuY2lhbWVudG8tcmV2aXNhci1wcm9jZXNzbyIsInVyYmFuaXNtby1saWNlbmNpYW1lbnRvLXByZS10cmlhZ2VtIiwiYXJxdWl2byIsImNyaWFyTWFyY2Fkb3JQdWJsaWNvIiwidXJiYW5pc21vLWxpY2VuY2lhbWVudG8tdXN1YXJpby1saWNlbmNpYW1lbnRvIiwidXJiYW5pc21vLWxpY2VuY2lhbWVudG8tY3JpYXItbWFyY2Fkb3ItcHVibGljbyJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19LCJhZ2VuZGFtZW50byI6eyJyb2xlcyI6WyJhZ2VuZGFtZW50by12ZXItYWdlbmRhLXNldG9yIiwidXNlciJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJSYWZhZWwgTGF1eCBUYWJiYWwiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJyYWZhZWwudGFiYmFsIiwiZ2l2ZW5fbmFtZSI6IlJhZmFlbCIsImZhbWlseV9uYW1lIjoiTGF1eCBUYWJiYWwiLCJlbWFpbCI6InJhZmFlbC50YWJiYWxAcG9ydG9hbGVncmUucnMuZ292LmJyIn0.jXEPplDkLkOK3glpIC0HRuBkP7XejWwZBjOpEMalvdH1IVF1nuxGUB5Nzn6rbzC9v6iG8VPC6iskuhAEHE5lGDz7BWJbOU26Tkhu_FkfH8xiKrfSQPuGMmV3aUrmVZt6s7Qa-YjBdJYHsoSpx_urM3QHKygJ_yGfkiTJPQCTBV7Tc-EUPPIwRFIUdd0QapjJl1Kue7ZOkHtruWSvdmu5R_t7gJXIOpxAprqpIYd-67qnvEHLx0vLbExOw1t4e24kvtKS_VMh0eNi3yJ11jrypq8GfYBIL9mBoxX-8HYpdQ11v4LUfv8Fj0eQRgADr_Ge66hi6mDJa6LVsB3LHDRwKQ"}    
    url = f'https://licenciamento-api.procempa.com.br/api/tasks-by-name/{task}?sei=true'
    r = requests.get(url)
    return r


# In[ ]:



def expCadastraEtapa(eu, dados, url = 'https://expedientes-api.procempa.com.br/api/eventhandler'):
    
    print('Etapa',dados['sei'],'EU',eu,end=' ... ')
    
    rr = etapasEU(eu)
    idExpediente = rr['id_eu']
    if dados['sei'] in rr['etapasOn'] + rr['etapasOff']:
        print('Já existe etapa cadastrada com este SEI.')
        return False
    
    r = consultaSEI(eu)
    idProcedimentoRelacionadoSei = r['dados']['idProcedimento']
    
    hoje = datetime.today().isoformat()[:-3]+'Z'
    cod = pegaCodigoEtapa(dados)
    ocorrencia = getEtapaPorCod(cod)
    ocorrenciaConcat = ''
    if ocorrencia['descricao']: ocorrenciaConcat += ocorrencia['descricao']
    if ocorrencia['tipo']: ocorrenciaConcat += ocorrencia['tipo']
    if ocorrencia['subtipo']: ocorrenciaConcat += ' - ' + ocorrencia['subtipo']
    ocorrencia['concatenada'] = ocorrenciaConcat
    
    # adivinha regtipo
    if dados['rt_regtipo'] == '':
        dados['rt_regtipo'] = 'CREA' # padrão
        rtreg = dados['rt_reg']
        if rtreg.lower().startswith('a'): dados['rt_regtipo'] = 'CAU'
        if rtreg.lower().startswith('rs'): dados['rt_regtipo'] = 'CREA'
        
    tiporeg = {'CREA':1,'CAU':2}[dados['rt_regtipo']]
    cpfcnpj = ('CNPJ','CPF')[len([x for x in dados['pr_cpfcnpj'] if x.isdigit()]) == 11]
    cpfcnpjcod = {'CPF':3,'CNPJ':1}[cpfcnpj]
    
    string = idExpediente + hoje
    m = hashlib.md5(string.encode()).hexdigest()
    idAleatorio = m[:8] + '-' + m[8:12] + '-' + m[12:16] + '-' + m[16:20] + '-' + m[20:]
    
    payload = {"type":"expedientes/SERVER_SALVAR_ETAPA",
    "payload":{"idExpediente":idExpediente,
    "isNew":True, # 
    "etapa":{
        "id":idAleatorio,#"e8a9eae0-628e-11eb-92a9-697e794ef7cb", # aleatório ?
        "data":hoje,
        "ocorrencia":{
            "id":ocorrencia['id'],
            "codigo":ocorrencia['codigo'],
            "descricao":ocorrencia['descricao'],
            "tipo":ocorrencia['tipo'],
            "subtipo":ocorrencia['subtipo'],
            "disabled":ocorrencia['disabled'],
            "descricaoConcatenada":ocorrenciaConcat},
        "situacao":{"key":1,"value":"Em Andamento"},
        "dataDespacho":hoje,
        "idProcedimentoRelacionadoSei":idProcedimentoRelacionadoSei,
        "procedimentoFormatadoSei":dados['sei'],
        "proprietario":{"nome":dados['pr_nome'],
                        "tipoDocumento":{"key":cpfcnpjcod,"value":cpfcnpj},
                        "documento":dados['pr_cpfcnpj'],
                        "endereco":dados['endereco']},
        "responsavelTecnico":{
            "nome":dados['rt_nome'],
            "tipoRegistro":{"key":tiporeg,"value":dados['rt_regtipo']},
            "registro":dados['rt_reg'],
            "email":dados['rt_email']},
        "marcacaoTramitadaOnline":True},
        "next":{"type":"app/Expedientes/Etapas/LIMPA_STORE"}}}
    x = requests.post(url, json = payload)
    resp = x.json()
    if resp['ok'] == 1:
        print('ok')
    else:
        print('ERRO!')
    return resp


# In[ ]:


def expCadastraSeloDigital(eu, url = 'https://expedientes-api.procempa.com.br/api/eventhandler'):
    rr = etapasEU(eu)
    idExpediente = rr['id_eu']
    hoje = datetime.today().isoformat()[:-3]+'Z'
    string = idExpediente + hoje
    m = hashlib.md5(string.encode()).hexdigest()
    idEtapa = m[:8] + '-' + m[8:12] + '-' + m[12:16] + '-' + m[16:20] + '-' + m[20:]
    payload = {"type":"expedientes/SERVER_SALVAR_ETAPA",
               "payload":{"idExpediente":idExpediente,
                          "isNew":True,
                          "etapa":{"id":idEtapa,
                                   "data":hoje,
                                   "ocorrencia":{"id":"5cd4db68-c908-11e9-a32f-2a2ae2dbcce4",
                                                 "codigo":"700",
                                                 "descricao":"PROCESSO 100% DIGITAL",
                                                 "tipo":"",
                                                 "subtipo":"",
                                                 "disabled":None,
                                                 "descricaoConcatenada":"PROCESSO 100% DIGITAL"},
                                   "situacao":{"key":3,"value":"Concluída"},
                                   "dataDespacho":hoje},
                          "next":{"type":"app/Expedientes/Etapas/LIMPA_STORE"}}}
    x = requests.post(url, json = payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
    resp = x.json()
    if resp['ok'] == 1:
        print('ok')
    else:
        print('ERRO!')
    return resp


# In[ ]:


def expedientesListaEtapas(url='https://expedientes-api.procempa.com.br/graphql'):
    payload = {"operationName":"QueryOcorrencias",
               "variables":{"term":"{\"$or\":[{\"disabled\":{\"$exists\":false}},{\"disabled\":false}],\"term\":\"\"}"},
               "query":"query QueryOcorrencias($term: String) {\n  ExpedientesOcorrenciaList(term: $term, skip: 0, limit: 2000) {\n    id\n    codigo\n    descricao\n    tipo\n    subtipo\n    disabled\n    __typename\n  }\n}\n"}
    x = requests.post(url, json=payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
    return x.json()


# In[ ]:


def expedientesBusca(EU, url='https://expedientes-api.procempa.com.br/graphql'):
    payload = {"operationName":"ExpedientesExpedienteUnicoListQuery",
               "variables":{"term":"{\"term\":\""+EU+"\",\"orderBy\":{\"codigo\":1}}",
                            "skip":0,
                            "limit":10},
               "query":"query ExpedientesExpedienteUnicoListQuery($term: String, $skip: Int, $limit: Int) {\n  count: ExpedientesExpedienteUnicoCount(term: $term)\n  ExpedientesExpedienteUnicoList(term: $term, skip: $skip, limit: $limit) {\n    id\n    numero\n    areaPrivativa\n    codigo\n    bloqueios {\n      id\n      __typename\n    }\n    enderecos {\n      id\n      tipo {\n        key\n        value\n        __typename\n      }\n      logradouro {\n        nomeLogradouro\n        nomeBairro\n        enderecoFormatadoCurto\n        __typename\n      }\n      numero\n      __typename\n    }\n    etapas {\n      id\n      ocorrencia {\n        id\n        codigo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    x = requests.post(url, json=payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
    return x.json()


# In[ ]:


def detalhesEUporId(id_eu, url='https://expedientes-api.procempa.com.br/graphql'):
    payload = {"operationName":"ExpedientesExpedienteUnicoByIdQuery","variables":{"id":id_eu},"query":"query ExpedientesExpedienteUnicoByIdQuery($id: String!) {\n  ExpedientesExpedienteUnicoById(id: $id) {\n    id\n    numero\n    codigo\n    areaPrivativa\n    codigo\n    idProcedimentoSei\n    procedimentoFormatadoSei\n    bloqueios {\n      id\n      motivo\n      data\n      unidadeSei {\n        id\n        sigla\n        descricao\n        __typename\n      }\n      orgao {\n        codigo\n        descricao\n        id\n        __typename\n      }\n      __typename\n    }\n    historicoBloqueios {\n      id\n      motivo\n      data\n      acao {\n        key\n        value\n        __typename\n      }\n      unidadeSei {\n        id\n        sigla\n        descricao\n        __typename\n      }\n      bloqueio {\n        id\n        data\n        unidadeSei {\n          id\n          sigla\n          descricao\n          __typename\n        }\n        motivo\n        __typename\n      }\n      __typename\n    }\n    enderecos {\n      id\n      tipo {\n        value\n        __typename\n      }\n      logradouro {\n        nomeLogradouro\n        nomeBairro\n        enderecoFormatadoCurto\n        __typename\n      }\n      numero\n      __typename\n    }\n    etapas {\n      id\n      data\n      idProcedimentoSei\n      procedimentoFormatadoSei\n      urlConsultaPublicaSei\n      ocorrencia {\n        id\n        codigo\n        tipo\n        subtipo\n        descricao\n        __typename\n      }\n      situacao {\n        key\n        value\n        __typename\n      }\n      proprietario {\n        nome\n        tipoDocumento {\n          key\n          value\n          __typename\n        }\n        documento\n        endereco\n        __typename\n      }\n      responsavelTecnico {\n        nome\n        tipoRegistro {\n          key\n          value\n          __typename\n        }\n        registro\n        email\n        artRrt\n        __typename\n      }\n      dataDespacho\n      observacoes\n      isFromLicencasOnline\n      isFromLicenciamento\n      inicioObra\n      conclusaoObra\n      marcacaoTramitadaOnline\n      __typename\n    }\n    estudosViabilidade {\n      id\n      data\n      resultado {\n        key\n        value\n        __typename\n      }\n      tipo {\n        key\n        value\n        __typename\n      }\n      assuntos {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      atividades {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      equipamentos {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      tipoParecer {\n        key\n        value\n        __typename\n      }\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        __typename\n      }\n      numeroParecer\n      expedienteComum\n      areaObjeto\n      indiceAdquirido\n      indicePermutado\n      observacoes\n      isFromLicenciamento\n      urlDocumentoSei\n      __typename\n    }\n    projetosEdificacao {\n      id\n      data\n      resultado {\n        key\n        value\n        __typename\n      }\n      tipoProjeto {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      areaTerreno\n      areaOcupada\n      areaCondominial\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        __typename\n      }\n      quantidadeBlocos\n      projetoEdificacaoBlocos {\n        id\n        blocos\n        pavimentos\n        subsolos\n        identificacao\n        __typename\n      }\n      detalhamentos {\n        id\n        atividade {\n          id\n          codigo\n          descricao\n          __typename\n        }\n        tipoConstrucao {\n          id\n          descricao\n          __typename\n        }\n        areaComputadaAConstruir\n        areaComputadaExistente\n        areaComputadaTotal\n        areaNaoAdensavelAConstruir\n        areaNaoAdensavelExistente\n        areaNaoAdensavelTotal\n        areaNaoAdensavelIsentaAConstruir\n        areaNaoAdensavelIsentaExistente\n        areaNaoAdensavelIsentaTotal\n        areaTotalAConstruir\n        areaTotalExistente\n        areaTotal\n        economiasAConstruir\n        economiasExistente\n        economiasTotal\n        observacoes\n        __typename\n      }\n      observacoes\n      __typename\n    }\n    parcelamentosSolo {\n      id\n      data\n      resultado {\n        key\n        value\n        __typename\n      }\n      tipoProjeto {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      tipo {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      areaTerrenoTitulada\n      areaTerrenoLocal\n      areaObjeto\n      areaCondominial\n      quantidadeLotes\n      modalidadeIndenizacao {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        proprietario {\n          nome\n          tipoDocumento {\n            key\n            value\n            __typename\n          }\n          documento\n          endereco\n          __typename\n        }\n        __typename\n      }\n      areaIndenizacao\n      nomeLoteamento\n      observacoes\n      condicionantes\n      formaDesmembramento {\n        key\n        value\n        __typename\n      }\n      valorRecompra\n      quantidadeLotesResultantes\n      areaTotal\n      quantidadeLotesDoacao\n      areaDoacao\n      aero\n      areaNaoEdificavel {\n        key\n        value\n        __typename\n      }\n      areaTitulada\n      areaTotalPrivada\n      areaTotalPublica\n      dataAprovacao\n      dataDeferimentoEVU\n      dataGarantias\n      dataLicenciamento\n      dataRegImoveis\n      dataViabilidade\n      docRegImoveis\n      escola\n      garantias\n      lei {\n        key\n        value\n        __typename\n      }\n      numLotes\n      pastaArquivo\n      pracas\n      recuoViario\n      sistemaViario\n      tipoParcSituacao {\n        key\n        value\n        __typename\n      }\n      nomeCondominio\n      areaProtecao {\n        key\n        value\n        __typename\n      }\n      areaAplicIATO\n      numAreasPrivativas\n      areaCPPDDUA\n      areaCPProjeto\n      taxaOcupacaoPDDUA\n      areaTotalProjHabit\n      areaTotalProjUsoComum\n      recuoJardim\n      estacionamentosProj\n      areaTotalTerrUnidAutonomas\n      __typename\n    }\n    vistorias {\n      id\n      dataVistoria\n      sequenciaVistoria\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        __typename\n      }\n      projetoEdificacao {\n        id\n        __typename\n      }\n      resultado {\n        key\n        value\n        __typename\n      }\n      tipoVistoria {\n        key\n        value\n        __typename\n      }\n      dataInicioObra\n      dataConclusaoObra\n      dataOcupacao\n      quantidadePavimentos\n      areaTotalVistoriada\n      observacoes\n      cartaHabitacao {\n        id\n        textoCarta\n        dataHomologacao\n        __typename\n      }\n      atividades {\n        id\n        atividade {\n          id\n          codigo\n          descricao\n          __typename\n        }\n        identificacao\n        areaVistoriada\n        quantidadeVistoriada\n        estacionamentosPrivativosCobertos\n        estacionamentosPrivativosDescobertos\n        estacionamentosPrivativosParcialmenteCobertos\n        estacionamentosCondominiaisCobertos\n        estacionamentosCondominiaisDescobertos\n        estacionamentosCondominiaisParcialmenteCobertos\n        estacionamentosPNE\n        temMarquise\n        tipoConstrucao {\n          id\n          descricao\n          __typename\n        }\n        endereco {\n          tipo {\n            key\n            value\n            __typename\n          }\n          logradouro {\n            id\n            nomeLogradouro\n            enderecoFormatadoCurto\n            __typename\n          }\n          numero\n          __typename\n        }\n        economias {\n          id\n          economiaInicio\n          economiaFim\n          __typename\n        }\n        observacoes\n        __typename\n      }\n      isSubstituida\n      dataSubstituicao\n      idVistoriaSubstituida\n      __typename\n    }\n    licencas {\n      id\n      data\n      ocorrencia {\n        id\n        codigo\n        descricao\n        tipo\n        subtipo\n        __typename\n      }\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          descricao\n          tipo\n          subtipo\n          __typename\n        }\n        __typename\n      }\n      resultado {\n        key\n        value\n        __typename\n      }\n      areaTotal\n      areaObjeto\n      areaAdensavel\n      atividades {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      estacionamentos\n      economiasExistentes\n      economiasPropostas\n      tipoConstrucao {\n        id\n        codigo\n        descricao\n        __typename\n      }\n      complemento\n      observacoes\n      codigoProcessamentoDam\n      artRrt\n      endereco {\n        tipo {\n          key\n          value\n          __typename\n        }\n        logradouro {\n          id\n          nomeLogradouro\n          enderecoFormatadoCurto\n          __typename\n        }\n        numero\n        __typename\n      }\n      tipoArt {\n        key\n        value\n        __typename\n      }\n      complementoEndereco\n      areaConstrucaoRegular\n      areaConstrucaoIrregular\n      areaExistente\n      areaTotalAPermanecer\n      areaTotalADemolir\n      areaExistenteAPermanecer\n      areaExistenteADemolir\n      areaAumento\n      tipoMaterial {\n        key\n        value\n        __typename\n      }\n      vagasProjeto\n      testada\n      dataInicioObra\n      dataTerminoObra\n      isFromLicencasOnline\n      isFromLicenciamento\n      codigoAutenticacao\n      codigoProcessamentoDam\n      grupamentoAtividade\n      restricaoPorte\n      vagasObrigatorias\n      atividadeReciclagem\n      atividadeEspecificaReciclagem\n      atendimentoVagasObrigatoriasPddua\n      perguntaTerrenoEsquina\n      prazoValidade\n      perguntaLicenciamentoAmbiental\n      perguntaGrandeGerador\n      perguntaCondicionantes\n      documentosAnexados\n      dataAprovacaoCondicionanteBacia\n      dataAprovacaoCondicionanteFossa\n      dataAprovacaoCondicionanteOutro\n      descricaoCondicionanteOutro\n      declaracaoExtraReciclagem\n      urlDocumentoSei\n      dataHomologacao\n      userHomologacao\n      dataIndeferimento\n      motivoIndeferimento\n      userIndeferimento\n      atividade\n      ga\n      validade\n      __typename\n    }\n    certidoes {\n      id\n      data\n      ocorrencia {\n        id\n        codigo\n        descricao\n        tipo\n        subtipo\n        __typename\n      }\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          descricao\n          tipo\n          subtipo\n          __typename\n        }\n        __typename\n      }\n      isFromLicenciamento\n      justificativa\n      numeroCertidao\n      texto\n      validade\n      prazoValidade\n      dataHomologacao\n      userHomologacao\n      dataIndeferimento\n      motivoIndeferimento\n      userIndeferimento\n      listaEnderecos\n      requerente\n      dadosTemplate\n      identificacaoProcesso\n      urlDocumentoSei\n      __typename\n    }\n    laudos {\n      id\n      referencia {\n        key\n        value\n        __typename\n      }\n      tipoLaudo {\n        key\n        value\n        __typename\n      }\n      proprietario {\n        nome\n        tipoDocumento {\n          key\n          value\n          __typename\n        }\n        documento\n        endereco\n        __typename\n      }\n      responsavelTecnico {\n        nome\n        tipoRegistro {\n          key\n          value\n          __typename\n        }\n        registro\n        email\n        __typename\n      }\n      dataLaudo\n      prazoAtendimento\n      caracteristicasObjeto {\n        key\n        value\n        __typename\n      }\n      pavimentos\n      alteracoesConstatadas {\n        key\n        value\n        __typename\n      }\n      recomendacoes\n      especificacaoCaracteristicasObjeto\n      especificacaoAlteracoesConstatadas\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        data\n        __typename\n      }\n      laudoInicial {\n        id\n        referencia {\n          value\n          __typename\n        }\n        dataLaudo\n        __typename\n      }\n      textoLaudo\n      dataValidade\n      artRrt\n      __typename\n    }\n    laudosLtip {\n      id\n      tipoLaudo {\n        key\n        value\n        __typename\n      }\n      dataLaudo\n      proprietario {\n        nome\n        tipoDocumento {\n          key\n          value\n          __typename\n        }\n        documento\n        endereco\n        __typename\n      }\n      responsavelTecnico {\n        nome\n        tipoRegistro {\n          key\n          value\n          __typename\n        }\n        registro\n        email\n        __typename\n      }\n      prazoAtendimento\n      tipoProprietario {\n        key\n        value\n        __typename\n      }\n      artrrt\n      pavimentos\n      riscoColapso {\n        key\n        value\n        __typename\n      }\n      interdicao {\n        key\n        value\n        __typename\n      }\n      marquiseSacada {\n        key\n        value\n        __typename\n      }\n      alvaraBombeiros {\n        key\n        value\n        __typename\n      }\n      elevador {\n        key\n        value\n        __typename\n      }\n      elevadorAtendeLei1275 {\n        key\n        value\n        __typename\n      }\n      recomendacoes\n      etapa {\n        id\n        ocorrencia {\n          id\n          codigo\n          tipo\n          subtipo\n          descricao\n          __typename\n        }\n        data\n        __typename\n      }\n      laudoInicial {\n        id\n        referencia {\n          value\n          __typename\n        }\n        dataLaudo\n        __typename\n      }\n      textoLaudo\n      ltipItems\n      dataVencimentoLaudo\n      __typename\n    }\n    __typename\n  }\n}\n"}
    x = requests.post(url, json=payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
    return x.json()


# In[ ]:


def etapasEU(eu):
    r = expedientesBusca(eu)
    while True:
        id_eu = None
        for idx, eulistado in enumerate(r['data']['ExpedientesExpedienteUnicoList']):
            if eulistado['codigo'] == eu.replace('.',''):
                id_eu = eulistado['id']
                break
        if id_eu == None:
            print(f'portalRequests.etapasEUoffline: EU {eu} não encontrado')
            return False
        else: break
    dets = detalhesEUporId(id_eu)
    if not dets['data']['ExpedientesExpedienteUnicoById']['etapas']: dets['data']['ExpedientesExpedienteUnicoById']['etapas']=[]
    etapasOff = [x['procedimentoFormatadoSei'] for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas'] if not x['marcacaoTramitadaOnline'] and x['procedimentoFormatadoSei']]
    etapasOn = [x['procedimentoFormatadoSei'] for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas'] if x['marcacaoTramitadaOnline'] and x['procedimentoFormatadoSei']]
    isDigital = '700' in [x['ocorrencia']['codigo'] for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas']]
    idProcSei = dets['data']['ExpedientesExpedienteUnicoById']['idProcedimentoSei']
    return {'etapasOff':etapasOff,'etapasOn':etapasOn,'isDigital':isDigital,'id_eu':id_eu,'idProcedimentoSei':idProcSei}


# In[ ]:


def etapasEUseitit(eu):
    r = expedientesBusca(eu)
    while True:
        id_eu = None
        for idx, eulistado in enumerate(r['data']['ExpedientesExpedienteUnicoList']):
            if eulistado['codigo'] == eu.replace('.',''):
                id_eu = eulistado['id']
                break
        if id_eu == None:
            print(f'portalRequests.etapasEUoffline: EU {eu} não encontrado')
            return False
        else: break
    dets = detalhesEUporId(id_eu)
    if not dets['data']['ExpedientesExpedienteUnicoById']['etapas']: dets['data']['ExpedientesExpedienteUnicoById']['etapas']=[]
    
    etapasOn = []
    etapasOff = []
    for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas']:
        if not x['procedimentoFormatadoSei']: continue
        etap = {
            'sei':x['procedimentoFormatadoSei'],
            'tit':x['ocorrencia']['descricao'],
            'tipo':x['ocorrencia']['tipo'],
            'subtipo':x['ocorrencia']['subtipo'],
            'situacao': '' if x['situacao'] == None else x['situacao']['value']
        }
        
        if x['marcacaoTramitadaOnline'] or x['isFromLicenciamento']: etapasOn += [etap]
        else: etapasOff += [etap]
        
    #etapasOff = [{'sei':x['procedimentoFormatadoSei'], 'tit':x['ocorrencia']['descricao'], 'situacao':x['situacao']['value']} for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas'] if not x['marcacaoTramitadaOnline'] and x['procedimentoFormatadoSei']]
    #etapasOn = [{'sei':x['procedimentoFormatadoSei'], 'tit':x['ocorrencia']['descricao'], 'situacao':x['situacao']['value']} for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas'] if x['marcacaoTramitadaOnline'] and x['procedimentoFormatadoSei']]
    isDigital = '700' in [x['ocorrencia']['codigo'] for x in dets['data']['ExpedientesExpedienteUnicoById']['etapas']]
    idProcSei = dets['data']['ExpedientesExpedienteUnicoById']['idProcedimentoSei']
    return {'etapasOff':etapasOff,'etapasOn':etapasOn,'isDigital':isDigital,'id_eu':id_eu,'idProcedimentoSei':idProcSei}


# In[ ]:


def isDigital(eu):
    r = expedientesBusca(eu)
    try:
        cods = [x['ocorrencia']['codigo'] for x in r['data']['ExpedientesExpedienteUnicoList'][0]['etapas']]
    except:
        return False
    return '700' in cods


# In[ ]:


def extraiDadosSEI(resultados):
    if not type(resultados) == list: resultados = [resultados]
    retorno = []
    for re in resultados:
        dados = {
                'titulo':re.get('dados',{}).get('tipoProcedimento',{}).get('nome',''),
                'sei':re.get('dados',{}).get('procedimentoFormatado',''),
                'dataEntrada':re.get('dados',{}).get('dataAutuacao',''),
                'abertoUnidades':[x['unidade']['sigla'] for x in re['dados']['unidadesProcedimentoAberto']],
                'relacionados':[x['procedimentoFormatado'] for x in re['dados']['procedimentosRelacionados']]
                }
        retorno.append(dados)
    return retorno


# In[ ]:


def consultaSEI(sei,url='https://expedientes-api.procempa.com.br/api/eventhandler'):
    payload = {"type":"sei/CONSULTA_PROCESSO_SEI","payload":{"codigo":sei}}
    x = requests.post(url, json = payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
#     procedimentos = [x['procedimentoFormatado'] for x in r['procedimentosRelacionados']]
#     sorted(procedimentos)
    #res = resp['data']['LicenciamentoFormDataList']
    return x.json()


# In[ ]:


def consultaEULocal(eu,url='https://expedientes-api.procempa.com.br/api/eventhandler'):
    payload = {"type":"consultasituacao/SERVER_CONSULTA_APISEI",
         "payload":{"numProcesso":eu, "next":{"type":"app/Expediente/LIMPA_STORE"}}}
    x = requests.post(url, json = payload)
    while not x.status_code == 200:
        servidor = x.url.split('/')[2]
        print(f'Problema no servidor {servidor}: código {x.status_code}. Tentando novamente...')
        x = requests.post(url, json=payload)
    resp = x.json()
    r = resp.get('ultAndUnidadeSigla','')
    return resp


# In[ ]:



def consultaProcessosSEI(procs):
    start = datetime.today()
    print(start,'\n')
    if not type(procs) == list: procs = [procs]
    rr=[]
    print('Total:',len(procs))
    c = 0
    skip = 100
    for p in procs:
        while True:
            r = consultaSEI(p)
            if 'error' in r['dados']:
                print('Erro do servidor ao consultar SEI:',p)
                print('Mensagem:',r['dados']['error'])
                print('Tentando novamente...\n')
            else:
                break
        rr += [r]
        c += 1
        if c % skip == 0: print(c)
    stop = datetime.today()
    print(f'\n{stop} ({stop-start})')
    return rr


# In[ ]:


def licListaProcessos(limit=100, url='https://licenciamento-api.procempa.com.br/graphql', tipo='revisao'):
    
    # setores variam conforme o login de cada usuário
    idsetores = ["6d8bbe34-b1f8-40c0-843b-1fbcec541850",
    "e7f82e3e-c236-4758-a71c-c42efa3f0706",
    "7944a370-1cdf-45c0-9eae-b2052b2beb6c",
    "33732631-c644-4b64-9de4-09d296b4ab36",
    "e52e3041-bf30-43fc-a510-7c69b4046c77",
    "fb204548-8a72-452a-906e-f8e641a19abf",
    "19966751-a6cf-4730-8197-1b8eb28d1273",
    "b3dc5648-9ea7-45ef-8b3a-a0015519fc06"]

    def montaPayload(skip,limit, idsetores, tipo = 'revisao'):
        idsetor = json.dumps(idsetores)
        if tipo == 'total':
            # payload para listar "TODOS" os processos
            p = {"operationName":"formsData","variables":{"skip":skip,"limit":limit,"term":"{\"$and\":[{\"$and\":[{\"procedimentoFormatadoSei\":{\"$exists\":true}},{\"procedimentoFormatadoSei\":{\"$ne\":null}}]},{},{}],\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1},\"dadosFormulario.idSetor\":{\"$in\":"+idsetor+"}}"},"query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
            
        else:
            # payload para listar processos "EM REVISÃO"
            p = {"operationName":"formsData","variables":{"skip":skip,"limit":limit,"term":"{\"$and\":[{\"$and\":[{\"procedimentoFormatadoSei\":{\"$exists\":true}},{\"procedimentoFormatadoSei\":{\"$ne\":null}}]},{\"resultado\":null},{\"$and\":[{\"documentos\":{\"$not\":{\"$elemMatch\":{\"invalido\":{\"$eq\":true},\"substituido\":{\"$ne\":true}}}}},{\"documentos\":{\"$not\":{\"$elemMatch\":{\"descricaoOutroDocumento\":{\"$ne\":null},\"documentoFormatadoSei\":null}}}}]},{\"$or\":[{\"$and\":[{\"$or\":[{\"dadosFormulario.idTipoFormulario\":\"licenca-expressa\"},{\"dadosFormulario.idTipoFormulario\":\"certidao\"}]},{\"data.dataCriacaoEtapa\":{\"$exists\":true},\"data.documentacaoMarcadaOk\":null}]},{\"$and\":[{\"dadosFormulario.idTipoFormulario\":{\"$ne\":\"licenca-expressa\"}},{\"dadosFormulario.idTipoFormulario\":{\"$ne\":\"certidao\"}}]}]}],\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1},\"dadosFormulario.idSetor\":{\"$in\":"+idsetor+"}}"},"query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
        return p
    
    skip=0
    total = 0
    resultados = []
    primeiroLote = True
    while True:
#         if total > 0 and skip+limit > total:
#             limit = total - skip 
        p = montaPayload(skip,limit,idsetores,tipo)
        x = requests.post(url, json = p)
        resp = x.json()
        res = resp['data']['LicenciamentoFormDataList']
        try:
            resultados += res
        except:
            print('ERRO ao receber resposta do Portal')
            print('skip:',skip,'   limit:',limit)
            print('baixados:',len(resultados))
            print('última resp:',resp)
            break
        total = resp['data']['count']
        if primeiroLote:
            resp1 = resp
            print('Total:',total)
            primeiroLote = False
        if len(resultados) == total: break
        skip += limit
        print(len(resultados),'baixados')
        
    #return (resultados, resp1)
    return resultados


# In[ ]:


def getEtapaPorCod(cod):
    cod = str(cod)
    r = expedientesListaEtapas()
    listaEtapas = r['data']['ExpedientesOcorrenciaList']

    for l in listaEtapas:
        if l['codigo'] == cod: return l
    return None

def pegaCodigoEtapa(r):
    tit = r['titulo']
    habitese = r.get('habitese')
    cod = None
    if habitese:
        cod = {
            'Total':'1242',
            'Parcial':'1240',
            'Parcial Final':'1241',
            'Final Parcial':'1241'
        }.get(habitese)
    else: cod = {'Estudo de Viabilidade Urbanística (EVU) p/ projetos especiais de impacto urbano de 1º grau': 1229,
                'Aquisição de Solo Criado (“Aquisição de Índice” 4802) - Pessoa Jurídica': 1311,
                'Aquisição de Solo Criado (“Aquisição de Índice” 4802) - Pessoa Física': 1311,
                'Aprovação de projeto de reservatório de amortecimento em edificações': 2036,
                'Transferência de Potencial Construtivo (TPC 4801) - Pessoa Jurídica': 1312,
                'Aprovação de projeto de extensão de rede pluvial e/ou envelopamento de coletor de fundos': 2038,
                'Transferência de Potencial Construtivo (TPC 4801) - Pessoa Física': 1312,
                'Estudo de Viabilidade Urbanística (EVU) em Imóvel Inventariado de Estruturação': 1229,
                'Autorização para edificação em faixa não edificável de drenagem': 2041,
                'Vistoria de Reservatório de Amortecimento em edificações': 2039,
                'Certidão de Conclusão de Obra': 1296,
                'Definição de regime urbanístico para lotes matriculados que se encontrem em AEIS': 1340,
                'Informação de alinhamento predial': 1343,
                'Estudo de Viabilidade Urbanística (EVU) em Imóvel Inventariado de Compatibilização': 1229,
                'Aprovação de Projeto Arquitetônico - Licenciamento Expresso': 2043,
                'Ajustes de Projeto Arquitetônico Aprovado - Licenciamento Expresso': 2053,
                'Estudo de Viabilidade Urbanística (EVU) em Imóvel Tombado': 1229}.get(tit)
    if not cod: print('pegaCodigoEtapa: Código da etapa não encontrado.',tit,habitese)
    return cod


# In[ ]:


def baixaListaPortal(tipo='revisao'):
    start = datetime.today()
    print(start,'\n')
    print('Baixando lista:',tipo)
    rr = licListaProcessos(tipo=tipo)
    # r = rr[1]
    # results = rr[0]
    #r['data']['count'], len(r['data']['LicenciamentoFormDataList'])
    stop = datetime.today()
    print(f'\n{stop} ({stop-start})')
    return rr


# In[ ]:


def extraiTipoForm(results):
    tipos = {}
    for r in results:
        tipoForm = r['dadosFormulario']['idTipoFormulario']
        if not tipoForm in tipos:
            tipos[tipoForm] = 0
        tipos[tipoForm] += 1
    return tipos


# In[ ]:


def camposFaltando(listagem):
    # 4 campos podem estar em branco
    # se outro campo além destes estiver em branco, mostrar aqui:
    for item in listagem:
        if any([item[x]=='' and not x in ['EUinformado','revisor','rt_regtipo'] for x in item]):
            if 'habite-se' in item['titulo'].lower() and not item['endereco']: continue
            return item
    return ''


# In[ ]:


def getFormData(procid, url = 'https://licenciamento-api.procempa.com.br/graphql'):
    payload = {
	"operationName": "formData",
	"query": "query formData($id: String!) {\n  LicenciamentoFormDataById(id: $id) {\n    id\n    idFormulario\n    dadosFormulario\n    data\n    documentos\n    idProcedimentoSei\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComparecimento\n    resultado\n    usuario\n    revisor\n    dataHomologacaoOuIndeferimentoExpedientes\n    bpmUser\n    bpmProcessDefinition\n    bpmProcessInstance\n    expirado\n    __typename\n  }\n}\n",
	"variables": { "id": procid }
    }
    x = requests.post(url, json = payload)
    return x.json()


# In[ ]:


def getFormularioBPM(procid, url='https://licenciamento-api.procempa.com.br/graphql'):
    payload = {
	"operationName": "formulario",
	"query": "query formulario($id: String!) {\n  LicenciamentoFormularioById(id: $id) {\n    id\n    nome\n    schema\n    uiSchema\n    documentos\n    validade\n    idTipoFormulario\n    processName\n    processVersion\n    idOrgao\n    __typename\n  }\n}\n",
	"variables": { "id": procid }
    }
    x = requests.post(url, json = payload)
    return x.json()


# In[ ]:


def getFormularioBPM2(procid,url='https://licenciamento-api.procempa.com.br/graphql'):
    payload = {
	"operationName": "formulario",
	"query": "query formulario($id: String!) {\n  LicenciamentoFormularioById(id: $id) {\n    id\n    nome\n    schema\n    uiSchema\n    documentos\n    validade\n    idTipoFormulario\n    processName\n    processVersion\n    idOrgao\n    codOcorrenciaLicenca\n    __typename\n  }\n}\n",
	"variables": { "id": procid }
    }
    x = requests.post(url, json = payload)
    return x.json()


# In[ ]:


def apiSEIdocs(processo, url = 'https://licenciamento-api.procempa.com.br/api/sei-docs?numeroProcesso='):
    url = url + processo
    x = requests.get(url)
    return x.json()


# In[ ]:


def pegaUsuariosBPM(procura):
    r = {}
    for u in usuariosBPM:
        fn = u['fullname']
        lg = u['username']
        if not procura in fn.lower() and not procura in lg.lower(): continue
        r['username'] = u['username']
        r['fullname'] = u['fullname']
        r['firstName'] = u['firstName']
        r['lastName'] = u['lastName']
        r['email'] = u['email']
        break
    return r


# In[ ]:


def trocaRevisor(processo, revisor=None, url = 'https://licenciamento-api.procempa.com.br/api/eventhandler'):
    
    r = buscaPortalRaw(processo)
    bpmid = r['data']['LicenciamentoFormDataList'][0]['id']
    
    formData = getFormData(bpmid)['data']['LicenciamentoFormDataById']
    _ = formData.pop('documentos', formData)
    formid = formData['idFormulario']
    
    pl = getFormularioBPM(formid)
    pl = pl['data']['LicenciamentoFormularioById']
    _ = pl.pop('__typename', pl)
        
    pl['documentos'] = r['data']['LicenciamentoFormDataList'][0]['documentos']
    pl['documentosSei'] = apiSEIdocs(processo)['documentos']
    pl['formData'] = formData
    
    payload = { 'payload':{
        "formulario": pl,
		"next": {
			"type": "app/Avaliacao/LIMPA_STORE"
		},
		"revisor": revisor,
		"usernameLogado": ""
	},
	"type": "formulario/SERVER_ATUALIZAR_REVISOR"
    }
    
    x = requests.post(url, json = payload)
    return x.json()


# In[ ]:


def complementarPlantas(processo, url = 'https://licenciamento-api.procempa.com.br/api/eventhandler'):
    
    # complemento = dicionario contendo "titulo", "descricao" e "extensao" do arquivo
    
    r = buscaPortalRaw(processo)
    bpmid = r['data']['LicenciamentoFormDataList'][0]['id']
    
    formData = getFormData(bpmid)['data']['LicenciamentoFormDataById']
    _ = formData.pop('documentos', formData)
    formid = formData['idFormulario']
    
    pl = getFormularioBPM(formid)
    pl = pl['data']['LicenciamentoFormularioById']
    _ = pl.pop('__typename', pl)
        
    docs = r['data']['LicenciamentoFormDataList'][0]['documentos']
    tdocs = [x.get('tituloDocumento','') for x in docs]
    if any(x in ['PLANTAS DO PROJETO APROVADO', 'Projeto ou Licença de aprovação com carimbo/assinatura da Prefeitura, objeto da solicitação deste habite-se'] for x in tdocs):
        return { 'erro': 'já está em comparecimento para plantas' }
    
    ordens = [x.get('ordem','') for x in docs]
    ordens = [int(x) for x in ordens if x!='']
    ids = [x.get('id','') for x in docs]
    ids = [x for x in ids if not x == '']
    ultimaordem = max(ordens)
    idaleatorio1 = geraIDaleatorioBPM(bpmid + ids[-1])
    idaleatorio2 = geraIDaleatorioBPM(bpmid + idaleatorio1)
    idaleatorio3 = geraIDaleatorioBPM(bpmid + idaleatorio2)
    ultimosdocs = [{
	"extensao": "pdf",
	"id": idaleatorio1,
	"idDocumento": "PROJ-UVP",
	"idOrgao": "22c96123-09da-4465-9c74-1252c75d874c",
	"linkHelp": None,
	"obrigatorio": False,
	"ordem": ultimaordem+100,
	"textoHelp": "Deverá ser anexado plantas digitalizadas do projeto aprovado pelo Município, mesmo nos casos de projetos oriundos do Licenciamento Expresso, as quais serão utilizadas para fins de expedição da carta de habitação a partir da validação dos dados com os registros nos cadastros técnicos da PMPA, a ser feita pela equipe da UVP. Em já havendo processo digitalizado, contendo plantas aprovadas, ou ainda o RT decida por aguardar a digitalização do processo, fica dispensada a apresentação das plantas pelo requerente.",
	"tituloDocumento": "Projeto ou Licença de aprovação com carimbo/assinatura da Prefeitura, objeto da solicitação deste habite-se",
	"versao": 1
},
{
	"descricaoOutroDocumento": "Anexar as plantas digitalizadas do projeto aprovado, sobre o qual deverá ser expedida a carta de habitação.\n",
	"extensao": "pdf",
	"id": idaleatorio2,
	"idDocumento": idaleatorio3,
	"linkHelp": None,
	"obrigatorio": True,
	"ordem": ultimaordem+200,
	"textoHelp": None,
	"tituloDocumento": "PLANTAS DO PROJETO APROVADO",
	"versao": 1
}]
    docs += ultimosdocs

    
    pl['documentos'] = docs
    pl['documentosSei'] = apiSEIdocs(processo)['documentos']
    pl['formData'] = formData
    
    hoje = datetime.today()
    millisecond = datetime(hoje.year,hoje.month,hoje.day) + timedelta(days=91, hours=23, minutes=59, seconds=59)
    millisecond = int(time.mktime(millisecond.timetuple()) * 1000)
    pl['formData']['dataComparecimento'] = millisecond
    
    payload = { 'payload':{
        "formulario": pl,
		"next": {
			"type": "app/Avaliacao/LIMPA_STORE"
		},
		"usernameLogado": ""
	},
	"type": "formulario/SERVER_SUBMETER_PARECER"
    }
    
    #return payload
    
    x = requests.post(url, json = payload)
    return x.json()
    
    


# In[ ]:


def geraIDaleatorioBPM(string):
    m = hashlib.md5(string.encode()).hexdigest()
    return m[:8] + '-' + m[8:12] + '-' + m[12:16] + '-' + m[16:20] + '-' + m[20:]


# In[ ]:


def listaTarefas(tarefa='VS0400', url='https://licenciamento-api.procempa.com.br/api/tasks-by-name/'):
    url = url + f'{tarefa}?sei=true'
    x = requests.get(url)
    return x.json()


# In[ ]:


def verificaBPMSEI(sei, tarefa):
    tarefas = listaTarefas(tarefa)
    filtro = [x for x in tarefas if x['formData']['procedimentoFormatadoSei']==sei]
    if filtro: return True
    return False

def verificaTarefasSEI(sei, todasTarefas=['AP0900','VS0400', 'LE0900']):
    tarefas=[]
    for t in todasTarefas:
        tarefas += verificaBPMSEI(sei, t)
    filtro = [x for x in tarefas if x['formData']['procedimentoFormatadoSei']==sei]
    if filtro: return True
    return False

def verificaVS0400SEI(sei):
    return verificaBPMSEI(sei, 'VS0400')

def verificaAP0900SEI(sei):
    return verificaBPMSEI(sei, 'AP0900')


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


class PortalRequests:
    
    def __init__(self, usuario=None, senha=None, fazlogin=True):
        self.url = {}
        self.url['portal'] = 'https://licenciamento-admin.procempa.com.br/'
        self.url['sso_auth'] = 'https://sso-pmpa.procempa.com.br/auth/realms/pmpa/protocol/openid-connect/auth'
        self.url['sso_token'] = 'https://sso-pmpa.procempa.com.br/auth/realms/pmpa/protocol/openid-connect/token'
        self.headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
                           }
        if fazlogin:
            if not usuario: usuario = getuser()
            if not senha: senha = getpass('senha: ')
            self.username = usuario
            self.password = senha
            self.tokens = {}
            self.pegaToken()
    
    def pegaToken(self, intervalo=1200, timeout=3):
        self.session = requests.Session()
        params = {
            'client_id': 'licenciamento-admin',
            'redirect_uri': self.url['portal'],
            'state': str(uuid4()),
            'response_mode': 'fragment',
            'response_type': 'code',
            'scope': 'openid',
            'nonce': str(uuid4()),
        }
        r = self.session.get(self.url['sso_auth'], params=params, headers=self.headers, timeout=timeout)
        rl = r.text
        action_tag = 'action="'
        i1 = rl.index(action_tag)
        i2 = rl.index('"', i1+len(action_tag))
        post_url = rl[i1+len(action_tag):i2]
        post_url = post_url.replace('&amp;','&')
        data1 = {
                    'username': self.username,
                    'password': self.password,
                    'login': 'Entrar',
                }
        token_url = self.session.post(post_url, data=data1, timeout=timeout)
        url_check = urlparse(token_url.url)
        if not url_check.netloc.startswith(params['client_id']): return {'erro': 'falha no login'}
        redirect_uri, dados = token_url.url.split('#')
        data2 = {
            'code': [x for x in dados.split('&') if x.startswith('code=')][0][5:],
            'grant_type': 'authorization_code',
            'client_id': 'licenciamento-admin',
            'redirect_uri': redirect_uri,
        }
        r = self.session.post(self.url['sso_token'], data=data2, timeout=timeout)
        self.tokens = r.json()
        self.tokens['recebido'] = datetime.now()
        self.headers['Authorization'] = 'Bearer ' + self.tokens['access_token']
        return {'ok': 'token recebido'}
        
    def post(self, url, json):
        while True:
            r = self.session.post(url, json = json, headers=self.headers)
            if r==None: continue
            elif r.text == 'Could not store grant code error': self.pegaToken()
            else: break
        return r
    
    def get(self, url):
        #if not 'Authorization' in self.headers: self.pegaToken()
        if not 'session' in dir(self):
            self.session = requests.Session()
            self.session.headers=self.headers
        while True:
            r = self.session.get(url, headers=self.headers)
            if r==None: continue
            elif r.text == 'invalid token': self.pegaToken()
            else: break
        return r
    
    def baixaListaBPMapi(self, task='ap0800'):
        url = f'https://licenciamento-api.procempa.com.br/api/tasks-by-name/{task}?sei=true'
        r = self.get(url)
        return r.json()
    
    def buscaPortalRaw(self, busca, url = 'https://licenciamento-api.procempa.com.br/graphql'):
        graphqlQuery = {"operationName":"formsData",
        "variables":{"skip":0,
        "limit":20,
        "term":"{\"procedimentoFormatadoSei\":{\"$regex\":\".*"+ busca +".*\"},\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1}}"},
        "query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
        x = self.post(url, json = graphqlQuery)
        return x.json()
        
    def buscaPortalRaw2(self, busca,url='https://licenciamento-api.procempa.com.br/graphql'):
        # em relação a buscaPortalRaw, a Raw2 tem 2 campos adicionais dentro de ['data']['LicenciamentoFormDataList']
        # ['dataAsString', 'dataUltimaAtualizacaoPortal']
        graphqlQuery = {"operationName":"formsData","variables":{"skip":0,"limit":20,"term":"{\"$and\":[{\"procedimentoFormatadoSei\":{\"$exists\":true}},{\"procedimentoFormatadoSei\":{\"$ne\":null}}],\"dadosFormulario.idSetor\":{\"$in\":[\"b83919a5-c7b4-495e-8647-3dc3e20d86ba\",\"fb204548-8a72-452a-906e-f8e641a19abf\",\"7f738961-7f4a-454f-bb2c-05c5eb05c1e3\",\"33732631-c644-4b64-9de4-09d296b4ab36\"]},\"$or\":[{\"procedimentoFormatadoSei\":{\"$regex\":\".*"+busca+".*\"}},{\"dataAsString\":{\"$regex\":\".*"+busca+".*\"}}],\"orderBy\":{\"dataUltimaAtualizacaoPortal\":1}}"},"query":"query formsData($term: String, $skip: Int, $limit: Int) {\n  LicenciamentoFormDataList(term: $term, skip: $skip, limit: $limit) {\n    id\n    idFormulario\n    formulario {\n      id\n      nome\n      __typename\n    }\n    data\n    dataAsString\n    documentos\n    extraInfo\n    usuario\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComplementacao\n    dataComparecimento\n    dataUltimaAtualizacaoPortal\n    resultado\n    createdAt\n    revisor\n    dadosFormulario\n    expirado\n    __typename\n  }\n  count: LicenciamentoFormDataCount(term: $term)\n}\n"}
        x = self.post(url, json = graphqlQuery)
        return x.json()
    
    def buscaPortalBPMRaw(self, procid,url='https://licenciamento-api.procempa.com.br/graphql'):
        graphqlQuery = {"operationName":"formData",
                        "variables":{"id":procid},
                        "query":"query formData($id: String!) {\n  LicenciamentoFormDataById(id: $id) {\n    id\n    idFormulario\n    formulario {\n      id\n      schema\n      uiSchema\n      documentos\n      __typename\n    }\n    dadosFormulario\n    data\n    documentos\n    documentosDados\n    extraInfo\n    idProcedimentoSei\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComparecimento\n    resultado\n    usuario\n    revisor\n    bpmUser\n    bpmProcessDefinition\n    bpmProcessInstance\n    bpmTasks {\n      id\n      taskName\n      contrato\n      checklist {\n        id\n        itens {\n          id\n          descricao\n          obrigatorio\n          ordem\n          done\n          username\n          data\n          __typename\n        }\n        __typename\n      }\n      username\n      data\n      taskData\n      __typename\n    }\n    marcadoresPublicos {\n      id\n      __typename\n    }\n    __typename\n  }\n}\n"}
        x = self.post(url, json = graphqlQuery)
        return x.json()
    
    def buscaPortalBPMRaw2(self, procid,url='https://licenciamento-api.procempa.com.br/graphql'):
        graphqlQuery = {"operationName":"formData",
                        "variables":{"id":procid},
                        "query":"query formData($id: String!) {\n  LicenciamentoFormDataById(id: $id) {\n    id\n    idFormulario\n    dadosFormulario\n    data\n    documentos\n    idProcedimentoSei\n    procedimentoFormatadoSei\n    urlConsultaPublicaSei\n    dataCriacaoSei\n    dataComparecimento\n    resultado\n    usuario\n    revisor\n    dataHomologacaoOuIndeferimentoExpedientes\n    bpmUser\n    bpmProcessDefinition\n    bpmProcessInstance\n    expirado\n    __typename\n  }\n}\n"}
        x = self.post(url, json = graphqlQuery)
        return x.json()
    
    
    def getFormularioBPM2(self, procid,url='https://licenciamento-api.procempa.com.br/graphql'):
        payload = {
        "operationName": "formulario",
        "query": "query formulario($id: String!) {\n  LicenciamentoFormularioById(id: $id) {\n    id\n    nome\n    schema\n    uiSchema\n    documentos\n    validade\n    idTipoFormulario\n    processName\n    processVersion\n    idOrgao\n    codOcorrenciaLicenca\n    __typename\n  }\n}\n",
        "variables": { "id": procid }
        }
        x = self.post(url, json = payload)
        return x.json()
    
    def apiSEIgetDocs(self, proc, url='https://licenciamento-api.procempa.com.br/api/sei-docs?numeroProcesso='):
        falhou = 0
        while True: # necessário para vencer instabilidades do Portal
            self.pegaToken()
            r = self.get(url+proc)
            if r.status_code==200: break
            falhou +=1
            if falhou==1:
                print('problemas no Portal [sei-docs] tentando novamente...',end='',flush=True)
            elif falhou>1:
                print('.',end='',flush=True)
        if falhou: print('ok! ',end='',flush=True)
        return r.json()
    
    def apiSEIconsulta(self, proc, url='https://licenciamento-api.procempa.com.br/api/consultarProcessoSei?numeroProcesso='):
        falhou = 0
        while True: # necessário para vencer instabilidades do Portal
            self.pegaToken()
            r = self.get(url+proc)
            if r.status_code==200: break
            falhou +=1
            if falhou==1:
                print('problemas no Portal [consultarProcessoSei] tentando novamente...',end='',flush=True)
            elif falhou>1:
                print('.',end='',flush=True)
        if falhou: print('ok! ',end='',flush=True)
        return r.json()
    
    def baixaVistas(self, proc, decisao='deferido'):
        r = self.buscaPortalRaw(proc)
        if not r: return {'erro':'buscaPortalRaw'}
        if not r['data']['LicenciamentoFormDataList']: return {'erro':'sem resultados no Portal'}
        idform = r['data']['LicenciamentoFormDataList'][0]['idFormulario']
        idproc = r['data']['LicenciamentoFormDataList'][0]['id']
        documentos = r['data']['LicenciamentoFormDataList'][0]['documentos']
        formulario = self.getFormularioBPM2(idform)
        formdata = self.buscaPortalBPMRaw2(idproc)
        documentosSEI = self.apiSEIgetDocs(proc)
        payload = {
            'payload':{
                'formulario':formulario['data']['LicenciamentoFormularioById'],
                'next':{'type':"app/Avaliacao/LIMPA_STORE"},
                'resultado':decisao,
                'usernameLogado':'EGD'
            },
            'type':'formulario/SERVER_SUBMETER_RESULTADO'
        }
        payload['payload']['formulario']['documentos']=documentos
        payload['payload']['formulario']['documentosSei']=documentosSEI['documentos']
        del formdata['data']['LicenciamentoFormDataById']['documentos']
        payload['payload']['formulario']['formData']=formdata['data']['LicenciamentoFormDataById']
        falhou=0
        while True: # necessário para vencer instabilidades do Portal
            x = self.post('https://licenciamento-api.procempa.com.br/api/eventhandler', payload)
            if x.status_code==200: break
            falhou+=1
            if falhou==1:
                print('problemas no Portal [eventhandler] tentando novamente...',end='',flush=True)
            elif falhou>1:
                print('.',end='',flush=True)
        if falhou: print('ok! ',end='',flush=True)
        return x.json()


# In[ ]:





# In[ ]:


# TESTES


# In[ ]:


# portal = PortalRequests()


# In[ ]:





# In[ ]:


# portal.pegaToken()
# r = portal.get('https://licenciamento-api.procempa.com.br/api/consultarProcessoSei?numeroProcesso=22.0.000080577-0')
# r


# In[ ]:


# [(x['procedimentoFormatado'],x['tipoProcedimento']['nome']) for x in r.json()['procedimentosRelacionados']]


# In[ ]:


# r = portal.apiSEIconsulta('22.0.000080577-0')
# r


# In[ ]:


# r.json()


# In[ ]:




