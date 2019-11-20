from tkinter import *
from Vehicle import *
from PVector import *
from PIL import Image, ImageTk
import numpy as np
import math
import perceptron

# Set the characteristics of the world: window dimensions and gravity (indicative value 4:
WIDTH = 1200; HEIGHT = 800; GRAVITY = 0
BUTTERFLIES = 10  # number of butterflies in the world
WASPS = 0  # number of wasps in the world

# flag to note if target exists or not so the butterfly does not seek target
target_exists = False

# flag to signify aggression from the mouse
aggression = False

TIME_INTERVAL = 100  # duration in ms of the dataframe to collect mouse speed and button hit numbers
x = 0 # temporary storage of mouse pointers to be used in calculating mouse speed
y = 0

#speed_list = []  # list of mouse speed records during the 50 ms frame
displacement_list = []
number_key_pressed = 0  # counter for number of any key clicks
data_slice = []  # list of tuples of data points - one for every data interval
data_frame = np.zeros([int(1000/TIME_INTERVAL), 2])  # rows x columns, rows represent time

#----------------------------------------------
# Create the main world window. Inputs: width, height and gravity. Outputs: top window, canvas and gravity vector
def create_world(title, width, height, gravity):

    # create the main window using Tk:
    top_window = Tk()
    top_window.title(title)
    top_window.resizable(False, False)  # turn off resizing of the top window

    # create canvas to draw inside with the dimensions defined above:
    canvas = Canvas(top_window, width=width, height=height, bg="white")
    # packs the elements in the window:
    canvas.pack()

    # create gravity vector:
    gravity = PVector(0, gravity)

    # return both the top window and the canvas:
    return top_window, canvas, gravity
#----------------------------------------------

# create the main window:
top_window, canvas, gravity = create_world("New World", WIDTH, HEIGHT, GRAVITY)

# initialize target in the middle of the window (this is a global variable)
target = PVector(WIDTH/2, HEIGHT/2)

# initialize steering force:
steer = PVector(WIDTH/2, HEIGHT/2)  # initialize steering vector

#----------------------------------------------
# create the butterflies:
def create_butterfly(canvas, speed, mass):
    # open butterfly png file, resize it and import it to tkinter:
    image = Image.open('/Users/konstantinosdimou/PycharmProjects/Vehicles/butterfly.png')
    im = image.resize((50, 50))
    img_butterfly = ImageTk.PhotoImage(im)
    # create a butterfly and draw it:
    butterfly = Vehicle(canvas, WIDTH, HEIGHT, speed, mass, img_butterfly)
    butterfly.draw()
    return butterfly

if BUTTERFLIES > 0:
    # create an array of butterflies with random characteristics: (list comprehension)
    butterflies = [create_butterfly(canvas, randrange(4, 10), randrange(4,7)) for i in range (BUTTERFLIES)]

#----------------------------------------------
# create the wasps:
def create_wasp(canvas, speed, mass):
    # open wasp png file, resize it and import it to tkinter:
    image = Image.open('/Users/konstantinosdimou/PycharmProjects/Vehicles/wasp.png')
    im2 = image.resize((50, 50))
    img_wasp = ImageTk.PhotoImage(im2)
    wasp = Vehicle(canvas, WIDTH, HEIGHT, speed, mass, img_wasp)  # max speed 10, mass 4
    wasp.draw()
    return wasp

# create an array of wasps with random characteristics: (list comprehension)
wasps = [create_wasp(canvas, randrange(6,12), randrange(4,7)) for i in range (WASPS)]

#----------------------------------------------
# define left mouse button press callback inside canvas:
def left_button_press(event):
    target.x = event.x
    target.y = event.y

    global target_exists
    target_exists = True

# bind mouse left button press with callback routine:
canvas.bind('<ButtonPress-1>', left_button_press)

#----------------------------------------------
# define right mouse button press callback inside canvas:
def right_button_press(event):
    global aggression
    aggression = False

# bind right mouse button press with callback routine:
canvas.bind('<ButtonPress-2>', right_button_press)

#----------------------------------------------
# define any key press callback inside canvas:
def any_key_press(event):
    global number_key_pressed
    number_key_pressed += 1

