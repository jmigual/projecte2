#!/usr/bin/env python3
# Music Director using Multicast Ethernet
# January 2016
# Manuel Moreno

import socket
import struct
import json
import argparse
from DirectorMidiFile import *
from logger import *

# 8 music voices
# message = identifier, length of data, 8 notes (one per instrument)
# note = 0 means hold the last note
# note = 255 means silence, stop the last note


dim = 1000
can_frame_fmt = "=IB3x8s"


def build_can_frame(can_id, data):
    can_dlc = len(data)
    data = data.ljust(8, b'\x00')
    return struct.pack(can_frame_fmt, can_id, can_dlc, data)

class Director:
    """ Fist version using multicast ethernet
    """

    def __init__(self, tracks=8):
        # create a raw socket
        print("Init Multicast socket")
        self.multicast_group = ('224.0.0.1', 10000)
        # Create the datagram socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set a timeout so the socket does not block indefinitely when trying
        # to receive data.
        self.s.settimeout(0.2)
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        ttl = struct.pack('b', 1)
        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        # print(str(self.notes[0]).replace(",", "\n"))

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == "file_name":
            self.mid = DirectorMidiFile(self.file_name)
            self.tracks = len(self.mid.tracks)

    def play(self):
        t = 0
        logging.info("Playing...")

        for msg, track in self.mid.play_tracks():
            msg_out = {}
            msg_in = {}

            if msg.type == 'note_on':
                msg_in[track] = [msg.note]
            elif msg.type == 'note_off':
                msg_out[track] = [msg.note]
            else:
                continue

            json_string = json.dumps({
                "in": msg_in,
                "out": msg_out,
                "tracks": self.tracks
            })
            logging.debug("data_sent:" + json_string)
            sent = self.s.sendto(json_string.encode(), self.multicast_group)

        json_string = json.dumps({
            "in": {},
            "out": list(range(self.tracks)),
            "tracks": self.tracks
        })
        self.s.sendto(json_string.encode(), self.multicast_group)
        logging.info("Play Over")
        self.s.close()


def main():
    parser = argparse.ArgumentParser(description="Start director to play music with Pi Orchestra")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Starting in DEBUG mode")

    dir1 = Director()
    dir1.file_name = "sheets/Mario.mid"
    dir1.play()


if __name__ == '__main__':
    set_default_logger("director.log")

    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down Director, Thanks for the ride!")
