# Wumpus-World

The instructions of the project are found in the link below
http://stephendavies.org/cpsc415/program4.html

All helper scripts in the repo are made by Stephen Davies

What did I do:
I created the aahmad3_Explorer agent where the core logic belongs.

What does it do:
The program has a method called program() method will be called by the simulator once each time you move. You will be given a 5-tuple of percept values each time, whose elements are as follows:

Element 0: either the string 'Stench' or None
Element 1: either the string 'Breeze' or None
Element 2: either the string 'Glitter' or None
Element 3: either the string 'Bump' or None
Element 4: either the string 'Scream' or None
the method should return one of the string values that are available in the ExplorerAgent.possible_actions list (see wumpus.py), namely: 'Forward', 'TurnRight', 'TurnLeft', 'Grab', 'Shoot', or 'Climb'.

