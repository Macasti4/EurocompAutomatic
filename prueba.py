import requests
import pandas as pd
import xml.etree.ElementTree as ET
def transformar(source):

	# Parsear el archivo XML
	tree = ET.parse(source)
	root = tree.getroot()

	# Crear una lista para almacenar los datos
	data = []

	# Recorrer los elementos XML y extraer los datos
	for child in root.iter('row'):
	    codigo = child.find('codigo').text
	    descripcion = child.find('descripcion').text
	    equivalencia = child.find('equivalencia').text
	    marca = child.find('marca').text
	    familia = child.find('familia').text
	    familia_id = child.find('familia_id').text
	    stock = child.find('stock').text
	    image_url = child.find('image_url').text
	    medida = child.find('medida').text
	    peso = child.find('peso').text
	    privacidad = child.find('privacidad').text
	    precio = child.find('precio').text

	    # Agregar los datos a la lista
	    data.append({
	        'codigo': codigo,
	        'descripcion': descripcion,
	        'equivalencia': equivalencia,
	        'marca': marca,
	        'familia': familia,
	        'familia_id': familia_id,
	        'stock': stock,
	        'image_url': image_url,
	        'medida': medida,
	        'peso': peso,
	        'privacidad': privacidad,
	        'precio': precio
	    })

	# Crear un DataFrame de pandas a partir de la lista de datos
	df = pd.DataFrame(data)

	# Realizar las transformaciones necesarias en el DataFrame
	df['familia_id'] = df['familia_id'].astype(int)
	df['stock'] = df['stock'].astype(int)
	df['equivalencia'] = df['equivalencia'].astype(int)
	df['precio'] = df['precio'].astype(float)

	# Eliminar columnas no deseadas
	df = df.drop(columns=['modelo', 'item_grupo_1', 'item_grupo_2', 'item_grupo_3', 'image_url_2', 'image_url_3', 'image_url_4', 'image_url_5', 'caracteristicas', 'privacidad', 'peso', 'itemref_1', 'itemref_2', 'itemref_3', 'itemref_4', 'itemref_5', 'itemref_6', 'itemref_7', 'itemref_8', 'itemref_9', 'itemref_10', 'itemref_11', 'itemref_12', 'itemref_13', 'itemref_14'])

	# Mostrar el DataFrame resultante
	print(df)



def realizarSolicitudSOAP():
    url = "https://www.eurocompcr.com/webservice.php?wsdl"
    usuario = 1550
    contraseña = "15502022"
    bid = 1

    xmlData = '''<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:server">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:wsc_request_bodega_all_items>
                    <ws_pid>{}</ws_pid>
                    <ws_passwd>{}</ws_passwd>
                    <bid>{}</bid>
                </urn:wsc_request_bodega_all_items>
            </soapenv:Body>
        </soapenv:Envelope>'''.format(usuario, contraseña, bid)

    headers = {"Content-Type": "text/xml"}
    response = requests.post(url, data=xmlData, headers=headers)

    responseCode = response.status_code
    responseData = response.text

    if responseCode == 200:
        #print(responseData)
        guardar(responseData)
        transformar("Inventario_EUROCOMP.xml");
    else:
        print("Error en la solicitud SOAP. Código de respuesta:", responseCode)

def guardar(responseData):
	with open("Inventario_EUROCOMP.xml", "w") as archivo:
		archivo.write(responseData)
		print("Archivos guardados exitosamente")

# Llamada a la función principal
realizarSolicitudSOAP()
