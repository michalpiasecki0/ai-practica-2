"""Heuristics to evaluate board.

    Authors:
        Fabiano Baroni <fabiano.baroni@uam.es>,
        Alejandro Bellogin <alejandro.bellogin@uam.es>
        Alberto Suárez <alberto.suarez@uam.es>

"""


from __future__ import annotations  # For Python 3.7

from typing import Callable, Sequence

import numpy as np

from game import TwoPlayerGameState

from reversi import from_dictionary_to_array_board


class Heuristic(object):
    """Encapsulation of the evaluation fucnction."""

    def __init__(
        self,
        name: str,
        evaluation_function: Callable[[TwoPlayerGameState], float],
    ) -> None:
        """Initialize name of heuristic & evaluation function."""
        self.name = name
        self.evaluation_function = evaluation_function

    def evaluate(self, state: TwoPlayerGameState) -> float:
        """Evaluate a state."""
        # Prevent modifications of the state.
        # Deep copy everything, except attributes related
        # to graphical display.
        state_copy = state.clone()
        return self.evaluation_function(state_copy)

    def get_name(self) -> str:
        """Name getter."""
        return self.name


def simple_evaluation_function(state: TwoPlayerGameState) -> float:
    """Return a random value, except for terminal game states."""
    state_value = 2*np.random.rand() - 1
    simple_evaluation_function.counter += 1
    if state.end_of_game:
        scores = state.scores
        # Evaluation of the state from the point of view of MAX

        assert isinstance(scores, (Sequence, np.ndarray))
        score_difference = scores[0] - scores[1]

        if state.is_player_max(state.player1):
            state_value = score_difference
        elif state.is_player_max(state.player2):
            state_value = - score_difference
        else:
            raise ValueError('Player MAX not defined')

    return state_value

def count_pieces(state: TwoPlayerGameState) -> float:
    "Return difference between white points and black points"
    count_pieces.counter += 1
    scores = state.scores

    # Evaluation of the state from the point of view of MAX
    assert isinstance(scores, (Sequence, np.ndarray))
    score_difference = scores[0] - scores[1]


    if state.is_player_max(state.player1):
        return score_difference
    elif state.is_player_max(state.player2):
        return -score_difference
    else:
        raise ValueError('Player MAX not defined')


def count_both_pieces_possible_catches(state: TwoPlayerGameState) -> float:
    """
    this functions takes into account number of player's pieces and number of pieces of enemy which can be captured in next move

    :state: current state of a game
    :return: value of heuristic for a given state
    """

    count_both_pieces_possible_catches.counter += 1
    scores = state.scores
    current_board = state.board
    player_sign = state.next_player.name
    if player_sign == "B":
        enemy_sign = "W"
    else:
        enemy_sign = "B"

    possible_positions = generate_all_possible_positions(state=state)
    enemy_positions = generate_all_enemy_positions(state=state, enemy_sign=enemy_sign)
    n_pieces_to_catch = count_how_many_enemies_could_you_catch(state=state, enemy_positions=enemy_positions, possible_positions=possible_positions, player_sign=player_sign)

    assert isinstance(scores, (Sequence, np.ndarray))
    score_difference = scores[0] - scores[1]

    if state.is_player_max(state.player1):
        return score_difference + n_pieces_to_catch
    elif state.is_player_max(state.player2):
        return -score_difference + n_pieces_to_catch
    else:
        raise ValueError('Player MAX not defined')

def generate_all_possible_positions(state: TwoPlayerGameState) -> list:
    """
    function returns a list with all possible positions

    :state: current state of a game
    :return: set of elements where piece can be placed, each element in format (x,y)
    """

    all_possible = set()
    for i in range(1, 9):
        for j in range(1, 9):
            all_possible.add((i, j))
    occupied_places = set()
    for k, v in state.board.items():
        occupied_places.add(k)
    all_possible_places = all_possible - occupied_places
    return list(all_possible)


def generate_all_enemy_positions(state: TwoPlayerGameState, enemy_sign: str) -> list:
    """
    function returns a list with all enemy positions

    :state: current state of a game
    :enemy_sign: sign of an opponent: either 'B' or 'W'
    :return: list of all enemy positions where every element is in format (x,y)
    """

    current_board = state.board
    all_enemy_positions = []

    for k in current_board.keys():
        if current_board[k] == enemy_sign:
            all_enemy_positions.append(k)
    return all_enemy_positions

def check_if_you_can_catch_this_point(x: int, y: int, state: TwoPlayerGameState, all_possible: list, player_sign) -> bool:
    """
       for a given oppoonent's point (x,y) function checks if in next move you can grab it in any manner (vertically, horizontally itd)

       :x: x-coordinate of enemy point
       :y: y-coordiante of enemy point
       :state: current state of a game
       :all_possible: list of all possible points where you COULD place a piece. in practice this mean all positions which ARE NOTin dictionary of a state.board
       :return: True if u can check this point, False otherwise
    """
    board = state.board

    # horizontally
    if 1 < x < 8:
        if ((x - 1, y) in all_possible) ^ ((x + 1, y) in all_possible):
            if (x - 1, y) in all_possible:
                if board[x + 1, y] == player_sign:
                    return True
            if (x + 1, y) in all_possible:
                if board[x - 1, y] == player_sign:
                    return True
    # vertically
    if 1 < y < 8:
        if ((x, y - 1) in all_possible) ^ ((x, y + 1) in all_possible):
            if (x, y - 1) in all_possible:
                if board[x, y + 1] == player_sign:
                    return True
            if (x, y + 1) in all_possible:
                if board[x, y - 1] == player_sign:
                    return True
    # diagonally left bottom - right upper
    if 1 < x < 8 and 1 < y < 8:
        if ((x - 1, y - 1) in all_possible) ^ ((x + 1, y + 1) in all_possible):
            if (x - 1, y - 1) in all_possible:
                if board[x + 1, y + 1] == player_sign:
                    return True
            if (x + 1, y + 1) in all_possible:
                if board[x - 1, y - 1] == player_sign:
                    return True
    # diagonally left upper - right bottom
    if 1 < x < 8 and 1 < y < 8:
        if ((x - 1, y + 1) in all_possible) ^ ((x + 1, y - 1) in all_possible):
            if (x - 1, y + 1) in all_possible:
                if board[x + 1, y - 1] == player_sign:
                    return True
            if (x + 1, y - 1) in all_possible:
                if board[x - 1, y + 1] == player_sign:
                    return True
    return False
def count_how_many_enemies_could_you_catch(state: TwoPlayerGameState,enemy_positions: list, possible_positions: list, player_sign: str) -> float:
    """

    """
    counter = 0
    for el in enemy_positions:
        if check_if_you_can_catch_this_point(el[0], el[1], state, possible_positions, player_sign):
            counter = counter + 1
    return counter


heuristic = Heuristic(name='Simple heuristic', evaluation_function=simple_evaluation_function)
heuristic_2 = Heuristic(name="still_simple_heuristic", evaluation_function=count_pieces)
heuristic_3 = Heuristic(name="added_possible_catches", evaluation_function=count_both_pieces_possible_catches)