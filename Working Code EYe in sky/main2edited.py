import heapq
from MQTTfuncs import MQTTClient
import time
import random
from huskyylib import HuskyLensLibrary
from collections import Counter
import sys
print("check1")
class PuzzleState:
    def __init__(self, board, parent=None, move=None, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.cost = cost
        self.blank_pos = self.find_blank()
        self.heuristic = self.calculate_heuristic()
        self.f_cost = self.cost + self.heuristic
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def find_blank(self):
        for i in range(2):
            for j in range(2):
                if self.board[i][j] == 0:
                    return (i, j)
    
    def calculate_heuristic(self):
        goal_positions = {goal_state[i][j]: (i, j) for i in range(2) for j in range(2)}
        return sum(abs(i - goal_positions[self.board[i][j]][0]) + abs(j - goal_positions[self.board[i][j]][1])
                   for i in range(2) for j in range(2) if self.board[i][j] != 0)
    
    def get_neighbors(self):
        neighbors = []
        x, y = self.blank_pos # type: ignore
        moves = [(0, -1, 'Left'), (0, 1, 'Right'), (-1, 0, 'Up'), (1, 0, 'Down')] 
        
        for dx, dy, move in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 2 and 0 <= ny < 2:
                new_board = [row[:] for row in self.board]
                new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
                neighbors.append(PuzzleState(new_board, self, move, self.cost + 1))
        
        return neighbors
    
    def is_goal(self):
        return self.board == goal_state
    
    def get_solution_path(self):
        path = []
        current = self
        while current.parent:
            path.insert(0, current.move)
            current = current.parent
        return path

def a_star_search(start_board):
    start_state = PuzzleState(start_board)
    open_set = []
    heapq.heappush(open_set, start_state)
    closed_set = set()
    
    while open_set:
        current_state = heapq.heappop(open_set)
        
        if current_state.is_goal():
            return current_state.get_solution_path()
        
        closed_set.add(tuple(map(tuple, current_state.board)))
        
        for neighbor in current_state.get_neighbors():
            if tuple(map(tuple, neighbor.board)) in closed_set:
                continue
            heapq.heappush(open_set, neighbor)
    
    return None  # No solution found

# Define the goal state for 2x2 puzzle
goal_state = [[1, 2],
              [3, 0]]

PORT = "/dev/tty.usbserial-110"
huskylens = HuskyLensLibrary("SERIAL", PORT)

huskylens.algorithm("ALGORITHM_TAG_RECOGNITION")  # Set AprilTag mode

def get_apriltag_matrix():
    matrix = [[0, 0], [0, 0]]
    try:
        blocks = huskylens.blocks()
        if blocks:
            if not isinstance(blocks, list):
                blocks = [blocks]
            x_vals = [b.x for b in blocks]
            y_vals = [b.y for b in blocks]
            x_mid = (min(x_vals) + max(x_vals)) / 2
            y_mid = (min(y_vals) + max(y_vals)) / 2
            for block in blocks:
                row = 0 if block.y < y_mid else 1
                col = 0 if block.x < x_mid else 1
                matrix[row][col] = block.ID
    except Exception as e:
        print("Error:", e)
    return matrix

def detect_start_board(duration=5.0):
    start_time = time.time()
    matrix_counts = Counter()

    while time.time() - start_time < duration:
        matrix = get_apriltag_matrix()
        # Convert matrix to an immutable type for hashing
        matrix_key = tuple(tuple(row) for row in matrix)
        matrix_counts[matrix_key] += 1
        time.sleep(0.1)

    # Get the most common matrix
    most_common_matrix, _ = matrix_counts.most_common(1)[0]
    start_board = [list(row) for row in most_common_matrix]
    return start_board

print("Getting Start Board...")
start_board=detect_start_board()
print("Done!")
time.sleep(.5)
print("start board: " + str(start_board))

def get_complete_apriltag_grid_positions():
    try:
        blocks = huskylens.blocks()
        if not blocks:
            print("No AprilTags detected.")
            return None

        if not isinstance(blocks, list):
            blocks = [blocks]

        # Step 1: Collect tag coordinates
        coords = [(b.x, b.y) for b in blocks]

        # Step 2: Determine midpoints to divide into quadrants
        x_vals = [x for x, y in coords]
        y_vals = [y for x, y in coords]
        x_mid = (min(x_vals) + max(x_vals)) / 2
        y_mid = (min(y_vals) + max(y_vals)) / 2

        # Step 3: Place detected tags into quadrant-based grid
        positions = {
            "position_1": None,  # top-left
            "position_2": None,  # top-right
            "position_3": None,  # bottom-left
            "position_4": None,  # bottom-right
        }

        for x, y in coords:
            if y < y_mid:
                if x < x_mid:
                    positions["position_1"] = (x, y)
                else:
                    positions["position_2"] = (x, y)
            else:
                if x < x_mid:
                    positions["position_3"] = (x, y)
                else:
                    positions["position_4"] = (x, y)

        # Step 4: Infer missing position
        def infer(pos_a, pos_b, delta_x, delta_y):
            """Given two positions and deltas, infer a new one."""
            if pos_a and pos_b:
                # Use vector addition: p_b + (p_b - p_a)
                x_diff = pos_b[0] - pos_a[0]
                y_diff = pos_b[1] - pos_a[1]
                return (pos_b[0] + x_diff, pos_b[1] + y_diff)
            elif pos_a:
                return (pos_a[0] + delta_x, pos_a[1] + delta_y)
            elif pos_b:
                return (pos_b[0] - delta_x, pos_b[1] - delta_y)
            return None

        # Try to infer the missing one based on neighbors
        if positions["position_1"] is None:
            # infer from position_2 and position_3
            if positions["position_2"] and positions["position_3"]:
                dx = positions["position_2"][0] - positions["position_4"][0]
                dy = positions["position_3"][1] - positions["position_4"][1]
                positions["position_1"] = (positions["position_2"][0] - dx, positions["position_3"][1] - dy)

        elif positions["position_2"] is None:
            if positions["position_1"] and positions["position_4"]:
                dx = positions["position_4"][0] - positions["position_3"][0]
                dy = positions["position_1"][1] - positions["position_3"][1]
                positions["position_2"] = (positions["position_1"][0] + dx, positions["position_1"][1])

        elif positions["position_3"] is None:
            if positions["position_1"] and positions["position_4"]:
                dx = positions["position_4"][0] - positions["position_2"][0]
                dy = positions["position_4"][1] - positions["position_2"][1]
                positions["position_3"] = (positions["position_1"][0], positions["position_4"][1] - dy)

        elif positions["position_4"] is None:
            if positions["position_2"] and positions["position_3"]:
                dx = positions["position_2"][0] - positions["position_1"][0]
                dy = positions["position_3"][1] - positions["position_1"][1]
                positions["position_4"] = (positions["position_3"][0] + dx, positions["position_2"][1] + dy)

        return positions

    except Exception as e:
        print("Error processing AprilTag grid:", e)
        return None

print("getting starting positions...")
for i in range(10):
    positions = get_complete_apriltag_grid_positions()
    print(positions)
    if positions != None:
        break
    else:
        continue
    time.sleep(.1)
print("starting positions: " + str(positions))

def get_target_pos(positions, zero_index):
    if zero_index==(0,0):
        target_pos=positions["position_1"]
    if zero_index==(0,1):
        target_pos=positions['position_2']
    if zero_index==(1,0):
        target_pos=positions["position_3"]
    if zero_index==(1,1):
        target_pos=positions["position_4"]
    return target_pos

# Example starting state for 2x2 puzzle
#start_board = [[3, 1],
#               [2, 0]]

# above needs to be replaced with camera code that detects april tag orientation

print("Getting Solution...")
solution = a_star_search(start_board)
if solution == None:
    print("Puzzle is not solvable")
    sys.exit()
else:
    pass



# Adjust move names to reflect correct direction
fixedsolution = []
for move in solution: # type: ignore
    if move == 'Up':
        fixedsolution.append('Down')
    elif move == 'Down':
        fixedsolution.append('Up')
    elif move == 'Left':
        fixedsolution.append('Right')
    elif move == 'Right':
        fixedsolution.append('Left')

print("Solution:", fixedsolution)
print("# of moves:", len(fixedsolution))
time.sleep(.5)

#function to get the coordinates of the empty space
def get_zero_index(current_board):
    for i, row in enumerate(current_board):
        for j, value in enumerate(row):
            if value == 0:
                zero_index = (i, j)
                break
    return zero_index

#function to determine which robot needs to move on the current board
def get_robot_number(current_board, zero_index, move):
    directions = {
        "Up":    (1, 0),   # a tile below moves up into zero
        "Down":  (-1, 0),  # a tile above moves down into zero
        "Left":  (0, 1),   # a tile right moves left into zero
        "Right": (0, -1),  # a tile left moves right into zero
        }
    move_translated=directions[move]
    row_index=zero_index[0]+move_translated[0]
    column_index=zero_index[1]+move_translated[1]
    robot_number=current_board[row_index][column_index]
    return robot_number

def update_board(current_board, zero_index, move):
    directions = {
        "Up":    (1, 0),   # a tile below moves up into zero
        "Down":  (-1, 0),  # a tile above moves down into zero
        "Left":  (0, 1),   # a tile right moves left into zero
        "Right": (0, -1),  # a tile left moves right into zero
        }
    move_translated=directions[move]
    zero_row=zero_index[0]
    zero_column=zero_index[1]
    robot_row_index=zero_index[0]+move_translated[0]
    robot_column_index=zero_index[1]+move_translated[1]
    new_board=current_board
    new_board[zero_row][zero_column]=current_board[robot_row_index][robot_column_index]
    new_board[robot_row_index][robot_column_index]=0
    return new_board


#MQTT 
client_id = "julianM"
server = "10.247.137.92"
topic = "SlidePuzzle/send/"

print("connecting to MQTT server...")
mqtt1 = MQTTClient(client_id=client_id, server=server)
mqtt1.connect()
time.sleep(.5)
print("Connected!")

current_board=start_board



def get_position(robot_number):
    xpos, ypos = None, None  # Default if no detection

    try:
        print(huskylens.knock())
        tags = huskylens.blocks()
        index = next((i for i, block in enumerate(tags) if block.ID == robot_number), None)        
        #print("index: " + str(index))
        # print("tag ID: " + block[index])
        tag=tags[index]
        #print("test")
        xpos=tag.x
        ypos=tag.y
        return xpos, ypos

    except Exception as e:
        print(f"An error occured: {e}")
        xpos=ypos=None
        return xpos, ypos
        



#main loop
for i in range(len(fixedsolution)):
    zero_index=get_zero_index(current_board) #get location of empy tile
    print("zero index: " + str(zero_index))
    move=fixedsolution[i] #get current move
    robot_number=get_robot_number(current_board, zero_index, move) #get current robot that should move
    new_board=update_board(current_board, zero_index, move) #update board for next move
    current_board=new_board #reset board for next move
    target_pos=get_target_pos(positions, zero_index)

    print("zero index: " + str(zero_index))
    print("target position: " + str(target_pos))
    #replace with state machine
    x, y = get_position(robot_number)
    dx=target_pos[0]-x
    dy=target_pos[1]-y
    print("dxi:" + str(dx))
    print("dyi: " + str(dy))
    payload=[dx, dy]
    mqtt1.publish(topic + str(robot_number), msg=str(payload), retain=False)


    while True:
        #dx=random.random()
        #dy=random.random()

        x, y = get_position(robot_number)
        try:
            time.sleep(.1)
            dx=target_pos[0]-x
            dy=target_pos[1]-y
            print("dx:" + str(dx))
            print("dy: " + str(dy))
            payload=[dx, dy]

            #if dx != None:
            #    print('published to robot ' + str(robot_number))
            #else:
            #    pass



            if abs(dx) < 30 and abs(dy) < 30:
                mqtt1.publish(topic + str(robot_number), msg=str(payload), retain=False)
                break
            else:
                continue

            
        except:
            pass


        #add break condition

        time.sleep(.1)
        


mqtt1.disconnect()

        


