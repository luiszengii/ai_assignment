from Reversi.reversi_model import ReversiGameRule
from template import Agent
import random
from Reversi.reversi_utils import Cell,filpColor,boardToString,countScore, GRID_SIZE


class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.current_agent_index = _id
        self.num_of_agent = 2
        self.validPos = ReversiGameRule._validPos(self)
        # self.best_action = None
    
    def SelectAction(self,actions,game_state):
        # initialize alpha and beta
        alpha = -float('inf')
        beta = float('inf')
        self.agent_colors = game_state.agent_colors
        
        _, best_action = self.minimax(alpha=alpha, beta=beta, actions=actions, game_state=game_state, depth=2, maxOrNot=True)
        # if we are at the corner, we choose the corner grid
        if (0,0) in actions:
            return (0,0)
        if (0,GRID_SIZE-1) in actions:
            return (0,GRID_SIZE-1)
        if (GRID_SIZE-1,0) in actions:
            return (GRID_SIZE-1,0)
        if (GRID_SIZE-1,GRID_SIZE-1) in actions:
            return (GRID_SIZE-1,GRID_SIZE-1)
        return best_action
# the below code is reference to the wikipedia pseudo code.
# https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning#:~:text=Alpha%E2%80%93beta%20pruning%20is%20a%20search%20algorithm%20that%20seeks,of%20two-player%20games%20%28Tic-tac-toe%2C%20Chess%2C%20Connect%204%2C%20etc.%29.
    def minimax(self, game_state, actions, depth, alpha, beta, maxOrNot):
        best_action = ''
        if depth == 0 or ((ReversiGameRule.getLegalActions(self, game_state=game_state, agent_id=0) == 'Pass') and (ReversiGameRule.getLegalActions(self, game_state=game_state, agent_id=1) == 'Pass')):
            score = ReversiGameRule.calScore(self, game_state=game_state, agent_id=self.id)
            return score, ''
        elif maxOrNot:
            
            value = -float('inf')
            for a in actions:
                successor_state = ReversiGameRule.generateSuccessor(self, state=game_state, action=a, agent_id=self.id)
                valid_actions = ReversiGameRule.getLegalActions(self, game_state=successor_state, agent_id=self.id)

                new_value, _ = self.minimax(successor_state, valid_actions, depth-1, alpha, beta, False)
                value = max(value, new_value)
                if value == new_value:
                    best_action = a
                if value >= beta:
                    break
                alpha = max(alpha, value)
            return value, best_action

        else:
            value = float('inf')
            for a in actions:
                successor_state = ReversiGameRule.generateSuccessor(self, state=game_state, action=a, agent_id=ReversiGameRule.getNextAgentIndex(self))
                valid_actions = ReversiGameRule.getLegalActions(self, game_state=successor_state, agent_id=ReversiGameRule.getNextAgentIndex(self))
                new_value, _ = self.minimax(successor_state, valid_actions, depth-1, alpha, beta, True)
                value = min(value, new_value)
                if value == new_value:
                    best_action = a
                if value <= alpha:
                    break
                beta = min(beta, value)
            return value, best_action
