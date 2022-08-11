# adaptação do código escrito pelo Prof. Dr. Fábio Nakano em 'grafico4.py'

# dependências (instalados via pip3): rdflib, csv, plotly, sparqlwrapper
# execução: 'python3 grafico.py'

debug = False # se 'True', mostra diversos dados de forma detalhada

import rdflib
import csv
from SPARQLWrapper import SPARQLWrapper, CSV
import plotly.express as px
import plotly.graph_objects as go

sparql = SPARQLWrapper('http://ip-50-62-81-50.ip.secureserver.net:8890/sparql')

fig = go.Figure()

numSensors = 10
queryResLimit = 60
numSensorsRange = range(1, numSensors+1) # o final do range não é inclusivo, por isso o '+1'

x = list(list() for i in numSensorsRange)
y = list(list() for i in numSensorsRange)

def queryBase(roomNumber, resLimit):
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX cdt: <http://w3id.org/lindt/custom_datatypes#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    SELECT ?s ?o ?t
    WHERE {
        ?s sosa:observedProperty <http://each.usp.br/SalaTeste"""+str(roomNumber)+"""#temperature>.
        ?s sosa:hasSimpleResult ?o.
        ?s sosa:resultTime ?t.
    }
    ORDER BY DESC(?t) LIMIT """+str(resLimit)+"""
    """

def conversivel(a):
    try:
        firstWord = a.split()[0]
        num = float(firstWord)
        return True
    except ValueError:
        return False

def converter(a):
    try:
        firstWord = a.split()[0]
        num = float(firstWord)

        if debug:
            print("firstWord["+str(firstWord)+"] >>>> num["+str(num)+"]")

        return num
    except ValueError:
        print("Não deveria falhar, pois deve ser usado depois de testar se é conversível.")
        return math.nan

for i in numSensorsRange:
    print('Resquesting data from sensor:'+str(i))

    query = queryBase(i, queryResLimit)
    sparql.setQuery(query)

    if debug:
        print(query)

    sparql.setReturnFormat(CSV)

    qres = sparql.query().convert().decode('u8')

    print("Success!")

    if debug:
        print(qres)

    lines = qres.splitlines()

    reader = csv.reader(lines)

    for row in reader:
        if(conversivel(row[1])):
            conv = converter(row[1])
            y[i-1].append(conv)
            x[i-1].append(row[2])

            if debug:
                print('conv: '+str(conv))
                print('row2 '+str(row[2]))
                print('arrayOfConvs '+str(y[i-1]))
                print('arrayOfRow2s '+str(x[i-1]))

    fig.add_trace(go.Scatter(x = x[i-1], y = y[i-1], name = 'sala'+str(i)))

fig.show()
