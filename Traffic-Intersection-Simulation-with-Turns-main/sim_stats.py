import random
import time
import threading
import pygame
import sys
import math
import matplotlib.pyplot as plt

# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultRed = 150
defaultYellow = 5
paused = False
pause_start_time = 0
signals = []
noOfSignals = 4
currentGreen = 0   # Indicates which signal is green currently
nextGreen = (currentGreen+1)%noOfSignals    # Indicates which signal will turn green next
currentYellow = 0   # Indicates whether yellow signal is on or off 
spawn_rate = 1
speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}  # average speeds of vehicles

# Coordinates of vehicles' start
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25   # moving gap

# set allowed vehicle types here
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
vehiclesNotTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
rotationAngle = 3
mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
# set random or default green signal time here 
randomGreenSignalTimer = True
# set random green signal time range here 
randomGreenSignalTimerRange = [10,20]
# set vehicle density here
vehicle_density = "medium"  # low, medium, high
density_coefficient = {'low': 0.2, 'medium': 0.5, 'high': 1.0}
base_green = 5 #minimum time for green light
k = 0.1 # constant for denoting importance of density
constant_flow = 2 #constant to estimate saturation flow rate
average_length_of_vehicle = 5 # assume length of vehicle is 5 meter

# Added global variables
time_of_day = 0.0  # initial time
time_increment = 1/(24) * 0.25 
max_density = 1.0
shift = 0.15 # constant to change shift of sine wave
frequency = 0.5 # how often peak of traffic comes in


