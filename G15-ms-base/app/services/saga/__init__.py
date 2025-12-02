def __init__(self, acciones, datos):
        self.acciones = acciones
        self.datos = datos.copy()
        
        
        self.ids_generados = [] 
        
        self.respuesta = {
            "mensaje": "OK",
            "codigo_estado": 201,
            "datos": {"mensaje": "Operación realizada con éxito"},
        }