import numpy as np
from multiprocessing import parent_process
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
    
    def SelectAction(self,actions,game_state):
        # color info
        self.agent_colors = game_state.agent_colors
        # if it's agent's first move allow 15s warm up, if not allow only 1 sec
        isAtFirstMove = (self.rootNode == None)
        self.rootNode = Node(self.current_agent_index, self.current_agent_index, current_state=game_state, validPos=self.validPos, agent_colors=self.agent_colors)
        try:
            if isAtFirstMove:
                func_timeout.func_timeout(1, self.rootNode.MCTS)
            else:    
                func_timeout.func_timeout(0.85, self.rootNode.MCTS)
        except:
            pass
        # choose the action results in highest (win rate + mobility) state
        bestWinRate = 0
        bestAction = None
        next_root = None
        for child in self.rootNode.child_nodes:
            if child.visited_count < 2 and child.win_count == 1:
                 continue
            else:
                if child.visited_count != 0:
                    winRate = child.win_count/child.visited_count
                    winRate += child.mobilityHeuristic() * 0.3
                    if winRate >= bestWinRate:
                        bestWinRate = winRate
                        bestAction = child.actionTaken
                        next_root = child
        self.rootNode = next_root
        return bestAction


class Node():
    def __init__(self, myAgent_id, curr_player_id, current_state, parent_node=None, actionTaken = None, validPos = None, agent_colors=None):
        self.myAgent_id = myAgent_id
        self.player_id = curr_player_id
        self.current_state = current_state
        self.win_count = 0
        self.visited_count = 0
        self.parent_node = parent_node
        self.actionTaken = actionTaken
        self.validPos = validPos
        self.agent_colors = agent_colors
        self.child_nodes = []

    # a complete select&expand&simulate&back propagation, a looped in the choose best action method
    def MCTS(self):
        while True:
            # select the leaf node with highest UCT
            target_node = self.selection()
            # if the target node has been visited, expand it, then select the first child to simulate then back propagate
            if target_node.visited_count != 0:
                target_node.expand()
                random.choice(target_node.child_nodes).simulation()
            # if the target node has not been visited, simulate from it right away then back propagate
            else:
                target_node.simulation()

    # find the leaf of current tree with highest UCT
    def selection(self):
        # if the root has not been expanded(no child), select the root itself and then proceed to expand
        if len(self.child_nodes) == 0:
            return self
        else:
            max_UCT = -float('inf')
            target_node = None
            for child in self.child_nodes:
                child_UCT = UCT(child)
                # if a child has not been visited yet return that child as the target
                if child_UCT == float('inf'):
                    return child
                if child_UCT > max_UCT:
                    max_UCT = child_UCT
                    target_node = child
            return target_node.selection()

    # get all children of self node
    def expand(self):
        all_actions = ReversiGameRule.getLegalActions(self, game_state=self.current_state, agent_id=self.player_id)
        for action in all_actions:
            next_state = ReversiGameRule.generateSuccessor(self, self.current_state, action, self.player_id)
            new_child = Node(self.myAgent_id,(self.player_id+1)%2, next_state, parent_node=self, actionTaken=action, validPos=self.validPos, agent_colors=self.agent_colors)
            self.child_nodes.append(new_child)

    # starting from self node, randomly play the game til the ends, and back propagate the result 
    def simulation(self):
        self.visited_count += 1
        # if our agent wins or tie, add self's win count and back propagation
        if self.random_result() == self.myAgent_id or self.random_result() == -1:
            self.win_count += 1
            self.backPropagation(True)
        # if our agent lose, back propagation
        else:
            self.backPropagation(False)

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

    # called by the target node that finised a simulation, updates all parents' win/visit count
    def backPropagation(self, win):
        if self.parent_node == None:
            return
        if win:
            self.parent_node.win_count += 1
            self.parent_node.visited_count += 1
            return self.parent_node.backPropagation(win)
        else:
            self.parent_node.visited_count += 1
            return self.parent_node.backPropagation(win)

    # calcualtes the mobility heuristic value of current state
    def mobilityHeuristic(self):
        agent_valid_moves = len(ReversiGameRule.getLegalActions(self, game_state=self.current_state, agent_id=self.player_id))
        opponent_valid_moves = len(ReversiGameRule.getLegalActions(self, game_state=self.current_state, agent_id=((self.player_id+1)%2)))
        value = 0
        if (agent_valid_moves == 0 and opponent_valid_moves > 0):
            value = -1
        if (agent_valid_moves > 0 and opponent_valid_moves == 0):
            value = 1
        if(agent_valid_moves > opponent_valid_moves):
            value = (agent_valid_moves)/(agent_valid_moves + opponent_valid_moves)
        if(agent_valid_moves < opponent_valid_moves):
            value = -(opponent_valid_moves)/(agent_valid_moves + opponent_valid_moves)
        return value

def UCT(node: Node):
    # if the node is not visited give it highest priority
    if node.visited_count == 0:
        return float('inf')
    # add the mobility to UCT value
    value = (node.win_count / node.visited_count) + (1.3 * np.sqrt(node.parent_node.visited_count/node.visited_count)) + node.mobilityHeuristic() * 3
    return value