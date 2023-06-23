import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree
import win32com.client
import time
import os 
import pandas as pd

def realizarsolicitudsoap():
    url = "https://www.eurocompcr.com/webservice.php?wsdl"
    usuario = 1550
    contrasena = "15502022"
    bid = 1

    xmldata = '''<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:server">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:wsc_request_bodega_all_items>
                    <ws_pid>{}</ws_pid>
                    <ws_passwd>{}</ws_passwd>
                    <bid>{}</bid>
                </urn:wsc_request_bodega_all_items>
            </soapenv:Body>
        </soapenv:Envelope>'''.format(usuario, contrasena, bid)

    headers = {"Content-Type": "text/xml"}
    response = requests.post(url, data=xmldata, headers=headers)

    responsecode = response.status_code
    responsedata = response.text

    if responsecode == 200:
        return responsedata

    else:
        print("Error en la solicitud SOAP. Código de respuesta:", responsecode)

def guardar(responsedata, nombre):
    with open(nombre, "w") as archivo:
        archivo.write(responsedata)
        print("Archivo XML guardado exitosamente")

def actualizarDatosExcel():
        print("Actualizando datos Excel...")
        xlapp = win32com.client.DispatchEx("Excel.Application")
        wb = xlapp.Workbooks.open(os.getcwd()+"\\Inventario_Eurocomp.xlsx")
        wb.RefreshAll()
        xlapp.CalculateUntilAsyncQueriesDone()
        xlapp.DisplayAlerts = False
        wb.Save() 
        xlapp.Quit() 
        salir = True
        print("Datos actualizados")

def exportarExcelACsv():
    print("Exportando Excel actualizado a CSV")
    salir = False
    while salir == False:
        try:
            wb = pd.read_excel ("Inventario_Eurocomp.xlsx")
            #wb.to_csv ("Inventario_Eurocomp.csv",encoding='utf-8-sig', index=False)
            salir = True
            csv_string = wb.to_csv(index=False, sep=',')
            print("Exportacion a CSV exitosa")
        except PermissionError as e:
            print("ERROR: Reitentando guardar el CSV")
            time.sleep(0.25)
    return csv_string

def tipoDeCambio():
    # URL de la API
    url = 'https://tipodecambio.paginasweb.cr/api'

    # Realiza la solicitud GET a la API
    response = requests.get(url)

    # Verificar el estado de la respuesta
    if response.status_code == 200:
        # Obtener el tipo de cambio del JSON de respuesta
        data = response.json()
        tipo_cambio = data['venta']
        print(tipo_cambio)
        return tipo_cambio
    else:
        print('Error al obtener el tipo de cambio.')

