import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables from .env.development
load_dotenv('.env.development')

# MongoDB connection
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['cmvalparaisoDas']
collection = db['opinionSaludValparaiso']

#testing
def reset_all_targets_to_3():
    collection.update_many({}, {'$set': {'target': 3}})

def get_documents():
    return collection.find({'target': 3})

def update_target(document_id, new_target):
    collection.update_one({'_id': document_id}, {'$set': {'target': new_target}})

def get_total_documents():
    return collection.count_documents({})

def get_uncategorized_documents():
    return collection.count_documents({'target': 3})



def search_documents(query, column='All'):
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

    # Function to try converting query to integer
    def try_int(val):
        try:
            return int(val)
        except ValueError:
            return val

    db_column = column_mapping.get(column, column)
    if db_column in ['edad', 'satisfaccion', 'recomendacion', 'target']:
        query = try_int(query)

    if column == 'All':
        regex_query = {"$regex": f"{query}", "$options": 'i'}
        int_query = try_int(query)

        # Fields to check with regex
        regex_fields = ["genero", "cesfam", "frecuencia", "razon"]
        regex_or_query = [{field: regex_query} for field in regex_fields]

        # Fields to check as integers or ObjectId
        int_fields = ["edad", "satisfaccion", "recomendacion", "target"]
        int_or_query = [{field: int_query} for field in int_fields if isinstance(int_query, int)]

        # Combining all queries
        or_query = regex_or_query + int_or_query

        results = collection.find({"$or": or_query})

    elif column == 'ID':
        regex_query = {"$regex": f"{query}", "$options": 'i'}
        results = collection.find({db_column: regex_query})
        
    elif column == 'Fecha':
        if query:
            results = collection.find({db_column: query})
        else:
            # If preprocessing failed, return an empty list
            return []
        
        
    else:
        if isinstance(query, int):
            results = collection.find({db_column: query})
        else:
            regex_query = {"$regex": f"{query}", "$options": 'i'}
            results = collection.find({db_column: regex_query})

    return list(results)



def get_all_documents():
    return collection.find({})


log_collection = db['log']

def log_update(num_updated):
    entry = {
        'date': datetime.now(),
        'num_updated': num_updated
    }
    log_collection.insert_one(entry)

def get_last_log():
    return log_collection.find_one(sort=[('date', -1)])
