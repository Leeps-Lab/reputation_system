from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree.models import subsession
import csv, random

author = 'Shuchen Zhao'
doc = """
This is an n-player trust game with reputation system. 
Players are equally divided into two roles: buyers (A) and sellers (B). 
(M,N) represents sellers's entry decisions. 
(X,Y) represents seller's quality decisions.
p represent the seller's choice of price.
seq_entry shows the treatment of sequential entry vs simultaneous entry.
fix_price shows the treatment of fixed price vs self-determined price.
"""


class Constants(BaseConstants):

    name_in_url = 'reputation_game'
    players_per_group = 4
    num_rounds = 15
    c_l = 5
    c_h = 30
    u_l = 60
    u_h = 95
    p_default = 55
    e_b = 20
    e_s = 10
    seq_entry = 0
    fix_price = 0


class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:

            players = self.get_players()

            buyer = [p for p in players if p.id_in_group % 2 == 1]
            seller = [p for p in players if p.id_in_group % 2 == 0]

            group_matrix = []

            while buyer:
                new_group = [
                    buyer.pop(),
                    buyer.pop(),
                    seller.pop(),
                    seller.pop(),
                ]
                group_matrix.append(new_group)

            self.set_group_matrix(group_matrix)
        else:
            self.group_like_round(1)

    def num_of_rounds(self):
        return random.randint(11, 15)


class Group(BaseGroup):

    def num_of_trade(self, seller_id):
        num_of_trade = 0
        for x in self.get_player_by_role('buyer'):
            if x.decision_buy == seller_id:
                num_of_trade = num_of_trade + 1
        return num_of_trade

    def set_payoffs(self):
        buyer = self.get_player_by_role('buyer')
        seller = self.get_player_by_role('seller')
        for p in buyer:
            if p.decision_buy == 0:
                p.payoff = Constants.e_b
            else:
                seller_id = p.decision_buy
                seller_id = self.get_player_by_id(seller_id)
                p.payoff = seller_id.decision_quality * Constants.u_h + (1-seller_id.decision_quality) * Constants.u_l - seller_id.decision_price
        for p in seller:
            if p.decision_entry == 0:
                p.payoff = Constants.e_s
            else:
                p.payoff = (p.decision_price - p.decision_quality * Constants.c_h - (1-p.decision_quality) * Constants.c_l) * self.num_of_trade(p)


class Player(BasePlayer):

    def role(self):
        if self.id_in_group % 2 == 1:
            return 'buyer'
        else:
            return 'seller'

    decision_entry = models.IntegerField(
        initial=0,
        choices=[
            [0, 'O'],
            [1, 'E'],
        ],
        widget=widgets.RadioSelect
    )

    decision_price = models.IntegerField()

    def decision_price_min(self):
        return (1-Constants.fix_price) * (Constants.u_l - Constants.e_b) + Constants.fix_price * Constants.p_default

    def decision_price_max(self):
        return (1-Constants.fix_price) * (Constants.u_h - Constants.e_b) + Constants.fix_price * Constants.p_default

    decision_buy = models.IntegerField(
        initial=0,
        widget=widgets.RadioSelect
    )

    def decision_buy_choices(self):
        players = self.get_others_in_group()
        current_seller = []
        for p in players:
            if p.decision_entry == 1:
                current_seller.append(p)
        choices = current_seller.append(0)
        return choices

    decision_quality = models.IntegerField(
        choices=[
            [0, 'X'],
            [1, 'Y'],
        ],
        widget=widgets.RadioSelect
    )