#simulation statistics 
car_counts = []
signal_switching = 0
density_log = {"low": 0, "medium": 0, "high": 0}
car_types_log = {}
density_over_time = []
start_time = None

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "E:\\Trafic Signal\\Traffic-Intersection-Simulation-with-Turns-main\\images\\" + direction + "\\" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):   
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().width 
                - stoppingGap         
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().width 
                + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().height 
                - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().height 
                + stoppingGap
        else:
            self.stop = defaultStop[direction]
            
        # Set new starting and stopping coordinate
        if(direction=='right'):
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.x+self.image.get_rect().width<stopLines[self.direction]+40):
                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):               
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.x+self.image.get_rect().width<mid[self.direction]['x']):
                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                 
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.y+self.image.get_rect().height)<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):
                                self.y += self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                        self.x += self.speed
                else:
                    if((self.crossedIndex==0) or (self.x+self.image.get_rect().width<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):                 
                        self.x += self.speed
        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<stopLines[self.direction]+50):
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.x + self.image.get_rect().width) < (vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):
                                self.x += self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<mid[self.direction]['y']):
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))): 
                                self.x -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                        self.y += self.speed
                else:
                    if((self.crossedIndex==0) or (self.y+self.image.get_rect().height<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):                
                        self.y += self.speed
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.x>stopLines[self.direction]-70):
                        if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else: 
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.y + self.image.get_rect().height) <(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y  -  movingGap))):
                                self.y += self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.x>mid[self.direction]['x']):
                        if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height +  movingGap))):
                                self.y -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x>=self.stop or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.x>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.y>stopLines[self.direction]-60):
                        if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.y>mid[self.direction]['y']):
                        if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y>=self.stop or (currentGreen==3 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.y>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed 

# Time to density mapping function
def get_density_from_time(time):
    time_of_day_24h = time * 24  
    if 0 <= time_of_day_24h < 6:
        return "low"
    elif 6 <= time_of_day_24h < 9:
        return "high"
    elif 9 <= time_of_day_24h < 16:  
        return "medium"
    elif 16 <= time_of_day_24h < 18:  
        return "high"
    else:  
        return "low"



def calculate_queue_length(direction):
    queue_length = 0
    for lane in range(1, 3):  # lanes 1 and 2
        for vehicle in vehicles[direction][lane]:
            if not vehicle.crossed: # Consider only vehicles that have not crossed
                if direction == 'right':
                    if vehicle.x + vehicle.image.get_rect().width <= stopLines[direction]: # Vehicle is behind the stop line
                        queue_length += 1
                elif direction == 'down':
                    if vehicle.y + vehicle.image.get_rect().height <= stopLines[direction]:
                        queue_length += 1
                elif direction == 'left':
                    if vehicle.x >= stopLines[direction]:
                        queue_length += 1
                elif direction == 'up':
                    if vehicle.y >= stopLines[direction]:
                        queue_length += 1
    return queue_length

def adapt_green_time(queue_length):
    """Adapts the green time based on the queue length."""
    min_green = 10
    max_green = 20
    green_time = min_green + (max_green - min_green) * (queue_length / 20)  # Scale green time (adjust divisor as needed)
    return max(min_green, min(max_green, int(green_time)))  # Clamp to range [10, 20]


def visualize_sine_curve(duration, time_increment, max_density, shift, frequency):
    time_points = []
    density_values = []
    time_of_day = 0.0
    
    for _ in range(int(duration/time_increment)):
        density = max_density * abs(math.sin((time_of_day+shift) * frequency * math.pi))
        time_points.append(time_of_day)
        density_values.append(density)
        time_of_day += time_increment
    
    plt.plot(time_points, density_values)
    plt.xlabel("Time of Day")
    plt.ylabel("Density (0 to 1)")
    plt.title("Sine Curve Visualization")
    plt.grid(True)
    plt.show()

# Initialization of signals with default values
def initialize():
    global vehicle_density
    # Call the `get_density_from_time` function to set initial density
    vehicle_density = get_density_from_time(time_of_day)

    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if(randomGreenSignalTimer):
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow+ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()

def repeat():
    global currentGreen, currentYellow, nextGreen, time_of_day, vehicle_density, paused, pause_start_time, signal_switching

    while(signals[currentGreen].green>0):
        if not paused:
            updateValues()
            time.sleep(1)
            time_of_day += time_increment
            time_of_day %= 1
            vehicle_density = get_density_from_time(time_of_day)

        elif pause_start_time == 0: # Only record pause start time once
            pause_start_time = time.time()
        time.sleep(0.1)  # Small delay to reduce CPU usage during pause
    currentYellow = 1   # set yellow signal on

    # reset stop coordinates of lanes and vehicles 
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    while(signals[currentGreen].yellow>0):
        if not paused:
            updateValues()
            time.sleep(1)
            time_of_day += time_increment #incrementing the time
            vehicle_density = get_density_from_time(time_of_day) # updating density every second
        elif pause_start_time == 0:
            pause_start_time = time.time()
        time.sleep(0.1)
        
    currentYellow = 0   # set yellow signal off
    queue_length = calculate_queue_length(directionNumbers[nextGreen])
    signals[nextGreen].green = adapt_green_time(queue_length)

    # calculate total green yellow time
    total_green_yellow_time = 0
    for signal in signals:
        total_green_yellow_time += signal.green + signal.yellow

    # calculate flow of current direction
    saturation_flow = (constant_flow * speeds[vehicleTypes[0]]) / average_length_of_vehicle # taking car as reference

    # set the green light time based on density and other constants
    density = density_coefficient[vehicle_density]
    calculated_green =  base_green + k * density * total_green_yellow_time
    signals[currentGreen].green = int(calculated_green)
    
    # reset all signal times of current signal to default/random times
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
       
    currentGreen = nextGreen # set next signal as green signal
    nextGreen = (currentGreen+1)%noOfSignals    # set next green signal
    signal_switching += 1
    signals[nextGreen].red = signals[currentGreen].yellow+signals[currentGreen].green    # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()  

# Update values of the signal timers after every second
def updateValues():
    global car_counts, car_types_log, density_log, density_over_time  
    car_count = 0
    if not paused:  
        car_counts_current_step = {'car': 0, 'bus': 0, 'truck': 0, 'bike': 0}
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 0:
                    signals[i].green -= 1
                else:
                    signals[i].yellow -= 1
            else:
                signals[i].red -= 1

        for direction in vehicles:
            for lane in vehicles[direction]:
                if isinstance(lane, int):
                    for vehicle in vehicles[direction][lane]:
                        car_counts_current_step[vehicle.vehicleClass] += 1 # Correctly increments for each vehicle type


        car_counts.append(car_counts_current_step)  # Append the dictionary of counts for the current step

        for vehicle_type in car_counts_current_step:
            car_types_log[vehicle_type] = car_types_log.get(vehicle_type, 0) + car_counts_current_step[vehicle_type]

        density_log[vehicle_density] = density_log.get(vehicle_density, 0) + 1
        density_over_time.append(density_coefficient[vehicle_density])



def visualize_stats():
    global car_counts, signal_switching, density_log, start_time, time_of_day, car_types_log, density_over_time

    end_time = time_of_day * 24 * 3600
    simulation_time_seconds = end_time - (start_time * 24 * 3600) if start_time is not None else 0

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))  # 2x2 grid of plots
    fig.suptitle(f"Traffic Simulation Statistics for {simulation_time_seconds:.2f} seconds", fontsize=16) # Main Title


    # 1. Car Counts Over Time (Line Plot)
    time_steps = range(len(car_counts))
    total_car_counts = [sum(step_counts.values()) for step_counts in car_counts]
    axes[0, 0].plot(time_steps, total_car_counts, label="Total Car Counts", color="blue")
    axes[0, 0].set_xlabel("Time Step (seconds)")
    axes[0, 0].set_ylabel("Number of Cars")
    axes[0, 0].set_title("Car Counts Over Time")
    axes[0, 0].grid(True)

    # 2. Density Distribution (Bar Plot)
    densities = list(density_log.keys())
    counts = list(density_log.values())
    axes[0, 1].bar(densities, counts, color="green", alpha=0.7)
    axes[0, 1].set_xlabel("Traffic Density Level")
    axes[0, 1].set_ylabel("Number of Time Steps")
    axes[0, 1].set_title("Density Distribution")

    # 3. Density Trends over Time (Line Plot)
    axes[1, 0].plot(range(len(density_over_time)), density_over_time, label="Density Over Time", color="orange")
    axes[1, 0].set_xlabel("Time Step (seconds)")
    axes[1, 0].set_ylabel("Traffic Density (0-1)")
    axes[1, 0].set_title("Density Trends Over Time")
    axes[1, 0].grid(True)

    # 4. Car Type Distribution (Pie Chart)
    car_types = list(car_types_log.keys())
    car_type_counts = list(car_types_log.values())
    axes[1, 1].pie(car_type_counts, labels=car_types, autopct='%1.1f%%', startangle=90, colors=["skyblue", "orange", "green", "red"])
    axes[1, 1].axis('equal')
    axes[1, 1].set_title("Car Type Distribution")

    # Summary Text (Now displayed below the plots)
    summary_text = f"Number of Signal Switches: {signal_switching}\n" \
                   f"Average Cars per Time Step: {sum(total_car_counts) / len(total_car_counts) if total_car_counts else 0:.2f}"

    plt.figtext(0.5, 0.02, summary_text, ha='center', va='center', fontsize=10, wrap=True) # Positioned at bottom
    plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Adjust layout to accommodate the summary text


    plt.show()



