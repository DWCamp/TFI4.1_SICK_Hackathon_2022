# README

Who the hell documents a Hackathon project???

## Variables API

An example response from the variable API:

    {
        "variables": [
            {
                "name": "TO_TargetNode",
                "value": 0.0,
                "type": "NUMBER"
            },
            {
                "name": "TO_MovePinUp",
                "value": 0.0,
                "type": "NUMBER"
            },
            {
                "name": "TO_MovePinDown",
                "value": 0.0,
                "type": "NUMBER"
            },
            {
                "name": "AgvBatteryChargeOk",
                "value": 1.0,
                "type": "NUMBER"
            },
            {
                "name": "mapOrientation",
                "value": 0.0,
                "type": "NUMBER"
            }
        ],
        "currentAndonStates": [
            {
                "timeActiveSeconds": 0,
                "uuid": 27759,
                "text": "Schutzfeld vorne",
                "description": "Sensorbereich prüfen",
                "errorCode": "ES38",
                "category": "ERROR"
            }
        ],
        "isPinUp": false,
        "isPinDown": true,
        "serialNumber": "AGVS201:Hackathon",
        "orderId": "",
        "orderUpdateId": 0,
        "lastNodeId": "4",
        "driving": true,
        "paused": false,
        "newBaseRequest": false,
        "operatingMode": "AUTOMATIC",
        "nodeStates": [],
        "edgeStates": [],
        "agvPosition": {
            "x": 0.0,
            "y": 0.0,
            "theta": 0.0,
            "mapId": "",
            "positionInitialized": false
        },
        "velocity": {
            "vx": 300.0,
            "vy": 0.0,
            "omega": 0.0
        },
        "loads": [],
        "actionStates": [
            {
                "actionId": "goto_0",
                "actionDescription": "GoTo7-183a39f3c6f",
                "actionStatus": "running"
            }
        ],
        "batteryState": {
            "batteryCharge": 70.22062183136615,
            "batteryVoltage": 24.35,
            "charging": false
        },
        "errors": [
            {
                "errorType": "ProtectionField",
                "errorReferences": [],
                "errorDescription": "ProtectionField",
                "errorLevel": "WARNING"
            }
        ],
        "information": [],
        "safetyState": {
            "eStop": "autoAck",
            "fieldViolation": true
        }
    }