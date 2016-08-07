import numpy as np
from constants import *
import mnist_loader
import batcher


def sigmoid(vector):
    """
    Applies sigmoid function element wise
    :param vector: Arbitrary matrix or a vector
    :return: Matrix/Vector of sigmoid activations
    """
    return 1 / (1 + np.exp(-vector))


def softmax(vector):
    """
    Applies softmax function to an arbitrary matrix or vector
    https://en.wikipedia.org/wiki/Softmax_function
    :param vector: Matrix or a vector
    :return: Softmaxed Matrix/vector
    """
    return np.exp(vector) / np.sum(np.exp(vector), axis=1, keepdims=True)


def log_loss(true_output, net_output):
    """
    Calculates logarithmic loss across all output classes.
    Takes the mean loss across all batch elements.
    https://en.wikipedia.org/wiki/Cross_entropy

    :param true_output: Real outputs
    :param net_output: Network outputs
    :return: Batch loss mean
    """
    sum = - np.sum((np.multiply(true_output, np.log(net_output))) / (
        net_output.shape[1]), axis=1)
    return np.mean(sum)


def backprop(y, y_, hidden_output_activations, hidden_weights,
             input_weights, bias_hidden, bias_input, input_x):
    """
    Runs the backpropagation algorithm.
    :param y: True outputs
    :param y_: Network outputs after the softmax transformation
    :param hidden_output_activations: Output of hidden layer after the applied activation
    :param hidden_weights: Weight matrix between the hidden and the output layer
    :param input_weights: Weight matrix between the input and the hidden layer
    :param bias_hidden: Bias Weight matrix between the hidden and the output layer
    :param bias_input: Bias Weight matrix between the input and the hidden layer
    :param input_x: Network input (images)
    :return: Updated weight matrices
    """
    # Derivative with respect to output (cross entropy + softmax)
    # https://math.stackexchange.com/questions/945871/derivative-of-softmax-loss-function#945918
    dLdy_ = (y_ - y) / y.shape[1]

    # Derivative of the error with respect to the hidden layer activations
    dLdhiddenActiv = np.dot(np.transpose(dLdy_), hidden_output_activations)

    delta_h = np.multiply(
        np.multiply(hidden_output_activations, (1 - hidden_output_activations)),
        (np.dot(dLdy_, hidden_weights.T)))

    dLdWinput = np.dot(input_x.T, delta_h)

    # Update weights
    hidden_weights = update_weights(hidden_weights, dLdhiddenActiv.T,
                                    LEARNING_RATE)
    bias_hidden = update_weights(bias_hidden,
                                 np.sum(dLdy_, axis=0, keepdims=True),
                                 LEARNING_RATE)
    input_weights = update_weights(input_weights, dLdWinput, LEARNING_RATE)
    bias_input = update_weights(bias_input,
                                np.sum(delta_h, axis=0, keepdims=True),
                                LEARNING_RATE)

    return hidden_weights, bias_hidden, input_weights, bias_input


def update_weights(weight_matrix, gradient, learning_rate):
    """
    Update weights using Gradient descent algorithm
    :param weight_matrix:
    :param gradient:
    :param learning_rate:
    :return:
    """
    weight_matrix -= learning_rate * gradient
    return weight_matrix


def forward_pass(input, input_hidden_weight, bias_input, hidden_output_weight,
                 bias_hidden):
    """
    Calculates the forward pass of the network
    :param input: Network input (images)
    :param input_hidden_weight: Weight matrix between the input and the hidden layer
    :param bias_input: Bias matrix between the input and the hidden layer
    :param hidden_output_weight: Weight matrix between the hidden and the output layer
    :param bias_hidden: Bias matrix between the hidden and the output layer
    :return: Softmax outputs for the current batch
    """
    hidden_layer = np.dot(input, input_hidden_weight) + bias_input
    hidden_activations = sigmoid(hidden_layer)
    return softmax(np.dot(hidden_activations,
                          hidden_output_weight) + bias_hidden), hidden_activations


def main():
    # Assert constants
    assert BATCH_SIZE % 2 == 0, "Must be devisable by 2"
    assert 0 <= NO_EXAMPLES_TEST <= 10000, "Must be in range [0, 10000]"
    assert 0 <= NO_EXAMPLES_TRAIN <= 60000, "Must be in range [0,60000]"

    # Load training data
    train_data = mnist_loader.load(TRAIN_INPUT, TRAIN_OUTPUT,
                                   NO_EXAMPLES_TRAIN)
    eval_data = mnist_loader.load(EVAL_INPUT, EVAL_OUTPUT,
                                  NO_EXAMPLES_TEST)

    # Create batchers for data batching
    batcher_train = batcher.Batcher(train_data, BATCH_SIZE)
    eval_batcher = batcher.Batcher(eval_data, 1)

    # initialize weights with standard distribution / number of inputs
    # Input -> hidden layer
    input_hidden_weights = np.random.randn(IMAGE_SIZE ** 2,
                                           HIDDEN_LAYER_SIZE) / np.sqrt(
        IMAGE_SIZE ** 2)
    bias_input_hidden = np.random.randn(1, HIDDEN_LAYER_SIZE)

    # Hidden layer -> output layer
    hidden_output_weights = np.random.randn(HIDDEN_LAYER_SIZE,
                                            CLASSES) / np.sqrt(
        HIDDEN_LAYER_SIZE)
    bias_output_hidden = np.random.randn(1, CLASSES)

    # Initialize helper variables
    correct_predictions = 0
    step = 0
    # Start training
    for epoch in range(EPOCHS):
        print("######### Starting epoch: ", epoch, "#########")

        for image, label in batcher_train.next_batch():
            # Reshape inputs so they fit the net architecture
            output_layer, hidden_activations = forward_pass(input=image,
                                                            input_hidden_weight=input_hidden_weights,
                                                            bias_input=bias_input_hidden,
                                                            hidden_output_weight=hidden_output_weights,
                                                            bias_hidden=bias_output_hidden)

            loss = log_loss(true_output=label, net_output=output_layer)

            # Do the backprop
            hidden_output_weights, bias_output_hidden, input_hidden_weights, bias_input_hidden = backprop(
                y=label,
                y_=output_layer,
                hidden_output_activations=hidden_activations,
                hidden_weights=hidden_output_weights,
                input_weights=input_hidden_weights,
                bias_hidden=bias_output_hidden,
                bias_input=bias_input_hidden,
                input_x=image)

            # Measure correct predicitons
            if np.argmax(output_layer) == np.argmax(label):
                correct_predictions += 1

            # Print loss
            if step % 10000 == 0:
                print('Iteration {}: Batch Cross entropy loss: {:.5f}'.format(
                    step,
                    loss))
            # Train set evaluation
            step += BATCH_SIZE

        # Evaluation on the test set
        correct_predictions = 0
        for image_eval, label_eval in eval_batcher.next_batch():
            # Reshape inputs so they fit the net architecture
            output_layer, hidden_activations = forward_pass(input=image_eval,
                                                            input_hidden_weight=input_hidden_weights,
                                                            bias_input=bias_input_hidden,
                                                            hidden_output_weight=hidden_output_weights,
                                                            bias_hidden=bias_output_hidden)
            # Count correct predictions
            if np.argmax(output_layer) == np.argmax(label_eval):
                correct_predictions += 1

        print("\nAccuracy on the test set: {:.3f}".format(
            correct_predictions / NO_EXAMPLES_TEST))


if __name__ == "__main__":
    main()
