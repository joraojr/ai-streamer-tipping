import time
import json

from otree import settings
from otree.api import *

from .image_utils import encode_image
from . import task_sliders

c = Currency

doc = """
This is a test run for the public goods experiment.
"""


##### Scrap country control treatments... #####


######## Models #############

class Constants(BaseConstants):
    name_in_url = 'Part1'
    num_rounds = 10
    players_per_group = 5

    # No leaderboard then False, otherwise True (has to be the same for introduction/init):
    leaderboard = False

    # Leaderboard info (dont touch in general, only topn if there are too few players to display topn which has to be the same for introduction/init)
    leaderboard_topn = 10
    # treatments_F = ['control', 'descriptive_quant', 'descriptive_non_quant', 'injunctive_active', 'injunctive_passive']
    treatments_T = ['control']
    treatments_F = ['control']
    roles = ['streamer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer',
             'viewer',
             'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer',
             'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer', 'viewer',
             'viewer', 'viewer', 'viewer', 'viewer']


class Player(BasePlayer):
    # only suported 1 iteration for now
    bot_assist = models.BooleanField(default=False)

    iteration = models.IntegerField(initial=0)
    minimum_number = models.IntegerField(initial=0)

    num_correct = models.IntegerField(initial=0)
    elapsed_time = models.FloatField(initial=0)
    tip = models.FloatField(initial=0)
    slider_earn = models.FloatField(initial=0)
    round_earn = models.FloatField(initial=0)
    rank = models.IntegerField(initial=0)
    drawn_earnings = models.StringField(initial=0)


def tip_max(player):
    return player.num_correct * 10


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
        sliders={s.idx: {'value': s.value, 'is_correct': s.is_correct, "target": s.target} for s in sliders}
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
    player_instance = player
    session = player_instance.session
    my_id = player_instance.id_in_group
    params = session.config

    now = time.time()

    # the current puzzle or none
    puzzle = get_current_puzzle(player_instance)

    message_type = message['type']

    if message_type == 'load':
        p = get_progress(player_instance)
        if puzzle:
            return {my_id: dict(type='status', progress=p, puzzle=encode_puzzle(puzzle))}
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "new":
        if puzzle is not None:
            raise RuntimeError("trying to create 2nd puzzle")

        player_instance.iteration += 1
        z = generate_puzzle(player_instance)
        p = get_progress(player_instance)

        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    if message_type == "value":
        for p in player.group.get_players():
            puzzle = get_current_puzzle(p)
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
            p.num_correct = puzzle.num_correct

        p = get_progress(player_instance)
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


class Group(BaseGroup):
    tips = models.FloatField(initial=0)
    leaderboard = models.BooleanField(initial=False)
    num_correct = models.IntegerField(initial=0)


########### PAGES  #############
class Subsession(BaseSubsession):
    num_groups_created = models.IntegerField(initial=0)


def creating_session(subsession: Subsession):
    if subsession.session.config['treatment'] == "HUMAN_PAYS_HUMAN":
        for player in subsession.get_players():
            player.bot_assist = True

    # TODO Check if this code is really necessary. Should I have 2 creating session? Here and in the introduction
    if subsession.round_number != 1:
        subsession.group_like_round(1)
    else:
        for player in subsession.get_players():
            participant = player.participant
            participant.account_balance = 0
    # session = subsession.session
    # defaults = dict(
    #     trial_delay=1.0,
    #     retry_delay=0.1,
    #     num_sliders=48,
    #     num_columns=3,
    #     attempts_per_slider=100
    # )
    # session.config = {}
    # for param in defaults:
    #     session.config[param] = session.config.get(param, defaults[param])


