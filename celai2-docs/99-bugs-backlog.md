# 99 — Bugs y backlog

Bugs concretos encontrados durante el análisis. **Independiente del rediseño**: casi todos se
pueden arreglar sobre `main` hoy.

Severidad: 🔴 rompe en producción · 🟡 comportamiento incorrecto · ⚪ limpieza

---

## ✅ 🔴 Alta — resueltos (septiembre 2026)

Los diez ítems de severidad alta están arreglados sobre `main`, cada uno con test de regresión
que falla contra el código previo.

| # | Dónde | Qué pasaba | Cómo se resolvió |
|---|---|---|---|
| 1 | `cel/gateway/http_callbacks.py` | `callback_id = id(handler)`. Colisiona si el mismo handler se usa para dos leads; el GC puede reciclar el `id()` y mapear un token válido a otro handler. | El id lo genera `shortuuid.uuid()` al crear el callback. `remove_callback(handler)` ahora cancela **todos** los links de ese handler y se agregó `remove_callback_by_id()`. Sigue pendiente el registro persistente (ver [S6](03-estrategias/S6-callbacks-y-eventos.md)): esto no sobrevive a restart ni a multi-worker. |
| 1b | `cel/gateway/http_callbacks.py` | **`single_use` no se cumplía.** El `return res` temprano estaba antes del `pop(handler_id)`, así que un link de pago o firma quedaba reusable dentro de su TTL. El mismo camino se salteaba el `RedirectResponse`. | El callback single-use se **reclama antes** de ejecutar el handler (`dict.pop` es atómico, así que dos requests concurrentes con el mismo token no pueden ejecutarlo dos veces), y el `RedirectResponse` se evalúa antes de devolver `res`. |
| 2 | `cel/connectors/cli/cli_connector.py` | `name()` devolvía `"telegram"`, rompiendo la unicidad de `ConnectorsRegistry`. | Devuelve `"cli"`. |
| 3 | `cel/assistants/macaw/macaw_nlp.py` | `llm_with_tools.invoke(...)` síncrono dentro de una corrutina: bloqueaba el event loop del gateway en cada tool call. | `await llm_with_tools.ainvoke(...)`. |
| 4 | `cel/assistants/macaw/macaw_nlp.py` | Agotar `core_max_function_calls_in_message` con un tool call pendiente no emitía ningún chunk: el usuario recibía silencio, y el `AIMessage` con `tool_calls` sin `ToolMessage` envenenaba el historial del turno siguiente. | Al salir del loop sin haber emitido nada (salvo `cancel_ai`, donde el silencio es intencional) se descarta el mensaje colgado y se pide una respuesta final al LLM **sin tools**. Si aun así no hay texto, se manda `TOOL_LOOP_FALLBACK_MESSAGE`. |
| 5 | `cel/assistants/macaw/macaw_nlp.py` | En el `except` general, `append_to_history(ctx.lead, response)` con `response` posiblemente `None`. | Sólo se persiste si `response is not None`, y un fallo al persistir se loguea en vez de tapar la excepción original. |
| 6 | `cel/stores/state/base_state_provider.py` | El ABC declaraba métodos sync y las implementaciones eran async. | El ABC declara `async def` (menos `get_key`, que es sync en todas las implementaciones) y se alineó la firma de `clear_all_stores`. |
| 7 | `cel/stores/state/state_redis_provider.py` | Usaba el cliente síncrono de `redis` dentro de métodos `async def`. | Una url de conexión ahora construye un `redis.asyncio.Redis`. Un cliente síncrono pasado a mano sigue funcionando, pero sus comandos van a un worker thread y se loguea un warning. |
| 8 | `pyproject.toml` | `fastapi`, `uvicorn` y `pydantic` no estaban declaradas; llegaban transitivamente vía `chromadb`. | Declaradas, junto con `cachetools` (que tenía el mismo problema: lo importa `cel/stores/common/`) y `httpx` en dev. **Confirmado en la práctica**: un `pip install` limpio hoy instala `chromadb` sin `fastapi`, y el repo no importaba. |
| 8b | `cel/gateway/message_gateway.py` | **Bypass de autenticación.** El middleware hacía `await call_next(request)` y después seteaba `response.status_code = 401`: la request protegida ya se había ejecutado. En la rama de header ausente ni siquiera había `return`, así que la ejecutaba dos veces y devolvía 200. | Devuelve `JSONResponse(status_code=401)` sin llamar a `call_next`. De paso dejó de loguear la API key inválida y los headers completos. |

## 🟡 Media

