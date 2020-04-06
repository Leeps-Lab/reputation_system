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
(X,Y) represents seller's product quality decisions.
seq_entry shows the treatment of sequential entry vs simultaneous entry.
fix_price shows the treatment of fixed price vs self-determined price.
"""


class Constants(BaseConstants):

    name_in_url = 'reputation_game'
    num_rounds = 15
    players_per_group = 4
    mid_round = 6
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
            incumbent = [p for p in players if p.id_in_group % 2 == 0 and p.id_in_group % 4 != 0]
            entrant = [p for p in players if p.id_in_group % 2 == 0 and p.id_in_group % 4 == 0]

            group_matrix = []

            while buyer:
                new_group = [
                    buyer.pop(),
                    buyer.pop(),
                    incumbent.pop(),
                    entrant.pop(),
                ]
                group_matrix.append(new_group)

            self.set_group_matrix(group_matrix)
        else:
            self.group_like_round(1)


class Group(BaseGroup):

    def set_payoffs(self):
        player_list = self.get_players()
        for p in player_list:
            if p.role() == 'buyer':
                if p.decision_buy == 0:
                    p.payoff = Constants.e_b
                else:
                    seller = self.get_player_by_id(p.decision_buy)
                    p.payoff = seller.decision_quality * Constants.u_h + (1 - seller.decision_quality) * Constants.u_l - seller.decision_price
            else:
                if p.decision_entry == 0:
                    p.payoff = Constants.e_s
                elif p.num_of_trade() > 0:
                    p.payoff = (p.decision_price - p.decision_quality * Constants.c_h - (1 - p.decision_quality) * Constants.c_l) * p.num_of_trade()
                else:
                    p.payoff = 0

    def seller_in_market(self):
        players = self.get_players()
        seller_in_market = [p for p in players if p.decision_entry == 1]
        return len(seller_in_market)


class Player(BasePlayer):

    def role(self):
        if self.id_in_group % 2 == 1:
            return 'buyer'
        else:
            return 'seller'

    def role2(self):
        if self.id_in_group % 2 == 1:
            return 'buyer'
        elif self.id_in_group % 2 == 0 and self.id_in_group % 4 != 0:
            return 'incumbent'
        else:
            return 'entrant'

    def num_of_trade(self):
        num_of_trade = 0
        player_id = self.id_in_group
        for x in self.get_others_in_group():
            if x.role() == 'buyer' and x.decision_buy == player_id:
                num_of_trade = num_of_trade + 1
        return num_of_trade

    def history_of_seller(self):
        history = []
        current = self.round_number
        for i in range(1, current):
            if self.in_round(i).num_of_trade() > 0 and self.in_round(i).decision_quality == 1:
                history.append({
                'round_number': i,
                'choice': 'Y',
                'price': self.in_round(i).decision_price,
                })
            elif self.in_round(i).num_of_trade() > 0 and self.in_round(i).decision_quality == 0:
                history.append({
                'round_number': i,
                'choice': 'X',
                'price': self.in_round(i).decision_price,
                })
            else:
                history.append({
                'round_number': i,
                'choice': 'N',
                'price': 'N',
                })
        return history

    decision_entry = models.IntegerField(
        initial=0,
        choices=[
            [0, 'No'],
            [1, 'Yes'],
        ],
        widget=widgets.RadioSelect
    )

    decision_price = models.IntegerField()

    def decision_price_min(self):
        price_maximum = (1-Constants.fix_price) * (Constants.u_l - Constants.e_b) + Constants.fix_price * Constants.p_default
        return price_maximum

    def decision_price_max(self):
        price_minimum = (1-Constants.fix_price) * (Constants.u_h - Constants.e_b) + Constants.fix_price * Constants.p_default
        return price_minimum

    decision_buy = models.IntegerField(
        initial=0,
        widget=widgets.RadioSelect,
        blank=True
    )

    def decision_buy_choices(self):
        choices = []
        players = self.get_others_in_group()
        seller_in_market = [p for p in players if p.decision_entry == 1]
        for i in seller_in_market:
            player_id = i.id_in_group
            choices.append(player_id)
        return choices

    decision_quality = models.IntegerField(
        choices=[
            [0, 'X'],
            [1, 'Y'],
        ],
        widget=widgets.RadioSelect
    )


