Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "HumanMessage"], "kwargs": {"content": "Me muestras la historia de Brenda Hernandez", "type": "human"}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "AIMessageChunk"], "kwargs": {"content": "", "additional_kwargs": {"tool_calls": [{"index": 0, "id": "call_gIGVj68mArzT534qGxmL7bVg", "function": {"arguments": "{\"apellido\":\"Hernandez\",\"nombre\":\"Brenda\"}", "name": "consultar_historial_paciente"}, "type": "function"}]}, "response_metadata": {"finish_reason": "tool_calls", "model_name": "gpt-4o-2024-08-06", "system_fingerprint": "fp_90354628f2"}, "type": "AIMessageChunk", "id": "run-b72ae5e4-2dc4-4e79-a634-476a451fac37", "tool_calls": [{"name": "consultar_historial_paciente", "args": {"apellido": "Hernandez", "nombre": "Brenda"}, "id": "call_gIGVj68mArzT534qGxmL7bVg", "type": "tool_call"}], "tool_call_chunks": [{"name": "consultar_historial_paciente", "args": "{\"apellido\":\"Hernandez\",\"nombre\":\"Brenda\"}", "id": "call_gIGVj68mArzT534qGxmL7bVg", "index": 0, "type": "tool_call_chunk"}], "invalid_tool_calls": []}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "ToolMessage"], "kwargs": {"content": "Historia cl\u00ednica del paciente: [('2024-10-21: Nuevo paciente, historia inicial2024-10-21: Comenz\u00f3 el tratamiento para los par\u00e1sitos.\\n2024-10-23: 2024-10-23: Se revisaron rodillas y pies.\\n',)]", "type": "tool", "tool_call_id": "call_gIGVj68mArzT534qGxmL7bVg", "status": "success"}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "HumanMessage"], "kwargs": {"content": "agrega que se hizo los controles de vacunas", "type": "human"}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "ToolMessage"], "kwargs": {"content": "Se ha actualizado la historia cl\u00ednica del paciente brenda hernandez exitosamente.", "type": "tool", "tool_call_id": "call_VKIalTV3waT2IfBqVgn8IgQX", "status": "success"}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "AIMessageChunk"], "kwargs": {"content": "", "additional_kwargs": {"tool_calls": [{"index": 0, "id": "call_VKIalTV3waT2IfBqVgn8IgQX", "function": {"arguments": "{\"apellido\":\"Hernandez\",\"nombre\":\"Brenda\",\"historia\":\"2024-10-23: Se realizaron los controles de vacunas.\"}", "name": "registra_historia_paciente"}, "type": "function"}]}, "response_metadata": {"finish_reason": "tool_calls", "model_name": "gpt-4o-2024-08-06", "system_fingerprint": "fp_90354628f2"}, "type": "AIMessageChunk", "id": "run-4cd60d84-5a4a-4905-9177-08d648b91689", "tool_calls": [{"name": "registra_historia_paciente", "args": {"apellido": "Hernandez", "nombre": "Brenda", "historia": "2024-10-23: Se realizaron los controles de vacunas."}, "id": "call_VKIalTV3waT2IfBqVgn8IgQX", "type": "tool_call"}], "tool_call_chunks": [{"name": "registra_historia_paciente", "args": "{\"apellido\":\"Hernandez\",\"nombre\":\"Brenda\",\"historia\":\"2024-10-23: Se realizaron los controles de vacunas.\"}", "id": "call_VKIalTV3waT2IfBqVgn8IgQX", "index": 0, "type": "tool_call_chunk"}], "invalid_tool_calls": []}}

Gedeon, [23/10/2024 21:44]
{"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "HumanMessage"], "kwargs": {"content": "muestrame como quedo la historia", "type": "human"}}