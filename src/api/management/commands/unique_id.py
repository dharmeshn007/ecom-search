from django.core.management.base import BaseCommand
import logging
import re
import uuid

import random
from datetime import datetime

def __uniqueid__():
    mynow=datetime.now
    sft=datetime.strftime
    # store old datetime each time in order to check if we generate during same microsecond (glucky wallet !)
    # or if daylight savings event occurs (when clocks are adjusted backward) [rarely detected at this level]
    old_time=mynow() # fake init - on very speed machine it could increase your seed to seed + 1... but we have our contingency :)
    # manage seed
    seed_range_bits=14 # max range for seed
    seed_max_value=2**seed_range_bits - 1 # seed could not exceed 2**nbbits - 1
    # get random seed
    seed=random.getrandbits(seed_range_bits)
    current_seed=str(seed)
    # producing new ids
    while True:
        # get current time
        current_time=mynow()
        if current_time <= old_time:
            # previous id generated in the same microsecond or Daylight saving time event occurs (when clocks are adjusted backward)
            seed = max(1,(seed + 1) % seed_max_value)
            current_seed=str(seed)
        # generate new id (concatenate seed and timestamp as numbers)
        #newid=hex(int(''.join([sft(current_time,'%f%S%M%H%d%m%Y'),current_seed])))[2:-1]
        newid=int(''.join([sft(current_time,'%f%S%M%H%d%m%Y'),current_seed]))
        # save current time
        old_time=current_time
        # return a new id
        yield newid

""" you get a new id for each call of uniqueid() """
# uniqueid=next(__uniqueid__())
# print(uniqueid)
seen = set()
doubles = set()
for i in range(200_000_000):
    id_ = next(__uniqueid__())
    if id_ in seen:
        doubles.add(id_)
    seen.add(id_)

print(f"Number of duplicate ids: {len(doubles)} / 200000000 generated")
# Number
# of
# duplicate
# ids: 31572 / 200000
# generated
# import unittest
# class UniqueIdTest(unittest.TestCase):
#     def testGen(self):
#         for _ in range(3):
#             m=[uniqueid() for _ in range(10)]
#             self.assertEqual(len(m),len(set(m)),"duplicates found !")