| # | Dónde | Qué pasa |
|---|---|---|
| 9 | `cel/assistants/context.py:141-148` | `cancel_ai_response` **definido dos veces**: método async y luego `@staticmethod`. La segunda pisa a la primera. La versión async es inalcanzable. |
| 10 | `cel/assistants/context.py` (`response_text`) | Pasa `text=`, `is_private=`, `blend=` a `EventResponse`, que solo acepta `disable_ai_response`. **TypeError** al llamarse. Los ejemplos la usan. |
| 11 | `cel/assistants/macaw/macaw_assistant.py:211-213` | Comando `set`: `self._state_store.get_store(...)` y `.set_store(...)` **sin `await`**. Devuelve corrutinas; la corrutina de escritura nunca se ejecuta. Mismo bug en `agentic_router.py:286-288`; `logic_router.py` lo hace bien. |
| 12 | `cel/gateway/message_gateway.py:266-270` | Los middlewares callable (la mayoría del repo) **se saltean en el dispatch de salida**. Solo se invocan los `BaseMiddleware`. |
| 13 | `cel/gateway/message_gateway.py` (`__startup`) | `asyncio.create_task(middleware.startup(...))` sin await: errores tragados y el gateway atiende antes de que los middlewares estén listos. |
| 15 | `cel/assistants/function_context.py` | `validate_params()` está implementada **y testeada**, y `call_function` nunca la llama. Los argumentos de las tools no se validan nunca. |
| 16 | `cel/rag/stores/chroma/chroma_store.py` | `upsert()` ignora el `vector` que recibe y pasa `documents=text` (string donde va una lista). |
| 17 | `cel/rag/providers/enhanced_rag.py` | `QueryRefiner` chequea `isinstance(response, SystemMessage)` después de `llm.invoke()`, que devuelve `AIMessage`. La rama de query mejorada **nunca se ejecuta**. |
| 18 | `cel/rag/providers/enhanced_rag.py` | `EnhancedRetriever.search()` recibe `history` y `state` y los ignora. |
| 19 | `cel/middlewares/moderation/openai_mod_endpoint.py` | `self.client.moderations.create()` es la llamada **síncrona** del SDK, dentro de un middleware async. |
| 20 | `cel/middlewares/geodecoding.py` | Devuelve `False` cuando está deshabilitado, lo que **bloquea todos los mensajes** en vez de dejarlos pasar. |
| 21 | `cel/assistants/base_assistant.py:79-88` | Un solo handler por nombre de evento: el segundo `@ast.event('message')` pisa al primero, en silencio. |
| 22 | `cel/gateway/message_gateway.py` + routers | Con router, el evento `message` se dispara dos veces (una en el router, otra en el assistant elegido). |
| 23 | `cel/assistants/router/agentic_router.py` | El comando `/prompt` referencia `self.prompt`, que el router no tiene. |
| 24 | `examples/4_events/assistant.py:92` | `ctx.send_text_message("pong")` **sin `await`**. El ejemplo no funciona. |
| 25 | `cel/connectors/whatsapp/whatsapp_connector.py` | `send_document_message` usa el `pywa.WhatsApp.send_document()` síncrono dentro de un método async. Además trae `pywa` como dependencia entera solo para eso, cuando el resto del archivo usa `aiohttp` directo. |
| 25b | `cel/connectors/whatsapp/whatsapp_connector.py:403-412` | `send_typing_action` loguea `"Whatsapp typing action not currently supported by Cloud API"` y no hace nada — pero `__mark_as_read` (línea ~198) **ya manda** `"typing_indicator": {"type": "text"}`. El typing sí está soportado y se está enviando desde el lugar equivocado, atado a marcar como leído. |
| 25c | `cel/connectors/whatsapp/whatsapp_connector.py` | Límites de la plataforma hardcodeados y repetidos: truncado a 20 chars de opciones y a 3 botones / 10 filas, con `log.critical` cuando se pasa. Tiene que ser `ChannelCapabilities` + degradación ([S5](03-estrategias/S5-channels.md)). |
| 26 | `cel/assistants/macaw/macaw_nlp.py:126` | Le pasa una lista de `BaseMessage` de LangChain a `rag_retriever.search()`, que espera `list[ContextMessage]`. Funciona por accidente porque solo se lee `.content`. |
| 44 | `cel/assistants/macaw/macaw_nlp.py` (`blend_message`) | `res = llm.invoke(messages)` síncrono dentro de una corrutina. Es el mismo bug que el 3, en otra función del mismo archivo. Debería ser `ainvoke`. |
| 45 | `pyproject.toml` | Rangos de versión sin techo (`langchain = ">=0.2.0"`, `deepgram-sdk = ">=3.2.7"`). El `poetry.lock` protege a CI, pero un `pip install celai` desde PyPI resuelve langchain 1.x y deepgram 5.x, y el repo **no importa** (`langchain.load` y `PrerecordedOptions` ya no existen). Hay que poner cotas superiores. |

