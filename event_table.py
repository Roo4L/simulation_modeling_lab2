from config import *

class EventChainEntry():
    def __init__(self, t, c):
        self.transact = t
        self.comment = c


def event_chain_sort_key(ec_entry):
    return ec_entry.transact.bdt

class EventTable():
    i = 0
    CEC = list()
    FEC = list()
    log_table = {
        i_column : list(),
        time_column: list(),
        cec_column: list(),
        fec_column: list(),
    }

    def _cec_str(self):
        ec_str_list = list()
        for ec_entry in self.CEC:
            t = ec_entry.transact
            comment = ec_entry.comment
            ec_str_list.append(("[{},{},{:.2f},{},{}]{}".format(t.id,t.priority,t.bdt,t.current,t.next,
                                                            " " + comment if comment is not None else "")))
        return "\n".join(ec_str_list)

    def _fec_str(self):
        ec_str_list = list()
        for ec_entry in self.FEC:
            t = ec_entry.transact
            ec_str_list.append("[{},{},{:.2f},{},{}]".format(t.id,t.priority,t.bdt,t.current,t.next))
        return "\n".join(ec_str_list)

    def log(self, time):
        self.i += 1
        self.log_table[i_column].append(self.i)
        self.log_table[time_column].append("{:.2f}".format(time))
        self.log_table[cec_column].append(self._cec_str())
        self.log_table[fec_column].append(self._fec_str())
        return

    def update_cec_status(self, time):
        for ec_entry in self.CEC:
            if ec_entry.transact.bdt < time:
                # Waiting in queue
                if ec_entry.transact.current == GEN1_BLOCK_ID:
                    # Waiting in channel queue
                    ec_entry.comment = CHANNEL_QUEUE_COMMENT
                elif ec_entry.transact.current == CHANNEL_BLOCK_ID:
                    # Waiting in server queue
                    ec_entry.comment = SERVER_QUEUE_COMMENT
                else:
                    print("unknown state entered")
                    exit(1)
                # Update time
                ec_entry.transact.bdt = time
            elif ec_entry.transact.bdt == time:
                # Current event happened
                if ec_entry.transact.current == GEN1_BLOCK_ID:
                    ec_entry.comment = CHANNEL_ENTRY_COMMENT
                elif ec_entry.transact.current == CHANNEL_BLOCK_ID:
                    ec_entry.comment = SERVER_ENTRY_COMMENT
                elif ec_entry.transact.current == SERVER_BLOCK_ID or ec_entry.transact.current == GEN2_BLOCK_ID:
                    ec_entry.comment = TERMINATE_COMMENT
                else:
                    print("unknown state entered")
                    exit(1)
            else:
                print("unknown state entered")
                exit(1)

    def cleanup_cec(self):
        # Remove transactions moved to FEC
        for ec_entry in self.FEC:
            ec_remove_id = None
            for i in range(len(self.CEC)):
                if ec_entry.transact.id == self.CEC[i].transact.id:
                    ec_remove_id = i
                    break
            if ec_remove_id is not None:
                self.CEC.pop(ec_remove_id)
        # Remove terminated transacts
        remove_candidates = list()
        for ec_entry in self.CEC:
            if ec_entry.comment == TERMINATE_COMMENT:
                remove_candidates.append(ec_entry)
        for candidate in remove_candidates:
            self.CEC.remove(candidate)
