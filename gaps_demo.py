#!/usr/bin/env python

"""Solves given jigsaw puzzle

This module loads puzzle and initializes genetic algorithm with given number of
generations and population. At the end, solution image is displayed.

"""
from __future__ import print_function

import argparse
from time import time

import matplotlib.pyplot as plt
import cv2 as cv

from gaps.genetic_algorithm import GeneticAlgorithm
from gaps.size_detector import SizeDetector
from gaps.plot import Plot

GENERATIONS = 20
POPULATION = 200


def show_image(img, title):
    if not args.verbose:
        Plot(img, title)
    plt.show()


def parse_arguments():
    """Parses input arguments required to solve puzzle"""
    parser = argparse.ArgumentParser(
        description="A Genetic based solver for jigsaw puzzles"
    )
    parser.add_argument("--image", type=str, default="out.jpg", help="Input image.")
    parser.add_argument(
        "--generations", type=int, default=GENERATIONS, help="Num of generations."
    )
    parser.add_argument(
        "--population", type=int, default=POPULATION, help="Size of population."
    )
    parser.add_argument("--size", type=int, help="Single piece size in pixels.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show best individual after each generation.",
    )
    parser.add_argument(
        "--save", action="store_true", help="Save puzzle result as image."
    )
    return parser.parse_args()

def main(path):
    args = parse_arguments()
    image = cv.imread(path)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    size = image.shape
    w = size[1] #宽度
    h = size[0] #高度
    piece_size = int(w/4)
    # Let the games begin! And may the odds be in your favor!
    start = time()
    algorithm = GeneticAlgorithm(image, piece_size, args.population, args.generations)
    solution = algorithm.start_evolution(args.verbose)
    end = time()
    res = solution._piece_mapping
    judge = [i for i in range(8)]
    for key in res.keys():
        if res[key]==key:  #int 型
            judge.remove(key)
    if len(judge)==2:
        return judge
    else:
        print("NOT MATCH!")
        return []
        

if __name__ == "__main__":
    main(r"C:\Users\Administrator\Desktop\gaps-master\bin\target_2.jpg")
    exit(0)
    args = parse_arguments()

    # image = cv.imread(args.image)
    image = cv.imread(r"C:\Users\Administrator\Desktop\gaps-master\bin\target_1.jpg")
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    if args.size is not None:
        piece_size = args.size
    else:
        detector = SizeDetector(image)
        # piece_size = detector.detect_piece_size()
        piece_size = 80

    print("\n=== Population:  {}".format(args.population))
    print("=== Generations: {}".format(args.generations))
    print("=== Piece size:  {} px".format(piece_size))

    # Let the games begin! And may the odds be in your favor!
    start = time()
    algorithm = GeneticAlgorithm(image, piece_size, args.population, args.generations)
    solution = algorithm.start_evolution(args.verbose)
    end = time()

    print("\n=== Done in {0:.3f} s".format(end - start))

    solution_image = solution.to_image()
    solution_image_name = args.image.split(".")[0] + "_solution.jpg"

    if args.save:
        cv.imwrite(solution_image_name, solution_image)
        print("=== Result saved as '{}'".format(solution_image_name))

    print("=== Close figure to exit")
    print(f"==={solution._piece_mapping}")
    show_image(solution_image, "Solution")
