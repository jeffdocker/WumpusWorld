# WumpusWorld
Adversarial game that consists of 3 piece types: mage, hero, and wumpus.
Mages may take heros, heros may take wumpuses, and wumpuses may take mages. Pieces of the same type cancel out and both pieces are lost.
Any pieces that try to take a piece that can capture them results in the piece being lost. An example would be a mage trying to take a wumpus.
The AI utilizes minimax with alpha beta pruning to choose the best moves to make with a provided heuristic. 
The user is given multiple heuristics to choose from that affects the playstyle of the AI.
