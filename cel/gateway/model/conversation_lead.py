from abc import ABC
import inspect
import json

import shortuuid
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_peer import ConversationPeer, ConversationPeerEncoder


class ConversationLead(ABC):

    def __init__(self, 
                 metadata : dict = None, 
                 connector_name: str = None,
                 conversation_from: ConversationPeer = None,
                 connector: BaseConnector = None):
        self.metadata = metadata
        self.conversation_from = conversation_from
        self.tmp_id = shortuuid.uuid()
        self.connector = connector
        self.connector_name = connector.name() if connector else connector_name or None

    def get_session_id(self):
        """ This method should be overriden in the child class """
        return self.tmp_id

    def to_dict(self):
        return {
            'connector_name': self.connector_name,
            'metadata': self.metadata,
            'conversation_from': self.conversation_from.to_dict() if self.conversation_from else None
        }

    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, lead_dict):
        # connector_name=lead_dict.get("connector_name")
        return ConversationLead(
            metadata=lead_dict.get("metadata", {}),
            conversation_from=ConversationPeer.from_dict(lead_dict.get("conversation_from", {}) or {})
        )
        
    def __str__(self):
        return f"ConversationLead: {self.connector_name}"
    

    @staticmethod
    def serialize(lead: 'ConversationLead') -> str:
        """ Serialize a ConversationLead object to JSON. If you want to take this
        this object outside the process, you can use this method to serialize it
        It allows you to serialize the object and then deserialize it in another process"""
        
        # Obtener el nombre de la clase
        class_name = f"{lead.__class__.__module__}.{lead.__class__.__name__}"
        # Obtener los atributos del objeto
        attributes = {k: v for k, v in lead.__dict__.items()}
        #  remove connector from attributes
        attributes.pop('connector', None)
        # Crear un diccionario con el nombre de la clase y los atributos
        data = {
            'class_name': class_name,
            'attributes': attributes
        }
        # Serializar a JSON
        return json.dumps(data, cls=ConversationPeerEncoder)
    
    
    @staticmethod
    def deserialize(serialized_data: str) -> 'ConversationLead':
        """ Deserialize a JSON string to a ConversationLead object. 
        and re-attach the source connector to the object attribute connector."""
        
        # Deserializar el JSON
        data = json.loads(serialized_data)
        class_name = data['class_name']
        attributes = data['attributes']
        
        import importlib

        def dynamic_class_instantiation(class_path: str):
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls
        
        def get_connector_instance(connector_name: str):
            if connector_name:
                return BaseConnector.get_connector_by_name(connector_name)
            return None   
        
        # Obtener la clase a partir del nombre
        cls = dynamic_class_instantiation(class_name)
        
        # Inspeccionar el constructor de la clase
        constructor_params = inspect.signature(cls).parameters
        
        # Filtrar los atributos que coinciden con los parámetros del constructor
        init_args = {k: attributes[k] for k in constructor_params if k in attributes}
        
        # Crear una instancia de la clase con los argumentos
        instance = cls(**init_args)
        
        # set attributes
        for k, v in attributes.items():
            if k not in constructor_params:
                setattr(instance, k, v)
        
        # set connector
        instance.connector = get_connector_instance(instance.connector_name)
        
        return instance