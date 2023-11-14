import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables
# Cargar variables de entorno
# Load environment variables
if getattr(sys, 'frozen', False):
    # If the application is running as a PyInstaller bundle
    app_dir = sys._MEIPASS
else:
    # If the application is running in a development environment
    app_dir = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(app_dir, '.env.development')
load_dotenv(dotenv_path)

# Establish MongoDB connection
# Establecer conexión MongoDB
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['cmvalparaisoDas']
collection = db['opinionSaludValparaiso']
log_collection = db['log']

def reset_all_targets_to_3():
    """ Reset all document targets to 3 in the collection. """
    """ Restablecer todos los objetivos de los documentos a 3 en la colección. """
    collection.update_many({}, {'$set': {'target': 3}})

def get_documents():
    """ Retrieve documents with target 3 from the collection. """
    """ Recuperar documentos con objetivo 3 de la colección. """
    return list(collection.find({'target': 3}))

def update_target(document_id, new_target):
    """ Update the target of a specific document. """
    """ Actualizar el objetivo de un documento específico. """
    collection.update_one({'_id': document_id}, {'$set': {'target': new_target}})

def get_total_documents():
    """ Get the total count of documents in the collection. """
    """ Obtener el conteo total de documentos en la colección. """
    return collection.count_documents({})

def get_uncategorized_documents():
    """ Get the count of uncategorized documents in the collection. """
    """ Obtener el conteo de documentos sin categorizar en la colección. """
    return collection.count_documents({'target': 3})

def search_documents(query, column='All'):
    """
    Search for documents in the collection based on a query and a specific column.
    Busca documentos en la colección basándose en una consulta y una columna específica.
    """
    # Mapping of front-end column names to database field names
    # Mapeo de nombres de columnas de front-end a nombres de campos de la base de datos
    column_mapping = {
        'ID': '_id',
        'Edad': 'edad',
        'Género': 'genero',
        'Centro de Salud': 'cesfam',
        'Frecuencia': 'frecuencia',
        'Satisfacción': 'satisfaccion',
        'Recomendación': 'recomendacion',
        'Comentario Abierto': 'razon',
        'Fecha': 'date',
        'Etiqueta': 'target'
    }

    db_column = column_mapping.get(column, column)

    # If column is one of 'edad', 'satisfaccion', 'recomendacion', 'target', try converting the query to an integer
    # Si la columna es 'edad', 'satisfaccion', 'recomendacion', 'target', intenta convertir la consulta en un entero
    if db_column in ['edad', 'satisfaccion', 'recomendacion', 'target']:
        query = try_int(query)

    # If searching across all columns
    # Si se busca en todas las columnas
    if column == 'All':
        regex_query = {"$regex": f"{query}", "$options": 'i'}
        int_query = try_int(query)

        # Fields to check with regex
        # Campos para verificar con regex
        regex_fields = ["genero", "cesfam", "frecuencia", "razon"]
        regex_or_query = [{field: regex_query} for field in regex_fields]

        # Fields to check as integers or ObjectId
        # Campos para verificar como enteros u ObjectId
        int_fields = ["edad", "satisfaccion", "recomendacion", "target"]
        int_or_query = [{field: int_query} for field in int_fields if isinstance(int_query, int)]

        # Combining all queries
        # Combinando todas las consultas
        or_query = regex_or_query + int_or_query

        results = collection.find({"$or": or_query})

    # Special handling for 'ID' column
    # Manejo especial para la columna 'ID'
    elif column == 'ID':
        regex_query = {"$regex": f"{query}", "$options": 'i'}
        results = collection.find({db_column: regex_query})
        
    # Special handling for 'Fecha' column
    # Manejo especial para la columna 'Fecha'
    elif column == 'Fecha':
        if query:
            results = collection.find({db_column: query})
        else:
            # If preprocessing failed, return an empty list
            # Si el preprocesamiento falla, devuelve una lista vacía
            return []
        
    else:
        # Searching in other columns
        # Buscando en otras columnas
        if isinstance(query, int):
            results = collection.find({db_column: query})
        else:
            regex_query = {"$regex": f"{query}", "$options": 'i'}
            results = collection.find({db_column: regex_query})

    return list(results)

def try_int(val):
    """ Try converting a value to integer, or return original value if conversion fails. """
    """ Intentar convertir un valor a entero, o devolver el valor original si la conversión falla. """
    try:
        return int(val)
    except ValueError:
        return val

def search_all_columns(query):
    """ Search all columns for a given query. """
    regex_query = {"$regex": f"{query}", "$options": 'i'}
    int_query = try_int(query)

    # Constructing query for various fields
    regex_fields = ["genero", "cesfam", "frecuencia", "razon"]
    int_fields = ["edad", "satisfaccion", "recomendacion", "target"]

    regex_or_query = [{field: regex_query} for field in regex_fields]
    int_or_query = [{field: int_query} for field in int_fields if isinstance(int_query, int)]

    or_query = regex_or_query + int_or_query
    return list(collection.find({"$or": or_query}))

def search_specific_column(query, db_column):
    """ Search a specific column with a query. """
    regex_query = {"$regex": f"{query}", "$options": 'i'}
    return list(collection.find({db_column: regex_query}))

def search_date_column(query, db_column):
    """ Search the date column for a specific query. """
    if query:
        return list(collection.find({db_column: query}))
    return []

def search_other_columns(query, db_column):
    """ Search other columns based on the type of the query. """
    if isinstance(query, int):
        return list(collection.find({db_column: query}))
    regex_query = {"$regex": f"{query}", "$options": 'i'}
    return list(collection.find({db_column: regex_query}))

def get_all_documents():
    """ Retrieve all documents from the collection. """
    """ Recuperar todos los documentos de la colección. """
    return list(collection.find({}))

def log_update(num_updated, average_confidence):
    """ Log an update action with the number of updated documents and their average confidence. """
    """ Registrar una acción de actualización con el número de documentos actualizados y su confianza promedio. """
    entry = {
        'date': datetime.now(), 
        'num_updated': num_updated,
        'average_confidence': average_confidence  # Include the average confidence in the log
    }
    log_collection.insert_one(entry)

def get_last_log():
    """ Get the most recent log entry. """
    """ Obtener la entrada de registro más reciente. """
    return log_collection.find_one(sort=[('date', -1)])