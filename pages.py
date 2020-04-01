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


class ShuffleWaitPage(WaitPage):

    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number == 1


class SellerEntry(Page):
    form_model = 'player'
    form_fields = ['decision_entry']

    #timeout_seconds = 10

    def is_displayed(self):
        return self.player.role() == 'seller' and self.round_number <= self.subsession.num_of_rounds()


class SellerPrice(Page):
    form_model = 'player'
    form_fields = ['decision_price']

    #timeout_seconds = 20

    def is_displayed(self):
        return self.player.role() == 'seller' and self.round_number <= self.subsession.num_of_rounds()

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
        return self.player.role() == 'buyer' and self.round_number <= self.subsession.num_of_rounds()


class SellerQuality(Page):
    form_model = 'player'
    form_fields = ['decision_quality']

    #timeout_seconds = 10

    def is_displayed(self):
        return self.player.role() == 'seller' and self.round_number <= self.subsession.num_of_rounds()


class Results(Page):
    #timeout_seconds = 10

    def is_displayed(self):
        return self.round_number <= self.subsession.num_of_rounds()

    def vars_for_template(self):
        return {
            'cumulative_payoff': sum([p.payoff for p in self.player.in_all_rounds()])
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self):
        return self.round_number <= self.subsession.num_of_rounds()


class PlayerWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.subsession.num_of_rounds()


page_sequence = [
    Welcome,
    Instruction1,
    Instruction2,
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
