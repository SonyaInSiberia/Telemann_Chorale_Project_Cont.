import music21
import math
from realization import *
import random


def promising(realization: Realization, minCost: float) -> bool:
    """
    Checks whether current solution could lead to a minimal-cost solution.

    Args:
        realization (Realization): partial or complete realization of inner voice notes in a phrase
    
    Returns: 
        bool: whether current solution could lead to a minimal-cost solution

    """
    # if realization.getCost() <= minCost:
    #     return True
    # return False
    return True


def solution(realization: Realization) -> bool:
    """
    Checks whether the input is a complete solution, i.e. realizes the whole phrase.

    Args:
        realization (Realization): partial or complete realization of inner voice notes in a phrase
    
    Returns: 
        bool: whether the input is a complete solution, i.e. realizes the whole phrase

    """
    # return random.randint(0, 1)
    # return len(realization.progression.chordIterable()[-1].pitches) == 4
    return True
    pass


def checkNode(realization: Realization, minCost: float) -> Progression:
    """
    Returns cost of lowest-cost solution. (TODO: should we be returning the realization itself?)

    Args:
        realization (Realization): partial or complete realization of inner voice notes in a phrase
        minCost (float): lowest cost seen so far
    
    Returns: 
        float: cost of lowest-cost solution

    """
    # TODO: is this the right spot for this?
    # realization.updateCost()
    best_Progression = None
    if promising(realization, minCost):
        if solution(realization):
            best_Progression = realization.progression
        else:
            for child in realization.getChildren():
                checkNode(child, minCost)
    return best_Progression


def stuff():
    # TODO: move stuff below elsewhere?
    # parse chorale #6 into a stream data structure: https://web.mit.edu/music21/doc/usersGuide/usersGuide_04_stream1.html#usersguide-04-stream1
    chorale = converter.parse('chorale_006.musicxml').flatten()

    # print out note name, its numerical representation (midi), its relative position in the song, and if it contains an fermata
    for n in chorale.getElementsByClass(note.Note):
        print(n.pitch, n.pitch.midi, n.offset, n.expressions)

    # change every pitch to F4
    for i in range(len(chorale)):
        chorale[i].pitch = pitch.Pitch('F4')

    # Print again
    for n in chorale.getElementsByClass(note.Note):
        print(n.pitch, n.pitch.midi, n.offset, n.expressions)


def main():
    # TODO: INITIAL cost that compares less than infinity
    # initial = Realization(music21.stream.Stream(), 1000000000)
    initial = Realization(Progression("Chorale_006_Separate_Parts.musicxml", chordify=True), 0, 0)
    result = checkNode(initial, math.inf)

    # TODO
    print(result)
    result.progression.show()


if __name__ == "__main__":
    main()
