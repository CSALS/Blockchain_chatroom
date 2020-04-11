chain = [
        {
            "data": "",
            "index": 1,
            "nonce": 1,
            "previous_hash": "0",
            "timestamp": "2020-04-11 19:11:41.157362"
        },
        {
            "data": [
                {
                    "msg": "This is the first message",
                    "sender": "rohith",
                    "time": "2020-04-11 19:11:52.439931"
                }
            ],
            "index": 2,
            "nonce": 533,
            "previous_hash": "f02b46d3288ef2bc19c141135e98ba715e43fa61b5ea19c7cb12b0b6ff1ed6af",
            "timestamp": "2020-04-11 19:11:59.457047"
        },
        {
            "data": [
                {
                    "msg": "This is the second message",
                    "sender": "rohith",
                    "time": "2020-04-11 19:12:15.578713"
                }
            ],
            "index": 3,
            "nonce": 45293,
            "previous_hash": "f17997ef7fcc8063734c26ba7a012dda8f4cd889515b07f94e35089f6d18979b",
            "timestamp": "2020-04-11 19:12:22.433557"
        }
]

response = []
for i, json in enumerate(chain):
    data = json['data']
    # Each data is a list containing messages
    for i, message in enumerate(data):
        response.append(message)


print(response)
    