from template import Agent
import random
from Reversi.reversi_model import ReversiGameRule
from Reversi.reversi_utils import Cell,filpColor,boardToString,countScore, GRID_SIZE

class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.current_agent_index = _id
        self.num_of_agent = 2
        self.validPos = ReversiGameRule._validPos(self)
        # self.best_action = None
    
    def SelectAction(self,actions,game_state):
        return random.choice(actions)
class tree():
    def __init__(self, player_id, current_state, win_count=0, visited_count=0, parent_node=None, child_nodes=[]):
        self.player_id = player_id
        self.win_count = win_count
        self.visited_count = visited_count
        self.parent_node = parent_node
        self.child_nodes = child_nodes
        self.current_state = current_state
    def selection(self):
        if len(self.child_nodes) == 0:
            return self
        else:
            max_UCT = 0
            target_node = None
            for child in self.child_nodes:
                if UCT(child) > max_UCT:
                    max_UCT = UCT(child)
                    target_node = child
            return target_node.selection()

    def expand(self, target_node):
        all_actions = ReversiGameRule.getLegalActions(self, game_state=target_node.current_state, agent_id=target_node.player_id)
        for action in all_actions:
            next_state = ReversiGameRule.generateSuccessor(self, target_node.current_state, action, (target_node.player_id+1)%2)
            new_child = tree((target_node.player_id+1)%2, next_state, 0, 0, target_node)
            target_node.child_nodes.append(new_child)

    


    # def UCT(node):

