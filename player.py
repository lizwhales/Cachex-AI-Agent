from cgi import test
from concurrent.futures import process
from itertools import count
from json.encoder import INFINITY
from re import S
import string
from typing import overload
import enum
from queue import PriorityQueue, Queue
from array import  *
from time import time

import numpy as np
from numpy import zeros, array, roll, vectorize
import itertools

#score = 0
MAX_LENGTH = +INFINITY

# 17-05
_PLAYER_AXIS = {
    "red": 0, # Red aims to form path in r/0 axis
    "blue": 1 # Blue aims to form path in q/1 axis
}

# Utility function to add two coord tuples
_ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])

# Neighbour hex steps in clockwise order
_HEX_STEPS = array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
    dtype="i,i")

# red players hex steps
_RED_STEPS = array([(1, -1),(1, 0),(-1, -1),(-1, 0)], 
dtype="i,i") 

# blue players hex steps 
_BLUE_STEPS = array( [(-1, 1),(0, 1),(1, -1),(0, -1)],
dtype="i,i")
       
# taken from referee implementation to detedt captures    
_CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
    for n1, n2 in 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1))) + 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 2)))]

# Map between player token types
_SWAP_PLAYER = { None: None, 'red': 'blue', 'blue': 'red' }

# Maps between player string and internal token type
_TOKEN_MAP_OUT = { None, "red", "blue" }


_PLAYER_DIRECTION = {
    'red': 0, 'blue': 1
    # red wants to make path in row/0
    # blue wants to make path in col/1
}

RED, BLUE = 'red', 'blue'


# defining triplet patterns to detect for formation of triplets
_TRIPLET_PATTERNS = [[n1, n2]

    for n1, n2 in
    list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1)))]

# define the weighting for static evaluations
class Weightings(enum.Enum):
    middle_val = 20
    corner_val = 40
    capturing_val = 3
    triplet_val = 10
    capture_occurs_val = 8
    prevent_capture_val = 16
    create_capture_oppurtunity_val = 6

