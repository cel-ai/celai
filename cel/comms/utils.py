import asyncio
import hashlib
import json
from loguru import logger as log

def get_invariant_hash(obj):
    """
    Returns an MD5 hash of a JSON-serialized copy of the input object, with the 'metadata' field removed.
    This hash can be used to check if two objects are equivalent, regardless of their metadata.
    """
    
    # Copiar el objeto para evitar modificar el original
    obj_copy = obj.to_dict()

    # Eliminar el campo 'metadata' del objeto copiado
    if 'metadata' in obj_copy:
        del obj_copy['metadata']

    # Serializar el objeto en formato JSON
    json_str = json.dumps(obj_copy, sort_keys=True)

    # Generar un hash MD5 del JSON serializado
    md5_hash = hashlib.md5(json_str.encode('utf-8')).hexdigest()

    return md5_hash


def async_run(coro, then=None):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            loop = None

        if loop and loop.is_running():
            log.debug('Async event loop already running. Adding coroutine to the event loop.')
            tsk = loop.create_task(coro)
            # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
            # Optionally, a callback function can be executed when the coroutine completes
            # tsk.add_done_callback(lambda t: print(f'Task done with result={t.result()}  << return val of main()'))
            tsk.add_done_callback(lambda t: then(t.result()))
            
        else:
            log.debug('Starting new event loop')
            result = asyncio.run(coro)
            
            
