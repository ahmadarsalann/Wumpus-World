from numpy.lib import copy
from wumpus import ExplorerAgent
import random
import numpy
from copy import deepcopy

class KB():

    def __init__(self):
        self.board = [[0] * 4 for i in range(4)]
        self.first_move = True
        self.facing_direction = "North"
        self.point = [len(self.board) - 1, 0]
        self.count = 0
        self.gold_in_hand = False
        self.hasShot = False
        self.hasBump = False
        self.last_move = 0
        self.shoot_available = False
        self.check_location = []
        self.dont_change_pm = False
        self.got_index = False
        self.pick_move = 0
        self.situational = False
        self.original_threat = []
        self.old_agent_location = 0
        self.path = []
        self.last_location = 0
        self.track = 0
        self.final_path = 0
        self.redundancy = []
        self.num = 0

    def what_to_do(self, possible_moves, percept, count):
        list(possible_moves)
        path = 0
        if self.first_move == True:
            self.set_base()
        board = numpy.array(self.board.copy())
        index = numpy.where(board == "E")
        index = numpy.array(index).tolist()

        if "Bump" in percept and "Stench" not in percept and "Breeze" not in percept:
            self.location(0, 0, index, percept, True)
            self.hasBump = True
            board = numpy.array(self.board.copy())
            index = numpy.where(board == "E")
            index = numpy.array(index).tolist()
            if count == 400:
                if self.board[self.path[len(self.path) - 1][0]][self.path[len(self.path) - 1][1]] == "W":
                    self.path.pop(len(self.path) - 1)

        if self.hasBump == True:
            possible_moves.remove("Forward")
            self.hasBump = False


        if "Glitter" not in percept:
            possible_moves.remove("Grab")
        else:
            self.gold_in_hand = True
            self.check_and_delete_walls()
            path = self.find_path_back()
            self.check_location.clear()
            return "Grab"

        if count == 400 and self.gold_in_hand == False:
            self.check_and_delete_walls()
            self.find_path_back()

        if self.gold_in_hand == False and count < 400:
            possible_moves.remove("Climb")
        elif self.compare_two_locations() == False:
            possible_moves.remove("Climb")
        elif self.compare_two_locations() == True and self.gold_in_hand == True or self.compare_two_locations() == True and count > 400 and self.gold_in_hand == False:
            return "Climb"
        
        if "Breeze" in percept and "Stench" not in percept and "Bump" not in percept:
            self.location(0, 0, index, percept, True)

        if "Stench" not in percept or self.hasShot == True:
            possible_moves.remove("Shoot")
        else:
            if "Stench" in percept and "Bump" not in percept and "Breeze" not in percept:
                self.location(0, 0, index, percept, True)
            self.shoot_available = True

        if "Stench" in percept and "Bump" in percept and "Breeze" not in percept:
            self.location(0, 0, index, percept, True)
            
        if "Stench" in percept and "Bump" in percept and "Breeze" in percept:
            self.location(0, 0, index, percept, True)
            
        if "Stench" in percept and "Bump" not in percept and "Breeze" in percept:
            self.location(0, 0, index, percept, True)
            
        if "Stench" not in percept and "Bump" in percept and "Breeze" in percept:
            self.location(0, 0, index, percept, True)

        if "Scream" in percept:
            self.location(0, 0, index, percept, True)
            self.dont_change_pm = False

        if len(self.check_location) > 0 and self.board[self.check_location[0][0]][self.check_location[0][1]] == "B" or len(self.check_location) > 0 and self.board[self.check_location[0][0]][self.check_location[0][1]] == "W":
            if self.board[self.check_location[0][0]][self.check_location[0][1]] == "W":
                board = numpy.array(self.board.copy())
                index = numpy.where(board == "E")
                index = numpy.array(index).tolist()
            self.check_location.pop(0)
            self.track = 0

        self.status()
        if self.first_move == True and "Breeze" in percept:
            return "Climb"
        else:
            while True:
                random_or_nah = False
                directions = ["North", "South", "East", "West"]
                moves = 5
                if self.final_path != 0 and len(self.final_path) != 1:
                    moves = self.reach_destination(percept, index)
                    break
                if self.shoot_available is True and self.hasShot == False or len(self.find_location("B")) > 1 and self.hasShot == False:
                    if self.got_index == False:
                        self.limit_Wumpus()
                    if len(self.find_location("PM")) == 1 or len(self.find_location("BM")) == 1:
                        moves = self.time_to_shoot()
                        if moves != 5 and moves != None:
                            random_or_nah = True
                            break

                if len(self.check_location) > 0 and moves == 5 or len(self.check_location) > 0 and moves == None:
                    moves = self.go_here(percept, index)
                    if moves == 0 and len(self.find_location("PM")) != 1:
                        random_or_nah = False
                    else:
                        if len(self.find_location("PM")) == 1 and moves != "Forward" and self.hasShot == False or len(self.find_location("BM")) == 1 and moves != "Forward" and self.hasShot == False:
                            move1 = self.time_to_shoot()
                            if move1 != None:
                                moves = move1
                        if moves != 0:
                            random_or_nah = True
                            break
                if random_or_nah == False:
                    moves = random.choice(possible_moves)
                    what_direction = self.facing(moves)
                    if index[0][0] == 3:
                        directions.remove("South")
                    if index[0][0] == 0:
                        directions.remove("North")
                    if index[1][0] == 0:
                        directions.remove("West")
                    if index[1][0] == 3:
                        directions.remove("East")

                    if what_direction not in directions:
                        self.undo_face(moves)
                        continue
                    else:
                        status = self.evaluate(what_direction, moves, index, percept)
                        if status == "Bad Move":
                            continue
                        elif status == "Undo Face":
                            self.undo_face(moves)
                            continue
                        else:
                            break
            self.count = self.count + 1
            if self.count > 0:
                self.first_move = False
            if moves == "Shoot":
                self.hasShot = True
            self.last_move = moves
            location = self.find_location("E")
            if self.last_location != location[0]:
                self.last_location = location[0]
                self.path.append(location[0])
            return moves

    def check_and_delete_walls(self):
        x = 0
        while x < len(self.path):
            if x == len(self.path):
                break 
            if self.board[self.path[x][0]][self.path[x][1]] == "W":
                self.path.pop(x)
                x = x - 1
                if x > 0:
                    self.path.pop(x)
                    x = x - 1
            x = x + 1     

    def reach_destination(self, percept, agent_location):
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if x == agent_location[0][0] and y == agent_location[1][0]:
                    if x + 1 < 4 and x + 1 == self.final_path[1][0] and y == self.final_path[1][1]:
                        if self.facing_direction == "North":
                            self.facing("TurnRight")
                            return "TurnRight"
                        elif self.facing_direction == "South":
                            self.location(self.facing_direction, "Forward", agent_location, percept)
                            self.final_path.pop(1)
                            return "Forward"
                        elif self.facing_direction == "West":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        elif self.facing_direction == "East":
                            self.facing("TurnRight")
                            return "TurnRight"
                    elif x - 1 >= 0 and x - 1 == self.final_path[1][0] and y == self.final_path[1][1]:
                        if self.facing_direction == "North":
                            self.location(self.facing_direction, "Forward", agent_location, percept)
                            self.final_path.pop(1)
                            return "Forward"
                        elif self.facing_direction == "South":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        elif self.facing_direction == "East":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        elif self.facing_direction == "West":
                            self.facing("TurnRight")
                            return "TurnRight"
                    
                    elif y - 1 >= 0 and x == self.final_path[1][0] and y - 1 == self.final_path[1][1]:
                        if self.facing_direction == "North":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        elif self.facing_direction == "South":
                            self.facing("TurnRight")
                            return "TurnRight"
                        elif self.facing_direction == "East":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        elif self.facing_direction == "West":
                            self.location(self.facing_direction, "Forward", agent_location, percept)
                            self.final_path.pop(1)
                            return "Forward"
                        
                    elif y + 1 < 4 and x == self.final_path[1][0] and y + 1 == self.final_path[1][1]:
                        if self.facing_direction == "North":
                            self.facing("TurnRight")
                            return "TurnRight"

                        elif self.facing_direction == "South":
                            self.facing("TurnLeft")
                            return "TurnLeft"
                        
                        elif self.facing_direction == "East":
                            self.location(self.facing_direction, "Forward", agent_location, percept)
                            self.final_path.pop(1)
                            return "Forward"
                        
                        elif self.facing_direction == "West":
                            self.facing("TurnRight")
                            return "TurnRight"

    def find_path_back(self):
        goal = (3, 0)
        self.path.reverse()
        start = self.path[0]
        temp_path = []
        final_path = []
        temp_path.append(start)
        compare = []
        agent = self.find_location("E")
        good = False
        i = 0
        while i <= len(self.path):
            if temp_path[len(temp_path) - 1] == goal:
                good = True
                break
            if len(self.path) == 1:
                break
            if i == len(self.path):
                if len(compare) == 0:
                    break
                self.num = self.num + 1
                temp_path.append(compare[-1])
                last_index = self.path.index(compare[-1])
                del self.path[0:last_index]
                start = compare[-1]
                compare.clear()
                i = 0
                
            a = float(start[0] + (start[1] / 10))
            b = float(self.path[i][0] + (self.path[i][1] / 10)) 
            c = round(float(a - b), 1)
            if c == 1  or c == -1 or c == 0.1 or c == -0.1:
                compare.append(self.path[i])
            i = i + 1

        if good == False:
            temp_path.append(goal)
        final_path = self.confirm_path(temp_path)
        self.final_path = final_path

    def confirm_path(self, temp_path):
        a = 0
        b = 0
        c = 1
        d = 1
        popped_variable = 0
        if temp_path[len(temp_path) - 1] == (3, 0):
            popped_variable = temp_path.pop(len(temp_path) - 1)

        count = 0
        while a < len(temp_path):
            if a == len(temp_path) - 2 and b == len(temp_path) - 1:
                break
            while b < len(temp_path):
                if b > len(temp_path) - 2 and d > len(temp_path) - 1:
                    break
                if temp_path[a] == temp_path[b] and temp_path[c] == temp_path[d]:
                    count = count + 1
    
                if count > 1:
                    temp_path.pop(b)
                    temp_path.pop(d - 1)
                else:
                    b = b + 2
                    d = d + 2

            a = a + 2
            c = c + 2
            b = a
            d = c
            count = 0

        if popped_variable != 0:
            temp_path.append(popped_variable)

        return temp_path

    def status(self):
        if len(self.check_location) > 0:
            a = 0
            x = 0
            y = 0
            while x < len(self.board):
                while y <= len(self.board):
                    if y == len(self.board):
                        y = 0
                        break
                    if len(self.check_location) == 0:
                        break
                    if a >= len(self.check_location):
                        break
                    if x == self.check_location[a][0] and y == self.check_location[a][1]:
                        if x - 1 < 0 and y - 1 < 0:
                            if self.board[x + 1][y] == "PM" and self.board[x][y + 1] == "PM":
                                self.check_location.pop(a)
                                x = 0
                                y = 0
                                a = 0
                        elif x - 1 < 0 and y + 1 > 3 : 
                            if self.board[x + 1][y] == "PM" and self.board[x][y - 1] == "PM":
                                self.check_location.pop(a)
                                x = 0
                                y = 0
                                a = 0
                        elif x + 1 > 3 and y - 1 < 0:
                            if self.board[x - 1][y] == "PM" and self.board[x][y + 1] == "PM":
                                self.check_location.pop(a)
                                x = 0
                                y = 0
                                a = 0
                        elif x + 1 > 3 and y + 1 > 3:
                            if self.board[x - 1][y] == "PM" and self.board[x][y - 1] == "PM":
                                self.check_location.pop(a)
                                x = 0
                                y = 0
                                a = 0
                        else:
                            a = a + 1
                            break
                    y = y + 1
                if len(self.check_location) == 0:
                        break
                if a >= len(self.check_location):
                    break
                x = x + 1


    def go_here(self, percept, agent_location):
        if self.track == 0:
            self.old_agent_location = agent_location.copy()
        self.track = self.track + 1
        move = 0
        num_of_pm = 0
        new_pm = []
        destination = self.check_location[0]
        
        if self.board[destination[0]][destination[1]] == "W":
            return move
        if destination[0] == agent_location[0][0] and destination[1] == agent_location[1][0]:
            if destination[0] + 1 < 4 and self.board[destination[0] + 1][destination[1]] == "PM" or destination[0] + 1 < 4 and self.board[destination[0] + 1][destination[1]] == "BM" or destination[0] + 1 < 4 and self.board[destination[0] + 1][destination[1]] == "B":
                num_of_pm = num_of_pm + 1
                new_pm.append((destination[0] + 1, destination[1]))
            if destination[0] - 1 >= 0 and self.board[destination[0] - 1][destination[1]] == "PM" or destination[0] - 1 >= 0 and self.board[destination[0] - 1][destination[1]] == "BM" or destination[0] - 1 >= 0 and self.board[destination[0] - 1][destination[1]] == "B":
                num_of_pm = num_of_pm + 1
                new_pm.append((destination[0] - 1, destination[1]))
            if destination[1] - 1 >= 0 and self.board[destination[0]][destination[1] - 1] == "PM" or destination[1] - 1 >= 0 and self.board[destination[0]][destination[1] - 1] == "BM" or destination[1] - 1 >= 0 and self.board[destination[0]][destination[1] - 1] == "B":
                num_of_pm = num_of_pm + 1
                new_pm.append((destination[0], destination[1] - 1))
            if destination[1] + 1 < 4 and self.board[destination[0]][destination[1] + 1] == "PM" or destination[1] + 1 < 4 and self.board[destination[0]][destination[1] + 1] == "BM" or destination[1] + 1 < 4 and self.board[destination[0]][destination[1] + 1] == "B":
                num_of_pm = num_of_pm + 1
                new_pm.append((destination[0], destination[1] + 1))
            what = 0
            if len(new_pm) > 0:
                what = self.board[new_pm[0][0]][new_pm[0][1]]
            final = 0
            for i in range(len(self.original_threat)):
                for j in range(len(new_pm)):
                    if self.original_threat[i] == new_pm[j]:
                        final = self.original_threat[i]

            if num_of_pm > 1:
                self.make_safe_spots_part_2(final, new_pm, percept, what)
                self.check_location.clear()
                self.track = 0
            else:
                status = self.make_safe_spots_part_2(final, new_pm, percept, what)
                if status == "Clear":
                    self.check_location.clear()

            if len(self.check_location) != 0:
                self.check_location.remove(destination)
                if len(self.find_location("PM")) == 1 or len(self.find_location("BM")) == 1:
                    self.check_location.clear()
                
                self.track = 0

        if len(self.check_location) > 0:
            hypothtical_move = []
            for x in range(len(self.board)):
                for y in range(len(self.board)):
                    if x == agent_location[0][0] and y == agent_location[1][0]:
                        if x + 1 < 4 and self.board[x + 1][y] == "S" or x + 1 < 4 and self.board[x + 1][y] == "PS" or x + 1 == destination[0] and y == destination[1] or x + 1 < 4 and self.board[x + 1][y] == "PS":
                            hypothtical_move.append((x + 1,y))
                        if x - 1 >= 0 and self.board[x - 1][y] == "S" or x - 1 >= 0 and self.board[x - 1][y] == "PS" or x - 1 == destination[0] and y == destination[1] or x - 1 >= 0 and self.board[x - 1][y] == "PS":
                            hypothtical_move.append((x - 1, y))
                        if y + 1 < 4 and self.board[x][y + 1] == "S" or y + 1 < 4 and self.board[x][y + 1] == "PS" or x == destination[0] and y + 1 == destination[1] or y + 1 < 4 and self.board[x][y + 1] == "PS":
                            hypothtical_move.append((x, y + 1))
                        if y - 1 >= 0 and self.board[x][y - 1] == "S" or y - 1 >=0 and self.board[x][y - 1] == "PS" or x == destination[0] and y - 1 == destination[1] or y - 1 >= 0 and self.board[x][y - 1] == "PS":
                            hypothtical_move.append((x, y - 1))

            hypothtical_move = self.closest_to_dest(hypothtical_move, destination)
            self.redundancy.append(hypothtical_move)
            a = 0
            for i in range(len(self.redundancy)):
                if self.redundancy[0] == self.redundancy[i]:
                    a = a + 1    
            if a > 7:
                self.check_location.pop(0)

            if destination[0] > self.old_agent_location[0][0] and destination[1] > self.old_agent_location[1][0]:
                if agent_location[0][0] + 1 == hypothtical_move[0] and agent_location[1][0] == hypothtical_move[1]:  
                    if self.facing_direction == "North":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "West":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "South":
                        move = "Forward"
                    elif self.facing_direction == "East":
                        self.facing("TurnRight")
                        return "TurnRight"

                elif agent_location[0][0] == hypothtical_move[0] and agent_location[1][0] + 1 == hypothtical_move[1]:
                    if self.facing_direction == "North":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "South":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "East":
                        move = "Forward"
                    elif self.facing_direction == "West":
                        self.facing("TurnRight")
                        return "TurnRight"

            elif destination[0] < self.old_agent_location[0][0] and destination[1] > self.old_agent_location[1][0]:
                if agent_location[0][0] - 1 == hypothtical_move[0] and agent_location[1][0] == hypothtical_move[1]:  
                    if self.facing_direction == "North":
                        move = "Forward"
                    elif self.facing_direction == "West":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "South":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "East":
                        self.facing("TurnLeft")
                        return "TurnLeft"

                elif agent_location[0][0] == hypothtical_move[0] and agent_location[1][0] + 1 == hypothtical_move[1]:
                    if self.facing_direction == "North":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "South":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "East":
                        move = "Forward"
                    elif self.facing_direction == "West":
                        self.facing("TurnRight")
                        return "TurnRight"
                    
            elif destination[0] < self.old_agent_location[0][0] and destination[1] < self.old_agent_location[1][0]:
                if agent_location[0][0] - 1 == hypothtical_move[0] and agent_location[1][0] == hypothtical_move[1]:
                    if self.facing_direction == "South":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "East":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "North":
                        move = "Forward"
                    elif self.facing_direction == "West":
                        self.facing("TurnRight")
                        return "TurnRight"

                elif agent_location[0][0] == hypothtical_move[0] and agent_location[1][0] - 1 == hypothtical_move[1]:
                    if self.facing_direction == "North":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "South":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "East":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "West":
                        move = "Forward"

            elif destination[0] > self.old_agent_location[0][0] and destination[1] < self.old_agent_location[1][0]:
                if agent_location[0][0] + 1 == hypothtical_move[0] and agent_location[1][0] == hypothtical_move[1]:
                    if self.facing_direction == "North":
                      self.facing("TurnLeft")
                      return "TurnLeft"
                    elif self.facing_direction == "South":
                        move = "Forward"
                    elif self.facing_direction == "East":
                        self.facing("TurnRight")
                        return "TurnRight"
                    elif self.facing_direction == "West":
                        self.facing("TurnLeft")
                        return "TurnLeft"

                elif agent_location[0][0] == hypothtical_move[0] and agent_location[1][0] - 1 == hypothtical_move[1]:
                    if self.facing_direction == "North":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "South":
                        self.facing("TurnRight") 
                        return "TurnRight"
                    elif self.facing_direction == "East":
                        self.facing("TurnLeft")
                        return "TurnLeft"
                    elif self.facing_direction == "West":
                        move = "Forward"

            if move == "Forward":
                self.location(self.facing_direction, move, agent_location, percept)

        return move

    def closest_to_dest(self, hypothetical_move, destination):
        which_is_the_least_steps = []
        for i in range(len(hypothetical_move)):
            a = abs(destination[0] - hypothetical_move[i][0])
            b = abs(destination[1] - hypothetical_move[i][1])
            c = a + b
            which_is_the_least_steps.append(c)

        if len(which_is_the_least_steps) > 0:
            smallest_number = min(which_is_the_least_steps)
            index = which_is_the_least_steps.index(smallest_number)
            return hypothetical_move[index]
        else:
            return "Nah"

    def time_to_shoot(self):
        agent = self.find_location("E")
        threat_near_by = 0
        if (len(self.find_location("PM"))) > 0:
            threat_near_by = self.find_location("PM")
        else:
            threat_near_by = self.find_location("BM")
        if len(threat_near_by) == 1:
            for x in range(len(self.board)):
                for y in range(len(self.board)):
                    if x == threat_near_by[0][0] and y == threat_near_by[0][1]:
                        if x - 1 >= 0 and self.board[x - 1][y] == "E":
                            if self.facing_direction == "North":
                                self.facing("TurnRight")
                                return "TurnRight"
                            elif self.facing_direction == "South":
                                return "Shoot"
                            elif self.facing_direction == "West":
                                self.facing("TurnLeft")
                                return "TurnLeft"
                            elif self.facing_direction == "East":
                                self.facing("TurnRight")
                                return "TurnRight"

                        if x + 1 < 4 and self.board[x + 1][y] == "E":
                            if self.facing_direction == "North":
                                return "Shoot"
                            elif self.facing_direction == "South":
                                self.facing("TurnLeft")
                                return "TurnLeft"
                            elif self.facing_direction == "West":
                                self.facing("TurnLeft")
                                return "TurnLeft"
                            elif self.facing_direction == "East":
                                self.facing("TurnLeft")
                                return "TurnLeft"

                        if y - 1 >= 0 and self.board[x][y - 1] == "E":
                            if self.facing_direction == "North":
                                self.facing("TurnRight")
                                return "TurnRight"
                            elif self.facing_direction == "South":
                                self.facing("TurnLeft")
                                return "TurnLeft"
                            elif self.facing_direction == "West":
                                self.facing("TurnRight")
                                return "TurnRight"
                            elif self.facing_direction == "East":
                                return "Shoot"

                        if y + 1 < 4 and self.board[x][y + 1] == "E":
                            if self.facing_direction == "North":
                                self.facing("TurnLeft")
                                return "TurnLeft"
                            elif self.facing_direction == "South":
                                self.facing("TurnRight")
                                return "TurnRight"
                            elif self.facing_direction == "West":
                                return "Shoot"
                            elif self.facing_direction == "East":
                                self.facing("TurnRight")
                                return "TurnRight"
                

    def make_safe_spots_part_2(self, final_threat, threat, percept, what):
        if "Stench" in percept and "Breeze" in percept:
            all_threat_spots = self.find_location("PM") + self.find_location("BM")
            new_all_threat_spots = [x for x in all_threat_spots if x not in threat]
            if final_threat != 0:
                threat.remove(final_threat)
            if len(threat) == 1:
                self.board[threat[0][0]][threat[0][1]] = "B"
            else:
                self.board[threat[0][0]][threat[0][1]] = "B"
                self.board[threat[1][0]][threat[1][1]] = "B"
            index = 0
            done = False
            for x in range(len(self.board)):
                for y in range(len(self.board)):
                    if index == len(new_all_threat_spots):
                        done = True
                        break 
                    if x == new_all_threat_spots[index][0] and y == new_all_threat_spots[index][1]:
                        self.board[x][y] = "0"
                        index = index + 1
                        self.dont_change_pm = True
                if done == True:
                    break

        if "Stench" in percept and "Breeze" not in percept and len(threat) > 1 :
            all_threat_spots = self.find_location(what)
            new_all_threat_spots = [x for x in all_threat_spots if x not in threat]
            if final_threat != 0:
                threat.remove(final_threat)
            if len(threat) == 1:
                self.board[threat[0][0]][threat[0][1]] = "0"
            else:
                self.board[threat[0][0]][threat[0][1]] = "0"
                self.board[threat[1][0]][threat[1][1]] = "0"
            index = 0
            done = False
            for x in range(len(self.board)):
                for y in range(len(self.board)):
                    if index == len(new_all_threat_spots):
                        done = True
                        break 
                    if x == new_all_threat_spots[index][0] and y == new_all_threat_spots[index][1]:
                        self.board[x][y] = "0"
                        index = index + 1
                        self.dont_change_pm = True
                if done == True:
                    break
        elif "Breeze" in percept and "Stench" not in percept:
            threat_spot = self.find_location("BM")
            if len(threat_spot) == 1:
                self.board[threat_spot[0][0]][threat_spot[0][1]] = "PM"
                self.dont_change_pm = True
        elif "Stench" in percept and len(threat) == 1 and "Breeze" not in percept:
            all_threat_spots = self.find_location(what)
            new_all_threat_spots = [x for x in all_threat_spots if x not in threat]
            if len(new_all_threat_spots) > 0:
                self.board[new_all_threat_spots[0][0]][new_all_threat_spots[0][1]] = "0"
            return "Clear"
        else:
            if "Breeze" not in percept and final_threat != 0:
                self.board[final_threat[0]][final_threat[1]] = "0"


    def evaluate(self, what_direction, move, index, percept):
        pm_array = self.find_location("PM")
        BM_array = self.find_location("BM")
        B_array = self.find_location("B")
        agent = self.find_location("E")
        Wall_array = self.find_location("W")
        board_copy = deepcopy(self.board)
        location = self.point.copy()
        board_status = self.location(what_direction, move, index, percept)
        if board_status == "Missed":
            return "Bad Move"
        new_agent_location = self.find_location("E")
        if new_agent_location[0] in pm_array or new_agent_location[0] in BM_array or new_agent_location[0] in B_array or new_agent_location[0] in Wall_array:
            self.board = deepcopy(board_copy)
            self.point = location.copy()
            return "Bad Move"
        else:
            return "good Move"

    def limit_Wumpus(self):
        pm_location = self.find_location("PM")
        BM_location = self.find_location("BM")
        explorer_location = self.find_location("E")
        i = 0
        if len(pm_location) > 1 and pm_location and not BM_location:
            while i < len(pm_location):
                if pm_location[i][0] < explorer_location[0][0] and pm_location[i][1] == explorer_location[0][1]:
                    if pm_location[i][1] - 1 >= 0 and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "S" and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "B" and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "W":
                        if (pm_location[i][0], pm_location[i][1] - 1) not in self.check_location: 
                            self.check_location.append((pm_location[i][0], pm_location[i][1] - 1))
                            self.original_threat.append((pm_location[i][0], pm_location[i][1]))

                if pm_location[i][0] > explorer_location[0][0] and pm_location[i][1] == explorer_location[0][1]:
                    if pm_location[i][1] - 1 >= 0 and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "S" and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "B" and self.board[pm_location[i][0]][pm_location[i][1] - 1] != "W":
                        if (pm_location[i][0], pm_location[i][1] - 1) not in self.check_location: 
                            self.check_location.append((pm_location[i][0], pm_location[i][1] - 1))
                            self.original_threat.append((pm_location[i][0], pm_location[i][1]))

                if pm_location[i][0] == explorer_location[0][0] and pm_location[i][1] > explorer_location[0][1]:
                    if pm_location[i][0] + 1 < 4 and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "S" and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "B" and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "W":
                        if (pm_location[i][0] + 1, pm_location[i][1]) not in self.check_location: 
                            self.check_location.append((pm_location[i][0] + 1, pm_location[i][1]))
                            self.original_threat.append((pm_location[i][0], pm_location[i][1]))

                if pm_location[i][0] == explorer_location[0][0] and pm_location[i][1] < explorer_location[0][1]:
                    if pm_location[i][0] + 1 < 4 and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "S" and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "B" and self.board[pm_location[i][0] + 1][pm_location[i][1]] != "W":
                        if (pm_location[i][0] + 1, pm_location[i][1]) not in self.check_location: 
                            self.check_location.append((pm_location[i][0] + 1, pm_location[i][1]))
                            self.original_threat.append((pm_location[i][0], pm_location[i][1]))
                i = i + 1
        elif BM_location and not pm_location:
            for i in range(len(BM_location)):
                if BM_location[i][0] < explorer_location[0][0] and BM_location[i][1] == explorer_location[0][1]:
                    if BM_location[i][1] - 1 >= 0:
                        self.check_location.append((BM_location[i][0], BM_location[i][1] - 1))
                        self.original_threat.append((BM_location[i][0], BM_location[i][1]))
                if BM_location[i][0] > explorer_location[0][0] and BM_location[i][1] == explorer_location[0][1]:
                    if BM_location[i][1] - 1 >= 0:
                        self.check_location.append((BM_location[i][0], BM_location[i][1] - 1))
                        self.original_threat.append((BM_location[i][0], BM_location[i][1]))
                if BM_location[i][0] == explorer_location[0][0] and BM_location[i][1] > explorer_location[0][1]:
                    if BM_location[i][0] + 1 < 4:
                        self.check_location.append((BM_location[i][0] + 1, BM_location[i][1]))
                        self.original_threat.append((BM_location[i][0], BM_location[i][1]))
                if BM_location[i][0] == explorer_location[0][0] and BM_location[i][1] < explorer_location[0][1]:
                    if BM_location[i][0] + 1 < 4:
                        self.check_location.append((BM_location[i][0] + 1, BM_location[i][1]))
                        self.original_threat.append((BM_location[i][0], BM_location[i][1]))

        elif BM_location and pm_location:
            self.board[pm_location[0][0]][pm_location[0][1]] = "0"
            self.dont_change_pm = True

        if len(self.check_location) > 0:
            self.got_index = True 

                
     
    def compare_two_locations(self):
        original = numpy.array([len(self.board) - 1, 0])
        now = numpy.array(self.point.copy())
        return numpy.array_equiv(original, now)
    
    def undo_face(self, moves):
        if moves == "TurnLeft":
            if self.facing_direction == "West":
                self.facing_direction = "North"
            elif self.facing_direction == "North":
                self.facing_direction = "East"
            elif self.facing_direction == "East":
                self.facing_direction = "South"
            elif self.facing_direction == "South":
                self.facing_direction = "West"
        if moves == "TurnRight":
            if self.facing_direction == "East":
                self.facing_direction = "North"
            elif self.facing_direction == "North":
                self.facing_direction = "West"
            elif self.facing_direction == "West":
                self.facing_direction = "South"
            elif self.facing_direction == "South":
                self.facing_direction = "East"

    def set_base(self):
        self.board[self.point[0]][self.point[1]] = "E"

    def facing(self, possible_action):
        
        if possible_action != "TurnLeft" and possible_action != "TurnRight":
            return self.facing_direction

        if possible_action == "TurnRight" and self.facing_direction == "North":
            self.facing_direction = "East"
        
        elif possible_action == "TurnRight" and self.facing_direction == "South":
            self.facing_direction = "West"
        
        elif possible_action == "TurnRight" and self.facing_direction == "East":
            self.facing_direction = "South"
        
        elif possible_action == "TurnRight" and self.facing_direction == "West":
            self.facing_direction = "North"

        elif possible_action == "TurnLeft" and self.facing_direction == "North":
            self.facing_direction = "West"
        
        elif possible_action == "TurnLeft" and self.facing_direction == "South":
            self.facing_direction = "East"
        
        elif possible_action == "TurnLeft" and self.facing_direction == "East":
            self.facing_direction = "North"
        
        elif possible_action == "TurnLeft" and self.facing_direction == "West":
            self.facing_direction = "South"

        return self.facing_direction

    def location(self, facing, location, index, percept, reset=False):       
        if reset == False:
            checkshooting = 5
            statement_hit = 5
            if location == "Shoot":
                checkshooting = True
                statement_hit = False
            if location == "Forward" and facing == "North" and index[0][0] >= 0:
                if "Stench" in percept or "Breeze" in percept:
                    self.board[self.point[0]][self.point[1]] = "PS"
                    self.point[0] = self.point[0] - 1
                    self.board[self.point[0]][self.point[1]] = "E"
                else:
                    self.board[self.point[0]][self.point[1]] = "S"
                    self.point[0] = self.point[0] - 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
            if location == "Forward" and facing == "South" and index[0][0] < 4:
                if "Stench" in percept or "Breeze" in percept:
                    self.board[self.point[0]][self.point[1]] = "PS"
                    self.point[0] = self.point[0] + 1
                    self.board[self.point[0]][self.point[1]] = "E"
                else:
                    self.board[self.point[0]][self.point[1]] = "S"
                    self.point[0] = self.point[0] + 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
            if location == "Forward" and facing == "East" and index[1][0] < 4:
                if "Stench" in percept or "Breeze" in percept:
                    self.board[self.point[0]][self.point[1]] = "PS"
                    self.point[1] = self.point[1] + 1
                    self.board[self.point[0]][self.point[1]] = "E"
                else:
                    self.board[self.point[0]][self.point[1]] = "S"
                    self.point[1] = self.point[1] + 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
            if location == "Forward" and facing == "West" and index[1][0] >= 0:
                if "Stench" in percept or "Breeze" in percept:
                    self.board[self.point[0]][self.point[1]] = "PS"
                    self.point[1] = self.point[1] - 1
                    self.board[self.point[0]][self.point[1]] = "E"
                else:
                    self.board[self.point[0]][self.point[1]] = "S"
                    self.point[1] = self.point[1] - 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
            if checkshooting == True:
                if location == "Shoot" and facing == "North" and index[0][0] - 1 >= 0 and self.board[index[0][0] - 1][index[1][0]] == "PM":
                    self.board[self.point[0] - 1][self.point[1]] = "0"
                    statement_hit = True
                if location == "Shoot" and facing == "South" and index[0][0] + 1 < 4 and self.board[index[0][0] + 1][index[1][0]] == "PM":
                    self.board[self.point[0] + 1][self.point[1]] = "0"
                    statement_hit = True
                if location == "Shoot" and facing == "East" and index[1][0] + 1 < 4 and self.board[index[0][0]][index[1][0] + 1] == "PM":
                    self.board[self.point[0]][self.point[1] + 1] = "0"
                    statement_hit = True
                if location == "Shoot" and facing == "West" and index[1][0] - 1 >= 0 and self.board[index[0][0]][index[1][0] - 1] == "PM":
                    self.board[self.point[0]][self.point[1] - 1] = "0"
                    statement_hit = True

            if statement_hit == False:
                return "Missed"
        else:
            if "Bump" in percept:
                if self.facing_direction == "North" and index[0][0] < 4 and self.point[0] + 1 < 4:
                    self.board[self.point[0]][self.point[1]] = "W"
                    self.point[0] = self.point[0] + 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
                if self.facing_direction == "South" and index[0][0] >= 0 and self.point[0] - 1 >= 0:
                    self.board[self.point[0]][self.point[1]] = "W"
                    self.point[0] = self.point[0] - 1
                    self.board[self.point[0]][self.point[1]] = "E"

                if self.facing_direction == "East" and index[1][0] >= 0 and self.point[1] - 1 >= 0:
                    self.board[self.point[0]][self.point[1]] = "W"
                    self.point[1] = self.point[1] - 1
                    self.board[self.point[0]][self.point[1]] = "E"
                
                if self.facing_direction == "West" and index[1][0] < 4 and self.point[1] + 1 < 4:
                    self.board[self.point[0]][self.point[1]] = "W"
                    self.point[1] = self.point[1] + 1
                    self.board[self.point[0]][self.point[1]] = "E"

            if "Stench" in percept:
                if self.point[0] + 1 < 4 and self.board[self.point[0] + 1][self.point[1]] != "S" and self.board[self.point[0] + 1][self.point[1]] != "W" and self.board[self.point[0] + 1][self.point[1]] != "PS" and self.board[self.point[0] + 1][self.point[1]] != "B" and len(self.find_location("BM")) != 1 and self.dont_change_pm == False:
                    self.point[0] = self.point[0] + 1
                    self.board[self.point[0]][self.point[1]] = "PM"
                    self.point[0] = self.point[0] - 1

                if self.point[0] - 1 >= 0 and self.board[self.point[0] - 1][self.point[1]] != "S" and self.board[self.point[0] - 1][self.point[1]] != "W" and self.board[self.point[0] - 1][self.point[1]] != "PS" and self.board[self.point[0] - 1][self.point[1]] != "B" and len(self.find_location("BM")) != 1 and self.dont_change_pm == False:
                    self.point[0] = self.point[0] - 1
                    self.board[self.point[0]][self.point[1]] = "PM"
                    self.point[0] = self.point[0] + 1

                if self.point[1] + 1 < 4 and self.board[self.point[0]][self.point[1] + 1] != "S" and self.board[self.point[0]][self.point[1] + 1] != "W" and self.board[self.point[0]][self.point[1] + 1] != "PS" and self.board[self.point[0]][self.point[1] + 1] != "B" and len(self.find_location("BM")) != 1 and self.dont_change_pm == False:
                    self.point[1] = self.point[1] + 1
                    self.board[self.point[0]][self.point[1]] = "PM"
                    self.point[1] = self.point[1] - 1 
    
                if self.point[1] - 1 >= 0 and self.board[self.point[0]][self.point[1] - 1] != "S" and self.board[self.point[0]][self.point[1] - 1] != "W" and self.board[self.point[0]][self.point[1] - 1] != "PS" and self.board[self.point[0]][self.point[1] - 1] != "B" and len(self.find_location("BM")) != 1 and self.dont_change_pm == False:
                    self.point[1] = self.point[1] - 1
                    self.board[self.point[0]][self.point[1]] = "PM"
                    self.point[1] = self.point[1] + 1

            if "Breeze" in percept:
                if self.point[0] + 1 < 4 and self.board[self.point[0] + 1][self.point[1]] != "S" and self.board[self.point[0] + 1][self.point[1]] != "W" and self.board[self.point[0] + 1][self.point[1]] != "PS" :
                    if self.board[self.point[0] + 1][self.point[1]] != "PM" and self.board[self.point[0] + 1][self.point[1]] != "KW" and self.board[self.point[0] + 1][self.point[1]] != "BM":
                        self.point[0] = self.point[0] + 1
                        self.board[self.point[0]][self.point[1]] = "B"
                        self.point[0] = self.point[0] - 1
                    elif self.dont_change_pm == False and self.board[self.point[0] + 1][self.point[1]] != "KW":
                        self.point[0] = self.point[0] + 1
                        self.board[self.point[0]][self.point[1]] = "BM"
                        self.point[0] = self.point[0] - 1

                if self.point[0] - 1 >= 0 and self.board[self.point[0] - 1][self.point[1]] != "S" and self.board[self.point[0] - 1][self.point[1]] != "W" and self.board[self.point[0] - 1][self.point[1]] != "PS":
                    if self.board[self.point[0] - 1][self.point[1]] != "PM" and self.board[self.point[0] - 1][self.point[1]] != "KW" and self.board[self.point[0] - 1][self.point[1]] != "BM":
                        self.point[0] = self.point[0] - 1
                        self.board[self.point[0]][self.point[1]] = "B"
                        self.point[0] = self.point[0] + 1
                    elif self.dont_change_pm == False and self.board[self.point[0] - 1][self.point[1]] != "KW":
                        self.point[0] = self.point[0] - 1
                        self.board[self.point[0]][self.point[1]] = "BM"
                        self.point[0] = self.point[0] + 1

                if self.point[1] + 1 < 4 and self.board[self.point[0]][self.point[1] + 1] != "S" and self.board[self.point[0]][self.point[1] + 1] != "W" and self.board[self.point[0]][self.point[1] + 1] != "PS":
                    if self.board[self.point[0]][self.point[1] + 1] != "PM" and self.board[self.point[0]][self.point[1] + 1] != "KW" and self.board[self.point[0]][self.point[1] + 1] != "BM":
                        self.point[1] = self.point[1] + 1
                        self.board[self.point[0]][self.point[1]] = "B"
                        self.point[1] = self.point[1] - 1
                    elif self.dont_change_pm == False and self.board[self.point[0]][self.point[1] + 1] != "KW":
                        self.point[1] = self.point[1] + 1
                        self.board[self.point[0]][self.point[1]] = "BM"
                        self.point[1] = self.point[1] - 1
    
                if self.point[1] - 1 >= 0 and self.board[self.point[0]][self.point[1] - 1] != "S" and self.board[self.point[0]][self.point[1] - 1] != "W" and self.board[self.point[0]][self.point[1] - 1] != "PS":
                    if self.board[self.point[0]][self.point[1] - 1] != "PM" and self.board[self.point[0]][self.point[1] - 1] != "KW" and self.board[self.point[0]][self.point[1] - 1] != "BM":
                        self.point[1] = self.point[1] - 1
                        self.board[self.point[0]][self.point[1]] = "B"
                        self.point[1] = self.point[1] + 1
                    elif self.dont_change_pm == False and self.board[self.point[0]][self.point[1] - 1] != "KW":
                        self.point[1] = self.point[1] - 1
                        self.board[self.point[0]][self.point[1]] = "BM"
                        self.point[1] = self.point[1] + 1
                    
            if "Scream" in percept:
                all_pm_location = 0
                temp = self.find_location("PM")
                if self.facing_direction == "North":
                    self.board[self.point[0] - 1][self.point[1]] = "KW"
                elif self.facing_direction == "South":
                    self.board[self.point[0] + 1][self.point[1]] = "KW"
                elif self.facing_direction == "East":
                    self.board[self.point[0]][self.point[1] + 1] = "KW"
                elif self.facing_direction == "West":
                    self.board[self.point[0]][self.point[1] - 1] = "KW"
                self.check_location.clear()
                if temp:
                    all_pm_location = self.find_location("PM")
                else:
                    all_pm_location = self.find_location("BM")
                i = 0
                for x in range(len(self.board)):
                    for y in range(len(self.board)):
                        if i == len(all_pm_location):
                            break
                        if x == all_pm_location[i][0] and y == all_pm_location[i][1]:
                            self.board[x][y] = "0"
                            i = i + 1
        self.eliminate_some_danger_spots()
        return self.board

                
    def find_location(self, what):
        board = numpy.array(self.board.copy())
        pm_location = numpy.where(board == what)
        new_pm_location = list(zip(pm_location[0], pm_location[1]))
        return new_pm_location

    def eliminate_some_danger_spots(self):
        pm_array = self.find_location("PM")
        safe_location = self.find_location("S")
        BM_array = self.find_location("BM")
        B_array = self.find_location("B")
        safe_spots = False
        if safe_location:
            safe_spots = True

        if pm_array and safe_spots:
            self.make_safe_spots(pm_array, safe_location)

        if BM_array and safe_spots:
            self.make_safe_spots(BM_array, safe_location)
        
        if B_array and safe_spots:
            self.make_safe_spots(B_array, safe_location)

    def make_safe_spots(self, threat_board, safe_board):
        i = 0
        is_wumpus_dead = self.find_location("KW")
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if i == len(threat_board):
                    break
                if x == threat_board[i][0] and y == threat_board[i][1]:
                    for a in range(len(safe_board)):
                        if a == len(safe_board):
                            break
                        if len(is_wumpus_dead) > 0 and self.board[threat_board[i][0]][threat_board[i][1]] == "BM":
                            self.board[threat_board[i][0]][threat_board[i][1]] = "B"

                        if x + 1 < 4 and x + 1 == safe_board[a][0] and y == safe_board[a][1]:
                            if x - 1 >= 0 and self.board[x - 1][y] != "0" and self.board[x - 1][y] != "S" and self.board[x - 1][y] != "PS" or x + 1 < 4 and self.board[x + 1][y] != "0" and self.board[x + 1][y] != "S" and self.board[x + 1][y] != "PS" or y + 1 < 4 and self.board[x][y + 1] != "0" and self.board[x][y + 1] != "S" and self.board[x][y + 1] != "PS" or y - 1 >= 0 and self.board[x][y - 1] != "0" and self.board[x][y - 1] != "S" and self.board[x][y - 1] != "PS":
                                self.board[threat_board[i][0]][threat_board[i][1]] = "PS"
                            else:
                                self.board[threat_board[i][0]][threat_board[i][1]] = "S"

                        if x - 1 >= 0 and x - 1 == safe_board[a][0] and y == safe_board[a][1]:
                            if x + 1 < 4 and self.board[x + 1][y] != "0" and self.board[x + 1][y] != "S" and self.board[x + 1][y] != "PS" or x - 1 >= 0 and self.board[x - 1][y] != "0" and self.board[x - 1][y] != "S" and self.board[x - 1][y] != "PS" or y + 1 < 4 and self.board[x][y + 1] != "0" and self.board[x][y + 1] != "S" and self.board[x][y + 1] != "PS" or y - 1 >= 0 and self.board[x][y - 1] != "0" and self.board[x][y - 1] != "S" and self.board[x][y - 1] != "PS":
                                self.board[threat_board[i][0]][threat_board[i][1]] = "PS"
                            else:
                                self.board[threat_board[i][0]][threat_board[i][1]] = "S"

                        if y + 1 < 4 and x == safe_board[a][0] and y + 1 == safe_board[a][1]:
                            if x - 1 >= 0 and self.board[x - 1][y] != "0" and self.board[x - 1][y] != "S" and self.board[x - 1][y] != "PS" or x + 1 < 4 and self.board[x + 1][y] != "0" and self.board[x + 1][y] != "S" and self.board[x + 1][y] != "PS" or y - 1 >= 0 and self.board[x][y - 1] != "0" and self.board[x][y - 1] != "S" and self.board[x][y - 1] != "PS" or y + 1 < 4 and self.board[x][y + 1] != "0" and self.board[x][y + 1] != "S" and self.board[x][y + 1] != "PS":
                                self.board[threat_board[i][0]][threat_board[i][1]] = "PS"
                            else:
                                self.board[threat_board[i][0]][threat_board[i][1]] = "S"

                        if y - 1 >= 0 and x == safe_board[a][0] and y - 1 == safe_board[a][1]:
                            if x - 1 >= 0 and self.board[x - 1][y] != "0" and self.board[x - 1][y] != "S" and self.board[x - 1][y] != "PS" or x + 1 < 4 and self.board[x + 1][y] != "0" and self.board[x + 1][y] != "S" and self.board[x + 1][y] != "PS" or y + 1 < 4 and self.board[x][y + 1] != "0" and self.board[x][y + 1] != "S" and self.board[x][y + 1] != "PS" or y - 1 >= 0 and self.board[x][y - 1] != "0" and self.board[x][y - 1] != "S" and self.board[x][y - 1] != "PS":
                                self.board[threat_board[i][0]][threat_board[i][1]] = "PS"
                            else:
                                self.board[threat_board[i][0]][threat_board[i][1]] = "S"
                            
                    i = i + 1

    def print_board(self):
        board = numpy.array(self.board.copy())
        print(board)

class aahmad3_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()
        self.count = 0

    def program(self, percept):
        possible_moves = deepcopy(ExplorerAgent.possible_actions)
        move = self.kb.what_to_do(possible_moves, percept, self.count)
        self.count = self.count + 1
        return move