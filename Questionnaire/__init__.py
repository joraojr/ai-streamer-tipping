import csv
from otree.api import *
import itertools
import random
import time

doc = """
Demo of o-Tree Questionnaire
"""


class Constants(BaseConstants):
    name_in_url = 'Questionnaire'
    players_per_group = None
    num_rounds = 1

    Likert = [
        [1, 'Strongly disagree'],
        [2, 'Disagree'],
        [3, 'Neither Agree nor Disagree'],
        [4, 'Agree'],
        [5, 'Strongly agree']
    ]

    Tipping_behaviour = [
        [1, 'Never'],
        [2, 'Rarely'],
        [3, 'Occasionally'],
        [4, 'Frequently'],
        [5, 'Always']
    ]


    Social_norms = [
        [1, 'Extremely uncharacteristic'],
        [2, 'Somewhat uncharacteristic'],
        [3, 'Uncertain'],
        [4, 'Somewhat characteristic'],
        [5, 'Extremely characteristic'],
    ]



    ####### ON the side font-weight: normal; header still bold.

    #########


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):




    QA1 = models.IntegerField(label='Receiving round earnings from streaming made me feel happy',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA2 = models.IntegerField(label='I had unpleasant feelings about receiving round earnings',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA3 = models.IntegerField(label='Receiving round earnings from streaming made me feel good',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA4 = models.IntegerField(label='Receiving round earnings from streaming made me feel bad',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA5 = models.IntegerField(label='Tipping the streamer made me feel happy',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA6 = models.IntegerField(label='I had unpleasant feelings about tipping the streamer',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA7 = models.IntegerField(label='Tipping the streamer made me feel good',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA8 = models.IntegerField(label='Tipping the streamer made me feel bad',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA9 = models.IntegerField(label="The streamer's performance made me feel happy",choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA10 = models.IntegerField(label="I had unpleasant feelings about the streamer's performance",choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA11 = models.IntegerField(label="The streamer's performance made me feel good",choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA12 = models.IntegerField(label="The streamer's performance made me feel bad",choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())

    QA13 = models.IntegerField(label='Have you ever tipped a streamer while watching a live-stream?',choices=Constants.Tipping_behaviour,widget=widgets.RadioSelectHorizontal())

    QA14 = models.IntegerField(label='The presence of a leaderboard during the results enhanced my experience.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA15 = models.IntegerField(label='I actively paid attention to the leaderboard during the results.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA16 = models.IntegerField(label='I appreciate seeing who has tipped the most during the results.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA17 = models.IntegerField(label='The presence of a tipping leaderboard influenced my decision to tip.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())

    QA18 = models.IntegerField(label='I want to support the streamer without expecting any compensation.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA19 = models.IntegerField(label='I enjoy supporting the streamer during the livestream, even if it involves some cost to myself.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA20 = models.IntegerField(label='I deeply enjoy helping the streamer through contributions, even if I have to make sacrifices.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA21 = models.IntegerField(label='I contribute to the streamer to match the contributions of others who have already contributed.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA22 = models.IntegerField(label='I see contributing to the streamer as a competition with other viewers.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA23 = models.IntegerField(label='I seek to contribute more to the streamer than other viewers have.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())

    QA24 = models.IntegerField(label='I want to receive recognition from other viewers on the livestream platform.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA25 = models.IntegerField(label='I am aiming to be recognized by other viewers on the livestream platform.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA26 = models.IntegerField(label='I hope to receive acknowledgement from the livestreamer based on my contributions.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA27 = models.IntegerField(label='I want to impress other viewers on the livestream.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA28 = models.IntegerField(label='I am aiming to give a positive impression to other viewers on the livestream.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA29 = models.IntegerField(label='I want the streamer to have a positive image of me based on my behavior during the livestream.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA30 = models.IntegerField(label='I contribute to a livestream in which many other viewers have already contributed.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA31 = models.IntegerField(label='I follow the contributions of other viewers in deciding whether or not to contribute to a livestream.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())
    QA32 = models.IntegerField(label='I would contribute to a livestream because many other viewers have already contributed to it.',choices=Constants.Likert,widget=widgets.RadioSelectHorizontal())

    QA33 = models.IntegerField(label='I go out of my way to follow social norms.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA34 = models.IntegerField(label='We shouldn’t always have to follow a set of social rules.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA35 = models.IntegerField(label='People should always be able to behave as they wish rather than trying to fit the norm.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA36 = models.IntegerField(label='People need to follow life’s unwritten rules every bit as strictly as they follow the written rules.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA37 = models.IntegerField(label='People who do what society expects of them lead happier lives.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA38 = models.IntegerField(label='Our society is built on unwritten rules that members need to follow.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA39 = models.IntegerField(label='I am at ease only when everyone around me is adhering to society’s norms.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA40 = models.IntegerField(label='We would be happier if we didn’t try to follow society’s norms.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())
    QA41 = models.IntegerField(label='I always do my best to follow society’s rules.',choices=Constants.Social_norms,widget=widgets.RadioSelectHorizontal())

    age = models.IntegerField(
        label="What is your age?",
        min=14,
        max=100
    )

    gender = models.StringField(
        label="What is your gender?",
        choices=["Male","Female","Other","Prefer not to say"]
    )

    subject = models.StringField(
        label="Which subject are you primarily enrolled in?",
        choices=["Economics/Business","Law","Humanities","Science/Engineering","None/Other"]
    )

    religion = models.StringField(
        label="Do you consider yourself a religious person?",
        choices=["Strongly Disagree","Disagree","Neither Agree nor Disagree","Agree","Strongly Agree"]
    )

    volunteer = models.StringField(
        label="Do you actively engage as a volunteer for an NGO, non-profit, or something similar?",
        choices=["Yes","No"]
    )


class part3(Page):
    pass

class S1(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer"

    form_model = 'player'
    form_fields = [
    'QA1',
    'QA2',
    'QA3',
    'QA4']

class S1a(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer"

    form_model = 'player'
    form_fields = [
    'QA5',
    'QA6',
    'QA7',
    'QA8']

class S1b(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer"

    form_model = 'player'
    form_fields = [
    'QA9',
    'QA10',
    'QA11',
    'QA12']

class S2(Page):
    form_model = 'player'
    form_fields = ['QA13']

class S3(Page):

    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer" and player.participant.leaderboard

    form_model = 'player'
    form_fields = [
    'QA14',
    'QA15',
    'QA16',
    'QA17']

class S4(Page):

    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer"

    form_model = 'player'
    form_fields = [
    'QA18',
    'QA19',
    'QA20',
    'QA21',
    'QA22',
    'QA23']

class S5(Page):

    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer" and player.participant.leaderboard

    form_model = 'player'
    form_fields = [
    'QA24',
    'QA25',
    'QA26',
    'QA27',
    'QA28',
    'QA29',
    'QA30',
    'QA31',
    'QA32']

class S6(Page):

    @staticmethod
    def is_displayed(player):
        return player.participant.role == "viewer"

    form_model = 'player'
    form_fields = [
    'QA33',
    'QA34',
    'QA35',
    'QA36',
    'QA37',
    'QA38',
    'QA39',
    'QA40',
    'QA41']

class Demo(Page):
    form_model = 'player'
    form_fields = [
    'gender',
    'age',
    'subject',
    'religion',
    'volunteer']

#The prime key is: 544877

class finalpage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        total_with_showup = round(player.participant.account_balance + 2.5,3)
        masked_payment = (total_with_showup*544877)
        return dict(
            total_with_showup=total_with_showup,
            masked_payment=masked_payment)

page_sequence = [
part3, S1, S1a, S1b, S2, S3, S4, S5, S6, Demo, finalpage
]
