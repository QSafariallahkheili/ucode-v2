INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('0', '{
    "detailedDescription": {
        "route1": [
            {
                "description": "Hallo, dies hier ist die erste mögliche Route, die durch die Hindenburgstraße verläuft. Hier, am Goetheplatz wäre ein Zu- und Ausstieg möglich.",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.255922557138092,
                        50.010616816813126
                    ]
                }
            },
            {
                "description": "Hier kreuzen wir die Kaiserstraße und der weitere Streckenverlauf ähnelt der Route 2.",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.264980374765543,
                        50.00575110794614
                    ]
                }
            }
        ],
        "route2": [
            {
                "description": "Dies ist die Route 2. Sie verläuft über die Wallausstraße. An dieser Stelle eignet sich ein Zu- und Ausstieg am Frauenlobplatz.",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.263283581926629,
                        50.00858185141479
                    ]
                }
            },
            {
                "description": "Hier überschneiden sich die Planungsvarianten und bieten eine gute Anbindung in die Mainzer Innenstadt",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.269433658695931,
                        49.99832606115242
                    ]
                }
            }
        ],
        "route3": [
            {
                "description": "Route 3 verläuft über die Rheinalle und bietet so eine tolle scenische Fahrt",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.255382760148137,
                        50.0120254698073
                    ]
                }
            },
            {
                "description": "Von hier aus gibt es eine gute Anbindung in die Innenstadt und touristische Attraktivität durch den Mainzer Dom.",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.272278519204008,
                        49.9991464156804
                    ]
                }
            },
            {
                "description": "Hier, am Adenauer-Ufer führt die Route weiter am Rhein entlang und bietet Zugang zum Hafen und Industriegelände.",
                "location": {
                    "type": "Point",
                    "coordinates": [
                        8.271518521977868,
                        50.00638943031129
                    ]
                }
            }
        ]
    },
    "title": "Erkundung",
    "description": "Sieh dir alle Planungsideen im Detail an. Verwende dafür die Filteroption im unteren Bereich."
}', 1, 3, 0);
delete from quests_user;