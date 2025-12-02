
class SagaAction:
    def __init__(self, execute_fn, compensate_fn):
        
        self.execute_fn = execute_fn
        self.compensate_fn = compensate_fn
        self.url = None  

    def ejecutar(self, data):
        
        url, response_data = self.execute_fn(data)
        self.url = url
        return url, response_data

    def compensar(self, id_recurso):
        
        return self.compensate_fn(id_recurso)