class Player:

    player: string
    n: int
    turn_count: int

    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue.
        """
        # put your code here
        self.player = player
        self.n = n 
        self.turn_count = 0
        self.player_opponent_diff = 0
        self.depth = 2

        if self.player == RED:
            self.opponent = BLUE
        else:
            self.opponent = RED

        #self.board = board
        self.board = np.empty(shape=(n,n), dtype=object)
        self.top_border_list = []
        self.bottom_border_list = []
        self.right_border_list = []
        self.left_border_list = []
        for i in range(self.n):
            self.left_border_list.append((i, 0))
            self.bottom_border_list.append((0, i))
            self.right_border_list.append((i, self.n-1))
            self.top_border_list.append((self.n-1, i))
        
        self.corners = [(0, 0), (self.n - 1, 0), (self.n - 1, self.n - 1), (0, self.n - 1)]
 
        
    
    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # if player is red, place a tile to counter act potential first turn steal implementations
        if self.player == RED and self.turn_count == 0:
            if self.n % 2 == 0:
                return ('PLACE', int((self.n ) / 2), int(self.n / 2 + 1))
            else:
                return ('PLACE', int((self.n - 1) / 2), int((self.n - 1) / 2 + 1))
        
        # checks to see if the player has a wind condition
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == None:
                    self.board[i][j] = self.player
                    if self.check_win(self.player, i, j):
                        #print("position for ",self.player," to win: ")
                        #print((i,j))
                        return ('PLACE', i, j)
                    self.board[i][j] = None
        
        # checks to see if the opponent has a win condition
        for i in range(self.n):
            for j in range(self.n):
                #print(self.board[i][j])
                if self.board[i][j] == None:
                    self.board[i][j] = self.opponent
                    #print(self.board[i][j])
                    if self.check_win(self.opponent, i, j): 
                        #print("hi")                       
                        #print("position for ",self.opponent," to win: ")
                        #print((i,j))
                        return ('PLACE', i, j)
                    self.board[i][j] = None
        
        # now that the win condition was been checked
        max_score = -INFINITY
        max_location = (None)

        for i in range(self.n):
            for j in range(self.n):
                if (self.board[i][j] == None):
                    score = self.minimax(i, j, self.depth, -INFINITY, +INFINITY, True, self.player, self.opponent)
                    if (score > max_score):
                        max_score = score
                        max_location = (i, j)       
        return ("PLACE", max_location[0], max_location[1])



    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of 
        their chosen action. Update your internal representation of the 
        game state based on this. The parameter action is the chosen 
        action itself. 
        
        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """
        # put your code here
        if action[0] ==  'STEAL':
            self.handle_steal()
        else:
            self.board[action[1]][action[2]] = player
            self._apply_captures(action[1], action[2])
        
        self.turn_count += 1


        
    
    def handle_steal(self):

        ''' logic to update board for when a steal occurs'''

        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == RED:
                    self.board[i][j] = None
                    self.board[j][i] = BLUE 

    
    def triplet_detection(self):

        ''' 
        loops through the board, ignoring the tiles that form the border, checking if triplet patterns are formed and evaluating the board accordingly
        '''

        score = 0
        for r in range((self.n - 2)):
            for q in range((self.n - 2)):
                if(self.board[r + 1][q + 1] == self.player):
                    for patterns in _TRIPLET_PATTERNS:
                        triplet = [_ADD((r + 1,q + 1), pattern) for pattern in patterns if self.inside_bounds(_ADD((r + 1,q + 1), pattern)) and self.board[_ADD((r + 1,q + 1), pattern)] == self.player]
                        if len(triplet) == 2:
                            score += Weightings.triplet_val.value    
        return score            
                            
    def border_occupation_eval(self, row, col):

        ''' 
        our main offensive evaluation:
        weights moving along a border where our agent controls the corner location in a straight path from
        win zone to win zone as most favourable 
        '''

        weighting_top = 1
        weighting_bot = 1
        weighting_right = 1
        weighting_left = 1
        coord = (row, col)
        score = 0

        #checking for red player to control both corners in a vertical path
        if self.player == RED:
            controlled_corners = [corner for corner in self.corners if self.board[corner] == RED]
            if self.corners[0] in controlled_corners and self.corners[1] in controlled_corners:
                weighting_left *= 2
            elif self.corners[2] in controlled_corners and self.corners[3] in controlled_corners:
                weighting_right *= 2

        #checking for blue player to control both corners in a vertical path           
        if self.player == BLUE:
            controlled_corners = [corner for corner in self.corners if self.board[corner] == RED]
            if self.corners[1] in controlled_corners and self.corners[2] in controlled_corners:
                weighting_top *= 2
            elif self.corners[0] in controlled_corners and self.corners[3] in controlled_corners:
                weighting_bot *= 2 

        #checking for red opponent to control both corners in a vertical path
        if self.opponent == RED:
            controlled_corners = [corner for corner in self.corners if self.board[corner] == RED]
            if self.corners[0] in controlled_corners and self.corners[1] in controlled_corners:
                weighting_left *= 1.5
            elif self.corners[2] in controlled_corners and self.corners[3] in controlled_corners:
                weighting_right *= 1.5

        #checking for blue opponent to control both corners in a vertical path           
        if self.opponent == BLUE:
            controlled_corners = [corner for corner in self.corners if self.board[corner] == RED]
            if self.corners[1] in controlled_corners and self.corners[2] in controlled_corners:
                weighting_top *= 1.5
            elif self.corners[0] in controlled_corners and self.corners[3] in controlled_corners:
                weighting_bot *= 1.5      

        # the weightings here, 12 10 8 and 6, are used to drive the agent to favor offensive moves over defensive moves
        # in the horizontal direction for Blue and vertical direction for Red
        if (coord in self.left_border_list):
            if(self.player == RED):
                if self.board[row][col] == self.player:
                    score += 12 * weighting_left
                elif self.board[row][col] == self.opponent:
                    score -= 10 * weighting_left
            elif(self.player == BLUE):
                if self.board[row][col] == self.player:
                    score += 8 * weighting_left
                elif self.board[row][col] == self.opponent:
                    score -= 6 * weighting_left
        elif (coord in self.top_border_list):
            if(self.player == BLUE):
                if self.board[row][col] == self.player:
                    score += 12 * weighting_top
                elif self.board[row][col] == self.opponent:
                    score -= 10 * weighting_top
            elif(self.player == RED):
                if self.board[row][col] == self.player:
                    score += 8 * weighting_top
                elif self.board[row][col] == self.opponent:
                    score -= 6 * weighting_top
        elif (coord in self.right_border_list):
            if(self.player == RED):
                if self.board[row][col] == self.player:
                    score += 12 * weighting_right
                elif self.board[row][col] == self.opponent:
                    score -= 10  * weighting_right
            elif(self.player == BLUE):
                if self.board[row][col] == self.player:
                    score += 8 * weighting_right
                elif self.board[row][col] == self.opponent:
                    score -= 6 * weighting_right
        elif (coord in self.bottom_border_list):
            if(self.player == BLUE):
                if self.board[row][col] == self.player:
                    score += 12 * weighting_bot
                elif self.board[row][col] == self.opponent:
                    score -= 10 * weighting_bot
            elif(self.player == RED):
                if self.board[row][col] == self.player:
                    score += 8 * weighting_bot
                elif self.board[row][col] == self.opponent:
                    score -= 6 * weighting_bot
        return score

    
    def check_for_captures(self , coord):

        ''' 
        loops through the board checking for capture patterns to detect when a capture may occur, 
        or when a capture is possible for our agent 
        '''

        token_friendly = self.board[coord]
        token_opponent = _SWAP_PLAYER[token_friendly]
        token_absent = None
        for pattern in _CAPTURE_PATTERNS:
            coords = [_ADD(coord, s) for s in pattern]
            if all(map(self.inside_bounds, coords)):
                tokens = [self.board[coord] for coord in coords]
               
                # making a capture and allowing a capture opportunity are weighted equally and oppositely,
                # while blocking off a potential capture oppurtunity is weighted highest, 
                # and making the opponent vulnerable to a capture is weighted slightly less than all
                if tokens == [token_friendly, token_opponent, token_opponent]:
                    return Weightings.capture_occurs_val.value
                elif tokens == [token_opponent, token_friendly, token_friendly]:
                    return Weightings.prevent_capture_val.value
                elif tokens == [token_friendly, token_absent, token_opponent]:
                    return -Weightings.capture_occurs_val.value
                elif tokens == [token_friendly, token_opponent, token_absent]:
                    return -Weightings.capture_occurs_val.value
                elif tokens == [token_absent, token_opponent, token_opponent]:
                    return Weightings.create_capture_oppurtunity_val.value
        return 0

    
    def eval_corners(self, row, col):

        ''' 
        weights taking the corners very highly and in particular, capturing a corner that creates a 
        straight line path from one win zone to another win zone with respect to the agents current colour
        '''

        coord = (row, col)
        score = 0
        corners = [(0, 0), (self.n-1, 0), (self.n-1, self.n-1) , (0, self.n-1)]
        if(coord in corners):
            if (self.board[row][col] == self.player):
                score += Weightings.corner_val.value/self.n
            elif(self.board[row][col] == self.opponent):
                score -= Weightings.corner_val.value

        # for when player is red
        if self.player == RED:
            
            # where:
            # corners[0] <- Bottom Left
            # corners[1] <- Top Left
            # corners[2] <- Top Right
            # corners[3] <- Bottom Right
            
            # add greater weighting to controlling 2 corners in a line that is winning for red
            if self.board[corners[0] == RED and self.board[corners[1]] == RED]:
                score += weighting_connected_corners * Weightings.corner_val.value
            elif self.board[corners[2] == RED and self.board[corners[3]] == RED]:
                score += weighting_connected_corners * Weightings.corner_val.value

            # add greater weighting to when the opponent controls 2 corners in a winning line
            elif self.board[corners[0] == BLUE and self.board[corners[3]] == BLUE]:
                score -= weighting_connected_corners * Weightings.corner_val.value
            elif self.board[corners[1] == BLUE and self.board[corners[2]] == BLUE]:
                score -= weighting_connected_corners * Weightings.corner_val.value
        # for when player is blue
        elif self.player == BLUE:
            # add greater weighting to controlling 2 corners in a line that is winning for blue
            if self.board[corners[0] == BLUE and self.board[corners[3]] == BLUE]:
                score += weighting_connected_corners * Weightings.corner_val.value
            elif self.board[corners[1] == BLUE and self.board[corners[2]] == BLUE]:
                score += weighting_connected_corners * Weightings.corner_val.value

            # add greater weighting to when the opponent controls 2 corners in a winning line
            elif self.board[corners[0] == RED and self.board[corners[1]] == RED]:
                score -= weighting_connected_corners * Weightings.corner_val.value
            elif self.board[corners[2] == RED and self.board[corners[3]] == RED]:
                score -= weighting_connected_corners * Weightings.corner_val.value
            
        
        return score
    
                 
    def eval_middle(self, row, col):

        ''' 
        adds weighting to place a token in the middle tile or there abouts,
        our agents values moving along the borders of the board highly,
        therefore placing in the middle is more essential on boards where n is less

        additionally, we place in the middle to hopefully trigger any other agent's
        implementations to regain control of the center to waste their time 
        '''

        coord = (row, col)
        score = 0
        if (coord == ((self.n-1)/2, (self.n-1)/2) and self.turn_count != 0):
            if(self.board[row][col] == self.player):
                score += Weightings.middle_val.value
            elif(self.board[row][col] == self.opponent):
                score -= Weightings.middle_val.value
        return score

    
    def get_eval(self, row, col):
        ''' 
        eval function returns the evaluation of the board at a given turn
        at lower turns it skips out on checking for captures and triplet formation
        mainly because for our agent it wastes time, and not many of these scenarios are
        present early
        '''

        # runtimer = time()
        coord = (row,col)
        #for red, the first turn will be a feint to guard against first turn steal implementations
        if self.player == RED:
            moves_to_control_start = 6
        else:
            moves_to_control_start = 5
        #for the first 5 turns corner control and middle control is the priority, captures and triplet formation shouldn't occur at this point
        if self.turn_count <= moves_to_control_start:
            evaluation = self.eval_corners(row, col) +  self.eval_middle(row, col)
        # based on the size of the board, moves from the opponent in the centre shouldnt be too impactful
        # in threatening a game loss    
        elif self.turn_count < 3*self.n/2:
            evaluation = self.border_occupation_eval(row, col) 
        # once it reaches this state where the game has progressed, triplets and capture will become more 
        # important, therefore our agent should take this into account while continuing its border conquest
        else: 
            evaluation = self.border_occupation_eval(row, col) + self.check_for_captures((row,col)) + self.triplet_detection()
        return evaluation           
    

    
    def minimax(self, row, col, depth, alpha, beta, max_player, player, opponent):

        ''' 
        calls minimax to evaluate the board to a given depth
        '''

        if(depth == 0) or self.check_win(player, row, col):
            if not self.check_win(player, row, col):
                return self.get_eval(row, col)
            elif player == self.player:
                return INFINITY
            elif player == self.opponent:
                return -INFINITY
              
        if(max_player):
            max_score = -INFINITY
            for i in range(self.n):
                for j in range(self.n):
                    child = self.board[i][j]
                    if(child == None):
                        self.board[i][j] = player
                        score = self.minimax(row, col, depth-1, alpha, beta, False, player, opponent)
                        self.board[i][j] = None
                        max_score = max(max_score, score)
                        alpha = max(alpha, score)
                        if beta <= alpha:
                            break
            return max_score
        else:
            min_score = +INFINITY
            for i in range(self.n):
                for j in range(self.n):
                    child = self.board[i][j]
                    if(child == None):
                        self.board[i][j] = opponent
                        score = self.minimax(row, col, depth-1, alpha, beta, True, opponent, player)
                        self.board[i][j] = None
                        min_score = min(min_score, score)
                        beta = min(beta, score)
                        if beta <= alpha:
                            break
            return min_score
        

    # taken and adapted from referee
    # checks a coordinate is within the bounds of the board 
    def inside_bounds(self, coord):
        """
        True iff coord inside board bounds.
        """
        r, q = coord
        return r >= 0 and r < self.n and q >= 0 and q < self.n
    
    # taken and adapted from referee
    # returns the valid neighbours of a given coordinate 
    def _coord_neighbours(self, coord):
        """
        Returns (within-bounds) neighbouring coordinates for given coord.
        """
        return [_ADD(coord, step) for step in _HEX_STEPS \
            if self.inside_bounds(_ADD(coord, step))]


    
    # function modified from referee.board.py to find connected coords
    def connected_coords(self, token, start_coord):
        """
        Find connected coordinates from start_coord. This uses the token 
        value of the start_coord cell to determine which other cells are
        connected (e.g., all will be the same value).
        """
        # Get search token type
        token_type = token

        # Use bfs from start coordinate
        reachable = set()
        queue = [start_coord]
        # queue.put(start_coord)

        while len(queue) != 0:
            curr_coord = queue.pop(0)
            reachable.add(curr_coord)
            for coord in self._coord_neighbours(curr_coord): 
                if self.board[coord[0]][coord[1]] == token_type and coord not in queue and coord not in reachable:
                    queue.append(coord)
        return list(reachable)

  
    
    def check_win(self, token, row, col):
        
        '''
        Checks for game end conditions for a given player
        Condition: a color completes a path from one side to another with respect to the rules
        '''
        coord=(row, col)
        reachable = self.connected_coords(token, coord)
        axis_vals = [coord[_PLAYER_AXIS[token]] for coord in reachable]
        if min(axis_vals) == 0 and max(axis_vals) == self.n - 1: 
            return True
        else:
            return False
    # taken from referee
    # used to update the board if a capture occurs at turn stage
    def _apply_captures(self, row, col):
        """
        Check coord for diamond captures, and apply these to the board
        if they exist. Returns a list of captured token coordinates.
        """
        opp_type = self.board[row][col]
        mid_type = _SWAP_PLAYER[opp_type]
        captured = set()
        
        # Check each capture pattern intersecting with coord
        for pattern in _CAPTURE_PATTERNS:
            coords = [_ADD((row,col), s) for s in pattern]
            # No point checking if any coord is outside the board!
            if all(map(self.inside_bounds, coords)):
                tokens = [self.board[coord[0]][coord[1]] for coord in coords]
                if tokens == [opp_type, mid_type, mid_type]:
                    # Capturing has to be deferred in case of overlaps
                    # Both mid cell tokens should be captured
                    captured.update(coords[1:])
        # Remove any captured tokens
        for coord in captured:
            self.board[coord[0]][coord[1]] = None
        return list(captured)
    # checks if a coordinate is occupied
    def is_occupied(self, coord):
        """
        True if coord is occupied by a token (e.g., not None).
        """
        return self[coord] != None
    def __getitem__(self, coord):
        """
        Get the token at given board coord (r, q).
        """
        return self.board[coord[0]][coord[1]]
    
        # moves that could result in a capture or capturing

    def _coord_neighbours(self, coord):
        """
        Returns (within-bounds) neighbouring coordinates for given coord.
        """
        return [_ADD(coord, step) for step in _HEX_STEPS \
            if self.inside_bounds(_ADD(coord, step))]

    
