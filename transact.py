class Transact():
    id = int()
    priority = int()
    bdt = float() # block departure time
    current = int() # current block
    next = int() # next block

    def __init__(self, id, priority, bdt, current, next):
        self.id = id
        self.priority = priority
        self.bdt = bdt
        self. current = current
        self.next = next
