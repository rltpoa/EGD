#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import sys
from datetime import datetime
from time import sleep
from getpass import getpass, getuser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import (NoSuchElementException, 
                                        WebDriverException, 
                                        StaleElementReferenceException, 
                                        UnexpectedAlertPresentException,
                                        NoAlertPresentException,
                                        InvalidArgumentException)


# # versão 30/06/2022

# In[ ]:


EGD_DEL = 'EGD-SMAMUS'
ERTP_DEL = 'ERTP-SMAMUS'
SD_DEL = 'SD-SMAMUS'


# In[ ]:


class operadorSEI:
    
    def __init__(self, headless=True, mudo=True, usuario=None, senha=None):
        self.driver = None
        self.url_sei = 'https://sei.procempa.com.br/'
        if not usuario: usuario = input('usuário: ')
        if not senha: senha = getpass('senha: ')
        self.username = usuario
        self.password = senha
        self.processo = ''
        self.arquivos = []
        self.locais = {}
        self.andamentos = None
        self.correntedeunidades = []
        self.relacionados = {}
        self.headless = headless
        self.mudo = mudo
        self.alerta = None
        self.bycss = By.CSS_SELECTOR
        self.download = os.environ['HOMEPATH']
        self.logaSei()
        
    def logaSei(self):
        if not self.driverLigado(): self.ligaChrome()
        self.driver.get(self.url_sei)
        while self.driver.title == 'SEI / PMPA':
            try:
                self.loginSEI()
            except UnexpectedAlertPresentException as e:
                print('')
                print(e.alert_text)
                self.username = input('usuário: ')
                self.password = getpass('senha: ')
                if self.username == '':
                    self.driver.quit()
                    return
    def quit(self):
        return self.driver.quit()

    def driverLigado(self):
        try:
            _ = self.driver.title
            return True
        except:
            return False
    
    def ligaChrome(self):
        mudo = self.mudo
        if not mudo: print('Ligando driver',end='... ')
        opt = webdriver.ChromeOptions()
        #opt.add_argument('--no-sandbox')
        if self.headless: opt.add_argument('--headless')
        #opt.add_argument('--window-size=1050,748')
        #opt.add_argument('--disable-gpu')
        #opt.add_argument('--lang=en_US,pt_BR')
        #opt.add_argument('--remote-debugging-port=9222')
        # profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
        #        "download.default_directory": self.download , "download.extensions_to_open": "applications/pdf"
        #           }
        #opt.add_experimental_option("prefs", profile)

        # opt.add_experimental_option("prefs",{"plugins.always_open_pdf_externally": True, # força download de PDF
        #                                     "download.default_directory": self.download, # configura a pasta de downloads para a raiz do usuário
        #                                      "download.extensions_to_open": "application/x-google-chrome-pdf",
        #                                      "prompt_for_download": False,
        #                                      "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}]
        #                                     }) 
        
        if mudo: opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=opt)
        if not mudo: print('ok.')

    def loginSEI(self):
        username = self.username
        password = self.password
        user = self.css('input[name="txtUsuario"]')
        if not user: return('input not found: username')
        user[0].clear()
        user[0].send_keys(username)
        pwd = self.css('input[name="pwdSenha"]')
        if not pwd: return('input not found: password')
        pwd[0].clear()
        pwd[0].send_keys(password)
        remember = self.css('input[type="checkbox"][name="chkLembrar"]')
        if not remember: return('checkbox not found: remember')
        if not remember[0].is_selected(): remember[0].click()
        orgao = Select(self.css1('select[name="selOrgao"]'))
        orgao.select_by_visible_text('PMPA')
        btn = self.css('button[name="sbmLogin"]')
        if not btn: return('button not found')
        btn[0].click()
                    
    def temAlerta(self,acao='aceitar'):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
        except NoAlertPresentException:
            return False
        if acao=='aceitar': alert.accept()
        if acao=='cancelar': alert.dismiss()
        self.alerta=alert_text
        return True

    def css(self,_css):
        return self.driver.find_elements(By.CSS_SELECTOR, _css)
    
    def css1(self,_css):
        return self.driver.find_element(By.CSS_SELECTOR, _css)

    def el(self,elemento,prop=None,txt=None,silencio=True):
        # prop = propriedade a ser retornada
        # txt = texto relacionado a propriedade
        if prop and txt:
            els = self.css(elemento)
            for el in els:
                if txt in str(el.get_attribute(prop)):
                    return el
        else:
            els = []
            els = self.css(elemento)
            if els: return els[0]

        if not silencio:
            print(f'Elemento não encontrado: {elemento} {prop} {txt}')

        return None

    def aguardaEl(self,elemento,prop=None,txt=None):
        e = None
        while not e:
            e = self.el(elemento,prop,txt,silencio=True)
        return e


    # troca iframe
    def iframe(self, ifr=None, reseta=True):
        if reseta: self.driver.switch_to.default_content()
        if ifr is None: return True
        arvore = []
        while not arvore:
            arvore = self.css(ifr)
        #if not arvore: return None
        self.driver.switch_to.frame(arvore[0])
        return 1

    def isource(self, iframe=None):
        if iframe: self.driver.switch_to.frame(iframe)
        return self.driver.source_page
        
    def unidadesDisponiveis(self):
        ifr = self.iframe()
        aguarda = self.aguardaEl('select[name="selInfraUnidades"]')
        unidadeAtual = Select(self.css1('select[name="selInfraUnidades"]'))
        opcoes = [x.text for x in unidadeAtual.options]
        return opcoes    

    def mudaUnidade(self,unidade=None):
        ifr = self.iframe()
        aguarda = self.aguardaEl('select[name="selInfraUnidades"]')
        unidadeAtual = Select(self.css1('select[name="selInfraUnidades"]'))
        if unidade == None: return unidadeAtual.first_selected_option.text
        unidade = str(unidade).upper()
        opcoes = [x.text for x in unidadeAtual.options if x.text.startswith(unidade)]
        if not opcoes:
            print(f'Usuário SEI sem acesso à unidade: {unidade}')
            return False
        ua = unidadeAtual.first_selected_option.text
        if not ua == unidade:
            unidadeAtual.select_by_visible_text(opcoes[0])
        while not ua == opcoes[0]:
            unidadeAtual = Select(self.css1('select[name="selInfraUnidades"]'))
            ua = unidadeAtual.first_selected_option.text
        return True


    def clicaControledeProcessos(self,):
        btn = []
        while not btn:
            btn = self.css('a[id="lnkControleProcessos"]')
        btn = btn[0]
        btn.click()
        #sleep(3)


    def selecionaVisualizacao(self,visualizar = 'Visualização detalhada'):
        vis = []
        while not vis:
            vis = self.css('a[id="ancTipoVisualizacao"]')
        vis = vis[0]
        if vis.text==visualizar: # visualização atual não é a desejada
            vis.click()
            vis = []
            while not vis:
                vis = self.css('a[id="ancTipoVisualizacao"]')

        # clica no ícone "primeira página" até o seletor mostrar página 1
        pagAtual = []
        cssSeletoresDePagina = 'select[id="selInfraPaginacaoSuperior"], select[id="selGeradosPaginacaoSuperior"]'
        while not pagAtual:
            pagAtual = self.css(cssSeletoresDePagina)
            if not pagAtual:
                #print('sem pagina atual')
                sleep(1)
                continue
            pagAtual = Select(pagAtual[0])
            if pagAtual.first_selected_option.text == '1': break
            primPagina = self.css('a[id="lnkInfraPrimeiraPaginaSuperior"]')
            if primPagina: primPagina[0].click()
            
    def pegaListaResumida(self, unidade=False, coluna = 'recebidos'):
        # retorna dict de processos da lista de ["recebidos" ou "gerados"] de uma unidade (visualização resumida)
        # cada chave tem uma outra chave "sinais" (lista de TDs para cada ícone que aparece ao lado do processo) e "atrib" (processo atribuido a alguem)
        unatual = self.mudaUnidade()
        if unidade:
            if not str(unatual).lower().startswith(unidade): self.mudaUnidade(unidade)
        else:
            unidade = unatual
        print(f'Abrindo lista da unidade {unidade}...',end=' ')
        ctrl = self.aguardaEl('a[id="lnkControleProcessos"]')
        ctrl.click()
        print('ok')

        print('Acessando a primeira página...',end=' ')
        if coluna == 'recebidos':
            divcol = ('div[id="divRecebidos"]')
        else:
            coluna = 'gerados'
            divcol = ('div[id="divGerados"]')
        lista = self.css1(divcol)
        temPagAnterior = lista.find_elements(By.CSS_SELECTOR, 'a[id="lnkRecebidosPaginaAnteriorSuperior"]')
        selPag = lista.find_elements(By.CSS_SELECTOR, 'select[id="selRecebidosPaginacaoSuperior"]')
        if temPagAnterior:
            if selPag:
                seletor = Select(selPag[0])
                seletor.select_by_visible_text('1')
            lista = self.css1(divcol)
            temPagAnterior = lista.find_elements(By.CSS_SELECTOR, 'a[id="lnkRecebidosPaginaAnteriorSuperior"]')
            while temPagAnterior:
                if temPagAnterior: temPagAnterior[0].click()
                lista = self.css1(divcol)
                temPagAnterior = lista.find_elements(By.CSS_SELECTOR, 'a[id="lnkRecebidosPaginaAnteriorSuperior"]')
        print('ok')

        total = lista.find_elements(By.CSS_SELECTOR, 'div table caption')
        if not total:
            print(f'Não há processos {coluna}.')
            return {}
        total = total[0].text.split(' ')[0]
        print(f'Extraindo lista de "{coluna}"... Total de', end=' ')
        print(f'{total} processos:')
        
        def pegaLista(lista):
            linhas = lista.find_elements(By.CSS_SELECTOR, 'tr')
            linhas = linhas[1:]
            tds = [x.find_elements(By.CSS_SELECTOR,'td') for x in linhas]
            processos = {}
            for td in tds:
                proc = td[2].find_element(By.CSS_SELECTOR,'a').text
                tipo = td[2].find_element(By.CSS_SELECTOR,'a').get_attribute('onmouseover').split("'")[-2]
                atrib = td[3].text.strip('()').strip(' ')
                sinais_a = td[1].find_elements(By.CSS_SELECTOR,'a')
                sinais = [x.get_attribute('onmouseover') for x in sinais_a]
                sinais = [x.split("'")[-2] for x in sinais]
                processos[proc] = {'tipo':tipo,'sinais':sinais,'atrib':atrib}
            return processos

        processos = {}
        while True:
            lista = self.css1(divcol)
            cap = lista.find_element(By.CSS_SELECTOR, 'div table caption').text
            if ' - ' in cap: cap = cap.split(' - ')[1].rstrip(':')
            else: cap = cap.split(' ')[0]
            print(f'{cap}...', end=' ', flush=True)
            processos.update(pegaLista(lista))
            print('ok')
            proxPag = lista.find_elements(By.CSS_SELECTOR,'a[id="lnkRecebidosProximaPaginaSuperior"]')
            if not proxPag: break
            proxPag[0].click()
        print('fim')

        return processos
        

    def pegaListaDetalhados(self, unidade = False):
        if unidade:
            unatual = self.mudaUnidade()
            if not str(unatual).lower().startswith(unidade): self.mudaUnidade(unidade)
        self.clicaControledeProcessos()
        self.selecionaVisualizacao()
        sleep(1)
        ultPag = self.css('a[id="lnkInfraUltimaPaginaSuperior"]')
        psel = Select(self.css1('select[id="selInfraPaginacaoSuperior"]'))
        totPag = max([int(x.text) for x in psel.options])
        procDetalhados = {}
        onmouseover = 'a[onmouseover="return infraTooltipMostrar(\'Requerimento Digital\');"]'
        c = 0
        #while not len(ultPag)==0:
        while True:
            c+=1
            print(f'Página {c} de {totPag}')
        #while True:
            #detalhados = self.css('div[id="divTabelaDetalhado"] tbody a[class^="processo"]')
            detalhados = self.css('div[id="divTabelaDetalhado"] table tbody tr')
            for tr in detalhados:
                tds = tr.find_elements(By.CSS_SELECTOR, 'td')
                if not tds: continue
                iconePortal = True if tds[1].find_elements(By.CSS_SELECTOR, onmouseover) else False
                #if not iconePortal: continue
                procNum = tds[2].text
                procTipo = tds[4].text
                procDetalhados[procNum] = {'tipo':procTipo, 'portal':iconePortal}
            procPag = self.css('a[id="lnkInfraProximaPaginaSuperior"]')
            if procPag:
                procPag[0].click()
                sleep(1)
            else: break
            cssSeletoresDePagina = 'select[id="selInfraPaginacaoSuperior"], select[id="selGeradosPaginacaoSuperior"]'
            paginaAtual = self.css(cssSeletoresDePagina)
            while not paginaAtual:
                pass
        return procDetalhados
    
    def filtraProcessos(self, unidade=False):
        if unidade:
            unatual = self.mudaUnidade()
            if not str(unatual).lower().startswith(unidade): self.mudaUnidade(unidade)
        sleep(1)
        btn = self.css('img[title="Controle de Processos"]')
        btn[0].click()
        sleep(1)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        info = self.aguardaEl('div[id="divArvoreAcoes"]')
        btns = info.find_elements(By.CSS_SELECTOR, 'a')
        btn = [x for x in btns if x.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')=='Filtro de Processos']
        btn[0].click()
        sleep(1)
        tipoFiltro = self.css1('select[id="selTipoFiltro"]')
        ordenacao = self.css1('select[id="selTipoFiltroOrd"]')
        direcao = self.css1('select[id="selTipoFiltroOrdDirecaoDataEntrada"]')
        lupa = self.css1('imag[id="imgLupaTipoProcedimento"]')
        lupa.click()
        sleep(1)
        janelaAtual = self.driver.getWindowHandle()
        novaJanela = self.driver.WindowHandles.Last()
        driver.SwitchTo().Window(novaJanela)
        caixa = self.css1('input[id="txtNomeTipoProcessoPesquisa"]')
        caixa.clear()
        caixa.send_keys('urbanismo - ' + Keys.ENTER)
        btn = self.css1('button[id="btnTransportarSelecao"]')
        btn.click()
        
        # terminar
        
        return

    def migrarProcesso(self,processo, unidade='ACERVO-EU'):
        self.logaSei()
        self.mudaUnidade(unidade)
        alinks = self.css('a')
        alinks = [x for x in alinks if 'Migrar Processo do GPA' in x.text]
        if not alinks:
            print('Link Migrar Processo do GPA não encontrado')
            return
        alinks[0].click()
        inp = el('input[name="txtNumeroProtocolo"]')
        inp.clear()
        inp.send_keys(processo)
        btn = el('button[name="sbmPesquisar"]')
        btn.click()

        while True:
            btnMigrar = []
            btnMigrar = self.css('button[id="sbmMigrarProtocoloGpa"]')
            if btnMigrar: break
            jamigrado = []
            jamigrado = self.css('div[id="divInfraExcecao"] > span[class="infraExcecao"]')
            if jamigrado:
                print(jamigrado[0].text)
                return False

        whPrincipal = self.driver.current_window_handle
        whTodasAntes = self.driver.window_handles
        btnMigrar[0].click()
        wh = whTodasAntes
        while wh == whTodasAntes:
            wh = self.driver.window_handles
        whNova = [x for x in wh if x not in whTodasAntes]
        if len(whNova)>1:
            print('erro: mais de uma janela nova')
            return False
        self.driver.switch_to.window(whNova[0])
        pwd = el('input[id="pwdSenha"]')
        pwd.clear()
        pwd.send_keys(password + Keys.ENTER)
        while wh != whTodasAntes:
            wh = self.driver.window_handles
        driver.switch_to.window(whPrincipal)
        return True

    def relacionaProcessos(self, principal, secundario, unidade='ACERVO-EU'):

        def concluiProc(self,proc=principal):
            self.iframe()
            pesq = self.aguardaEl('input[name="txtPesquisaRapida"]')
            pesq.clear()
            pesq.send_keys(proc + Keys.ENTER)
            ifr = self.iframe('iframe#ifrVisualizacao')
            btn = self.aguardaEl('a','onclick','concluirProcesso')
            btn.click()
            btnReabrir = self.aguardaEl('a','onclick','reabrirProcesso')

        self.logaSei()
        self.mudaUnidade(unidade)
        self.iframe()
        pesq = self.aguardaEl('input[name="txtPesquisaRapida"]')
        pesq.clear()
        pesq.send_keys(principal + Keys.ENTER)
        ifr = self.iframe('iframe#ifrVisualizacao')

        reabriu = False
        while True:
            btnRel = self.el('a','href','procedimento_relacionar')
            if btnRel:
                btnRel.click()
                break
            btnReabrir = self.el('a','onclick','reabrirProcesso')
            if btnReabrir and not reabriu:
                btnReabrir.click()
                reabriu = True

        inp = self.aguardaEl('input[id="txtProtocolo"]')
        inp.clear()
        inp.send_keys(secundario + Keys.ENTER)
        btnAdd = self.aguardaEl('button[id="sbmAdicionar"]')
        while not btnAdd.is_enabled() or not btnAdd.is_displayed(): # aguarda botão estar disponível
            pass
        # pega lista de relacionados antes de clicar no botão
        relacionadosAntes = []
        relacionadosLinhas = self.css('div[id="divInfraAreaTabela"] tr')
        if relacionadosLinhas:
            relacionadosLinhas = relacionadosLinhas[1:]
            relacionadosAntes = [x.find_elements(By.CSS_SELECTOR, 'td')[1] for x in relacionadosLinhas]
            relacionadosAntes = [x.text for x in relacionadosAntes]

        # se os processos já estão relacionados, retorna Falso
        if secundario in relacionadosAntes:
            if reabriu: concluiProc()
            iframe()
            return (False,'processo já relacionado')
        btnAdd.click()
        # monitora se houve mudanças na lista
        relacionadosDepois = relacionadosAntes
        while relacionadosDepois == relacionadosAntes:
            relacionadosLinhas = self.css('div[id="divInfraAreaTabela"] tr')
            if relacionadosLinhas:
                relacionadosLinhas = relacionadosLinhas[1:]
                relacionadosDepois = [x.find_elements(By.CSS_SELECTOR, 'td')[1] for x in relacionadosLinhas]
                relacionadosDepois = [x.text for x in relacionadosDepois]
        if reabriu: concluiProc()
        self.iframe()
        # ERRO: a lista mudou, mas o processo desejado não foi relacionado
        if not secundario in relacionadosDepois:
            return (False,'erro: processo não foi relacionado')
        # relacionado com sucesso
        return (True,'relacionado com sucesso')
    
    def pesquisaInicial(self, processo, unidade):
        self.logaSei()
        self.mudaUnidade(unidade)
        self.iframe()
        pesq = self.aguardaEl('input[name="txtPesquisaRapida"]')
        pesq.clear()
        pesq.send_keys(processo + Keys.ENTER)
        self.processo = processo
        while True:
            if self.css('iframe#ifrArvore'): break
            if self.css('div[class="sem-resultado"]'):
                self.processo=''
                return None
        self.iframe()
        self.iframe('iframe#ifrArvore')
        consultarAndamento = self.aguardaEl('img[alt="Consultar Andamento"]')
        plink = [x for x in self.css('a') if x.text==processo and x.get_attribute('target')=='ifrVisualizacao']
        href=''
        if plink: href = plink[0].get_attribute('href')
        if href == 'about:blank': return 'restrito' # area de visualização em branco, provavelmente o processo é bloqueado
        self.processo=processo
        return self.processo
            
    
    def pegaDataEntrada(self, processo, unidade=ERTP_DEL, destino=EGD_DEL):
        unatual = self.mudaUnidade()
        if not str(unatual).lower().startswith(unidade.lower()):
            self.mudaUnidade(unidade)
            self.pesquisaInicial(processo,unidade)
        if not self.processo == processo: self.pesquisaInicial(processo,unidade)
        ifr = self.iframe('iframe#ifrArvore')
        consultarAndamento = self.aguardaEl('img[alt="Consultar Andamento"]')
        consultarAndamento.click()
        ifr = self.iframe('iframe#ifrVisualizacao')
        #localizacao = self.aguardaEl('div[id="divInfraBarraLocalizacao"]')
        tabela = self.aguardaEl('table[id="tblHistorico"] tbody')
        rows = tabela.find_elements(By.CSS_SELECTOR, 'tr')
        for tr in rows:
            td = tr.find_elements(By.CSS_SELECTOR, 'td')
            if not len(td)==4: continue
            unid = td[1].text
            if not unid == destino: continue
            desc = td[3].text
            if not desc.startswith('Processo remetido pela unidade'): continue
            return td[0].text
        return False
    
    def pegaAndamentos_old(self, processo, unidade=SD_DEL):
        unatual = self.mudaUnidade()
        if not str(unatual).lower().startswith(unidade.lower()):
            self.mudaUnidade(unidade)
            self.processo=''
        if not self.processo == processo:
            pesq = self.pesquisaInicial(processo,unidade)
            if pesq == 'restrito':
                self.andamentos = 'restrito'
                return self.andamentos
        #if not self.processo == processo: self.pesquisaInicial(processo,unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrArvore')
        consultarAndamento = self.aguardaEl('img[alt="Consultar Andamento"]')
        consultarAndamento.click()
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        #localizacao = self.aguardaEl('div[id="divInfraBarraLocalizacao"]')
        tabela = self.aguardaEl('table[id="tblHistorico"]')
        outer = tabela.get_attribute('outerHTML')
        self.andamentos = outer
        
        rows = tabela.find_elements(By.CSS_SELECTOR,'body table tbody tr')
        origens = []
        coluna_unidades = []
        for idx, el in enumerate(rows):
            tds = el.find_elements(By.CSS_SELECTOR,'td')
            if not tds: continue
            dun = tds[3].find_elements(By.CSS_SELECTOR,'a')
            unid = tds[1].text
            coluna_unidades += [unid]
            if not dun: continue
            dun = dun[0]
            duntext = rows[idx+1].find_elements(By.CSS_SELECTOR,'td')[1].text
            origens += [(duntext,unid)]
        coluna_unidades.reverse()  # a primeira unidade deverá ser a unidade de origem (índice 0)
        self.andamento_unidades = coluna_unidades
        corrente = [unidade]
        for origem in origens:
            if not origem[1]==corrente[-1]: continue
            corrente += [origem[0]]
        self.correntedeunidades = corrente
        
        return self.andamentos
    
    def pegaAndamentos(self, processo, unidade=SD_DEL):
        unatual = self.mudaUnidade()
        if not str(unatual).lower().startswith(unidade.lower()):
            self.mudaUnidade(unidade)
            self.processo=''
        if not self.processo == processo:
            pesq = self.pesquisaInicial(processo,unidade)
            if pesq == 'restrito':
                self.andamentos = 'restrito'
                return self.andamentos
        #if not self.processo == processo: self.pesquisaInicial(processo,unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrArvore')
        consultarAndamento = self.aguardaEl('img[alt="Consultar Andamento"]')
        consultarAndamento.click()
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        tabela = self.aguardaEl('table[id="tblHistorico"]')
        outer = tabela.get_attribute('outerHTML')
        self.andamentos = outer
        # retorna páginas se não estiver na primeira
        while True:
            ifr = self.iframe()
            ifr = self.iframe('iframe#ifrVisualizacao')
            pagina_anterior = self.css('div[id="divInfraAreaPaginacaoSuperior"] a[id="lnkInfraPaginaAnteriorSuperior"]')
            if not pagina_anterior: break
            pagina_anterior[0].click()
        # extrai linhas de remessa de unidade
        unidesc = []
        while True:
            ifr = self.iframe()
            ifr = self.iframe('iframe#ifrVisualizacao')
            tabela = self.aguardaEl('table[id="tblHistorico"]')
            tds = [x.find_elements(By.CSS_SELECTOR,'td') for x in tabela.find_elements(By.CSS_SELECTOR,'body table tbody tr')]
            for linha in tds:
                if not linha: continue
                col_unid = linha[1].text
                a = linha[3].find_elements(By.CSS_SELECTOR,'a')
                if linha[3].text.startswith('Processo remetido pela unidade ') and a: col_desc = a[0].text
                else: col_desc = ''
                unidesc += [[col_unid, col_desc]]
            proxima_pagina = self.css('div[id="divInfraAreaPaginacaoSuperior"] a[id="lnkInfraProximaPaginaSuperior"]')
            if not proxima_pagina: break
            proxima_pagina[0].click()
        # atualiza nome das unidades em col_desc conforme próxima linha em col_unid
        for idx, linha in enumerate(unidesc):
            u = linha[0]
            d = linha[1]
            if not d: continue
            unidesc[idx]=[u,unidesc[idx+1][0]]
        
        # salva a coluna de unidades atualizada
        coluna_unidades = [x[0] for x in unidesc]
        coluna_unidades.reverse()  # a primeira unidade deverá ser a unidade de origem (índice 0)
        self.andamento_unidades = coluna_unidades
        
        # salva corrente de unidades iniciando da unidade atual
        origens = [(x[1],x[0]) for x in unidesc if x[1]]
        corrente = [unidade]
        for origem in origens:
            if not origem[1]==corrente[-1]: continue
            corrente += [origem[0]]
        self.correntedeunidades = corrente
        
        return self.andamentos
    
    def pegaUnidadeRemetente(self, processo, unidade=EGD_DEL):
        unatual = self.mudaUnidade()
        if not str(unatual).lower().startswith(unidade.lower()):
            self.mudaUnidade(unidade)
            self.pesquisaInicial(processo,unidade)
        if not self.processo == processo: self.pesquisaInicial(processo,unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrArvore')
        consultarAndamento = self.aguardaEl('img[alt="Consultar Andamento"]')
        consultarAndamento.click()
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        #localizacao = self.aguardaEl('div[id="divInfraBarraLocalizacao"]')
        tabela = self.aguardaEl('table[id="tblHistorico"] tbody')
        rows = tabela.find_elements(By.CSS_SELECTOR, 'tr')
        for tr in rows:
            td = tr.find_elements(By.CSS_SELECTOR, 'td')
            if not len(td)==4: continue
            unid = td[1].text
            if not unid == unidade: continue
            desc = td[3].text
            if not desc.startswith('Processo remetido pela unidade '): continue
            return desc.split(' ')[-1]
        return False
    
    def abreProc(self, proc, unidade=SD_DEL):
        _ = self.pegaLocaisAbertos(processo, unidade)
        _ = self.listaArquivos(processo, unidade)
        _ = self.listaRelacionados(processo, unidade)
    
    def pegaLocaisAbertos(self, processo, unidade=SD_DEL):
        _ = self.mudaUnidade(unidade)
        pesq = self.pesquisaInicial(processo,unidade)
        if pesq == 'restrito':
            self.locais = {'restrito':''}
            return self.locais
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        info1 = self.aguardaEl('div[id="divInformacao"]')
        info = info1.text
        locais = {}
        #if info == 'Processo não possui andamentos abertos.': return locais
        if info.startswith('Processo aberto somente na unidade '):
            local = info1.find_element(By.CSS_SELECTOR, 'a').get_property('text')
            atribuido = ''
            if ' (atribuído para ' in info: atribuido = info[info.index(' (atribuído para '):-1]
            locais[local]=atribuido
        if info.startswith('Processo aberto nas unidades:'):
            locais0 = info1.find_elements(By.CSS_SELECTOR, 'br + a')
            linhas = info.split('\n')[1:]
            for l in linhas:
                for locEl in locais0:
                    loc = locEl.get_property('text')
                    if loc in l:
                        atribuido = ''
                        if ' (atribuído para ' in l: atribuido = l[l.index(' (atribuído para '):-1]
                        locais[loc]=atribuido
        self.locais = locais
        return self.locais
    
    def listaArquivos(self, processo, unidade=SD_DEL):
        unidadeAtual = self.mudaUnidade()
        if not self.processo == processo or not unidadeAtual.lower().startswith(unidade.lower()):
            self.pesquisaInicial(processo,unidade)
        
        ifr = self.iframe()
        if not self.css('iframe#ifrArvore'): self.pesquisaInicial(processo,unidade)
        ifr = self.iframe('iframe#ifrArvore')
        
        while True:
            abrirPastas = self.css('div[id="topmenu"] a img[title="Abrir todas as Pastas"]')
            abrirPastas = [x for x in abrirPastas if x.find_elements(By.CSS_SELECTOR,'img[title="Abrir todas as Pastas"]')]
            if not abrirPastas: break
            abrirPastas[0].click()
            divPastas = self.css('div[id="divArvore"] div[class="infraArvore"] div[id^="divPASTA"]')
            if all([x.is_displayed() for x in divPastas]) or not divPastas: break
        
        abrirtodas = [x for x in self.css('a[id^="anchor"]') if x.find_elements(By.CSS_SELECTOR,'img[title="Abrir todas as Pastas"]')]
        if abrirtodas: self.driver.get(abrirtodas[0].get_attribute('href'))
        
        if not abrirtodas: self.iframe('iframe#ifrArvore')
        alinks = self.css('div.infraArvore div.infraArvore a')
        
        arqs = {}
        for idx, a in enumerate(alinks):
            if not a.get_attribute('class')=='clipboard': continue
            icone = a.find_elements(By.CSS_SELECTOR,'img')
            if icone: icone = [x.get_attribute('src').split('/')[-1] for x in icone]
            nome = alinks[idx+1].text
            link = alinks[idx+1].get_attribute('href')
            if link=='about:blank': link = 'BLOQUEADO'
            arqs[nome]={'icone':icone, 'link':link}
        
        if abrirtodas: self.driver.back()
        self.arquivos = arqs
        return arqs
    
    def listaRelacionados(self, processo, unidade=SD_DEL):
        self.pegaLocaisAbertos(processo,unidade)
        ifr = self.iframe('iframe#ifrArvore')
        aguarda = self.aguardaEl('div[id="divRelacionados"]')
        relacionados = self.css('div[id="divRelacionadosParciais"]')
        if len(relacionados) <1:
            self.relacionados = {}
            return self.relacionados
        else: relacionados = relacionados[0]
        children = relacionados.find_elements(By.CSS_SELECTOR, 'a')
        relacionados = {}
        tipo = ''
        for x in children:
            if not x.text=='':
                tipo = x.text
                if not tipo in relacionados: relacionados[tipo] = {}
                continue
            relacionados[tipo][x.get_property('text')] = x.get_attribute('class')
        self.relacionados = relacionados
        return self.relacionados
    
    def listaEU(self, proc, unidade):
        # retorna lista de relacionados que sejam do tipo EXPEDIENTE ÚNICO
        # sem verificar se o relacionado é realmente EU ou não (pode não iniciar por 002)
        if not self.processo==proc:
            self.listaRelacionados(proc, unidade)
        euKey = [x for x in self.relacionados if x.startswith('EXPEDIENTE ÚNICO (')]
        if not euKey: return []
        return list(self.relacionados[euKey[0]].keys())
    
    def enviarProcesso(self, processo, destino, origem=SD_DEL, mudo=True, forcaEnvio=False):
        destino = destino.upper()
        orgeim = origem.upper()
        locais = self.pegaLocaisAbertos(processo,unidade=origem)
        if not any([x.lower().startswith(origem.lower()) for x in locais]):
            if not mudo: print(locais,'\nERRO: o processo não está aberto em',origem)
            return locais
        ifr = self.iframe('iframe#ifrVisualizacao')
        btn = self.aguardaEl('div[id="divArvoreAcoes"] a[href*="acao=procedimento_enviar"]')
        btn.click()
        ifr = self.iframe('iframe#ifrVisualizacao')
        caixa = self.aguardaEl('input[id="txtUnidade"]')
        caixa.clear()
        caixa.send_keys(destino)
        
        # espera spinner aparecer e desaparecer
        while not self.css('input#txtUnidade[class*="infraProcessando"]'):
            pass
        while self.css('input#txtUnidade[class*="infraProcessando"]'):
            pass
        
        ac = self.css1('div[class="infraAjaxAutoCompletar"]')
        if not ac.is_displayed(): # destino não localizado
            return {None}
        
        lista = ac.text.split('\n')
        c=0
        for op in lista:
            c+=1
            if op.startswith(destino): break
                
        downs = Keys.DOWN * c
        caixa.send_keys(downs + Keys.ENTER)
        
        btn = self.aguardaEl('button[value="Enviar"]')
        btn.click()
        try:
            locais = self.pegaLocaisAbertos(processo, unidade=origem)
        except UnexpectedAlertPresentException as err:
            if 'informe as unidades de destino' in str(err).lower(): return locais
        if not any([x.lower().startswith(destino.lower()) for x in locais]):
            return locais
        locais[destino]=''
        return locais
    
    def concluiProcesso(self, processo, unidade=SD_DEL):
        return self.clicaBtnAguarda(processo,'Concluir Processo',unidade)
    
    def reabreProcesso(self, processo, unidade=SD_DEL):
        return self.clicaBtnAguarda(processo,'Reabrir Processo',unidade)

    def clicaBtnAguarda(self, processo, btnAlt, unidade = SD_DEL):
        self.pesquisaInicial(processo,unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        info = self.aguardaEl('div[id="divArvoreAcoes"]')
        btns = info.find_elements(By.CSS_SELECTOR, 'a')
        btn = [x for x in btns if x.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')==btnAlt]
        if btn == []: return False
        btn[0].click()
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        info = self.aguardaEl('div[id="divArvoreAcoes"] a')
        btns = self.css('div[id="divArvoreAcoes"] a')
        btn = [x for x in btns if x.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')==btnAlt]
        if btn: return False
        return True
    
    def clicaBtn(self, processo, btnAlt, unidade=SD_DEL):
        self.pesquisaInicial(processo,unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        info = self.aguardaEl('div[id="divArvoreAcoes"]')
        btns = info.find_elements(By.CSS_SELECTOR, 'a')
        btn = [x for x in btns if x.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')==btnAlt]
        if btn == []: return False
        btn[0].click()
        sleep(1)
        return True
        
    def insereAndamento(self, processo, msg, unidade=SD_DEL):
        self.clicaBtn(processo, 'Atualizar Andamento',unidade)
        ifr = self.iframe()
        ifr = self.iframe('iframe#ifrVisualizacao')
        box = self.aguardaEl('textarea[class="infraTextarea"]')
        btn = self.aguardaEl('button[id="sbmSalvar"]')
        box.clear()
        box.send_keys(msg)
        btn.click()
        return True
    
    def insereArquivo(self, proc, unid, arquivo_fullpath, aceitadocjaexiste = True):
        '''
        proc : número do processo SEI
        unid : unidade
        arquivo_fullpath : caminho completo do arquivo a ser inserido
        aceitadocjaexiste = True : aceitar mensagem do SEI indicando que o documento já existe.
        
        retorna: {'erro': 'MENSAGEM'} ou {'ok':''}
        
        '''

        arquivo = os.path.split(arquivo_fullpath)[1]
        unatual = self.mudaUnidade()
        if not str(unatual).lower().startswith(unid.lower()):
            u = self.mudaUnidade(unid)
            if u is False:
                return {'erro':f'sem acesso à unidade {unid}'}
            self.pesquisaInicial(proc,unid)
        if not self.processo == proc:
            self.pesquisaInicial(proc,unid)

        r = self.clicaBtn(proc,'Incluir Documento',unid)
        if not r:
            return {'erro':f'sem botão de incluir documento no processo {proc} na unidade {unid}'}
        txt = self.aguardaEl('input[id="txtFiltro"]')
        txt.clear()
        txt.send_keys('externo' + Keys.ENTER)
        externo = self.aguardaEl('table[summary="Tabela de Tipos de Documento."] tbody tr[data-desc~="externo"]')
        externo.click()

        tipoDoc = Select(self.aguardaEl('select[id="selSerie"]'))
        tipoDoc.select_by_visible_text('Documento')

        dataDoc = self.aguardaEl('input[id="txtDataElaboracao"]')
        dataDoc.clear()
        dataHoje = datetime.today().strftime("%d/%m/%Y")
        dataDoc.send_keys(dataHoje)

        nome = self.aguardaEl('input[id="txtNumero"]')
        nome.clear()
        nome.send_keys(arquivo)
        
        formato = self.aguardaEl('input[type="radio"][id="optNato"]')
        if not formato.is_selected(): formato.click()

        aguarda = self.aguardaEl('button[id="btnUploadCancelarfrmAnexos"]')
        upload = self.aguardaEl('input[type="file"][id="filArquivo"]')
        try:
            upload.send_keys(arquivo_fullpath)
        except InvalidArgumentException as e:
            ifr = self.iframe('iframe#ifrArvore')
            link = self.aguardaEl('div[id="topmenu"] a[target="ifrVisualizacao"]')
            link.click()
            return {'erro': e.msg}

        # aguarda o upload se completar e pega mensagem de alerta
        try:
            while not aguarda.is_displayed():
                pass
            while aguarda.is_displayed():
                pass
        except UnexpectedAlertPresentException as e:
            if 'Arquivo excede o tamanho máximo' in e.msg:
                self.pesquisaInicial(proc,unid)
                return {'erro': 'tamanho máximo excedido'}
            

        botao = self.aguardaEl('button[id="btnSalvar"]')
        botao.click()

        ifr = self.iframe('iframe#ifrVisualizacao')
        #info = self.aguardaEl('div[id="divArvoreAcoes"]')
        
        
        while True:
            try:
                alert = Alert(self.driver)
                txt = alert.text
                if 'Já existe um documento' in txt and 'cadastrado com estas características.' in txt:
                    alert.accept()
            except NoAlertPresentException:
                if self.css('div[id="divArvoreAcoes"]'): break
            
        self.pesquisaInicial(proc,unid)
        return {'ok':''}
    
    def disponibilizaAcessoExterno(self, proc, requerente, email_requerente, motivo, unidade='ACERVO-EU', prazo=90):
        self.pegaLocaisAbertos(proc,unidade)
        if not unidade in self.locais:
            #print(f'não está em {unidade}')
            return None
        self.clicaBtn(proc,'Gerenciar Disponibilizações de Acesso Externo',unidade)
        self.iframe('iframe#ifrVisualizacao')
        selEmail = Select(self.css1('select[id="selEmailUnidade"]'))
        emailUnidade = [x.text for x in selEmail.options if '@' in x.text]
        if not emailUnidade:
            #print('email da unidade não localizado')
            return False
        selEmail.select_by_visible_text(emailUnidade[0])
        nome = self.css1('input[id="txtDestinatario"]')
        nome.clear()
        nome.send_keys(requerente)

        email = self.css1('input[id="txtEmailDestinatario"]')
        email.clear()
        email.send_keys(email_requerente)

        textarea = self.css1('textarea[id="txaMotivo"]')
        textarea.clear()
        textarea.send_keys(motivo)

        integral = self.css1('label[id="lblIntegral"]')
        integral.click()

        dias = self.css1('input[id="txtDias"]')
        dias.clear()
        dias.send_keys(str(prazo))

        senha = self.css1('input[id="pwdSenha"]')
        senha.clear()
        senha.send_keys(self.password)

        self.alerta=''

        disp = self.css1('button[id="btnDisponibilizar"]')
        disp.click()

        while True:
            if self.temAlerta(): break

        return self.alerta
    
    def marcador(self, proc, unidade, marcar=None, texto=None):
    
        self.pesquisaInicial(proc, unidade)
        self.clicaBtn(proc, 'Gerenciar Marcador', unidade)

        self.iframe('iframe#ifrVisualizacao')
        salvar = self.css1('button[value="Salvar"]')
        seletor = self.css1('a[class="dd-selected"]')
        seletor.click()
        marcadores = self.css('ul li a')
        for m in marcadores:
            label = m.find_elements(By.CSS_SELECTOR,'label')
            txt = label[0].get_attribute('innerHTML') if label else ''
            selecionado = 'dd-option-selected' in m.get_attribute('class')
            if marcar == None and selecionado:
                salvar.click()
                return txt
            if txt == marcar:
                while not m.is_displayed():
                    pass
                m.click()

                if texto:
                    textarea = self.css1('textarea[id="txaTexto"]')
                    textarea.clear()
                    textarea.send_keys(texto)
                salvar.click()
                return marcar
        salvar.click()
        return None
    
    def atribuir(self, proc, unidade, atribuir=None):
        if atribuir==None:
            locs = self.pegaLocaisAbertos(proc, unidade)
            match = [x for x in locs if x.lower().startswith(unidade.lower())]
            if match: return {'atribuido':locs[match[0]].split(' ')[-1][:-1]}
            else: return {}

        clicou = self.clicaBtn(proc, 'Atribuir Processo', unidade=unidade)
        if not clicou: return {'erro':'sem botão'}
        self.iframe('iframe#ifrVisualizacao')
        salvar = self.css1('button[id="sbmSalvar"]')
        seletor = Select(self.css1('select[id="selAtribuicao"]'))

        if not atribuir: atribuir=' '
        for op in seletor.options:
            txt = op.text
            if txt.startswith(atribuir):
                seletor.select_by_visible_text(txt)
                salvar.click()
                if txt==' ': return {}
                return {'atribuido':txt}
    


# In[ ]:





# In[ ]:


# ### TESTES ###

# sei = operadorSEI(headless=False, usuario=getuser())


# In[ ]:


# proc = '19.0.000058930-9'
# proc = '19.0.000057016-0'
# unidade = 'ACERVO FISICO-SMAMUS'
# ands = sei.pegaAndamentos(proc, unidade)


# In[ ]:


# ands2 = sei.pegaAndamentos_old(proc,unidade)


# In[ ]:


# ands == ands2


# In[ ]:





# In[ ]:





# In[ ]:


# sei.quit()


# In[ ]:





# In[ ]:




