import numpy as np
from contextlib import nullcontext
from multiprocessing import parent_process
from xmlrpc.client import boolean
from template import Agent
import random
from Reversi.reversi_model import ReversiGameRule
from Reversi.reversi_utils import Cell,filpColor,boardToString,countScore, GRID_SIZE
import func_timeout

class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.current_agent_index = _id
        self.num_of_agent = 2
        self.validPos = ReversiGameRule._validPos(self)
        self.rootNode = None

    def getCurrentRoot(self, game_state):
        if self.rootNode == None:
            self.rootNode = Node(self.current_agent_index, self.current_agent_index, current_state=game_state, validPos=self.validPos, agent_colors=self.agent_colors)
        else:
            target_child = None
            if len(self.rootNode.child_nodes) == 0:
                opp_actions = ReversiGameRule.getLegalActions(self, self.rootNode.current_state, self.rootNode.player_id)
                for action in opp_actions:
                    next_state = ReversiGameRule.generateSuccessor(self, self.rootNode.current_state, action, self.rootNode.player_id)
                    same_state = True
                    for x in self.validPos:
                        if next_state.getCell(x) != game_state.getCell(x):
                            same_state = False
                            break
                    if same_state:
                        target_child = Node(self.rootNode.myAgent_id,(self.rootNode.player_id+1)%2, next_state, parent_node=None, actionTaken=action, validPos=self.rootNode.validPos, agent_colors=self.rootNode.agent_colors)
                        break
                
                self.rootNode = target_child
            else:
                for child in self.rootNode.child_nodes:
                    same_state = True
                    for x in self.validPos:
                        if child.current_state.getCell(x) != game_state.getCell(x):
                            same_state = False
                            break
                    if same_state:
                        target_child = child
                        break
                
                self.rootNode = target_child
                self.rootNode.parent_node = None


    
    def SelectAction(self,actions,game_state):
        # color info
        self.agent_colors = game_state.agent_colors
        isAtFirstMove = (self.rootNode == None)

        self.getCurrentRoot(game_state)

        # # iterate MCTS for 3 times
        # if isAtFirstMove:
        #     for i in range(10):
        #         self.rootNode = self.rootNode.MCTS()
        # else:
        #     for i in range(2):
        #         self.rootNode = self.rootNode.MCTS()
        
        # # return the action
        # bestWinRate = 0
        # bestAction = None
        # next_root = None
                
        # for child in self.rootNode.child_nodes:
        #     if child.visited_count == 1:
        #         pass
        #     winRate = child.win_count/child.visited_count
        #     if winRate >= bestWinRate:
        #         bestWinRate = winRate
        #         bestAction = child.actionTaken
        #         next_root = child

        # print("MCTS next move:")
        # print(bestAction)
        # self.rootNode = next_root
        # return bestAction


        # start a timer of 0.8s for simulation
        try:
            if isAtFirstMove:
                func_timeout.func_timeout(14.8, self.rootNode.MCTS)
            else:    
                func_timeout.func_timeout(0.8, self.rootNode.MCTS)
            print("MCTS ended")
        except:
            print("time out")

        bestWinRate = 0
        bestAction = None
        next_root = None
                
        for child in self.rootNode.child_nodes:
            winRate = child.win_count/child.visited_count
            if winRate >= bestWinRate:
                bestWinRate = winRate
                bestAction = child.actionTaken
                next_root = child

        print("MCTS next move:")
        print(bestAction)
        self.rootNode = next_root
        return bestAction


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
        while True:
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
            next_state = ReversiGameRule.generateSuccessor(self, self.current_state, action, self.player_id)
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