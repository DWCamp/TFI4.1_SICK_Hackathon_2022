"""
AGV Controller

This is a script for translating taking input from a Natural Language Processor
and translating it to REST API calls for a SafeLoc Autonomous Guided Vehicle.

Author: D. William Campman
Date: 2022-10-04
"""
import asyncio

from agv import AGV
from audio_processing import LanguageEngine


def dirty_filthy_hacks(agv):
    while True:
        val = input("X").upper()
        print(val)
        if val == "S":
            agv.set_driving(False)
        elif val == "L":
            agv.rotate_left()
        elif val == "R":
            agv.rotate_right()
        elif val == "F":
            agv.go_forwards()


def main():
    agv = AGV()
    # dirty_filthy_hacks(agv)

    le = LanguageEngine(agv)
    asyncio.run(le.listen_for_command())
    _ = input("Press enter to quit... ")


if __name__ == '__main__':
    main()
