from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree.models import subsession
import csv, random

author = 'Shuchen Zhao'
doc = """
This is an n-player trust game with reputation system. 
Players are equally divided into two roles: buyers (player1) and sellers (player2). 
(A,B) represents sellers's entry decisions. 
(X,Y) represents seller's quality decisions.
p represent the seller's choice of price.
seq_entry shows the treatment of sequential entry vs simultaneous entry.
fix_price shows the treatment of fixed price vs self-determined price.
"""


class Constants(BaseConstants):

    name_in_url = 'reputation_game'
    players_per_group = 4
    num_rounds = random.randint(11, 15)


def parse_config(config_file):
    with open('reputation_system/configs/' + config_file) as f:
        rows = list(csv.DictReader(f))

    blocks = []
    for row in rows:
        blocks.append({
            'num_block': int(row['num_block']),
            'c_l': int(row['c_l']),
            'c_h': int(row['c_h']),
            'u_l': int(row['u_l']),
            'u_h': int(row['u_h']),
            'p_default': int(row['p_default']),
            'e_b': int(row['e_b']),
            'e_s': int(row['e_s']),
            'seq_entry': int(row['seq_entry']),
            'fix_price': int(row['fix_price'])
        })
    return blocks


class Subsession(BaseSubsession):
    def do_my_shuffle(self):
        if self.round_number == 1:
            players = self.get_players()

            buyer = [p for p in players if self.get_players_by_role('player1')]
            seller = [p for p in players if self.get_players_by_role('player2')]

            group_matrix = []

            while buyer:
                new_group = [
                    buyer.pop(),
                    buyer.pop(),
                    seller.pop(),
                    seller.pop()
                ]
                group_matrix.append(new_group)

            self.set_group_matrix(group_matrix)
        else:
            self.group_like_round(1)

    def num_block(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['num_block']

    def c_l(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['c_l']

    def c_h(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['c_h']

    def u_l(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['u_l']

    def u_h(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['u_h']

    def p_default(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['p_default']

    def e_b(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['e_b']

    def e_s(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['e_s']

    def seq_entry(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['seq_entry']

    def fix_price(self):
        return parse_config(self.session.config['config_file'])[self.round_number - 1]['fix_price']


class Group(BaseGroup):

    def min_price(self):
        return self.subsession.u_l - self.subsession.e_b

    def max_price(self):
        return self.subsession.u_h-self.subsession.e_b

    def current_seller(self):
        seller_in_market = self.get_player_by_role('player2')
        return seller_in_market.append(0)

    decision_entry = models.IntegerField(
        initial=0,
        choices=[
            [0, 'B'],
            [1, 'A'],
        ],
        widget=widgets.RadioSelect
    )

    if Subsession.fix_price == 1:
        decision_price = Subsession.p_default
    else:
        decision_price = models.IntegerField(
            min=min_price,
            max=max_price
        )

    decision_buy = models.IntegerField(
        initial=0,
        choices=current_seller(),
        widget=widgets.RadioSelect
    )

    decision_quality = models.IntegerField(
        choices=[
            [0, 'X'],
            [1, 'Y'],
        ],
        widget=widgets.RadioSelect
    )

    def num_of_trade(self):
        num_of_trade = dict()
        for x in self.get_player_by_role('player2'):
            num_of_trade[x] = 0
        for y in self.get_player_by_role('player1'):
            num_of_trade[self.decision_buy[y]] = num_of_trade[self.decision_buy[y]] + 1

    def set_payoffs(self):
        buyer = self.get_player_by_role('player1')
        seller = self.get_player_by_role('player2')
        for p in buyer:
            if self.decision_buy == 0:
                p.payoff = self.subsession.e_b
            elif self.decision_quality == 1:
                p.payoff = self.subsession.u_h - self.subsession.decision_price
            else:
                p.payoff = self.subsession.u_l - self.subsession.decision_price
        for p in seller:
            if self.decision_entry == 0:
                p.payoff = self.subsession.e_s
            elif self.num_of_trade[p] == 0:
                p.payoff = 0
            elif self.decision_quality == 1:
                p.payoff = self.subsession.decision_price - self.subsession.c_h
            else:
                p.payoff = self.subsession.decision_price - self.subsession.c_l


class Player(BasePlayer):

    def role(self):
        if self.id_in_group % 2 == 1:
            return 'player1'
        else:
            return 'player2'









