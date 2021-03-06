#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
#Se importa los modulos necesarios de pdfminer

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import re

def convertir(archivo, paginas=None):
    #Si no se le pasa el numero de paginas se inicializa pagenums si no se le pasa 
    #a pagenums el numero de paginas.
    if not paginas:
        pagenums = set()
    else:
        pagenums = set(paginas)

    #Se define la salida
    output = StringIO()
    #Se crea la instancia del manejador
    manager = PDFResourceManager()
    #se instancia el conversor de texto donde se le pasa el manejador y la salida
    converter = TextConverter(manager, output, laparams=LAParams())
    #Se instancia el interprete pasando el manejador y el conversor
    interpreter = PDFPageInterpreter(manager, converter)

    #Se abre el archivo de entrada
    infile = file(archivo, 'rb')
    #Se crea un ciclo pasando el archivo de entrada y el numero de paginas.
    for page in PDFPage.get_pages(infile, pagenums):
        #Se procesa cada pagina
        interpreter.process_page(page)
    #Se cierra el archivo de entrada
    infile.close()
    #Se cierra el conversor
    converter.close()
    #Se obtiene los valores de la salida en texto
    texto = output.getvalue()
    #Se cierra la salida
    output.close
    #Se devuelve el texto
    resultado = string.split(texto,"\n")

    return resultado

#Se le pasa el archivo pdf de cencoex del sector salud
def extraerDatos(archivo):
    #Se pasa el archivo a la funcion convertir que convierte la informacion
    #en una lista
    listado = convertir(archivo)
    
    #Se define el patron de la expresion regular del RIF y de numero.
    patron_rif = re.compile(r"(J-\d+)")
    patron_numero = re.compile(r"(\d+)")
    pattern = re.compile(r"(\d+)")

    #Se crea una lista vacia.
    lista = []
    #Se recorre la lista
    for i in listado: 
        #Se recorre cada elemento de la lista buscando los numeros.
        resultado_numero=  patron_numero.findall(i)
        #Si la cantidad de elementos devuelto es 1 y es una lista que contiene 3 elementos o menos
        if (len(resultado_numero) == 1) and (len(resultado_numero[0]) <= 3):
            #Se hace un split eliminando los espacios en blanco, agregando a nombre desde el 2do elemento de la lista 
            #hasta el final
            nombre = i.split(" ")[1:]
            #Luego se vuelve a agregar esos espacios
            nombre = string.join(nombre," ")
            #Se agrega a la lista un diccionario con el numero y el nombre de la empresa
            lista.append({'numero': int(resultado_numero[0]),"empresa": nombre})
    
    #Se crea un diccionario de contadores, en este caso 2.
    #el del ciclo del rif y el del monto
    contador = { "rif": 1, "monto":1}

    #Se vuelve a recorrer el listado

    for i in listado:
        #Se busca en cada elemento el rif por una expresion regular
        resultado_rif = patron_rif.findall(i)
        #Si el resultado es diferente de cero
        if len(resultado_rif) <> 0:
            #Se recorre la lista generada anteriormente (la lista de diccionarios)
            for num in range(len(lista)):
                #Si el elemento del diccionario de esa lista es igual al contador de rif
                #Se agrega el rif al diccionario actual de la lista y se finaliza el recorrido
                if  (lista[num]["numero"] == contador["rif"]):
                    lista[num]["rif"] = resultado_rif[0]
                    break
            #Se incrementa el contador de rif.
            contador["rif"] = contador["rif"] + 1
        #Si se encuentra una coma en la lista y al eliminar el espacio en blanco la longitud
        #de la lista es 1, se recorre la lista de diccionario para buscar el monto, en este caso se
        #consulta si el numero del diccionario es igual al contador de monto, si es así se agrega
        #el monto al diccionario y se finaliza el recorrido del ciclo
        if (string.find(i,",") <> -1 and len(i.split(" ")) == 1):
            for num in range(len(lista)):
                if  (lista[num]["numero"] == contador["monto"]):
                    lista[num]["monto"] = i
                    break
            #Se incrementa el contador monto
            contador["monto"] = contador["monto"] +1
    #Se retorna la lista de diccionarios con los elementos necesarios
    return lista





if __name__ == "__main__":
    #Se importa el modulo pymongo
    import pymongo
    #Se conecta a la base de datos mongodb local
    connection = pymongo.MongoClient("mongodb://localhost")
    #Se usa la base de datos cencoex y la coleccion salud
    db=connection.cencoex
    salud = db.salud
    #Se extraen los datos del archivo salud.pdf y se guarda en datos
    datos = extraerDatos("salud.pdf")
    #Se recorre datos, si la longitud de los elementos de los diccionarios es igual a 4 
    #Se inserta en la base de datos
    for num in range(len(datos)):
        if len(datos[num].keys()) == 4:
            try:
                salud.insert_one(datos[num])
            except Exception as e:
                print "Unexpected error:", type(e), e


