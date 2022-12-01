from transact import *

transact_counter = 0

class Generator():
    block_id = int()

    def __init__(self, block_id):
        self.block_id = block_id

    def gen_transact(self, bdt, priority=0):
        global transact_counter
        transact_counter += 1
        return Transact(transact_counter, priority, bdt, 0, self.block_id)