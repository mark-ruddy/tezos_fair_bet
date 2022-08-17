# TODO: take comments out, put into documentation instead
# TODO: int size and gas fees, do I need to enforce that at contract level?
import smartpy as sp

Utils = sp.io.import_script_from_url("https://raw.githubusercontent.com/RomarQ/tezos-sc-utils/main/smartpy/utils.py")

class FairBet(sp.Contract):
    def __init__(self):
        self.init(
            creator = sp.none,
            matcher = sp.none,
            bet = sp.mutez(0),
            creator_sha256_hex_hash = sp.none,
            matcher_sha256_hex_hash = sp.none,
            random_nat_creator = sp.none,
            random_nat_matcher = sp.none,
        )

    @sp.entry_point
    def create_bet(self, creator_sha256_hex_hash):
        # Minimum bet amount is 0.1 Tez or 100000 MuTez
        sp.verify(sp.amount > sp.utils.nat_to_mutez(100000))

        self.data.bet = sp.amount
        self.data.creator_sha256_hex_hash = sp.some(Utils.Bytes.of_string(creator_sha256_hex_hash))
        self.data.creator = sp.some(sp.sender)

    @sp.entry_point
    def match_bet(self, matcher_sha256_hex_hash):
        sp.verify(self.data.creator.is_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())
        sp.verify(sp.amount == self.data.bet)

        self.data.matcher_sha256_hex_hash = sp.some(Utils.Bytes.of_string(matcher_sha256_hex_hash))
        self.data.matcher = sp.some(sp.sender)

    # TODO: transition to both users being able to settle and hash, remove asymmetry, remove front-running benefit
    @sp.entry_point
    def creator_reveal_nat(self, random_nat_creator):
        sp.verify(sp.sender == self.data.creator.open_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())

        sp.verify(self.data.matcher.is_some())
        sp.verify(self.data.matcher_sha256_hex_hash.is_some())

        # sp.verify(sp.sha256(Utils.Bytes.of_string(random_nat_creator)) == self.data.matcher_sha256_hex_hash.open_some())
        self.data.random_nat_matcher = sp.some(sp.as_nat(Utils.Int.of_string(random_nat_creator), message = "Not a valid natural number"))

        sp.verify(sp.amount == sp.mutez(0))
        sp.verify(sp.balance == self.data.bet * sp.mutez(2))

        sp.if self.data.random_nat_matcher.is_some():
            self.settle_bet()

    @sp.entry_point
    def matcher_reveal_nat(self, random_nat_matcher):
        sp.verify(sp.sender == self.data.matcher.open_some())
        sp.verify(self.data.matcher_sha256_hex_hash.is_some())

        sp.verify(self.data.creator.is_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())

        # sp.verify(sp.sha256(Utils.Bytes.of_string(random_nat_matcher)) == self.data.matcher_sha256_hex_hash.open_some())
        self.data.random_nat_matcher = sp.some(sp.as_nat(Utils.Int.of_string(random_nat_matcher), message = "Not a valid natural number"))

        sp.verify(sp.amount == sp.mutez(0))
        sp.verify(sp.balance == self.data.bet * sp.mutez(2))

        sp.if self.data.random_nat_creator.is_some():
            self.settle_bet()

    def settle_bet(self):
        agreed_random = self.data.random_nat_creator.open_some() ^ self.data.random_nat_matcher.open_some()
        sp.if agreed_random % 2 == 0:
            # creator wins
            sp.send(self.data.creator.open_some(), sp.balance)
        sp.else:
            # matcher wins
            sp.send(self.data.matcher.open_some(), sp.balance)

# TODO: test the current logic on the "happy path", then we need to add the forfeit endpoints to solve the "never reveal" problem
@sp.add_test(name = "Test Standard Bet")
def test_standard_bet():
    creator = sp.test_account("Creator")
    matcher = sp.test_account("Matcher")

    scenario = sp.test_scenario()
    scenario.h1("Test Standard Bet")

    contract = FairBet()
    scenario += contract
    # Creator uses a sha256 hash for the number 45009943213
    # generated with: "echo -n 45009943213 | sha256sum"
    scenario += contract.create_bet("6f69f6f2d77b836acfd8810fd6649511279a849cbb3e9447f496554a2d85fd15").run(creator, amount = sp.tez(1))
    # Matcher uses a sha256 hash for the number 96940671234343
    scenario += contract.match_bet("5225ea4f514d012f1fe71afc0cb6c802224abe53a0af9c5de1626f44fbe6b2af").run(matcher, amount = sp.tez(1))

    # Either the creator/matcher can now reveal their number first, in this case the matcher reveals first
    scenario += contract.creator_reveal_nat("45009943213").run(creator, amount = sp.tez(0))
    # When both numbers are revealed, the bet will execute
    # In this case the creator will win after the XOR and modulo as the result is 0: 45009943213 ^ 96940671234343 = 96897558170506 % 2 == 0
    scenario += contract.matcher_reveal_nat("96940671234343").run(matcher, amount = sp.tez(0))
