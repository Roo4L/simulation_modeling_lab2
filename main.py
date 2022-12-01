# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import random
from copy import deepcopy

from generator import *
from event_table import *
from config import *
import csv
import pandas as pd

random.seed(40)

def channel_available(table):
    for ec_entry in table.FEC:
        if ec_entry.transact.current == CHANNEL_BLOCK_ID:
            return False
    return True


def server_available(table):
    for ec_entry in table.FEC:
        if ec_entry.transact.current == SERVER_BLOCK_ID:
            return False
    return True


def generate_events(a, b, c, d, M):
    generator_events = list()
    out_events = list()
    server_events = list()

    while len(out_events) == 0 or out_events[-1] < M:
        generator_event = round(random.uniform(a,b), 1)
        out_event = (out_events[-1] + generator_event) if len(out_events) > 0 else generator_event
        server_event = round(random.uniform(c,d), 1)

        generator_events.append(generator_event)
        out_events.append(out_event)
        server_events.append(server_event)

    return generator_events, out_events, server_events


generator_events,out_events,server_events = generate_events(a,b,c,d,M)
# Print lists
print(generator_events)
print(out_events)
print(server_events)

# init variables

time = 0
gen1 = Generator(GEN1_BLOCK_ID)
gen2 = Generator(GEN2_BLOCK_ID)
table = EventTable()

# init table
modeling_stop = False
t = gen1.gen_transact(out_events.pop(0))
table.FEC.append(EventChainEntry(t, None))
t = gen2.gen_transact(M)
table.FEC.append(EventChainEntry(t, None))
table.log(time)

# main loop
while not modeling_stop and len(table.FEC) > 0:
    # Update CEC

    t = table.FEC.pop(0).transact
    time = t.bdt

    if t.current == ZERO_BLOCK_ID:
        # Transit to channel
        t.current = t.next
        if t.current == GEN1_BLOCK_ID:
            t.next = CHANNEL_BLOCK_ID
        else:
            t.next = GEN2_TERMINATE_BLOCK_ID

        table.CEC.append(EventChainEntry(t, None))
    else:
        table.CEC.append(EventChainEntry(t, None))

    # Update FEC
    if t.current == GEN1_BLOCK_ID:
        # Append new transact to FEC
        tt = gen1.gen_transact(out_events.pop(0))
        table.FEC.append(EventChainEntry(tt, None))
        # t_copy = Transact(t.id, 0, t.bdt + channel_t, CHANNEL_BLOCK_ID,SERVER_BLOCK_ID)
        # table.FEC.append(EventChainEntry(t_copy, None))
    if channel_available(table):
        # Append next transact from channel queue
        t_id = None
        index = None
        for i in range(len(table.CEC)):
            tmp_id = table.CEC[i].transact.current
            next_device = table.CEC[i].transact.next
            if next_device == CHANNEL_BLOCK_ID and (t_id is None or tmp_id < t_id):
                t_id = tmp_id
                index = i

        if index is not None:
            # There is a transact in queue, push it
            tt = deepcopy(table.CEC[index].transact)
            tt.bdt += channel_t
            tt.current = tt.next
            tt.next = SERVER_BLOCK_ID
            table.FEC.append(EventChainEntry(tt, None))
    if server_available(table):
        # Append next transact from server queue
        t_id = None
        index = None
        for i in range(len(table.CEC)):
            tmp_id = table.CEC[i].transact.current
            next_device = table.CEC[i].transact.next
            if next_device == SERVER_BLOCK_ID and (t_id is None or tmp_id < t_id):
                t_id = tmp_id
                index = i

        if index is not None:
            # There is a transact in queue, push it
            tt = deepcopy(table.CEC[index].transact)
            tt.bdt += server_events.pop(0)
            tt.current = tt.next
            tt.next = TERMINATE_BLOCK_ID
            table.FEC.append(EventChainEntry(tt, None))

    if t.current == GEN2_BLOCK_ID:
        modeling_stop = True

    # log table
    table.update_cec_status(time)
    table.FEC.sort(key=event_chain_sort_key)
    table.log(time)
    table.cleanup_cec()

print(pd.DataFrame.from_dict(table.log_table))
with open("out.csv", 'w', newline='') as f:
    keys = list(table.log_table.keys())
    writer = csv.DictWriter(f, fieldnames=keys)

    for i in range(len(table.log_table[keys[0]])):
        writer.writerow({key:table.log_table[key][i] for key in keys})