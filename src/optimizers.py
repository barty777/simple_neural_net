import numpy as np


class Optimizer:
    def update_weights(self, weight_matrix, gradient):
        raise NotImplementedError


class GradientDescent(Optimizer):
    def __init__(self, learning_rate=0.001):
        self.learning_rate = learning_rate

    def update_weights(self, weight_matrix, gradient):
        weight_matrix -= self.learning_rate * gradient
        return weight_matrix


class RMSProp(Optimizer):
    def __init__(self, gamma=0.9, alpha=0.001, eps=0.00000001):
        self.r = 0
        self.gamma = gamma
        self.velocity = 0
        self.alpha = alpha
        self.eps = eps

    def update_weights(self, weight_matrix, gradient):
        self.r = self.gamma * np.square(gradient) + (1 - self.gamma) * self.r
        self.velocity = np.multiply((self.alpha / (np.sqrt(self.r) + self.eps)),
                                    gradient)
        weight_matrix -= self.velocity

        return weight_matrix
