LEVEL_DATA = [
    {
        "id": 1,
        "grid_cols": 6,
        "grid_rows": 8,
        "layout": [
            [1, 1, 1, 1, 1, 1], # 1=Wall
            [1, 0, 0, 0, 0, 1], # 0=Empty
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        "blocks": [
            {"shape": "T", "color": "RED", "count": 1, "start_pos": (2, 2)}
        ],
        "coins": {
            "static": [
                {"color": "RED", "pos": (3, 3)}
            ],
            "queues": []
        },
        "stars_thresholds": [3, 5, 8]  # 3 stars: ≤3 moves, 2 stars: ≤5 moves, 1 star: ≤8 moves
    },
    {
        "id": 2,
        "grid_cols": 6,
        "grid_rows": 8,
        "layout": [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        "blocks": [
            {"shape": "L", "color": "BLUE", "count": 2, "start_pos": (1, 1)},
            {"shape": "T", "color": "RED", "count": 1, "start_pos": (4, 1)}
        ],
        "coins": {
            "static": [],
            "queues": [
                {"pos": (1, 6), "items": ["BLUE", "BLUE"]},
                {"pos": (4, 6), "items": ["RED"]}
            ]
        },
        "stars_thresholds": [6, 10, 15]
    },
    {
        "id": 3,
        "grid_cols": 7,
        "grid_rows": 7,
        "layout": [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ],
        "blocks": [
            {"shape": "S", "color": "GREEN", "count": 1, "start_pos": (1, 1)},
            {"shape": "Z", "color": "YELLOW", "count": 1, "start_pos": (5, 1)}
        ],
        "coins": {
            "static": [
                {"color": "GREEN", "pos": (1, 5)},
                {"color": "YELLOW", "pos": (5, 5)}
            ],
            "queues": []
        },
        "stars_thresholds": [5, 8, 12]
    },
    {
        "id": 4,
        "grid_cols": 8,
        "grid_rows": 8,
        "layout": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
        "blocks": [
            {"shape": "O", "color": "PURPLE", "count": 4, "start_pos": (1, 1)}
        ],
        "coins": {
            "static": [
                {"color": "PURPLE", "pos": (3, 3)},
                {"color": "PURPLE", "pos": (4, 3)},
                {"color": "PURPLE", "pos": (3, 4)},
                {"color": "PURPLE", "pos": (4, 4)}
            ],
            "queues": []
        },
        "stars_thresholds": [8, 12, 18]
    },
    {
        "id": 5,
        "grid_cols": 6,
        "grid_rows": 9,
        "layout": [
            [2, 2, 1, 1, 2, 2],
            [2, 0, 0, 0, 0, 2],
            [1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 0, 0, 1, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1],
            [2, 0, 0, 0, 0, 2],
            [2, 2, 1, 1, 2, 2],
        ],
        "blocks": [
            {"shape": "I", "color": "RED", "count": 1, "start_pos": (1, 1)},
            {"shape": "I", "color": "BLUE", "count": 1, "start_pos": (4, 1)},
            {"shape": "I", "color": "GREEN", "count": 1, "start_pos": (2, 7)}
        ],
        "coins": {
            "static": [
                {"color": "RED", "pos": (4, 7)},
                {"color": "BLUE", "pos": (1, 7)},
                {"color": "GREEN", "pos": (2, 1)}
            ],
            "queues": []
        },
        "stars_thresholds": [6, 10, 15]
    }
]
