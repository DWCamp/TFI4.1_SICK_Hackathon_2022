"""
Code for transcribing spoken language and converting
them into AGV commands

Authors: Varun Burde, Marina Ionova
Version: 2022-10-05
"""

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
        self.confidence = None

    def set_confidence(self, value):
        self.confidence = value

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
    command.set_confidence(response['prediction']['intents'][intent])
    if intent == "Move":
        print("Intent: Move ")
        if 'location' in response['prediction']['entities']:
            print("Location: ", response['prediction']['entities']['location'][0])
            command.set_location(response['prediction']['entities']['location'][0])
        else:
            if 'distance' in response:
                command.set_distance(response['prediction']['entities']["distance"][0])
                print("Distance: ", response['prediction']['entities']["distance"][0])
            else:
                command.set_distance(1)
                print("Distance: 1")
            command.set_direct(response['prediction']['entities']["direction"][0])
            print("Direction: ", response['prediction']['entities']["direction"][0])
            if 'units' in response:
                command.set_units(response['prediction']['entities']["units"][0])
                print("Units: ", response['prediction']['entities']["units"][0])
            else:
                command.set_units("meters")
                print("Units: meters")
    elif intent == "Turn":
        print("Intent: Turn")
        if response['prediction']['entities']["direction"][0] == 'clockwise':
            command.set_direct('right')
        elif response['prediction']['entities']["direction"][0] == 'anticlockwise':
            command.set_direct('left')
        elif response['prediction']['entities']["direction"][0] == 'around':
            command.set_direct('around')
        else:
            command.set_direct(response['prediction']['entities']["direction"][0])
        print("Direction: ", response['prediction']['entities']["direction"][0])
        if 'units' in response:
            print("Units:", response['prediction']['entities']["units"][0])
        else:
            print("Units: meters")
    if intent == "Stop":
        print("Intent: Stop")

    return command


class LanguageEngine:

    # YOUR-PREDICTION-ENDPOINT: Replace with your prediction endpoint.
    # For example, "https://westus.api.cognitive.microsoft.com/"
    PREDICTION_ENDPOINT = 'https://predicitnlp.cognitiveservices.azure.com/'

    def __init__(self, agv, command_confidence=0.2):
        """
        The class for processing language and listening for a
        :param agv: The object representing the being controlled
        :param
        """
        self.loop = asyncio.get_event_loop()
        self.agv = agv
        self.listening = True

        with open("keys.json") as fp:
            keys = json.load(fp)

        # YOUR-APP-ID: The App ID GUID found on the www.luis.ai Application Settings page.
        self.app_id = keys["app_id"]

        # YOUR-PREDICTION-KEY: Your LUIS prediction key, 32 character value.
        self.prediction_key = keys["prediction_key"]

        # === speech to text keys
        speech_key = keys["speech_key"]
        service_region = keys["region"]
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    async def listen_for_command(self):
        """
        Triggers Azure to begin speech recognition. The returned speech will then
        be sent to another thread for processing
        """
        # Listens to mic input and prints transcription result on screen
        speech_result = self.speech_recognizer.recognize_once_async().get()
        print(speech_result.text)
        # Runs natural language processing on transcription
        asyncio.run(self.process_speech(speech_result.text))

    async def process_speech(self, text) -> None:
        """
        Processes the text Azure transcription in the user audio
        :param text: The text the speech_recognizer returned
        """
        # The URL parameters to use in this REST call.
        params = {
            'query': text,
            'timezoneOffset': '0',
            'verbose': 'true',
            'show-all-intents': 'true',
            'spellCheck': 'false',
            'staging': 'false',
            'subscription-key': self.prediction_key
        }

        # Make the REST call
        response, status = await utils.async_get_json(
            f'{LanguageEngine.PREDICTION_ENDPOINT}luis/prediction/v3.0/apps/{self.app_id}/slots/production/predict',
            params=params)
        command = find_prediction(response.json())

        # ================== Process command

        # Abort if the
        if command.confidence < 0.5:
            return
        if command.intent == "Move":
            # Move to location
            if command.location:
                node_id = locations[command.location]
                self.agv.go_to_node(node_id)
                # agv.navigate_to_node(node_id)

    async def start_microphone(self):
        """
        Begin listening to the
        :return:
        """
        while self.listening:
            await self.listen_for_command()
