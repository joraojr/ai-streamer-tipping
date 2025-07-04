from os import environ

SESSION_CONFIGS = [
    dict(
        name='AI_streamer',
        app_sequence=['introduction', 'streaming', 'Questionnaire'],  # 'introduction', 'questionnaire', 'payout_info'
        num_demo_participants=5,
        trial_delay=1.0,
        retry_delay=0.1,
        num_sliders=48,
        num_columns=3,
        attempts_per_slider=100,
    )

]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=4.50,
    doc="",
    bot_assist=False,
    streamers_receive_per_slider=0.02,
    viewers_receive_per_slider=0.06,
    streamer_deduction=1.30,
    treatment='HUMAN_PAYS_HUMAN',
    # [HUMAN_NO_PAY_HUMAN],   # Human plays - Human no pay - Human earns (CONTROL)
    # [HUMAN_PAYS_HUMAN],     # Human plays - Human pays   - Human earns (Bot assist)
    # [BOT_NO_PAY_HUMAN],     # Bot plays   - Human no pay - Human earns
    # [BOT_PAYS_HUMAN],       # Bot plays   - Human pays   - Human earns
    # [BOT_NO_PAY_BOT]        # Bot plays   - Human no pay - Bot earns
    # [BOT_PAYS_BOT],         # Bot plays   - Human pays   - Bot earns
)
# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = 'principalagentgame23'

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

PARTICIPANT_FIELDS = ['account_balance', 'treatment', 'role', 'group_id', 'leaderboard', 'within_group_id',
                      'earnings_list', 'drawn_rounds', 'drawn_earnings']

SECRET_KEY = '2570135731236'

INSTALLED_APPS = ['otree']

# adjustments for testing
# generating session configs for all varieties of features
import sys

if sys.argv[1] == 'test':
    MAX_ITERATIONS = 5
    FREEZE_TIME = 0.1
    TRIAL_PAUSE = 0.2
    TRIAL_TIMEOUT = 0.3

    SESSION_CONFIGS = [
        dict(
            name=f"testing_sliders",
            num_demo_participants=1,
            app_sequence=['sliders'],
            trial_delay=TRIAL_PAUSE,
            retry_delay=FREEZE_TIME,
            num_sliders=50,
            bot_assist=False,
            attempts_per_slider=3,
        ),
    ]
    for task in ['decoding', 'matrix', 'transcription']:
        SESSION_CONFIGS.extend(
            [
                dict(
                    name=f"testing_{task}_defaults",
                    num_demo_participants=1,
                    app_sequence=['real_effort'],
                    puzzle_delay=TRIAL_PAUSE,
                    retry_delay=FREEZE_TIME,
                ),
                dict(
                    name=f"testing_{task}_retrying",
                    num_demo_participants=1,
                    app_sequence=['real_effort'],
                    puzzle_delay=TRIAL_PAUSE,
                    retry_delay=FREEZE_TIME,
                    attempts_per_puzzle=5,
                ),
                dict(
                    name=f"testing_{task}_limited",
                    num_demo_participants=1,
                    app_sequence=['real_effort'],
                    puzzle_delay=TRIAL_PAUSE,
                    retry_delay=FREEZE_TIME,
                    max_iterations=MAX_ITERATIONS,
                ),
            ]
        )
