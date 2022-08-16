import smartpy as sp

class Repeater(sp.Contract):
    def __init__(self):
        self.init(storage = 0)

    @sp.entry_point
    def repeat(self, params):
        # use of sp.verify(condition) - very common
        # basically in most contracts we only want to accept a transaction/instruction IF it matches certain conditions
        # So the use of sp.verify() is extremely common, we want to check if it matches the conditions
        # There is also sp.if, sp.while, etc. just rememmber to use the sp form when possible instead of normal python
        sp.verify(params > 0)
        self.data.storage = params

@sp.add_test(name = "First_Test")
def test():
    first_contract = Repeater()
    scenario = sp.test_scenario()
    scenario.register(first_contract, show = True)
    scenario += first_contract.repeat(2)

# remember this: there is an sp.test_account(), much better than faking a Tezos address

# SmartPy itself offers us self.data which corresponds with storage in Michelson
# We initialise this self.data with self.init() in the __init__ of the contract class - because it inherits from sp.Contract, this is all setup for us
# Notice how we directly assign to self.data.storage, that is our only reference point to "storage" which is the confusing name they decided to call it - it could be anything, self.data.X.
# Also see the @sp.entry_point, the previious self.init() will iterate over all of the entry_points to build out the contract - makes sense
