# So this is an escrow trustless system for making a payment
# The seller sets the price of the item, and deposits twice that price into the contract i.e. the price is 1 token, the seller deposits 2
# The buyer deposits 2 tokens 
# Option A: the buyer receives the item, the item is received which allows the buyer to get the deposit back and send the seller thereamaining 3 tokens
# Option B: the seller can roll everything back and refund the buyer - both get 2 tokens back
import smartpy as sp

class Escrow(sp.Contract):
    def __init__(self):
        self.init(seller = sp.none, buyer = sp.none, price = sp.nat(0))

    @sp.entry_point
    def set_seller(self, params):
        self.data.price = params
        sp.verify(sp.amount == sp.utils.nat_to_tez(self.data.price * 2))
        self.data.seller = sp.some(sp.sender)

    @sp.entry_point
    def set_buyer(self):
        sp.verify(self.data.seller.is_some())
        sp.verify(sp.amount == sp.utils.nat_to_tez(self.data.price * 2))
        self.data.buyer = sp.some(sp.sender)

    @sp.entry_point
    def confirm_received(self):
        sp.verify(sp.sender == self.data.buyer.open_some())
        balance_after = sp.balance - sp.utils.nat_to_tez(self.data.price)
        sp.send(self.data.buyer.open_some(), sp.utils.nat_to_tez(self.data.price))
        sp.send(self.data.seller.open_some(), balance_after)
        self.reset_contract()

    @sp.entry_point
    def refund_buyer(self):
        sp.verify(sp.sender == self.data.seller.open_some())
        sp.send(self.data.buyer.open_some(), sp.utils.nat_to_tez(self.data.price * 2))
        sp.send(self.data.seller.open_some(), sp.utils.nat_to_tez(self.data.price * 2))
        self.reset_contract()

    def reset_contract(self):
        self.data.buyer = sp.none
        self.data.seller = sp.none
        self.data.price = 0

@sp.add_test(name = "Test Escrow")
def test_escrow():
    seller = sp.test_account("Seller")
    buyer = sp.test_account("Buyer")

    scenario = sp.test_scenario()
    scenario.h1("Normal sale with escrow")

    contract = Escrow()
    scenario += contract
    scenario += contract.set_seller(1).run(seller, amount = sp.tez(2))
    scenario += contract.set_buyer().run(buyer, amount = sp.tez(2))
    scenario += contract.confirm_received().run(buyer)

sp.add_compilation_target("escrow", Escrow())
