from models.dynamic_module import Module, ModuleField
from extensions import db
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError

class ModuleService:
    @staticmethod
    def create_module(name: str, module_type: str, description: str = None, parent_id: int = None) -> Optional[Module]:
        try:
            module = Module(
                name=name,
                description=description,
                module_type=module_type,
                parent_id=parent_id
            )
            db.session.add(module)
            db.session.commit()
            return module
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @staticmethod
    def get_module_by_id(module_id: int) -> Optional[Module]:
        return Module.query.get(module_id)

    @staticmethod
    def get_modules_by_type(module_type: str) -> List[Module]:
        return Module.query.filter_by(module_type=module_type, is_active=True).all()

    @staticmethod
    def get_root_modules() -> List[Module]:
        return Module.query.filter_by(parent_id=None, is_active=True).all()

    @staticmethod
    def add_field_to_module(
        module_id: int,
        name: str,
        label: str,
        field_type: str,
        required: bool = False,
        options: Dict = None,
        validation_rules: Dict = None,
        order: int = 0
    ) -> Optional[ModuleField]:
        try:
            field = ModuleField(
                module_id=module_id,
                name=name,
                label=label,
                field_type=field_type,
                required=required,
                options=options,
                validation_rules=validation_rules,
                order=order
            )
            db.session.add(field)
            db.session.commit()
            return field
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @staticmethod
    def update_module(module_id: int, data: Dict[str, Any]) -> Optional[Module]:
        try:
            module = Module.query.get(module_id)
            if not module:
                return None
            
            for key, value in data.items():
                if hasattr(module, key):
                    setattr(module, key, value)
            
            db.session.commit()
            return module
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @staticmethod
    def delete_module(module_id: int) -> bool:
        try:
            module = Module.query.get(module_id)
            if not module:
                return False
            
            # Instead of hard delete, we'll soft delete by setting is_active to False
            module.is_active = False
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False
