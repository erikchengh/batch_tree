def load_mock_batch(batch_id: str):
    """
    Mock PAS-X batch execution data
    """

    return {
        "batch": {
            "id": batch_id,
            "product": "Paracetamol 500 mg Tablets",
            "status": "COMPLETED"
        },

        "phases": [
            {"id": "10", "name": "Dispensing"},
            {"id": "20", "name": "Blending"},
        ],

        "pis": [
            {
                "id": "PI-101",
                "phase": "10",
                "name": "Weigh API",
                "result": "PASS",
                "timestamp": "2026-01-07 08:00",
                "deviation": None
            },
            {
                "id": "PI-102",
                "phase": "10",
                "name": "Charge API",
                "result": "PASS",
                "timestamp": "2026-01-07 08:15",
                "deviation": None
            },
            {
                "id": "PI-201",
                "phase": "20",
                "name": "Set Blender Speed",
                "result": "FAIL",
                "timestamp": "2026-01-07 09:00",
                "deviation": "DEV-000234"
            },
            {
                "id": "PI-202",
                "phase": "20",
                "name": "Blend for 30 Minutes",
                "result": "PASS",
                "timestamp": "2026-01-07 09:30",
                "deviation": None
            },
        ],

        "materials": [
            {
                "name": "API-PAR-001 / LOT A123",
                "pi": "PI-101",
                "type": "consumed"
            },
            {
                "name": "Final Blend / LOT FB456",
                "pi": "PI-202",
                "type": "produced"
            }
        ]
    }
