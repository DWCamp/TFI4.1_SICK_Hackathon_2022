"""
AGV Controller

This is a script for translating taking input from a Natural Language Processor
and translating it to REST API calls for a SafeLoc Autonomous Guided Vehicle.

Author: D. William Campman
Date: 2022-10-04
"""
import asyncio

from agv import AGV
from audio_processing import listen_for_command


def main():
    agv = AGV()
    asyncio.run(listen_for_command(agv))


if __name__ == '__main__':
    main()
