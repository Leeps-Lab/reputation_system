from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Welcome(Page):

    def is_displayed(self):
        return self.round_number == 1


class Instruction(Page):

    def is_displayed(self):
        return self.round_number == 1


class SellerEntry(Page):
    form_model = 'group'
    form_fields = ['decision_entry']

    timeout_seconds = 10

    def is_displayed(self):
        return self.player.role == 'player2' and self.round_number <= self.Constants.num_rounds


class SellerPrice(Page):
    form_model = 'group'
    form_fields = ['decision_price']

    timeout_seconds = 20

    def is_displayed(self):
        return self.player.role == 'player2' and self.round_number <= self.Constants.num_rounds


class BuyerBuy(Page):
    form_model = 'group'
    form_fields = ['decision_buy']

    timeout_seconds = 20

    def is_displayed(self):
        return self.player.role == 'player1' and self.round_number <= self.Constants.num_rounds

    '''
    def vars_for_template(self):
        return {
            'player_in_previous_rounds': self.player.in_previous_rounds(),
            'player_in_block': self.player.in_rounds(1 + Constants.round_in_block*(self.subsession.block()-1), self.round_number),
        }
    '''


class SellerQuality(Page):
    form_model = 'group'
    form_fields = ['decision_quality']

    timeout_seconds = 10

    def is_displayed(self):
        return self.player.role == 'player2' and self.round_number <= self.Constants.num_rounds


class Results(Page):
    timeout_seconds = 10

    def is_displayed(self):
        return self.group.invest_amount != 0 and self.round_number <= self.Constants.num_rounds

    def vars_for_template(self):
        return {
            'cumulative_payoff': sum([p.payoff for p in self.player.in_all_rounds()])
        }


class PayoffWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self):
        return self.round_number <= self.Constants.num_rounds


class AllGroupsWaitPage(WaitPage):

    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.Constants.num_rounds


class WaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.Constants.num_rounds


class ShuffleWaitPage(WaitPage):

    wait_for_all_groups = True
    after_all_players_arrive = 'do_my_shuffle'

    def is_displayed(self):
        return self.round_number == 1


page_sequence = [
    Welcome,
    Instruction,
    ShuffleWaitPage,
    SellerEntry,
    WaitPage,
    SellerPrice,
    WaitPage,
    BuyerBuy,
    WaitPage,
    SellerQuality,
    WaitPage,
    PayoffWaitPage,
    AllGroupsWaitPage,
    Results
]
