# Cachex-AI-Agent
An AI Agent created with the MiniMax Algorithm to look into future states when playing a game of "Cachex". Rules and specfications of the game can be found under the *specification/* directory. 

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