def transformar(responsedata):
    #se convierte el xml en string y luego a un objeto xml para buscar la informacion 
    xml_data = ET.fromstring(responsedata)
    data = []
    cols = []
    columnas = []
    for child in xml_data:
        for subchild in child:
            for subsubchild in subchild:
                for subsubsubchild in subsubchild:
                    for subsubsubsubchild in subsubsubchild:
                        data.append([subsubsubsubchild.text for subsubsubsubchild in subsubsubchild])
                        cols.append(subsubsubsubchild.tag for subsubsubsubchild in subsubsubchild)
                        
                        #este if busca el nombre de las columnas
                        if subsubsubsubchild.tag not in columnas:
                            columnas.append(subsubsubsubchild.tag)
    #se convierte la data en un dataframe de pandas y se rota 90°
    df = pd.DataFrame(data).T
    #se agrega una columna  con el nombre que van a tener las columnas una vez que se rote de nuevo 
    df.columns = cols 
    #se elimina la primer columna que era indice, se rota, y se eliminan duplicados de la columna codigo
    df = df.iloc[:, 1:].T.set_axis(columnas, axis=1).drop_duplicates(subset=['codigo'])   

    #se intenta eliminar las columnas innecesarias
    try:
        del df["cod_producto"]
        del df["cod_proveedor"]     
        del df["cod_hacienda"]  
        del df["desc_corta"]
        del df["modelo"]
        del df["presentacion"]
        del df["colores"]
        del df["familia_id"]
        del df["clase"]
        del df["item_grupo_1"]
        del df["item_grupo_2"]
        del df["item_grupo_3"]
        del df["image_url_2"]
        del df["image_url_3"]
        del df["image_url_4"]
        del df["image_url_5"]
        del df["caracteristicas"]
        del df["itemref_1"]
        del df["itemref_2"]
        del df["itemref_3"]
        del df["itemref_4"]
        del df["itemref_5"]
        del df["itemref_6"]
        del df["itemref_7"]
        del df["itemref_8"]
        del df["itemref_9"]
        del df["itemref_10"]
        del df["itemref_11"]
        del df["itemref_12"]
        del df["itemref_13"]
        del df["itemref_14"]
        del df["privacidad"]
        del df["peso"]
        del df["medida"]
        del df["equivalencia"]
    
    except KeyError as e:
        print("ERROR: Una columna original se le cambio el nombre o ya no existe")

    #se le pone el prefijo a las columnas para obtener una url con la imagen
    prefijo = "eurocompcr.com/"
    df['image_url'] = df['image_url'].apply(lambda x: prefijo + x if x else '')
    df['image_url_1'] = df['image_url_1'].apply(lambda x: prefijo + x if x else '')

    #se concatenan las columnas para crear una sola y se eliminan las anteriore
    separador = ';'
    df['productImageUrl'] = df['image_url'] + separador + df['image_url_1']
    del df["image_url"]
    del df["image_url_1"]

    #reemplaza las filas que solo contienen ";"
    df['productImageUrl'] = df['productImageUrl'].apply(lambda x: '' if x == ';' else x)

    #renombra las columnas
    df = df.rename(columns={"codigo":"sku"}, inplace=False)
    df = df.rename(columns={"descripcion":"name"}, inplace=False)
    df = df.rename(columns={"familia":"collection"}, inplace=False)      
    df = df.rename(columns={"marca":"brand"}, inplace=False)
    df = df.rename(columns={"precio":"price"}, inplace=False)
    df = df.rename(columns={"stock":"inventory"}, inplace=False)

    #hace el cambio de dolares a colones, multiplica por el IVA y un 20% de ganancia
    df['price'] = df['price'].astype(float)
    df['inventory'] = df['inventory'].astype(float)
    df['price'] = round((df['price'] * 1.13 * 1.25 * (tipoDeCambio() + 10.0)) / 1000.0, 2) * 1000.0
    
    #elimina los productos que tienen 0 de precio 
    df = df.loc[df['price'] != 0]
    df = df.loc[df['inventory'] != 0]
    df = df.loc[df['inventory'] != 1]
    df = df.loc[df['inventory'] != 2]

    #reemplaza los inventarios mayores a 30 por 30
    df.loc[df['inventory'] > 30, 'inventory'] = 30

    #crea las columnas nuevas 
    df["handleId"] = "handleId_" + df["sku"] 
    df["fieldType"] = "Product" 
    df["description"] = """Imágenes de referencia
    ¿Cómo comprar?
    1-Agrega al carrito en “COMPRAR”
    2-Registro: Completa tus datos y sigue los pasos
    3-Selecciona el método de entrega: """
    df["visible"] = "TRUE"
    df["discountMode"] = "PERCENT"
    df["discountValue"] = 0 
    
    listColumnasNuevasVacias = ["ri`bbon","surcharge","weight","cost","productOptionName1","productOptionType1","productOptionDescription1","productOptionName2","productOptionType2","productOptionDescription2","productOptionName3","productOptionType3","productOptionDescription3","productOptionName4","productOptionType4","productOptionDescription4","productOptionName5","productOptionType5","productOptionDescription5","productOptionName6","productOptionType6","productOptionDescription6","additionalInfoTitle1","additionalInfoDescription1","additionalInfoTitle2","additionalInfoDescription2","additionalInfoTitle3","additionalInfoDescription3","additionalInfoTitle4","additionalInfoDescription4","additionalInfoTitle5","additionalInfoDescription5","additionalInfoTitle6","additionalInfoDescription6","customTextField1","customTextCharLimit1","customTextMandatory1","customTextField2","customTextCharLimit2","customTextMandatory2"]

    for columna in listColumnasNuevasVacias:
        df[columna] = ""

    df = df[['handleId','fieldType','name','description','productImageUrl','collection','sku','ribbon','price','surcharge','visible','discountMode','discountValue','inventory','weight','cost','productOptionName1','productOptionType1','productOptionDescription1','productOptionName2','productOptionType2','productOptionDescription2','productOptionName3','productOptionType3','productOptionDescription3','productOptionName4','productOptionType4','productOptionDescription4','productOptionName5','productOptionType5','productOptionDescription5','productOptionName6','productOptionType6','productOptionDescription6','additionalInfoTitle1','additionalInfoDescription1','additionalInfoTitle2','additionalInfoDescription2','additionalInfoTitle3','additionalInfoDescription3','additionalInfoTitle4','additionalInfoDescription4','additionalInfoTitle5','additionalInfoDescription5','additionalInfoTitle6','additionalInfoDescription6','customTextField1','customTextCharLimit1','customTextMandatory1','customTextField2','customTextCharLimit2','customTextMandatory2','brand']]

    print("Guardando archivo de Excel...")
    df.to_csv("Inventario_EUROCOMP.csv",index=False, encoding='utf-8-sig')
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    print(csv)
    print("Archivo de Excel guardado exitosamente")

def main():
    responsedata = realizarsolicitudsoap()
    guardar(responsedata, "Inventario_EUROCOMP.xml")
    #actualizarDatosExcel()   
    transformar(responsedata)
    #exportarExcelACsv()

main()
