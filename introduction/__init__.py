from otree.api import *
import time
import json
from otree import settings
from .image_utils import encode_image
from . import task_sliders

c = Currency

doc = """
This is a test run for the public goods experiment.
"""


######## Models #############

class Constants(BaseConstants):
    name_in_url = 'intro'
    num_rounds = 1
    players_per_group = None

    # No leaderboard then False, otherwise True (has to be the same for streaming/init):
    leaderboard = False

    # Leaderboard info (dont touch in general, only topn if there are too few players to display topn, which has to be the same for streaming/init)
    leaderboard_topn = 10
    leaderboard_list_T = [False, True]
    leaderboard_list_F = [False]

    PoDIRS_6_SCALES = [
        [1, "I strongly disagree"],
        [2, "I disagree"],
        [3, "I rather disagree"],
        [4, "It is indifferent to me"],
        [5, "I rather agree"],
        [6, "I agree"],
        [7, "I strongly agree"],
    ]

    Likert = [
        [1, 'Strongly disagree'],
        [2, 'Disagree'],
        [3, 'Neither Agree nor Disagree'],
        [4, 'Agree'],
        [5, 'Strongly agree']
    ]


class Player(BasePlayer):
    prolific_id = models.StringField()
    bot_assist = models.BooleanField(default=False)
    comprehension_activity = models.StringField(initial="initialize")
    comprehension_activity1 = models.StringField(initial="initialize")
    iteration = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    elapsed_time = models.FloatField(initial=0)

    """
        LEGEND:
        RT = Risk Taking
        T = TRUST
        A - Altruism
        NR = Negative reciprocity
        PR = Positive reciprocity

    """

    Pr1 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="If someone does me a favor, I am prepared to return it.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    Pr2 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="I go out of my way to help somebody who has been kind to me in the past.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    Pr3 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="I am ready to assume personal costs to help somebody who helped me in the past.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    Nr1 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="If I suffer a serious wrong, I will take revenge as soon as possible, no matter what the cost.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    Nr2 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="If somebody puts me in a difficult position, I will do the same to him/her.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    Nr3 = models.StringField(
        choices=Constants.PoDIRS_6_SCALES,
        label="If somebody offends me, I will offend him/her back.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )

    BAII_1 = models.StringField(
        choices=Constants.Likert,
        label="Bots that can perform this kind of task better than humans make me uncomfortable.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    BAII_2 = models.StringField(
        choices=Constants.Likert,
        label="Bots that can perform this kind of task go against what I believe computers should be used for.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    BAII_3 = models.StringField(
        choices=Constants.Likert,
        label="Bots that can perform this kind of task are unsettling.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    BAII_4 = models.StringField(
        choices=Constants.Likert,
        label="I can see the benefits in bots that can perform this kind of task better than humans.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )
    BAII_5 = models.StringField(
        choices=Constants.Likert,
        label="I believe this kind of bot can perform well.",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )

    BAI_1 = models.StringField(
        choices=Constants.Likert,
        label="How much confidence do you have in the bot's performance at the slider task?",
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )

    BAI_2 = models.IntegerField(
        label="How much confidence do you have in your own performance at the slider task?",
        choices=Constants.Likert,
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )

    BAI_3 = models.IntegerField(
        label="How likely is the bot to make a really bad performance?",
        choices=list(range(0, 9)),
        widget=widgets.RadioSelectHorizontal(),
        blank=False
    )


class Group(BaseGroup):
    pass


########### PAGES  #############
class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    import itertools

    if Constants.leaderboard is True:
        leaderboard_iter = itertools.cycle(Constants.leaderboard_list_T)
    else:
        leaderboard_iter = itertools.cycle(Constants.leaderboard_list_F)
    for p in subsession.get_players():
        p.participant.leaderboard = next(leaderboard_iter)


# puzzle-specific stuff


class Puzzle(ExtraModel):
    """A model to keep record of sliders setup"""

    player = models.Link(Player)
    iteration = models.IntegerField()
    timestamp = models.FloatField()

    num_sliders = models.IntegerField()
    layout = models.LongStringField()

    response_timestamp = models.FloatField()
    num_correct = models.IntegerField(initial=0)
    is_solved = models.BooleanField(initial=False)


class Slider(ExtraModel):
    """A model to keep record of each slider"""

    puzzle = models.Link(Puzzle)
    idx = models.IntegerField()
    target = models.IntegerField()
    value = models.IntegerField()
    is_correct = models.BooleanField(initial=False)
    attempts = models.IntegerField(initial=0)


def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    params = player.session.config
    num = params['num_sliders']
    layout = task_sliders.generate_layout(params)
    puzzle = Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(),
        num_sliders=num,
        layout=json.dumps(layout)
    )
    for i in range(num):
        target, initial = task_sliders.generate_slider()
        Slider.create(
            puzzle=puzzle,
            idx=i,
            target=target,
            value=initial
        )
    return puzzle


