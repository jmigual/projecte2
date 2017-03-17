#!/usr/bin/env python3

import getopt
import sys

import player
from logger import *


def usage():
    print("clientPlayer -i number [-v number]")
    print("-i track number")
    print("-v volume")
    print("-d set debug mode")


def main():
    logger = logging.getLogger()

    try:
        opts, args = getopt.gnu_getopt(sys.argv, "")
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    track = 0
    velocity = 40

    for o, a in opts:
        if o == "-i":
            track = int(a)
        elif o == "v":
            velocity = int(a)
        elif o == "d":
            logger.setLevel(logging.DEBUG)
            logger.debug("Starting debug mode")
        else:
            logger.error("Unknown option {0}", o)

    # Start playing
    sock_player = player.SocketPlayer(track=track, velocity=velocity)
    sock_player.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.getLogger().info("Shutting down, Thanks for the ride!")
