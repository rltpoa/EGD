#!/usr/bin/env python
# coding: utf-8

# In[26]:


import os
from shutil import move
import configparser

class Checador:
    
    def __init__(self,atualiza=False):
        configfile = 'configpastas.ini'
        self.roots = []
        self.apelidos = {}
        if os.path.isfile(configfile):
            self.pegaconfig(configfile)
        else:
            self.salvaconfig(configfile,padrao=True)
            self.pegaconfig(configfile)

        self.listagem = {}
        self.pastas = {}
        if atualiza: self.atualizaListagem()

    def salvaconfig(self, configfile, padrao=False):
        config = configparser.ConfigParser()
        if padrao:
            config['unidades'] = {'0':'z:\\'}
            config['apelidos'] = {
                'p1':'@_parte_1',
                'p2':'@_parte_2',
                'p3':'@_parte_3',
                'digi':'_100%% DIGITAL',
                'anexos':'_ANEXOS',
                'orquestra':'_ORQUESTRA'
            }
        else:
            config['unidades'] = self.roots
            config['apelidos'] = self.apelidos
        with open(configfile, 'w') as f:
            config.write(f)
    
    def pegaconfig(self, configfile):
        conf = configparser.ConfigParser()
        conf.read(configfile)
        if 'unidades' in conf:
            unidades = []
            for u in conf['unidades']:
                unidades.append(conf['unidades'][u])
        if 'apelidos' in conf:
            apelidos = {}
            for ap in conf['apelidos']:
                apelidos[ap] = conf['apelidos'][ap]
        self.roots = unidades
        self.apelidos = apelidos
              
    def achaPastasEU(self,root):
        listagem = {}
        path, pastas, files=os.walk(root).__next__()
        for p in pastas:
            if self.padraoEU(p):
                if not p in listagem: listagem[p]=[]
                listagem[p].append(path)
                continue
            subpath, subpastas, subfiles = os.walk(path+'\\'+p).__next__()
            for pp in subpastas:
                if self.padraoEU(pp):
                    if not pp in listagem: listagem[pp]=[]
                    listagem[pp].append(subpath)
                    continue
        return listagem
        
    def padraoEU(self,eu):
        eu = eu.replace(' ','')
        if not eu.replace('.','').isdigit() and len(eu)>=9: return False
        #if not len(eu) == 21: return False
        if not eu.startswith(('002','001')): return False
        #if not eu[3:4] + eu[10:11] + eu[13:14] + eu[15:16] == '....': return False
        #if not str(eu[0:3] + eu[11:13] + eu[14:15] + eu[16:21]).isnumeric(): return False
        return True
        
    def atualizaListagem(self, roots=''):
        if not roots: roots = self.roots
        listagem = {}
        for root in roots:
            path, folders, files = os.walk(root).__next__()
            pastas = [x for x in folders if x.startswith(tuple(self.apelidos.values()))]
            pastas = [path+x for x in pastas]
            for p in pastas:
                lista = self.achaPastasEU(p)
                for l in lista:
                    if not l in listagem: listagem[l]=[]
                    if not lista[l] in listagem[l]: listagem[l]+=lista[l]
        self.listagem = listagem
        return self.listagem
    
    def pegaCaminhoEU(self,eu,apelidoDesejado=''):
        pastas = self.listagem.get(eu,[])
        pastasApelidadas = {}
        for apelido in self.apelidos:
            if not apelido in pastasApelidadas: pastasApelidadas[apelido]=[]
            pastasApelidadas[apelido] = [x for x in pastas if self.apelidos[apelido] in x]
        if apelidoDesejado in pastasApelidadas: return pastasApelidadas[apelidoDesejado]
        return [x for x in pastasApelidadas.keys() if pastasApelidadas[x]]
        #return list(pastasApelidadas.keys())
    
    def movePasta(self,eu,pastaEU,destino):
        caminhos = self.pegaCaminhoEU(eu)
        if not pastaEU in caminhos:
            #print('1') # debug
            return False