## ⚪ Limpieza

| # | Dónde | Qué |
|---|---|---|
| 27 | `cel/assistants/macaw/macaw_test_chat_model.py` | Archivo scratch entero. Crea un `llm` que no se usa. Borrar. |
| 28 | `cel/assistants/macaw/macaw_nlp.py:7,16-17` | Imports sin usar: `ChatOpenRouter`, `message_to_dict`, `messages_from_dict`. |
| 29 | `cel/assistants/macaw/macaw_nlp.py:202-229` | 28 líneas de validación de historial comentadas. Decidir: revivir o borrar. |
| 30 | `cel/gateway/__init__.py`, `cel/gateway/model/__init__.py` | Barrels comentados. Descomentar (ver [S1](03-estrategias/S1-api-surface-e-imports.md)). |
| 31 | `cel/assistants/common.py:23-31` | `EventResponse` con la mayoría de los campos comentados. |
| 32 | `cel/assistants/function_response.py` | `request_mode` y `callback` definidos y nunca consumidos. |
| 33 | Varios | `@dataclass class X(ABC)` sin métodos abstractos: `Param`, `FunctionDefinition`, `EventResponse`, `VectorRegister`, `Slice`, `CallbackEntry`, `HttpCallbackProvider`. El `ABC` no aporta nada. |
| 34 | `cel/assistants/base_assistant.py:18-23` | `Events.START`, `IMAGE`, `AUDIO`, `END` declarados y nunca despachados. |
| 35 | `cel/assistants/base_assistant.py` | `@ast.timeout` registra handlers que nunca se disparan. No hay scheduler. |
| 36 | `cel/gateway/message_gateway.py` | `StreamMode.WORD` declarado, sin implementar. |
| 37 | `cel/connectors/cli/cli_connector.py` | Los logs dicen "telegram". |
| 38 | `cel/rag/providers/markdown_rag.py` | `ChromaStore` con `chromadb.Client()` en proceso: no persiste entre reinicios. Está como default. |
| 39 | `pyproject.toml` | `langchain-chroma` declarada y no importada en ningún archivo. |
| 40 | `tests/rag_stores/` | El archivo de test de Chroma está mal nombrado: testea embeddings, no el store. |
| 41 | `cel/assistants/macaw/macaw_assistant.py:15` | Import `loads` sin usar. |
| 42 | `cel/assistants/macaw/macaw_history_adapter.py` | `close_conversation` es un `NotImplementedError`. |
| 43 | Varios | Mutable default `state: dict = {}` en `RAGRetriever.search`, `PromptTemplate.__init__`, `BaseAssistant.new_message`. |

---

## Orden sugerido

1. ~~**🔴 8b, 1b** — los dos de seguridad.~~ ✅
2. ~~**🔴 1, 2, 8** — bugs de producción con arreglo trivial.~~ ✅
3. **🟡 19, 25, 44** — los bloqueos del event loop que quedan. Cambiar a las variantes async del SDK.
4. ~~**🔴 3, 7** — bloqueos del event loop.~~ ✅ · ~~**🔴 4, 5, 6** — agent loop y contratos de stores.~~ ✅
5. **🟡 9, 10, 11, 24** — cosas que hacen que los ejemplos publicados no funcionen.
6. **🟡 45** — cotas superiores en las dependencias, antes del próximo release a PyPI.
7. El resto, junto con la fase correspondiente del [roadmap](04-roadmap.md).

---

## Nota de verificación

Los bugs 1, 2, 8b, 9, 10, 11, 14, 17, 20, 24 fueron confirmados leyendo el código directamente
durante el análisis inicial. Los bugs **1b, 12, 25, 25b, 25c** fueron confirmados leyendo
`http_callbacks.py`, `message_gateway.py` y `whatsapp_connector.py` durante la revisión de
septiembre 2026. El resto proviene del relevamiento automatizado y conviene revalidarlos antes de
abrir issues.

Los diez ítems 🔴 se arreglaron en septiembre 2026. Cada uno quedó cubierto por tests que fallan
contra el código previo (verificado con `git stash`):

- `tests/gateway/http_callbacks_test.py` — bugs 1 y 1b.
- `tests/gateway/message_gateway_auth_test.py` — bug 8b.
- `tests/connectors/connector_names_test.py` — bug 2.
- `tests/assistants/macaw/macaw_tool_loop_test.py` — bugs 3 y 4.
- `tests/stores/state/base_state_provider_test.py` — bug 6.
- `tests/stores/state/state_redis_provider_test.py` — bug 7.

Los bugs 44 y 45 salieron de esa misma tanda: 44 es el gemelo del 3 en `blend_message`, y 45 se
descubrió al instalar el proyecto desde cero sin el lock.
