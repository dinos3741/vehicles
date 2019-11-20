#definition of perceptron class
import random
SIZE = 2000  # training model size

# this is a neuron with an array of inputs and one output. The input array can be one or two dimensional and can
# represent pixels of a hand written number for example
class Perceptron:
    weights = []  # weights is global to class
    def __init__(self, nr_inputs, learning_rate):
        self.nr_inputs = nr_inputs
        self.learning_rate = learning_rate
        # initialize weights:
        for i in range(nr_inputs):
            self.weights.append(random.randrange(-1, 1))

    def activate(self, sum):
        if sum > 0:
            return 1
        else:
            return 0

    # inputs is a list
    def feed_forward(self, inputs):
        sum = 0
        for i in range(len(inputs)):
            sum += inputs[i] * self.weights[i]
        return self.activate(sum)

# back-propagation to readjust weights:
    def train(self, inputs, desired):
        # compute the estimated output
        guess = self.feed_forward(inputs)
        # compute the error as difference between answer and guess
        error = desired - guess
        # adjust the weights based on the error and learning rate:
        for i in range(len(inputs)):
            self.weights[i] += self.learning_rate * error * inputs[i]

# line equation to classify points
#def f(x):
#    return 2*x-3

# create the training set of size SIZE as a two dimensional list:
#training_set = []  # list of points
#for i in range(SIZE):  # create random training points
#    point = []  # list of inputs
#    x = random.randint(0, SIZE)
#    point.append(x)
#    y = random.randint(0, SIZE)
#    point.append(y)
#    point.append(1)
#    if y < f(x):
#        answer = -1
#    else:
#        answer = 1
#    point.append(answer)
#    training_set.append(point)

#training_set = [[0,1,1,0], [1,1,1,1], [1,0,1,0], [0,0,1,0]]  # AND gate

# initialise neuron with three inputs (two and the bias):
ptron = Perceptron(3, 0.01)

# train the preceptron with the dataset:
#for i in range(SIZE):
    #ptron.train([training_set[i][0], training_set[i][1]], training_set[i][3])

# a AND gate has two inputs and one output, and all the combinations are 4, so the input length is 4
inputs = [[0,1], [1,1], [1,0], [0,0]]
answer = [0, 1, 0, 1]

# create the input with bias adding 1 as 3rd element:
for i in range(len(inputs)):
    inputs[i].append(1)

for j in range(2000):  # train 2000 times to adjust the weights
    for i in range(len(inputs)):
        ptron.train(inputs[i], answer[i])

print(ptron.feed_forward([0,1,1]))  # an XOR gate cannot be predicted because of non-linearity