def get_current_puzzle(player):
    puzzles = Puzzle.filter(player=player, iteration=player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle


def get_slider(puzzle, idx):
    sliders = Slider.filter(puzzle=puzzle, idx=idx)
    if sliders:
        [puzzle] = sliders
        return puzzle


def encode_puzzle(puzzle: Puzzle):
    """Create data describing puzzle to send to client"""
    layout = json.loads(puzzle.layout)
    sliders = Slider.filter(puzzle=puzzle)
    # generate image for the puzzle
    image = task_sliders.render_image(layout, targets=[s.target for s in sliders])
    return dict(
        image=encode_image(image),
        size=layout['size'],
        grid=layout['grid'],
        sliders={s.idx: {'value': s.value, 'is_correct': s.is_correct} for s in sliders}
    )


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        iteration=player.iteration,
        solved=player.num_correct
    )


def handle_response(puzzle, slider, value, bot_assist):
    slider.value = task_sliders.snap_value(value, slider.target)
    # if bot_assitant treatment:
    if bot_assist:
        if abs(slider.value - slider.target) <= 15:  # 5%
            slider.is_correct = True
            slider.value = slider.target
        else:
            slider.is_correct = False
    else:
        slider.is_correct = slider.value == slider.target
    puzzle.num_correct = len(Slider.filter(puzzle=puzzle, is_correct=True))
    puzzle.is_solved = puzzle.num_correct == puzzle.num_sliders