#         if destino in caminhos:
#             #print('2') # debug
#             return False
        if not destino in self.apelidos:
            #print('3') # debug
            return False
        caminhoEU = self.pegaCaminhoEU(eu,pastaEU)[0] + '\\' + eu
        unidade = caminhoEU[:1] + ':\\'
        destino = self.apelidos[destino]
        path, folders, files = os.walk(unidade).__next__()
        f = [unidade+x for x in folders if x.startswith(destino)]
        if not f: return False
        destino = f[0]
        self.move_renomeando(caminhoEU, destino)
        
    def acha_novo_nome(self, nome, destino):
        # acrescenta sufixo ao final do nome do arquivo caso já exista no destino
        novo_nome = nome
        i=2
        while os.path.exists(os.path.join(destino, novo_nome)):
            ext = nome.split('.')[-1]
            nome1 = nome.rsplit('.',1)[0]
            novo_nome = f'{nome1} ({i}).{ext}'
            i += 1
        return novo_nome
    
    def move_renomeando(self, pasta, destino):
        '''
        move pasta renomeando arquivos se eles já existem no destino, padrão Windows.
        '''
        if not os.path.exists(pasta): return
        path, pastas, files=os.walk(pasta).__next__()

        tail = os.path.split(pasta)[1]
        nova_pasta = os.path.join(destino, tail)
        dst = os.path.join(destino,tail)

        if not os.path.exists(dst):

            try:
                r = move(path, destino)
                #print(f'movendo pasta {path} para {destino}')
            except Exception as e:
                print(f'Erro ao mover pasta {path} para {destino}')
                print(e)
                input('[ENTER] para continuar... ')
        else:

            for p in pastas:
                src = os.path.join(pasta,p)
                dst = os.path.join(destino,tail)
                #print('entrando pasta:',src,dst)
                self.move_renomeando(src, dst)

            for f in files:
                src = os.path.join(pasta,f)
                dst = os.path.join(destino, tail)
                dst_nome = os.path.join(dst,f)
                if os.path.exists(dst_nome):
                    nome = self.acha_novo_nome(f, dst)
                    nome = os.path.join(pasta,nome)
                    os.rename(src, nome)
                    #print(f'renomeando arquivo {src} para {nome}')
                    src = nome
                try:
                    r = move(src, dst)
                    #print(f'movendo arquivo {src} para {dst}')
                except Exception as e:
                    print(f'Erro ao mover arquivo {src} para {dst}')
                    print(e)
                    input('[ENTER] para continuar... ')

            path, pastas, files=os.walk(pasta).__next__()
            if len(files) == 0:
                os.rmdir(path)
        
    def subpastasRelacionados(self, eu, apelido=''):
        if not apelido:
            apelido = self.pegaCaminhoEU(eu)
            if not apelido: return []
            if len(apelido)==1: apelido=apelido[0]
            else: return apelido
        caminho = self.pegaCaminhoEU(eu,apelido)[0] + '\\' + eu
        walker = os.walk(caminho)
        return walker.__next__()[1]
    
    def listaPasta(self,eu,pasta=''):
        pastas = self.listagem[eu]
        if not pasta and len(pastas)==1: pasta = pastas[0]
        if not pasta in pastas: return pastas
        subpath, subpastas, subfiles = os.walk(pasta).__next__()
        fullpasta = subpath + '\\' + eu
        subpath, subpastas, subfiles = os.walk(fullpasta).__next__()
        return (subpastas, subfiles)
    


# In[ ]:





# In[27]:


# TESTES


# In[30]:


# checador = Checador(atualiza=True)
# eu = '002.221179.00.3.00000'
# c = checador.pegaCaminhoEU(eu)
# c


# In[31]:


#checador.movePasta(eu,'p3','digi')


# In[3]:


#checa.listagem[eu]


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