# Generating vehicles in the simulation
def generateVehicles():
    global spawn_rate
    while True:
        current_time = time_of_day * 24  
        vehicle_density = get_density_from_time(time_of_day)

        if vehicle_density == "high": # Check density levels, and modify if needed
            spawn_rate = 0.25  # Increased spawn rate during peak hours
        elif vehicle_density == "medium":
            spawn_rate = 0.5 # Medium Spawn rate
        elif vehicle_density == "low":
            spawn_rate = 1  # Normal spawn rate

        if not paused: #Generate vehicle only if not paused
            vehicle_type = random.choice(allowedVehicleTypesList)
            lane_number = random.randint(1,2)
            will_turn = 0
            
            if(lane_number == 1):
                temp = random.randint(0,99)
                if(temp<40):
                    will_turn = 1
            elif(lane_number == 2):
                temp = random.randint(0,99)
                if(temp<40):
                    will_turn = 1
            temp = random.randint(0,99)
            direction_number = 0
            dist = [25,50,75,100]
            if(temp<dist[0]):
                direction_number = 0
            elif(temp<dist[1]):
                direction_number = 1
            elif(temp<dist[2]):
                direction_number = 2
            elif(temp<dist[3]):
                direction_number = 3
            car_types_log[vehicleTypes[vehicle_type]] = car_types_log.get(vehicleTypes[vehicle_type], 0) + 1
            Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
            
        time.sleep(spawn_rate) #Sleep outside the if not paused condition

        