def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from browser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'puzzle': data}
      in case of midgame page reload

    - receive: {'type': 'new'} -- request for a new puzzle
    - generate new sliders
    - respond: {'type': 'puzzle', 'puzzle': data}

    - receive: {'type': 'value', 'slider': ..., 'value': ...} -- submitted value of a slider
      - slider: the index of the slider
      - value: the value of slider in pixels
    - check if the answer is correct
    - respond: {'type': 'feedback', 'slider': ..., 'value': ..., 'is_correct': ..., 'is_completed': ...}
      - slider: the index of slider submitted
      - value: the value aligned to slider steps
      - is_corect: if submitted value is correct
      - is_completed: if all sliders are correct
    """
    session = player.session
    my_id = player.id_in_group
    params = session.config

    now = time.time()
    # the current puzzle or none
    puzzle = get_current_puzzle(player)

    message_type = message['type']
    if message_type == 'load':
        p = get_progress(player)
        if puzzle:
            return {my_id: dict(type='status', progress=p, puzzle=encode_puzzle(puzzle))}
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "new":
        if puzzle is not None:
            raise RuntimeError("trying to create 2nd puzzle")

        player.iteration += 1
        z = generate_puzzle(player)
        p = get_progress(player)

        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    if message_type == "value":
        if puzzle is None:
            raise RuntimeError("missing puzzle")
        if puzzle.response_timestamp and now < puzzle.response_timestamp + params["retry_delay"]:
            raise RuntimeError("retrying too fast")

        slider = get_slider(puzzle, int(message["slider"]))

        if slider is None:
            raise RuntimeError("missing slider")
        if slider.attempts >= params['attempts_per_slider']:
            raise RuntimeError("too many slider motions")

        value = int(message["value"])

        handle_response(puzzle, slider, value, player.bot_assist)
        puzzle.response_timestamp = now
        slider.attempts += 1
        player.num_correct = puzzle.num_correct

        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                slider=slider.idx,
                value=slider.value,
                is_correct=slider.is_correct,
                is_completed=puzzle.is_solved,
                progress=p,
            )
        }

    if message_type == "cheat" and settings.DEBUG:
        return {my_id: dict(type='solution', solution={s.idx: s.target for s in Slider.filter(puzzle=puzzle)})}

    raise RuntimeError("unrecognized message from client")


class Introduction(Page):
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.prolific_id = player.participant.label


class Explanation1(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            treatment=player.session.config['treatment'],
            streamer_deduction=cu(player.session.config['streamer_deduction'])
        )


class Explanation1a(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            treatment=player.session.config['treatment'],
            streamer_deduction=cu(player.session.config['streamer_deduction'])
        )


class Explanation1b(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            treatment=player.session.config['treatment'],
            streamer_deduction=cu(player.session.config['streamer_deduction'])
        )


class Demo(Page):
    timeout_seconds = 45
    live_method = play_game

    @staticmethod
    def js_vars(player: Player):
        return dict(
            params=player.session.config,
            slider_size=task_sliders.SLIDER_BBOX,
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            params=player.session.config,
            DEBUG=settings.DEBUG,
            treatment=player.session.config['treatment'],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        puzzle = get_current_puzzle(player)

        if puzzle and puzzle.response_timestamp:
            player.elapsed_time = puzzle.response_timestamp - puzzle.timestamp
            player.num_correct = puzzle.num_correct
            player.payoff = player.num_correct


class Explanation1c(Page):
    @staticmethod
    def vars_for_template(player: Player):
        solved_sliders = 10
        return dict(
            solved_sliders=solved_sliders,
            viewers_receive_per_slider=cu(player.session.config['viewers_receive_per_slider']),
            streamers_receive_per_slider=cu(player.session.config['streamers_receive_per_slider']),
            performance_streamers=cu(player.session.config['streamers_receive_per_slider']) * solved_sliders,
            performance_viewers=cu(player.session.config['viewers_receive_per_slider']) * solved_sliders
        )


class Explanation2(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            treatment=player.session.config['treatment'],
        )


class Explanation3(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            show_up_fee=player.session.config['participation_fee'],
            treatment=player.session.config['treatment']
        )


class Comprehension(Page):
    @staticmethod
    def live_method(player, data):
        epoch_time = int(time.time())
        to_export = [data["which_option"], data["which_question"], epoch_time, player.participant.code]
        player.comprehension_activity = player.field_maybe_none("comprehension_activity") + "," + str(to_export)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            show_up_fee=player.session.config['participation_fee'],
            viewers_receive_per_slider=cu(player.session.config['viewers_receive_per_slider']),
            streamers_receive_per_slider=cu(player.session.config['streamers_receive_per_slider']),
            treatment=player.session.config['treatment'],
        )


class Part0(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            show_up_fee=player.session.config['participation_fee'],
        )


class Part1(Page):
    pass


class PreSurvey(Page):
    form_model = 'player'
    form_fields = ['Pr1', 'Pr2', 'Pr3', 'Nr1', 'Nr2', 'Nr3']


class BotAversionII(Page):
    form_model = 'player'
    form_fields = [
        'BAII_1',
        'BAII_2',
        'BAII_3',
        'BAII_4',
        'BAII_5',
    ]


class BotAversionI1(Page):
    @staticmethod
    def is_displayed(player):
        return player.session.config['treatment'] in ["BOT_PAYS_HUMAN", "BOT_NO_PAY_HUMAN", "BOT_PAYS_BOT", "BOT_NO_PAY_BOT"]

    form_model = 'player'
    form_fields = [
        'BAI_1',
        'BAI_2',
    ]


class BotAversionI2(Page):
    @staticmethod
    def is_displayed(player):
        return player.session.config['treatment'] in ["BOT_PAYS_HUMAN", "BOT_NO_PAY_HUMAN", "BOT_PAYS_BOT", "BOT_NO_PAY_BOT"]

    form_model = 'player'
    form_fields = [
        'BAI_3',
    ]


## Setting the sequence of the pages shown to the user below
page_sequence = [
    Part0, Part1, PreSurvey,
    Introduction, Explanation1, Explanation1a, BotAversionII, Explanation1b, Explanation1c, BotAversionI1, BotAversionI2,
    Explanation2,
    Explanation3,
    Comprehension,
    Demo
]

# page_sequence = [Demo]
