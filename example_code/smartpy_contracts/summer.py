import smartpy as sp

class Summarize(sp.Contract):
    def __init__(self):
        # It is recommended/just_simpler to give all of your types a type instead of letting smartpy guess what your int is
        # Python is dynamically typed, but michelson is strongly typed, so basically we aare simulating using a type system here
        self.init(storage = sp.nat(0))

    @sp.entry_point
    def sum(self, params):
        # So we could do this with normal python loop, just add to `self.data.storage` each time
        # The problem is that this creates more michelson ADD instructions(every instruction costs money) in the contract than necessary
        # So we are instead encouraged to use `sp.for` and `sp.range` that will minimise the required michelson instructions generated
        sp.for i in sp.range(1, params+1):
            self.data.storage += i

@sp.add_test(name = "Second_Test")
def test():
    scenario = sp.test_scenario()
    second_contract = Summarize()
    scenario += second_contract
    scenario += second_contract.sum(5)
