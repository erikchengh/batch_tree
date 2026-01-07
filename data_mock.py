# def load_mock_batch(batch_id):
#     return {
#         "batch": {"id": batch_id, "product": "Tablet_A", "status": "Completed"},

#         "phases": [
#             {"id": "P10", "name": "Dispensing"},
#             {"id": "P20", "name": "Mixing"},
#         ],

#         "pis": [
#             {"id": "PI101", "phase": "P10", "name": "Weigh API", "result": "PASS"},
#             {"id": "PI102", "phase": "P10", "name": "Charge API", "result": "PASS"},
#             {"id": "PI201", "phase": "P20", "name": "Set Speed", "result": "FAIL"},
#             {"id": "PI202", "phase": "P20", "name": "Mix for Time", "result": "PASS"},
#         ],

#         "materials": [
#             {"pi": "PI101", "name": "API Lot A", "type": "consumed"},
#             {"pi": "PI202", "name": "Final Blend", "type": "produced"},
#         ]
#     }

def load_mock_batch(batch_id):
    return {
        "batch": {
            "id": batch_id,
            "product": "Tablet_A",
            "status": "Completed"
        },
        "phases": [
            {"id": "P10", "name": "Dispensing"},
            {"id": "P20", "name": "Mixing"},
        ],
        "pis": [
            {"id": "PI101", "phase": "P10", "name": "Weigh API", "result": "PASS"},
            {"id": "PI102", "phase": "P10", "name": "Charge API", "result": "PASS"},
            {"id": "PI201", "phase": "P20", "name": "Set Speed", "result": "FAIL"},
            {"id": "PI202", "phase": "P20", "name": "Mix for Time", "result": "PASS"},
        ],
        "materials": [
            {"pi": "PI101", "name": "API Lot A", "type": "consumed"},
            {"pi": "PI202", "name": "Final Blend", "type": "produced"},
        ]
    }


