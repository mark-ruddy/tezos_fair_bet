import smartpy as sp

class Adder(sp.Contract):
    def __init__(self):
        self.init(storage = 0)

    @sp.entry_point
    def add(self, params):
        self.data.storage = params.first + params.second

@sp.add_test(name = "First_Test")
def test():
    adder_contract = Adder()
    scenario = sp.test_scenario()
    scenario += adder_contract
    scenario += adder_contract.add(first=2, second=3)
