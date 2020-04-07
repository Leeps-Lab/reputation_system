from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Welcome(Page):

    def is_displayed(self):
        return self.round_number == 1


class Instruction1(Page):

    def is_displayed(self):
        return self.round_number == 1


class Instruction2(Page):

    def is_displayed(self):
        return self.round_number == 1


class Instruction3(Page):

    def is_displayed(self):
        return self.round_number == 1


class ShuffleWaitPage(WaitPage):

    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class SellerEntry(Page):
    form_model = 'player'
    form_fields = ['decision_entry']

    #timeout_seconds = 10

    if Constants.seq_entry == 0:
        def is_displayed(self):
            return self.player.role() == 'seller' and self.round_number <= self.subsession.num_rounds
    else:
        def is_displayed(self):
            return self.round_number <= self.subsession.num_rounds \
                   and (self.player.role2() == 'incumbent' or (self.player.role2() == 'entrant' and self.round_number >= Constants.mid_round) )


class SellerPrice(Page):
    form_model = 'player'
    form_fields = ['decision_price']

    #timeout_seconds = 20

    if Constants.seq_entry == 0:
        def is_displayed(self):
            return self.player.role() == 'seller' and self.round_number <= self.subsession.num_rounds and self.player.decision_entry == 1
    else:
        def is_displayed(self):
            return self.round_number <= self.subsession.num_rounds and self.player.decision_entry == 1 \
                   and (self.player.role2() == 'incumbent' or (self.player.role2() == 'entrant' and self.round_number >= Constants.mid_round) )

    def vars_for_template(self):
        return {
            'max_price': Constants.u_h - Constants.e_b,
            'min_price': Constants.u_l - Constants.e_b
        }


class BuyerBuy(Page):
    form_model = 'player'
    form_fields = ['decision_buy']

    #timeout_seconds = 20

    def is_displayed(self):
        return self.player.role() == 'buyer' and self.round_number <= self.subsession.num_rounds


class SellerQuality(Page):
    form_model = 'player'
    form_fields = ['decision_quality']

    #timeout_seconds = 10

    if Constants.seq_entry == 0:
        def is_displayed(self):
            return self.player.role() == 'seller' and self.round_number <= self.subsession.num_rounds and self.player.decision_entry == 1 and self.player.num_of_trade() > 0
    else:
        def is_displayed(self):
            return self.round_number <= self.subsession.num_rounds and self.player.decision_entry == 1 and self.player.num_of_trade() > 0 \
                   and (self.player.role2() == 'incumbent' or (self.player.role2() == 'entrant' and self.round_number >= Constants.mid_round) )



class Results(Page):
    #timeout_seconds = 10

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        return {
            'cumulative_payoff': sum([p.payoff for p in self.player.in_all_rounds()])
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class PlayerWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


page_sequence = [
    Welcome,
    Instruction1,
    Instruction2,
    Instruction3,
    ShuffleWaitPage,
    SellerEntry,
    PlayerWaitPage,
    SellerPrice,
    PlayerWaitPage,
    BuyerBuy,
    PlayerWaitPage,
    SellerQuality,
    PlayerWaitPage,
    ResultsWaitPage,
    Results
]
