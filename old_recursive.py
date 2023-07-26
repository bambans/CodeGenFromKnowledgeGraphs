from rdflib import Graph
from rdflib.query import Result
from ast import AST, Tuple, Call, ImportFrom
from classToToken import astToTokenList

pythonAST = Graph()
# pythonAST.parse(location = 'rdfs/PythonAbstractSyntax.rdf', format = 'xml')

digital_locker_lib = Graph()
digital_locker_lib.parse(location = 'rdfs/digitalLocker_libray.rdf', format = 'xml')

digital_locker_ref = Graph()
digital_locker_ref.parse(location = 'rdfs/digitalLockerRef.rdf', format = 'xml')

ASTlist = {}
"""
It is the default dictionary used in `astList` method. 
"""

codeString = ''
"""
This is the variable in which will be stored the code itself.
"""

fieldsFilter = {'kind', 'ctx'}
"""
A bunch of fields that should not be computed.
"""

def astList(node:AST = AST, list:dict = ASTlist):
    """
    This function maps all AST nodes into a dictionary in which we can get an object class inherit from <class 'ast'>.
    
    Ex.:
    - `ASTlist['AST'] = <class 'ast.AST'>`; 
    - `ASTlist['ExceptHandler'] = <class 'ast.ExceptHandler'>`.
    """
    list[node.__name__] = node
    subclasses = node.__subclasses__()
    for subclass in subclasses:
        astList(node = subclass)

def getAstObject(nodeName:str, ASTlist:dict = ASTlist) -> AST:
    if nodeName == 'NoneStmt':
        return ''
    else:
        return ASTlist[nodeName]

def RDFQuery(graph:Graph, query:str) -> Result:
    """
    It performes a `rdflib.query` in a `rdflib.graph` and returns a `rdflib.query.Result`.
    """
    prefixes = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX mpl2kdl: <http://ufs.br/ontologies/mpl2kdl#>
        PREFIX cdt: <http://w3id.org/lindt/custom_datatypes#ucum>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    """
    return graph.query(prefixes+query)

def query(type = "SELECT", subject = "?s", predicate = "?p", object = "?o") -> str:
    """
    This function receives these following arguments (type and RDF semantic triple - subject, predicate and object) and it returns a SPARQL query string:
    - `subject`: "?s" (default) or a given value;
    - `predicate`: "?p" (default) or a given value;
    - `object`: "?o" (default) or a given value.
    """
    return """
        """+type+""" ?s ?p ?o WHERE{
            """+subject+""" """+predicate+""" """+object+""" .
        }
    """

def tokenTranslator(astClassNode:AST, field:str = None, value:any = None):
    """
    This method receives an AST node and returns its python token version for that tokenizable nodes. It supports the following arguments:
    - `astClassNode:AST`: an AST node;
    - `alt:bool`: a boolean variable which makes possible to change what token string will be returned.
    """
    if field == None:
        return astToTokenList[astClassNode]
    else:
        return astToTokenList[astClassNode][field].format('' if value == None else value)

def GraphRecursive(graph:Graph = pythonAST, graphNode = None):
    """
    This function walks recursively on the given RDFS graph. For each graph node, its type is tested and, from searching on `ASTlist`, it becomes possible to performe a new query for this node by each node field (described by the AST).
    
    This function needs these following arguments:
    - `graphNode`: graph node for which will be performed its fields searching and the recursive subqueries;
    - `graph:Graph`: graph object in which will be performed all SPARQL queries.
    """
    try:
        for subject in RDFQuery(graph, query(subject = "mpl2kdl:" + graphNode.fragment, predicate="rdf:type")):
            print(astToTokenList[getAstObject(subject.o.fragment)]['tokenValue'], end="")
            fields = getAstObject(subject.o.fragment)._fields
            if len(fields) > 0:
                for field in fields:
                    if field in fieldsFilter:
                        continue
                    objects = RDFQuery(graph, query(subject = "mpl2kdl:" + graphNode.fragment, predicate = "mpl2kdl:_" + field))
                    if len(objects) > 0:
                        print(astToTokenList[getAstObject(subject.o.fragment)][field]['open'], end="")
                        for index, object in enumerate(objects):
                            # se houver mais de uma iteração, colocar as vírgulas
                            # print('\n<', subject.o.fragment, field, object.o, '>\n')
                            value = GraphRecursive(graph = graph, graphNode = object.o)
                            # print("!-{debug: ", value.__class__, value, '}-!')
                            
                            # observar o 'body' como marcador de bloco
                            print(value if value is not None else '', '', end="")

                            if (getAstObject(subject.o.fragment) is Tuple and index != len(objects)-1) or (getAstObject(subject.o.fragment) is ImportFrom and field == 'names' and len(objects) > 1 and index != len(objects)-1) or (getAstObject(subject.o.fragment) is Call and field == 'args' and index != len(objects)-1):
                                # Para as tuplas é mais fácil, mas no caso abaixo, tenho que estudar outra alternativa:
                                # getAstObject(subject.o.fragment) is alias and field == 'name' and len(objects) > 1 and index != len(objects)-1
                                print(', ', end='')
                        print(astToTokenList[getAstObject(subject.o.fragment)][field]['close'], end="")
                    else:
                        # resolver o caso do 'as' no ImportFrom
                        if field in fieldsFilter:
                            print(astToTokenList[getAstObject(subject.o.fragment)][field]['open'], end="")
                            print(astToTokenList[getAstObject(subject.o.fragment)][field]['close'], end="")
    except:
        # print('<-{',graphNode,'}->')
        if graphNode == 'None':
            # Aparente os termos que são da classe rdflib.term.literal possuem conversão implícita para tipos como 'string' e, sendo assim, é possível diferenciar None (NoneType) de 'None' (String)
            graphNode = None
            # Estou forçando a variável graphNone, quando 'None', recebe None (NoneType)
            return graphNode
        else:
            return graphNode

def ASTRecursive(node:AST = AST, level:int = 0, graph:Graph = pythonAST) -> bool:
    """
    In a recursive walking on AST, it performes `GraphRecursive()` for first leaf.
    """
    subclasses = node.__subclasses__()
    for subclass in subclasses:
        if ASTRecursive(node = subclass, level = level+1, graph = graph) == True:
            return True
        else:
            return False
    if level > 1:
        try:
            for subject in RDFQuery(graph, query(predicate = "rdf:type", object = "mpl2kdl:" + node.__name__)):
                for field in node._fields:
                    for object in RDFQuery(graph, query(subject = "mpl2kdl:" + subject.s.fragment, predicate = "mpl2kdl:_" + field)):
                        GraphRecursive(graph = graph, graphNode = object.o)
            return True
        except:
            return False

def Recursive(node:AST = AST, graph:Graph = pythonAST) -> bool:
    """
    This function only dispatch `ASTRecursive`.
    """
    return ASTRecursive(node = node, graph = graph)

if __name__ == "__main__":
    astList()

    print("-------------------------- DIGITAL LOCKER REF -------------------------")
    Recursive(graph = digital_locker_ref)
    print("-----------------------------------------------------------------------")

    # print()

    # print("-------------------------- DIGITAL LOCKER LIB -------------------------")
    # Recursive(graph = digital_locker_lib)
    # print("-----------------------------------------------------------------------")
