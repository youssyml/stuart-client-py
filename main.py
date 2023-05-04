import os
import json
from stuart_client.StuartClient import (
    Environment,
    Authentication,
    StuartClient,
)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

env = Environment("SANDBOX")
auth = Authentication(env, client_id=client_id, client_secret=client_secret)
client = StuartClient(auth)

job = {
    "job": {
        "transport_type": "bike",
        "pickups": [
            {
                "address": "46 Boulevard Barbès, 75018 Paris",
                "comment": "Wait outside for an employee to come.",
                "contact": {
                    "firstname": "Martin",
                    "lastname": "Pont",
                    "phone": "+33698348756'",
                    "company": "KFC Paris Barbès",
                },
            }
        ],
        "dropoffs": [
            {
                "address": "156 rue de Charonne, 75011 Paris",
                "package_description": "Red packet.",
                "client_reference": "12345678ABCDEFC",
                "comment": "code: 3492B. 3e étage droite. Sonner à Durand.",
                "contact": {
                    "firstname": "Alex",
                    "lastname": "Durand",
                    "phone": "+33634981209",
                    "company": "Durand associates.",
                },
            }
        ],
    }
}

# response = client.get(
#     "/v2/addresses/validate",
#     params={"address": "32 Coombe Ln, Raynes Park, London SW20 0LA", "type": "picking"},
# )

response = client.post("/v2/jobs", json.dumps(job))

print(response)
