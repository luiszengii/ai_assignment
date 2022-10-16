import numpy as np
from contextlib import nullcontext
from multiprocessing import parent_process
from xmlrpc.client import boolean
from template import Agent
import random
from Reversi.reversi_model import ReversiGameRule
from Reversi.reversi_utils import Cell,filpColor,boardToString,countScore, GRID_SIZE
import func_timeout

# debugger
import pdb

class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.current_agent_index = _id
        self.num_of_agent = 2
        self.validPos = ReversiGameRule._validPos(self)
        # self.best_action = None
    
    def SelectAction(self,actions,game_state):
        # color info
        self.agent_colors = game_state.agent_colors

        root = Node(self.current_agent_index, self.current_agent_index, current_state=game_state, validPos=self.validPos, agent_colors=self.agent_colors)

        # iterate MCTS for 3 times (for debugging)
        for i in range(3):
            root.MCTS()
        # return the action
        bestWinRate = 0
        bestAction = None
        for child in root.child_nodes:
            winRate = child.win_count/child.visited_count
            if winRate > bestWinRate:
                bestWinRate = winRate
                bestAction = child.actionTaken
        print("NEXT ACTION: ")
        print(bestAction)
        return bestAction


        # start a timer of 0.8s for simulation
        # try:
        #     func_timeout.func_timeout(800, root.MCTS())
        # except func_timeout.FunctionTimedOut:
        #     bestWinRate = 0
        #     bestAction = None
        #     for child in root.child_nodes:
        #         winRate = child.win_count/child.visited_count
        #         if winRate > bestWinRate:
        #             bestWinRate = winRate
        #             bestAction = child.actionTaken
        #     return bestAction


class Node():
    def __init__(self, myAgent_id, curr_player_id, current_state, win_count=0, visited_count=0, parent_node=None, actionTaken = None, validPos = None, agent_colors=None):
        self.current_agent_index = myAgent_id
        self.num_of_agent = 2
        self.validPos = validPos
        self.myAgent_id = myAgent_id
        self.player_id = curr_player_id
        self.win_count = win_count
        self.visited_count = visited_count
        self.parent_node = parent_node
        self.child_nodes = []
        self.current_state = current_state
        self.actionTaken = actionTaken
        self.agent_colors = agent_colors

    # a complete select&expand&simulate&back propagation, a looped in the choose best action method
    def MCTS(self):
        # 1. select the leaf node with highest UCT
        target_node = self.selection()
        # 2. expand the target node
        target_node.expand()
        # 3. simulation
        target_node.simulation()

    # find the leaf of current tree with highest UCT
    def selection(self):
        # if the root has not been expanded(no child), select the root itself and then proceed to expand
        if len(self.child_nodes) == 0:
            return self
        else:
            print(len(self.child_nodes), self.actionTaken, self.parent_node)
            max_UCT = -1
            target_node = None
            for child in self.child_nodes:
                if UCT(child) > max_UCT:
                    max_UCT = UCT(child)
                    target_node = child
            return target_node.selection()

    def expand(self):
        all_actions = ReversiGameRule.getLegalActions(self, game_state=self.current_state, agent_id=self.player_id)
        for action in all_actions:
            next_state = ReversiGameRule.generateSuccessor(self, self.current_state, action, (self.player_id+1)%2)
            new_child = Node(self.myAgent_id,(self.player_id+1)%2, next_state, parent_node=self, actionTaken=action, validPos=self.validPos, agent_colors=self.agent_colors)
            self.child_nodes.append(new_child)

    def random_result(self):
        # if the game ends at this state(action), return the winner's id, -1 if tie
        if ReversiGameRule.getLegalActions(self, self.current_state, self.player_id) == ["Pass"] and ReversiGameRule.getLegalActions(self, self.current_state, (self.player_id+1)%2) == ["Pass"]:
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
            new_node = Node(self.myAgent_id, (self.player_id+1)%2, next_state, parent_node=self, validPos=self.validPos, agent_colors=self.agent_colors)
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
            return self.parent_node.backPropagation(win)
        else:
            self.parent_node.visited_count += 1
            return self.parent_node.backPropagation(win)

def UCT(node: Node):
    value = (node.win_count / node.visited_count) + (1.3 * np.sqrt(node.parent_node.visited_count/node.visited_count))
    return value