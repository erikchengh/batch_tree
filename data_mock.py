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
            {
                "id": "PI101",
                "phase": "P10",
                "name": "Weigh API",
                "result": "PASS",
                "parameters": {"weight": "500g"},
                "limits": {"min": "495g", "max": "505g"},
                "timestamp": "2026-01-07 08:00",
                "deviation": None
            },
            {
                "id": "PI102",
                "phase": "P10",
                "name": "Charge API",
                "result": "PASS",
                "parameters": {"charge": "1000ml"},
                "limits": {"min": "995ml", "max": "1005ml"},
                "timestamp": "2026-01-07 08:30",
                "deviation": None
            },
            {
                "id": "PI201",
                "phase": "P20",
                "name": "Set Speed",
                "result": "FAIL",
                "parameters": {"speed": "200 rpm"},
                "limits": {"min": "180 rpm", "max": "220 rpm"},
                "timestamp": "2026-01-07 09:00",
                "deviation": "Speed exceeded upper limit"
            },
            {
                "id": "PI202",
                "phase": "P20",
                "name": "Mix for Time",
                "result": "PASS",
                "parameters": {"time": "30 min"},
                "limits": {"min": "29 min", "max": "31 min"},
                "timestamp": "2026-01-07 09:30",
                "deviation": None
            },
        ],
        "materials": [
            {"pi": "PI101", "name": "API Lot A", "type": "consumed"},
            {"pi": "PI202", "name": "Final Blend", "type": "produced"},
        ]
    }
