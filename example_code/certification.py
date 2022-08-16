import smartpy as sp

class Certification(sp.Contract):
    def __init__(self, certifier):
        self.init(certified = sp.list(t = sp.TString), certifier = certifier.address)

    @sp.entry_point
    def certify(self, params):
        # So when the contract is created, a certifier is set, now with this verify if a different address attempts to add to the list, it will be rejected(invalid transaction)
        sp.verify(sp.sender == self.data.certifier)
        self.data.certified.push(params)

@sp.add_test(name = "Certify")
def test():
    anil = sp.test_account("Anil")
    ibo = sp.test_account("Ibo")

    contract = Certification(certifier = anil)
    scenario = sp.test_scenario()

    scenario += contract
    scenario += contract.certify("Anil Oener").run(sender = anil)
    scenario += contract.certify("Ibo Sy").run(sender = ibo)
