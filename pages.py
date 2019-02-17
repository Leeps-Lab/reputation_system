from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class WelcomePage(Page):

    def is_displayed(self):
        return self.round_number == 1


class SellerReward(Page):
    # form_model = 'group'
    # form_fields = ['reward_amount']

    timeout_seconds = 30

    def is_displayed(self):
        return self.player.id_in_group == 1 and self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            'player_in_previous_rounds': self.player.in_previous_rounds(),
            'player_in_block': self.player.in_rounds(1 + Constants.round_in_block*(self.subsession.block()-1), self.round_number),
        }

    def reward_amount_choices(self):
        return[0, self.subsession.reward()]


class BuyerSend(Page):
    form_model = 'group'
    form_fields = ['invest_amount']

    timeout_seconds = 50

    def is_displayed(self):
        return self.player.id_in_group == 2 and self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            'partner_in_previous_rounds': self.player.get_partner().in_previous_rounds(),
            'partner_in_block': self.player.get_partner().in_rounds(1 + Constants.round_in_block*(self.subsession.block()-1), self.round_number),
        }


class SellerSendBack(Page):
    form_model = 'group'
    form_fields = ['quality_amount']

    timeout_seconds = 20

    def is_displayed(self):
        return self.player.id_in_group == 1 and self.group.invest_amount != 0 and self.round_number <= self.group.num_rounds()

    def quality_amount_choices(self):
        return range(0, int(self.group.invest_amount) + 1, 1)


class BuyerFeedback(Page):
    form_model = 'group'
    form_fields = ['feedback_choice', 'feedback_amount']

    timeout_seconds = 60
    timeout_submission = {'feedback_amount': 4}

    def is_displayed(self):
        return self.player.id_in_group == 2 and self.group.invest_amount != 0 and self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            'tripled_amount': self.group.quality_amount * Constants.multiplier,
        }


class ResultsSend(Page):
    timeout_seconds = 20

    def is_displayed(self):
        return self.group.invest_amount != 0 and self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            'tripled_amount': self.group.quality_amount * Constants.multiplier,
            'cumulative_payoff': sum([p.payoff for p in self.player.in_all_rounds()])
        }


class ResultsNoSend(Page):
    timeout_seconds = 20

    def is_displayed(self):
        return self.group.invest_amount == 0 and self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            'cumulative_payoff': sum([p.payoff for p in self.player.in_all_rounds()])
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()
        self.group.current_reputation()

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


class AllGroupsWaitPage(WaitPage):

    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


class WaitForSeller(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


class WaitForBuyer(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


page_sequence = [
    WelcomePage,
    AllGroupsWaitPage,
    SellerReward,
    WaitForSeller,
    BuyerSend,
    WaitForBuyer,
    SellerSendBack,
    WaitForSeller,
    BuyerFeedback,
    ResultsWaitPage,
    AllGroupsWaitPage,
    ResultsSend,
    ResultsNoSend
]
