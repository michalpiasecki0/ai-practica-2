import time
from game import (
    TwoPlayerGameState,
)
from tournament import (
    StudentHeuristic,
)

from typing import Any, Sequence, Callable
import numpy as np

######################
#                    #
#  Helper Functions  #
#                    #
######################

def get_valid_moves(state: TwoPlayerGameState, player_label: Any) -> list:
  """Returns the list of valid moves for the player judging from the board."""
  width = state.game.width
  height = state.game.height
  board = state.board
  enemy_label = state.player2.label if player_label == state.player1.label else state.player1.label
  return [(x, y) for x in range(1, width + 1)
            for y in range(1, height + 1)
            if (x, y) not in board.keys() and
            enemy_captured_by_move(board, (x, y), player_label, enemy_label)]

def enemy_captured_by_move(board: dict, move, player_label: Any, enemy_label: Any) -> list:
  return capture_enemy_in_dir(board, move, player_label, enemy_label, (0, 1)) \
           + capture_enemy_in_dir(board, move, player_label, enemy_label, (1, 0)) \
           + capture_enemy_in_dir(board, move, player_label, enemy_label, (1, -1)) \
           + capture_enemy_in_dir(board, move, player_label, enemy_label, (1, 1))

def capture_enemy_in_dir(board: dict, move, player_label: Any, enemy_label: Any, delta_x_y) -> list:
  (delta_x, delta_y) = delta_x_y
  x, y = move
  x, y = x + delta_x, y + delta_y
  enemy_list_0 = []
  while board.get((x, y)) == enemy_label:
    enemy_list_0.append((x, y))
    x, y = x + delta_x, y + delta_y
  if board.get((x, y)) != player_label:
    del enemy_list_0[:]
  x, y = move
  x, y = x - delta_x, y - delta_y
  enemy_list_1 = []
  while board.get((x, y)) == enemy_label:
    enemy_list_1.append((x, y))
    x, y = x - delta_x, y - delta_y
  if board.get((x, y)) != player_label:
    del enemy_list_1[:]
  return enemy_list_0 + enemy_list_1

