"""Illustration of tournament.

Authors:
    Alejandro Bellogin <alejandro.bellogin@uam.es>

"""

from __future__ import annotations  # For Python 3.7

import time
import timeit

import numpy as np

from game import Player, TwoPlayerGameState, TwoPlayerMatch
from heuristic import simple_evaluation_function, count_pieces, count_both_pieces_possible_catches
from reversi import (
    Reversi,
    from_array_to_dictionary_board,
    from_dictionary_to_array_board,
)
from tournament import StudentHeuristic, Tournament


class Heuristic1(StudentHeuristic):

    def get_name(self) -> str:
        return "player"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Use an auxiliary function.
        return count_pieces(state)

    def dummy(self, n: int) -> int:
        return n + 4


class Heuristic2(StudentHeuristic):

    def get_name(self) -> str:
        return "count all"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        return count_both_pieces_possible_catches(state)


class Heuristic3(StudentHeuristic):

    def get_name(self) -> str:
        return "count pieces"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        return count_pieces(state)


def create_match(player1: Player, player2: Player) -> TwoPlayerMatch:

    initial_board = None
    #np.zeros((dim_board, dim_board))
    initial_player = player1

    """game = TicTacToe(
        player1=player1,
        player2=player2,
        dim_board=dim_board,
    )"""

    initial_board = (
        ['..B.B..',
        '.WBBW..',
        'WBWBB..',
        '.W.WWW.',
        '.BBWBWB']
    )

    if initial_board is None:
        height, width = 8, 8
    else:
        height = len(initial_board)
        width = len(initial_board[0])
        try:
            initial_board = from_array_to_dictionary_board(initial_board)
        except ValueError:
            raise ValueError('Wrong configuration of the board')
        else:
            print("Successfully initialised board from array")

    game = Reversi(
        player1=player1,
        player2=player2,
        height=8,
        width=8
    )

    game_state = TwoPlayerGameState(
        game=game,
        board=initial_board,
        initial_player=initial_player,
    )

    return TwoPlayerMatch(game_state, max_seconds_per_move=1000, gui=False)

simple_evaluation_function.counter = 0
count_both_pieces_possible_catches.counter = 0
count_pieces.counter = 0
start = time.time()
tour = Tournament(max_depth=3, init_match=create_match)
#strats = {'opt1': [Heuristic1], 'opt2': [Heuristic1]}
strats = {'opt1': [Heuristic3], 'opt2': [Heuristic3]}
n = 1
scores, totals, names = tour.run(
    student_strategies=strats,
    increasing_depth=False,
    n_pairs=1,
    allow_selfmatch=False,
)
elapsed = time.time() - start
print(
    'Results for tournament where each game is repeated '
    + '%d=%dx2 times, alternating colors for each player' % (2 * n, n),
)

# print(totals)
# print(scores)

print('\ttotal:', end='')
for name1 in names:
    print('\t%s' % (name1), end='')
print()
for name1 in names:
    print('%s\t%d:' % (name1, totals[name1]), end='')
    for name2 in names:
        if name1 == name2:
            print('\t---', end='')
        else:
            print('\t%d' % (scores[name1][name2]), end='')
    print()

print(f'Time needed to perform tournament with pruning: {elapsed}')
#print(f'Number of simple function execution {simple_evaluation_function.counter}')
#print(f'Number of simple function execution {count_both_pieces_possible_catches.counter}')
print(f'Number of simple function execution {count_pieces.counter}')