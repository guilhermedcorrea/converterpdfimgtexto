from pdf2image import convert_from_path, convert_from_bytes
import tempfile
import cv2
import pytesseract
import re
import pandas as pd
from itertools import zip_longest
from os import listdir, path, makedirs
from os.path import isfile, join
import time
import pyodbc
from testes_aplicacao import funcoes_aplicacao
import os
import numpy as np

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
imagens_sense = 'D:\\Trabalhos Python\\converter_pdffiles\\imagemsense\\'


save_file = 'D:\\Trabalhos Python\\converter_pdffiles\\'
sense = 'sense'
filename = sense + " - " + \
           time.strftime("%d-%b").replace(":", ".") + ".csv"




referencias = []
saldos = []
prazos = []


def ajuste_referencias(elementos):
    ajustados = []
    for elemento in elementos:
        valor = elemento.split("-")
        ref = valor[0].strip()
        ajustados.append(ref)
    return ajustados


def organiza_informaces(elementos):
    ref = []
    saldo = []

    for elemento in elementos:
        try:
            ref.append(elemento[0])
        except Exception as e:
            print(e)
            ref.append("Não encontrado")

        try:
            saldo.append(elemento[-2])
        except Exception as e:
            print(e)
            saldo.append("Não encontrado")

    return ref, saldo

def referencia_merge(elementos):
    valor = elementos.replace(".", "").strip()
    return valor

def formatar_saldo(elementos):
    ajustados = []
    for elemento in elementos:
        valor = str(elemento).replace(",", ".")
        ajustados.append(valor)

    return ajustados
try:
    arquivo = os.listdir('D:\\Trabalhos Python\\converter_pdffiles\\sense\\')
    files = arquivo[0]
    print(files)
except:
    pass

try:
    path = f'D:\\Trabalhos Python\\converter_pdffiles\\sense\\{files}'
    print(path)
except:
    pass
try:
    images = convert_from_path(path, 200, poppler_path='D:\\Trabalhos Python\\converter_pdffiles\\poppler-21.10.0\\Library\\bin')
    for i in range(len(images)):
        images[i].save(imagens_sense + 'sense' + str(i) + '.jpg', 'JPEG')
except Exception as e:
    print(e)



lista_imagens = [f for f in listdir(imagens_sense) if isfile(join(imagens_sense, f))]
for lista in lista_imagens:
    imagem = cv2.imread(f'D:\\Trabalhos Python\\converter_pdffiles\\imagemsense\\{lista}')
    imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
    texto = pytesseract.image_to_string(imagem_gray)
    valor = texto.split("\n")
    remov_esp = [x.split() for x in valor if x != '' if x != ' ']
    refs, sds = organiza_informaces(remov_esp)
    for x, y in zip_longest(refs, sds):
        referencias.append(x)
        saldos.append(y)
        prazos.append(np.nan)


def converte_infos():
    try:
        df_sense = pd.DataFrame({"Referencias": referencias, "Saldos": saldos,"Prazo":prazos})
        df_sense["Referencias"] = ajuste_referencias(df_sense["Referencias"])

        df_bdhausz = pd.read_sql_query(select_bd, conn)
        df_bdhausz["Referencias"] = df_bdhausz["SKU"].apply(lambda x: referencia_merge(x))
        finall_df = pd.merge(df_bdhausz, df_sense, left_on='Referencias', right_on='Referencias', how='left')
        finall_df["Saldos"].fillna(0, inplace=True)
        finall_df["Saldos"] = formatar_saldo(finall_df["Saldos"])
        finall_df["Saldos"] = finall_df["Saldos"].astype(float)
        finall_df = finall_df[["IdMarca", "SKU",  "Saldos","Prazo"]]
        finall_df = finall_df.drop_duplicates()

        json_sense = finall_df.to_json(orient='records')
        print(json_sense)
        return json_sense
    except Exception as e:
        return {"Valor":"Não encontrado"}



