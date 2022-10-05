import asyncio
import azure.cognitiveservices.speech as speechsdk
import json

import utils


locations = {
    "rack": "103"
}

class Command:
    def __init__(self, intent):
        self.intent = intent
        self.units = None
        self.direct = None
        self.distance = None
        self.location = None

    def set_direct(self, direct):
        self.direct = direct

    def set_distance(self, distance):
        self.distance = distance

    def set_units(self, units):
        self.units = units

    def set_location(self, location):
        self.location = location


def find_prediction(response) -> Command:
    # === intent
    intent = response['prediction']['topIntent']
    command = Command(intent)
    if intent == "Move":
        print("intent is Move ")
        if 'location' in response['prediction']['entities']:
            print("location", response['prediction']['entities']['location'][0])
            command.set_location(response['prediction']['entities']['location'][0])
        else:
            if 'distance' in response:
                command.set_distance(response['prediction']['entities']["distance"][0])
                print("distance :", response['prediction']['entities']["distance"][0])
            else:
                command.set_distance(1)
                print("distance 1")
            command.set_direct(response['prediction']['entities']["direction"][0])
            print("in direction :", response['prediction']['entities']["direction"][0])
            if 'units' in response:
                command.set_units(response['prediction']['entities']["units"][0])
                print("units :", response['prediction']['entities']["units"][0])
            else:
                command.set_units("meters")
                print("meters")
    elif intent == "Turn":
        print("intent is Turn")
        if response['prediction']['entities']["direction"][0] == 'clockwise':
            command.set_direct('right')
        elif response['prediction']['entities']["direction"][0] == 'anticlockwise':
            command.set_direct('left')
        elif response['prediction']['entities']["direction"][0] == 'around':
            command.set_direct('around')
        else:
            command.set_direct(response['prediction']['entities']["direction"][0])
        print("in direction :", response['prediction']['entities']["direction"][0])
        if 'units' in response:
            print("units :", response['prediction']['entities']["units"][0])
        else:
            print("meters")
    if intent == "Stop":
        print("Intend is Stop")

    return command


async def listen_for_command(agv):
    # === NLP keys

    key_file = "keys.json"
    with open(key_file) as fp:
        keys = json.load(fp)

    # YOUR-APP-ID: The App ID GUID found on the www.luis.ai Application Settings page.
    app_id = keys["app_id"]

    # YOUR-PREDICTION-KEY: Your LUIS prediction key, 32 character value.
    prediction_key = keys["prediction_key"]

    # YOUR-PREDICTION-ENDPOINT: Replace with your prediction endpoint.
    # For example, "https://westus.api.cognitive.microsoft.com/"
    prediction_endpoint = 'https://predicitnlp.cognitiveservices.azure.com/'

    # === speech to text keys
    speech_key, service_region = keys["speech_key"], keys["region"]
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    # Asks user for mic input and prints transcription result on screen
    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()

    # The utterance you want to use.
    # utterance = result
    # utterance = 'Move robot three meters right'
    utterances = ["go to the rack"] #, "go to the left", "turn around", "move to the left", "move to the right",
    # "move 84 meters to the left", "move 7 meters to the left", "move minus 10 meters to the right",
    # "turn left 10 degrees", "turn left minus 10 degrees", "move forward"]

    ##########
    for utterance in utterances:

        # The headers to use in this REST call.
        headers = {}

        # The URL parameters to use in this REST call.
        params ={
            'query': utterance,
            'timezoneOffset': '0',
            'verbose': 'true',
            'show-all-intents': 'true',
            'spellCheck': 'false',
            'staging': 'false',
            'subscription-key': prediction_key
        }

        # Make the REST call.
        response, status = await utils.async_get_json(
            f'{prediction_endpoint}luis/prediction/v3.0/apps/{app_id}/slots/production/predict',
            headers=headers,
            params=params
        )
        result = find_prediction(response)
        # Display the results on the console.
        if result.intent is "Move":
            if result.location:
                node_id = locations[result.location]




    return response


def main():
    asyncio.run(listen_for_command())


if __name__ == '__main__':
    main()