class Main:
    global allowedVehicleTypesList, start_time
    i = 0
    start_time = time.time()
    for vehicleType in allowedVehicleTypes:
        if(allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    
    # visualize_sine_curve(duration=10, time_increment = time_increment, max_density = max_density, shift= shift, frequency = frequency)

    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('E:\\Trafic Signal\\Traffic-Intersection-Simulation-with-Turns-main\\images\\intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('E:\\Trafic Signal\\Traffic-Intersection-Simulation-with-Turns-main\\images\\signals\\red.png')
    yellowSignal = pygame.image.load('E:\\Trafic Signal\\Traffic-Intersection-Simulation-with-Turns-main\\images\\signals\\yellow.png')
    greenSignal = pygame.image.load('E:\\Trafic Signal\\Traffic-Intersection-Simulation-with-Turns-main\\images\\signals\\green.png')
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    start_time = time_of_day # Record the start time

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        pause_start_time = time.time()
                        pygame.display.set_caption("SIMULATION (PAUSED)")
                    else:
                        pause_duration = time.time() - pause_start_time
                        time_of_day += pause_duration / (24 * 3600)
                        pause_start_time = 0
                        pygame.display.set_caption("SIMULATION")
        
        if not paused:
            screen.blit(background,(0,0))   # display background in simulation
            for i in range(noOfSignals):
                if(i==currentGreen): # Only one signal is green or yellow at a time.
                    if(currentYellow==1):
                        signals[i].signalText = signals[i].yellow
                        screen.blit(yellowSignal, signalCoods[i])
                    else:
                        signals[i].signalText = signals[i].green
                        screen.blit(greenSignal, signalCoods[i])
                else: # All other signals are red.
                    if(signals[i].red<=10):
                        signals[i].signalText = signals[i].red
                    else:
                        signals[i].signalText = "---"
                    screen.blit(redSignal, signalCoods[i])

            signalTexts = ["","","",""]

            # display signal timer
            for i in range(0,noOfSignals):  
                signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
                screen.blit(signalTexts[i],signalTimerCoods[i])

            # display the vehicles
            for vehicle in simulation:  
                screen.blit(vehicle.image, [vehicle.x, vehicle.y])
                vehicle.move()
            hours = int(time_of_day * 24)  # Get the hour (0-23)
            minutes = int((time_of_day * 24 * 60) % 60)  # Get the minutes (0-59)
            time_text = font.render(f"Time: {int(time_of_day * 24):02}:{int((time_of_day * 24 * 60) % 60):02}", True, white, black)  # Format time as HH:MM
            # print(time_of_day * 24)
            screen.blit(time_text, (10, 10)) # Display in top-left corner
            if time_of_day * 24 >= 23:  # Check if a full day (24 hours) has passed
                visualize_stats()  # Display statistics after one day
                pygame.quit()  # Close Pygame
                exit()    # Exit the program
        pygame.display.update()


Main()

