# Cachex-AI-Agent
An AI Agent created with the MiniMax Algorithm to look into future states when playing a game of "Cachex". Rules and specfications of the game can be found under the *specification/* directory. Created by Elizabeth Wong and Sean Maher. 

## 1.1 Approach to the Cachex

Due to the nature of Cachex being a game with both properties of perfect information and
deterministic, our approach to Cachex uses the Minimax algorithm - which is pessimistic - as
a foundation for our game agent. Due to the adversarial nature of the game, the player’s
advantageous state is considered to be disadvantageous for their opponent. The algorithm
looks ahead into future states through the creation of a tree-like structure. The two users will
be assigned red or blue where the player becomes the maximising player and the opponent is
seen as the minimising player. The maximising player will select the action with the highest
score whilst the minimising player will move accordingly to the lowest score - both scores
are generated via an evaluation function calculated based on the board state recursively.
The time and space complexity of Minimax are O(bd) and O(b × d) respectively where b is
the possible actions made at each level and d is the depth of the tree. Thus, due to the large
search tree that will realistically result in extremely slow computational times when scaled
up, in an attempt to speed up our games agent we implemented Alpha-Beta Pruning.
Alpha-Beta Pruning is a technique applied within the minimax algorithm in order to
terminate the completion of looking for states that need to be searched within the tree without
affecting the final outcome. It does so by setting upper and lower bounds before proceeding
to remove sub-trees.
Overall, the effectiveness of Alpha-Beta Pruning is greatly dependent on the sequential order
of the evaluation function and actions generated. If the action has more variance and is
optimal, the effectiveness of this technique is exacerbated as most branches are pruned; thus
reducing computational time for search through irrelevant states. However, in the scenario
where no branch is pruned, Minimax will still need to search all board states through the
entire tree.

## 2.1 Player Strategy and Evaluation Function
Our AI agent’s gameplay leans towards a more greedy approach, focusing on three main
objectives respectively: Offence, Objectives and Defence. The game agent is created with the
notion of ‘Offence is the best Defence’, where it attempts to win as its focal point as opposed
to predicting and reactionary responses based on its opponent. Its defensive capabilities
mainly focus on blocking the opponent if they are about to achieve a winning state. The
evaluation function used to calculate the score for our game agent employs the strategies
listed below.

## 2.2 Corner and Middle Priority
The corners of each board take precedence as it allows the game agent more control over a
directional tile that could be used to create a game winning state for either Red or Blue
player. As the corners are considered to be both Red and Blue (see Figure 1), our agent
prioritises corner placement. Additionally, occupation of each corner also takes away a tile
that could be used for the opponent’s win condition path.
![image](https://user-images.githubusercontent.com/70874436/210519366-092af6fa-9556-4b4a-a79a-ac4e3e7cda58.png)
Middle priority is used within the game agent as a feint move to confuse the opponent’s
decision making.

## 2.3 Border Control
Our agent employs the strategy to take bordering tiles of the board. This enables the player to
have greater chances of creating more win opportunity paths as well as lessening the
opponent’s win opportunity options. The agent evaluates borders based on whether it controls
the corners linking one side of the border to the other, i.e. red looks to capture the borders
vertically, preferably between 2 red occupied corners and blue vice versa.
![image](https://user-images.githubusercontent.com/70874436/210519430-22c59f5f-0a7c-4ae9-be26-02b67533577d.png)

## 2.4 Capturing the opponent
Capturing is seen as an important objective as it increases the agent’s presence on the board
by reducing the number of their opponent’s tiles (See Figure 3). Due to the amount of
uncertainty in the game state, having more tiles is always better. Hence capture situations are
prioritised. Our agent weighs scenarios regarding this mechanic accordingly. For example, if
an action by red or blue results in a capture, our agent weighs this as 8 or -8 depending on if
the capture is for or against it. Furthermore, an action where our agent blocks off a potential
capture opportunity, a weighting of 16 is evaluated. Finally, if an action is made whereby the
agent places the opponent in a potential capture scenario, is action is weighted at 6.
![image](https://user-images.githubusercontent.com/70874436/210519465-3f5fd78e-fbe7-4c34-856d-477652e2ed76.png)

## 2.5 Triplet Pattern
The triplet pattern (See Figure 4) is a formation created by placing three tiles in a triangular
shape on the board. This triplet pattern is seen as extremely strong as when this tile formation
is created, there is little action that can be taken to capture this pattern. Thus, this can force
the attacker into a passive state.

![image](https://user-images.githubusercontent.com/70874436/210519502-82b562c9-03c3-4bbb-8876-2b74e3fbe4cd.png)

## 2.5 Blocking the Opposing Win
In situations where our game agent sees the opponent is able to win in future states, our AI
will attempt to block the opponent’s win situation with a tile of its own (see Figure 5).

![image](https://user-images.githubusercontent.com/70874436/210519539-3a54f3ea-4684-4a09-9f3c-54bcae8e1a97.png)

## 3.1 Performance Evaluation
We ran the game agent under multiple tests where it fought in a game of Cachex against itself
in order to check for correct behaviour of the evaluations score in accordance with the player
strategies we hoped to employ. Performance testing was a crucial part of our development in
order to modify the weightings and scores for certain evaluation functions in order to reflect
the strategy described above. Additionally, we also tested our AI agent against another
group’s agent to see how it would fare against another group’s player strategy. After several
tests it became apparent that our AI seemed to work better within smaller n sized boards as
opposed to larger ones. A serious problem that became apparent quickly was that our game
agent was poorly optimised. As the board size expands beyond sizes n=7 or n=8, our agent’s
decision making time drastically increases. For size n=9, it seemed to still work within a
reasonable amount of time, however when handling edge cases it broke.

## 4.1 Optimization
Due to the slow nature of our game agent, we tried very hard to optimise it where we saw
possible. These optimisations included using a numpy array for the board initialization and
the usage of list comprehensions when iterating through lists with conditionals in order to
save some computational time. Additionally, the sequence of each evaluation function used in
the evaluation score was placed in order to future optimise as well as the usage of Alpha-Beta
Pruning within the Minimax algorithm.
The board state evaluation was also modified based on turn number and board size to prevent
less relevant processing. Firstly, 6 turns for red and 5 turns for blue were allocated to
capturing the corners and middle tiles. This is because there are 4 corners and 1 middle tile
hence 5. For red, the first move is a feint to bait out agents that implement a first turn steal
strategy. Following these first 5 turns, our border taking strategy begins and continues until
3 * n/2 turns happen. This is because as the board size increases, the usefulness of checking for
capture and triplet creation is lower at earlier turns. Finally, our evaluation continues its
border conquest, however, it also takes into account triplet and capture patterns.
Furthermore, we limited the triplet searching function to only consider non-border tiles. This
will improve efficiency more as the board size increases and is effective due to forming
triplets using the border tiles is less important because the border tiles are already difficult to
recapture once they’re taken.

## 5.1 Future Work
If our group could have additional time to make more modifications in the future, we would
look into increasing our game agent’s intelligence and efficiency on larger sized boards. This
would include the creation of a pathfinding evaluation function for the game agent to find a
goal state once the border occupation has ended. An example of how we could implement
this is checking which border tile is closest to the nearest winning zone, and calculating the
shortest available path. In order to further optimise the AI, we should have implemented a
function to keep track of available tiles on the board so the Minimax algorithm does not have
to perform a full search on the board each evaluation. Finally, taking depth into consideration
by creating a function that calculates the depth dynamically could also help with both
increasing the brains of our game agent as well as its speed