def get_potential_moves(state: TwoPlayerGameState, player_label: Any) -> Any:
  checkCells = [(1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (1,1)]
  width = state.game.width
  height = state.game.height 
  board = state.board
  enemy_label = state.player2.label if player_label == state.player1.label else state.player1.label  
  num = 0
  for x, y in board.keys():
    if board.get((x, y)) == enemy_label:
      for direction in checkCells:
        x_check, y_check = tuple(map(sum,zip((x, y),direction)))
        if x_check in range(1, width+1) and y_check in range(1, height+1) and (x_check, y_check) not in board.keys():
          num += 1
  return num

#################
#               #
#   Solution1   #
#               #
#################

class Solution1(StudentHeuristic):
  StudentHeuristic.evaluation_function.counter = 0
  def get_name(self) -> str:
    return "linear"
  def evaluation_function(self, state: TwoPlayerGameState) -> float:
    StudentHeuristic.evaluation_function.counter += 1
    heuristic_components = {
      "parity_heuristic": 1,
      "mobility_heuristic": 1,
      "potentialMobility_heuristic": 1,
      "corners_heuristic": 8,
      "staticWeights_heuristic": 2
    }
    if state.end_of_game:
      heuristic_components = {"parity_heuristic": 13}

    if state.is_player_max(state.player1):
      self.maxMoves = get_valid_moves(state, state.player1.label)
      self.minMoves = get_valid_moves(state, state.player2.label)
    else:
      self.maxMoves = get_valid_moves(state, state.player2.label)
      self.minMoves = get_valid_moves(state, state.player1.label)

    value = 0
    for component, weight in heuristic_components.items():
      value += weight * getattr(self, component)(state)
    return value

  def parity_heuristic(self, state: TwoPlayerGameState) -> float:
    if state.is_player_max(state.player1):
      maxScore = state.scores[0]
      minScore = state.scores[1]
    else:
      maxScore = state.scores[1]
      minScore = state.scores[0]
    heuristic = 100*(maxScore - minScore)/(maxScore + minScore)
    return heuristic

  def mobility_heuristic(self, state: TwoPlayerGameState) -> float:
    maxMoves = len(self.maxMoves)
    minMoves = len(self.minMoves)
    if maxMoves + minMoves != 0:
      heuristic = 100 * (maxMoves - minMoves)/(maxMoves + minMoves)
    else:
      heuristic = 0
    return heuristic

  def potentialMobility_heuristic(self, state: TwoPlayerGameState) -> float:
    if state.is_player_max(state.player1):
      maxMoves = get_potential_moves(state, state.player1.label)
      minMoves = get_potential_moves(state, state.player2.label)
    else:
      maxMoves = get_potential_moves(state, state.player2.label)
      minMoves = get_potential_moves(state, state.player1.label)
    if maxMoves + minMoves != 0:
      heuristic = 100 * (maxMoves - minMoves)/(maxMoves + minMoves)
    else:
      heuristic = 0
    return heuristic

  def corners_heuristic(self, state: TwoPlayerGameState) -> float:
    corners = [(1,1), (1,8), (8,1), (8,8)]
    maxCorners = 0
    minCorners = 0
    commonCorners = 0
    maxPotentialCorners = 0
    minPotentialCorners = 0
    maxLabel = state.player1.label if state.is_player_max(state.player1) else state.player2.label
    for corner in corners:
      if corner in state.board.keys():
        if state.board.get(corner) == maxLabel:
          maxCorners += 1
        else:
          minCorners += 1
      else:
        if corner in self.maxMoves and corner in self.minMoves:
          commonCorners += 1
        elif corner in self.maxMoves:
          maxPotentialCorners +=1
        elif corner in self.minMoves:
          minPotentialCorners += 1
    num = maxCorners - minCorners - commonCorners + maxPotentialCorners - minPotentialCorners
    den = maxCorners + minCorners + commonCorners + maxPotentialCorners + minPotentialCorners
    if num + den != 0:
      heuristic = num/den 
    else:
      heuristic = 0
    return heuristic

  def staticWeights_heuristic(self, state: TwoPlayerGameState) -> float:
    weights = np.array([[4, -3, 2, 2, 2, 2, -3, 4],
                        [-3, -4, -1, -1, -1, -1, -4, -3],
                        [2, -1, 1, 0, 0, 1, -1, 2],
                        [2, -1, 0, 1, 1, 0, -1, 2],
                        [2, -1, 0, 1, 1, 0, -1, 2],
                        [2, -1, 1, 0, 0, 1, -1, 2],
                        [-3, -4, -1, -1, -1, -1, -4, -3],
                        [4, -3, 2, 2, 2, 2, -3, 4]])
    maxLabel = state.player1.label if state.is_player_max(state.player1) else state.player2.label
    maxValue = 0
    minValue = 0
    for cell in state.board.keys():
      if state.board.get(cell) == maxLabel:
        maxValue += weights[cell[0]-1,cell[1]-1]
      else:
        minValue += weights[cell[0]-1,cell[1]-1]
    if maxValue + minValue != 0:
      heuristic = (maxValue - minValue) / (maxValue + minValue)
    else:
      heuristic = 0
    return heuristic

#################
#               #
#   Solution2   #
#               #
#################

class Solution2(StudentHeuristic):
  StudentHeuristic.evaluation_function.counter = 0
  def get_name(self) -> str:
    return "only-corners"
  def evaluation_function(self, state: TwoPlayerGameState) -> float:
    StudentHeuristic.evaluation_function.counter += 1
    if state.end_of_game:
      if state.is_player_max(state.player1):
        maxScore = state.scores[0]
        minScore = state.scores[1]
      else:
        maxScore = state.scores[1]
        minScore = state.scores[0]
      score_difference = maxScore - minScore
      if score_difference > 0:
        return 100
      return -100  
    if state.is_player_max(state.player1):
      maxMoves = get_valid_moves(state, state.player1.label)
      minMoves = get_valid_moves(state, state.player2.label)
    else:
      maxMoves = get_valid_moves(state, state.player2.label)
      minMoves = get_valid_moves(state, state.player1.label)
    corners = [(1,1), (1,8), (8,1), (8,8)]
    maxCorners = 0
    minCorners = 0
    commonCorners = 0
    maxPotentialCorners = 0
    minPotentialCorners = 0
    maxLabel = state.player1.label if state.is_player_max(state.player1) else state.player2.label
    for corner in corners:
      if corner in state.board.keys():
        if state.board.get(corner) == maxLabel:
          maxCorners += 1
        else:
          minCorners += 1
      else:
        if corner in maxMoves and corner in minMoves:
          commonCorners += 1
        elif corner in maxMoves:
          maxPotentialCorners +=1
        elif corner in minMoves:
          minPotentialCorners += 1
    num = maxCorners - minCorners - commonCorners + maxPotentialCorners - minPotentialCorners
    den = maxCorners + minCorners + commonCorners + maxPotentialCorners + minPotentialCorners
    if num + den != 0:
      heuristic = 100 * ( num / den )
    else:
      heuristic = 0
    return heuristic

#################
#               #
#   Solution3   #
#               #
#################

class Solution3(StudentHeuristic):

  StudentHeuristic.evaluation_function.counter = 0
  def get_name(self) -> str:
    return "only-corners-2"
  def evaluation_function(self, state: TwoPlayerGameState) -> float:
    StudentHeuristic.evaluation_function.counter += 1
    if state.end_of_game:
      if state.is_player_max(state.player1):
        maxScore = state.scores[0]
        minScore = state.scores[1]
      else:
        maxScore = state.scores[1]
        minScore = state.scores[0]
      score_difference = maxScore - minScore
      if score_difference > 0:
        return 100
      return -100  
    if state.is_player_max(state.player1):
      maxMoves = get_valid_moves(state, state.player1.label)
      minMoves = get_valid_moves(state, state.player2.label)
    else:
      maxMoves = get_valid_moves(state, state.player2.label)
      minMoves = get_valid_moves(state, state.player1.label)
    corners = [(1,1), (1,8), (8,1), (8,8)]
    maxCorners = 0
    minCorners = 0
    maxLabel = state.player1.label if state.is_player_max(state.player1) else state.player2.label
    for corner in corners:
      if corner in state.board.keys():
        if state.board.get(corner) == maxLabel:
          maxCorners += 1
        else:
          minCorners += 1
    if maxCorners + minCorners != 0:
      heuristic = 100 * ( maxCorners - minCorners ) / ( maxCorners + minCorners )
    else:
      heuristic = 0
    return heuristic