# bind any key press with callback routine:
top_window.bind('<Key>', any_key_press)  # bound to top_window because canvas does not get focus immediately

#----------------------------------------------
# define left mouse button release callback inside canvas:
def left_button_release(event):
    # when left button released, butterfly stops seeking target:
    global target_exists
    target_exists = False  # flag is down

# bind mouse left button release with callback routine:
canvas.bind('<ButtonRelease-1>', left_button_release)

#------------------------------------------------------------------
# define mouse move callback inside canvas => get the current mouse position:
def mouse_motion(event):
    # calculate mouse speed:
    global x, y

    dx = event.x - x
    dy = event.y - y

    dist = math.sqrt(dx ** 2 + dy ** 2) # displacement for every mouse move event
    #speed = dist / (TIME_INTERVAL/1000)  # current speed for every mouse move event - may be used later
    #speed_list.append(speed)
    displacement_list.append(dist)  # for every mouse move event, data is entered in the displacement list

    x = event.x
    y = event.y

# bind mouse left button press with callback routine:
canvas.bind('<Motion>', mouse_motion)

#------------------------------------------------------------------
# create gravity callback: using the after method it re-runs inside the mainloop
def apply_gravity(gravity):
    #wasps[0].apply_force(gravity)
    canvas.after(10, apply_gravity, gravity)  # re-runs the method after 10 msec

#------------------------------------------------------------------
# create desired velocity callback also using the after method: it re-runs the seek method every frame.
# Here we define all the desires (by passing target as parameter) for the vehicles specified inside the method.
def apply_desired(target):
    global target_exists  # declare the flag as global variable
    mouse = PVector(x, y)  # get current mouse pointer

    # start creating behaviour for the list of butterflies (I need to create a state machine here):
    for butterfly in butterflies:
        # each butterfly starts wandering around:
        butterfly.wandering(randrange(50, 150), randrange(150, 250))
        if aggression == True:  # if aggression detected, avoid mouse
            butterfly.avoid_point(mouse, 200)

        # each butterfly will seek the mouse when button pressed (food):
        if target_exists:
            butterfly.seek(target)

        # each butterfly will detect any other butterfly close and avoid falling on it:
        butterfly.separate(butterflies)

        # each butterfly avoids the wasp if there's one closer than 200 pixels:
        if len(wasps) > 0:
            butterfly.avoid_point(wasps[0].position, 200)

            # when butterfly is near, wasp kills her and it disappears:
            if wasps[0].position.distance(butterfly.position) < 20:
                butterfly.canvas.delete(butterfly.id)
                butterflies.pop(butterflies.index(butterfly))

    if len(wasps) > 0:  # if at least one wasp existing:
        # wasp starts wandering also:
        wasps[0].wandering(100, 200)
        wasps[0].chase_butterflies(butterflies)

    canvas.after(10, apply_desired, target)  # re-runs the method after 10 msec

#------------------------------------------------------------------
# apply the forces:
#apply_gravity(gravity)  # pass the gravity vector as argument
apply_desired(target)  # pass target as argument

#------------------------------------------------------------------
# collects one data point at specific time periods and adds in a data frame
def get_data_frame():
    global number_key_pressed
    global data_frame
    global aggression

    if len(displacement_list) > 0:
        displacement_list.pop(0)  # discard the first entry: initial event.x,y are possibly large and previous are zero

    total_displacement = sum(displacement_list)  # the total displacement within the time interval is calculated
    average_speed = int(total_displacement/(TIME_INTERVAL/1000)) # average speed is total displacement / time interval
    displacement_list.clear()

    # push every sample in the data slice list
    data_slice.append([average_speed, number_key_pressed])
    # when 20 samples are pushed, copy to the data frame
    if len(data_slice) == int(1000/TIME_INTERVAL):
        data_frame = np.array(data_slice)
        data_slice.clear()  # reset the data slice to be reused
    # reset counter:
    number_key_pressed = 0

    # now send data frame to mouse_attack method to each butterfly:
    for butterfly in butterflies:
        if butterfly.mouse_attack(data_frame) == True:  # if aggression detected raise the flag:
            aggression = True

    canvas.after(TIME_INTERVAL, get_data_frame)

get_data_frame()

# main event loop of tkinter:
top_window.mainloop()