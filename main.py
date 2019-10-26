from tkinter import *
from Vehicle import *
from PVector import *
from PIL import Image, ImageTk
import numpy as np

# Set the characteristics of the world: window dimensions and gravity (indicative value 4:
WIDTH = 1200; HEIGHT = 800; GRAVITY = 0
BUTTERFLIES = 1  # number of butterflies in the world
WASPS = 0  # number of wasps in the world

# flag to note if target exists or not so the butterfly does not seek target
target_exists = False

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
    butterflies = [create_butterfly(canvas, randrange(10,11), randrange(4,5)) for i in range (BUTTERFLIES)]

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

if WASPS > 0:  # only if number of wasps more than 0:
    # create an array of wasps with random characteristics: (list comprehension)
    wasps = [create_wasp(canvas, randrange(5,13), randrange(1,5)) for i in range (WASPS)]

#----------------------------------------------
# define mouse left button press callback inside canvas:
def left_button_press(event):
    target.x = event.x
    target.y = event.y

    global target_exists
    target_exists = True

# bind mouse left button press with callback routine:
canvas.bind('<ButtonPress-1>', left_button_press)

#----------------------------------------------
# define mouse left button release callback inside canvas:
def left_button_release(event):

# when left button released, butterfly stops seeking target:
    global target_exists
    target_exists = False  # flag is down

# bind mouse left button release with callback routine:
canvas.bind('<ButtonRelease-1>', left_button_release)

#------------------------------------------------------------------
# define mouse move callback inside canvas => get the current mouse position:
def mouse_motion(event):
    target.x = event.x
    target.y = event.y

# bind mouse left button press with callback routine:
#canvas.bind('<Motion>', mouse_motion)

#------------------------------------------------------------------
# create gravity callback: using the after method it re-runs inside the mainloop
def apply_gravity(gravity):
    #butterfly.apply_force(gravity)  # apply gravity force to the vehicle
    #wasp.apply_force(gravity)
    canvas.after(10, apply_gravity, gravity)  # re-runs the method after 10 msec

#------------------------------------------------------------------
# create desired velocity callback also using the after method: it re-runs the seek method every frame.
# Here we define the desired location (by passing target as parameter) for the vehicles specified inside the method.
def apply_desired(target):
    global target_exists  # declare the flag as global variable

    if target_exists == True:
        for i in range(BUTTERFLIES):
            butterflies[i].seek(target)

    for i in range(BUTTERFLIES):
        if WASPS > 0:
            butterflies[i].avoid_wasp(wasps[0])

    # calculate the distance between the wasp and all butterflies:
    if WASPS > 0:
        distance = []
        for i in range(BUTTERFLIES):
            dist = wasps[0].position.distance(butterflies[i].position)
            distance.append(dist)

        # find the nearest butterfly:
        #a = np.array(distance)
        #idx = np.argmin(a)
        wasps[0].seek(butterflies[randrange(0,BUTTERFLIES)].position)

    canvas.after(10, apply_desired, target)  # re-runs the method after 10 msec
#------------------------------------------------------------------

# apply the forces:
apply_gravity(gravity)  # pass the gravity vector as argument
apply_desired(target)  # pass target as argument

# main event loop of tkinter:
top_window.mainloop()