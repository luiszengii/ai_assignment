from cmath import sqrt
from contextlib import nullcontext
from multiprocessing import parent_process
from xmlrpc.client import boolean
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
        # start a timer of 1s for simulation



        # proceed a MCTS
        # 1. create a root MCT Node 
        root = Node(self.current_agent_index, self.current_agent_index, game_state)

        # 2. select the leaf node with highest UCT
        target_node = root.select()

        # 3. expand the target node
        target_node = 



        return
        

# from interruptingcow import timeout
# try:
#     with timeout(60*5, exception=RuntimeError):
#         while True:
#             test = 0
#             if test == 5:
#                 break
#             test = test - 1
# except RuntimeError:
#     pass

class Node():
    def __init__(self, myAgent_id, curr_player_id, current_state, win_count=0, visited_count=0, parent_node=None, child_nodes=[]):
        self.myAgent_id = myAgent_id
        self.player_id = curr_player_id
        self.win_count = win_count
        self.visited_count = visited_count
        self.parent_node = parent_node
        self.child_nodes = child_nodes
        self.current_state = current_state

    def selection(self):
        # if the root has not been expanded(no child), select the root itself and then proceed to expand
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
            new_child = Node(self.myAgent_id,(target_node.player_id+1)%2, next_state, parent_node=target_node)
            target_node.child_nodes.append(new_child)

    def random_result(self):
        # if the game ends at this state(action), return the winner's id, -1 if tie
        if ReversiGameRule.getLegalActions(self, self.current_state, self.player_id) == "Pass" and ReversiGameRule.getLegalActions(self, self.current_state, (self.player_id+1)%2) == "Pass":
            selfScore = ReversiGameRule.calScore(self, self.current_state, self.player_id)
            opponentScore = ReversiGameRule.calScore(self, self.current_state, (self.player_id+1)%2)
            if selfScore > opponentScore:
                return self.player_id
            if selfScore < opponentScore:
                return (self.player_id+1)%2
            else:
                return -1
        
        # if the game not ends keep randomly choose next action for both self and opponents
        else:
            action = random.choice(ReversiGameRule.getLegalActions(self, self.current_state, self.player_id))
            next_state = ReversiGameRule.generateSuccessor(self, self.current_state, action, self.player_id)
            new_node = Node(self.myAgent_id, (self.player_id+1)%2, next_state, parent_node=self)
            return new_node.random_result()

    def simulation(self):
        for child in self.child_nodes:
            child.visited_count += 1
            # if our agent wins, add child's win count and back propagation
            if child.random_result() == child.myAgent_id or child.random_result() == -1:
                child.win_count += 1
                child.backPropagation(True)
            # if our agent lose, back propagation
            else:
                child.backPropagation(False)


    # called by the child that finised a simulation, updates all parents' win/visit count
    def backPropagation(self, win: boolean):
        if self.parent_node == None:
            return
        
        if win:
            self.parent_node.win_count += 1
            self.parent_node.visited_count += 1
        else:
            self.parent_node.visited_count += 1

        return self.parent_node.backPropagation(win)
                

def UCT(node: Node):
    value = (node.win_count / node.visited_count) + (1.3 * sqrt(node.parent_node.visited_count/node.visited_count))
    return value