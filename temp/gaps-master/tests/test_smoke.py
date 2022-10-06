import cv2 as cv
import numpy as np
import pytest

from gaps_demo import image_helpers
from gaps.genetic_algorithm import GeneticAlgorithm


GENERATIONS = 3
POPULATION = 100
PIECE_SIZE = 128

image = cv.imread("images/baboon.jpg")


@pytest.fixture
def puzzle():
    pieces, rows, columns = image_helpers.flatten_image(image, PIECE_SIZE)
    np.random.shuffle(pieces)
    return image_helpers.assemble_image(pieces, rows, columns)


def test_puzzle_solver(puzzle):
    algorithm = GeneticAlgorithm(puzzle, PIECE_SIZE, POPULATION, GENERATIONS)
    solution = algorithm.start_evolution(verbose=False)

    assert np.array_equal(image, solution.to_image())
