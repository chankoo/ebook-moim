from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch('http://127.0.0.1:9200/')
es.info()

def make_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))

idx_name = 'test'
make_index(es, idx_name)

ds = [
    {'test_name': 'hihi', 'number':124},
    {'test_name': 'hihi2', 'number':11324},
    {'test_name': 'hello', 'number':4545},
]
for d in ds:
    es.index(index=idx_name, doc_type='string', body=d)

es.indices.refresh(index=idx_name)

es.search(
    index=idx_name, 
    body={
        'from':0,
        'size':10,
        'query':{
            'match':{
                'test':'hihi'
            }
        }
    })