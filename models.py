from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree.models import subsession
import csv

author = 'Shuchen Zhao'
doc = """
This is a 2 person buyer and seller game with reputation system. p1 (player A) is seller. p2 (player B) is buyer.
"""


class Constants(BaseConstants):

    name_in_url = 'reputation_game'
    players_per_group = 2
    num_rounds = 40
    endowment = 100
    multiplier = 3
    round_in_block = 10


def parse_config(config_file):
    with open('reputation_system/configs/' + config_file) as f:
        rows = list(csv.DictReader(f))

    rounds = []
    for row in rows:
        rounds.append({
            'block': int(row['block']),
            'reward_from_experimenter': int(row['reward_from_experimenter']),
            'feedback_cost': int(row['feedback_cost']),
            'reward': int(row['reward'])
        })
    return rounds


class Subsession(BaseSubsession):

    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)

    def block(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['block']

    def reward_from_experimenter(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['reward_from_experimenter']

    def feedback_cost(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['feedback_cost']

    def reward(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['reward']


class Group(BaseGroup):

    def num_rounds(self):
        return len(parse_config(self.session.config['config_file']))

    reward_amount = models.IntegerField(initial=0)

    invest_amount = models.IntegerField(
        choices=[
            [0, 'No'],
            [Constants.endowment, 'Yes'],
        ],
        widget=widgets.RadioSelect
    )

    quality_amount = models.IntegerField()

    feedback_choice = models.BooleanField(
        choices=[
            [False, 'No'],
            [True, 'Yes'],
        ],
        widget=widgets.RadioSelect,
        initial=False
    )

    feedback_amount = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )

    def set_payoffs(self):
        p1 = self.get_player_by_id(1)
        p2 = self.get_player_by_id(2)
        if self.invest_amount == 0:
            p1.payoff = Constants.endowment
            p2.payoff = Constants.endowment
        elif self.feedback_choice == False:
            p1.payoff = Constants.endowment + self.invest_amount - self.quality_amount
            p2.payoff = Constants.endowment - self.invest_amount + self.quality_amount * Constants.multiplier
        else:
            p1.payoff = Constants.endowment + self.invest_amount - self.quality_amount - self.reward_amount
            p2.payoff = Constants.endowment - self.invest_amount + self.quality_amount * Constants.multiplier - self.subsession.feedback_cost() + self.reward_amount

    def current_reputation(self):
        p1 = self.get_player_by_id(1)
        p2 = self.get_player_by_id(2)
        if self.feedback_choice == True:
            p1.current_reputation = self.feedback_amount
            p2.current_reputation = self.feedback_amount
        else:
            p1.current_reputation = 0
            p2.current_reputation = 0


class Player(BasePlayer):

    current_reputation = models.IntegerField(initial=0)

    def role(self):
        return {1: 'seller', 2: 'buyer'}[self.id_in_group]

    def get_partner(self):
        return self.get_others_in_group()[0]









