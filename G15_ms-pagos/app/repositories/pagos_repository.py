from typing import List
from app import db
from app.models import Pagos
from .repository import Repository_delete, Repository_get, Repository_save

class PagosRepository(Repository_save, Repository_get, Repository_delete):
    def save(self, entity: Pagos) -> Pagos:
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all(self) -> List[Pagos]:
        return Pagos.query.all()

    def get_by_id(self, id: int) -> Pagos:
        return Pagos.query.get(id)

    def delete(self, id: int) -> bool:
        try:
            pago = self.get_by_id(id)
            if pago:
                db.session.delete(pago)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
    def update(self, id: int, new_data: Pagos) -> Pagos:
        pago = self.get_by_id(id)
        if not pago:
            return None
        
        try:
            for key, value in new_data.__dict__.items():
                if value is not None:
                    setattr(pago, key, value)
            
            db.session.commit()
            return pago
        except Exception as e:
            db.session.rollback()
            raise e
