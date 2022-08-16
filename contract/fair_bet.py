# TODO: take comments out, put into documentation instead
import smartpy as sp

class FairBet(sp.Contract):
    def __init__(self):
        self.uint64_max = 18446744073709551615
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
    def set_creator(self, creator_sha256_hex_hash):
        # Minimum bet amount is 0.1 Tez or 100000 MuTez
        sp.verify(sp.amount > sp.utils.nat_to_mutez(100000))
        sp.verify(sp.len(sp.bytes(creator_sha256_hex_hash)) == 64)

        self.data.bet = sp.amount
        creator_sha256_hex_hash_notation = sp.concat("0x", creator_sha256_hex_hash)
        self.data.creator_sha256_hex_hash = sp.some(sp.bytes(creator_sha256_hex_hash_notation))
        self.data.creator = sp.some(sp.sender)

    @sp.entry_point
    def match_bet(self, matcher_sha256_hex_hash):
        sp.verify(self.data.creator.is_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())
        sp.verify(sp.amount == self.data.bet)
        sp.verify(sp.len(sp.bytes(matcher_sha256_hex_hash)) == 64)

        matcher_sha256_hex_hash_notation = sp.concat("0x", matcher_sha256_hex_hash)
        self.data.matcher_sha256_hex_hash = sp.some(sp.bytes(matcher_sha256_hex_hash_notation))
        self.data.matcher = sp.some(sp.sender)

    # TODO: transition to both users being able to settle and hash, remove asymmetry, remove front-running benefit
    @sp.entry_point
    def creator_reveal_nat(self, random_nat_creator):
        sp.verify(sp.sender == self.data.creator.open_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())

        sp.verify(self.data.matcher.is_some())
        sp.verify(self.data.matcher_sha256_hex_hash.is_some())

        sp.verify(random_nat_creator > 0)
        sp.verify(random_nat_creator < self.uint64_max)

        sp.verify(sp.sha256(sp.bytes(random_nat_creator)) == self.data.creator_sha256_hex_hash.open_some())
        self.data.random_nat_creator = sp.some(sp.nat(random_nat_creator))

        sp.verify(sp.amount == sp.mutez(0))
        sp.verify(sp.balance == sp.mutex(self.data.bet * 2))

        sp.if self.data.random_nat_matcher.is_some():
            self.settle_bet()

    @sp.entry_point
    def matcher_reveal_nat(self, random_nat_matcher):
        sp.verify(sp.sender == self.data.matcher.open_some())
        sp.verify(self.data.matcher_sha256_hex_hash().is_some())

        sp.verify(self.data.creator.is_some())
        sp.verify(self.data.creator_sha256_hex_hash.is_some())

        sp.verify(random_nat_matcher > 0)
        sp.verify(random_nat_matcher < self.uint64_max)

        sp.verify(sp.sha256(sp.bytes(random_nat_matcher)) == self.data.matcher_sha256_hex_hash.open_some())
        self.data.random_nat_matcher = sp.some(sp.nat(random_nat_matcher))

        sp.verify(sp.amount == sp.mutez(0))
        sp.verify(sp.balance == sp.mutex(self.data.bet * 2))

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
    pass
