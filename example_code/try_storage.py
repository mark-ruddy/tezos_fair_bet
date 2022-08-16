import smartpy as sp

class StoreValue(sp.Contract):
    def __init__(self, value):
        self.init(stored_value = value)

    @sp.entry_point
    def replace(self, value):
        self.data.stored_value = value

    @sp.entry_point
    def double(self):
        self.data.stored_value *= 2

@sp.add_test(name = "TestStoreValue")
def test():
    scenario = sp.test_scenario()
    scenario.h1("Store Value")

    contract = StoreValue(1)
    scenario += contract
    scenario += contract.replace(2)
    scenario += contract.double()

sp.add_compilation_target("store_value", StoreValue(2))