class GroupWait(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def after_all_players_arrive(group: Group):
        subsession = group.subsession
        import random
        import itertools
        if Constants.leaderboard is True:
            treatment = itertools.cycle(Constants.treatments_T)
        else:
            treatments = Constants.treatments_F.copy()
            random.shuffle(treatments)
            treatment = itertools.cycle(treatments)
        role_iter = itertools.cycle(Constants.roles)
        rounds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        drawn_rounds = random.sample(rounds, 5)
        drawn_rounds.sort()
        i = 0
        for p in group.get_players():
            if i == 0:
                p1 = p
                params = p.session.config
                num = params['num_sliders']
                layout = task_sliders.generate_layout(params)
                puzzle = Puzzle.create(
                    player=p1, iteration=p1.iteration, timestamp=time.time(),
                    num_sliders=num,
                    layout=json.dumps(layout)
                )
                for j in range(num):
                    target, initial = task_sliders.generate_slider()
                    Slider.create(
                        puzzle=puzzle,
                        idx=j,
                        target=target,
                        value=initial
                    )
            else:
                params = p.session.config
                num = params['num_sliders']
                sliders = Slider.filter(puzzle=puzzle)
                current_puzzle = Puzzle.create(
                    player=p, iteration=p.iteration, timestamp=time.time(),
                    num_sliders=num,
                    layout=json.dumps(layout)
                )
                for j in range(num):
                    Slider.create(
                        puzzle=current_puzzle,
                        idx=j,
                        target=sliders[j].target,
                        value=sliders[j].value
                    )

            # since we want the treatment to persist for all rounds, we need to assign it
            # in a participant field (which persists across rounds)
            # rather than a group field, which is specific to the round.

            if p.round_number == 1:
                p.participant.drawn_rounds = drawn_rounds
                p.participant.earnings_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                if p.participant.leaderboard is False and Constants.leaderboard is True:
                    p.participant.role = "viewer"
                else:
                    p.participant.role = next(role_iter)

                p.participant.treatment = next(treatment)
                p.participant.within_group_id = i + 1
                p.participant.group_id = subsession.num_groups_created
            p.id_in_group = p.participant.within_group_id
            i += 1

        # Whether leaderboard treatment is true for the session or not
        group.leaderboard = Constants.leaderboard
        subsession.num_groups_created += 1

    title_text = "Part 2"
    body_text = "Please wait for the other participants."


class Slider_task(Page):
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
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        puzzle = get_current_puzzle(player)

        if puzzle and puzzle.response_timestamp:
            player.elapsed_time = puzzle.response_timestamp - puzzle.timestamp
            if player.participant.role == "streamer":
                player.group.num_correct = puzzle.num_correct
            if player.participant.role == "viewer":
                player.slider_earn = round(player.group.num_correct * 0.03, 2)
            else:
                player.slider_earn = round(player.group.num_correct * 0.01, 2)
            # player.participant.account_balance = puzzle.num_correct*12
            player.payoff = 0


class part1(Page):
    pass


class Tipping(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.role == 'viewer'

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment

        treatment_text = ""

        if treatment == 'control':
            treatment_text = ""
        elif treatment == 'descriptive_quant':
            treatment_text = "About half of the viewers leave tips."
        elif treatment == 'descriptive_non_quant':
            treatment_text = "Many viewers leave tips."
        elif treatment == 'injunctive_active':
            treatment_text = "Viewers should leave a tip."
        elif treatment == 'injunctive_passive':
            treatment_text = "It's good to leave a tip."

        return dict(
            maxtip=round(player.group.num_correct * 0.03, 2),
            treatment_text=treatment_text
        )

    form_model = "player"
    form_fields = ['tip']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.participant.role == "viewer":
            player.slider_earn = round(player.group.num_correct * 0.03, 2)
        else:
            player.slider_earn = round(player.group.num_correct * 0.01, 2)
        player.group.tips = round(player.group.tips + player.tip, 2)
        if player.participant.role == "viewer":
            player.round_earn = round(player.slider_earn - player.tip, 2)


class Results(Page):

    @staticmethod
    def vars_for_template(player: Player):

        streamer_round_earn = 0

        if player.participant.role == "streamer":
            streamer_round_earn = round(player.slider_earn + player.group.tips, 2)

        if player.group.leaderboard:
            players = player.group.get_players()
            sorted_players = sorted(players, key=lambda x: x.tip, reverse=True)
            top_players = sorted_players[:(Constants.leaderboard_topn)]
            for index, player in enumerate(top_players, start=1):
                player.rank = index

            return dict(players=top_players, streamer_round_earn=streamer_round_earn)

        if player.participant.role == "streamer":
            return dict(streamer_round_earn=streamer_round_earn)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.participant.role == "streamer":
            player.round_earn = round(player.slider_earn + player.group.tips, 2)
        earnings_list = player.participant.earnings_list
        earnings_list[player.round_number - 1] = player.round_earn
        player.participant.earnings_list = earnings_list


class StreamerWait(WaitPage):
    pass


class ExtraWait(WaitPage):
    pass


class Lobby(Page):
    timeout_seconds = 10

    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment=player.session.config["treatment"])


class RandomDraw(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def before_next_page(player, timeout_happened):
        drawn_indices = [x - 1 for x in player.participant.drawn_rounds]
        earnings_list = player.participant.earnings_list
        player.drawn_earnings = str([earnings_list[i] for i in drawn_indices])
        player.participant.drawn_earnings = [earnings_list[i] for i in drawn_indices]
        player.participant.account_balance = round(sum(player.participant.drawn_earnings), 2)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            show_up_fee=player.session.config["participation_fee"],
        )


class RandomDrawResult(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        # TODO double-check this logic

        total_payoff = player.participant.account_balance

        if player.session.config["treatment"] in {"BOT_PAYS_HUMAN", "BOT_PAYS_BOT", "HUMAN_PAYS_HUMAN"}:
            total_payoff -= player.session.config["streamer_deduction"]

        total_payoff = max(total_payoff, 0)
        player.payoff = total_payoff

        total_payoff = round(total_payoff + player.session.config["participation_fee"], 2)

        return dict(
            show_up_fee=player.session.config["participation_fee"],
            total_payoff=total_payoff
        )


## Setting the sequence of the pages shown to the user below
page_sequence = [GroupWait, Lobby, Slider_task, ExtraWait, Tipping, StreamerWait, Results, RandomDraw, RandomDrawResult]
