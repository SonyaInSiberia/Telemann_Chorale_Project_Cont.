from music21 import note, pitch, stream, converter, chord, interval
from music21.figuredBass import notation
import json
from progression import *


class Realization(object):
    """
    Incomplete or complete realization of inner voice notes in a phrase
    """

    def __init__(self, progression: Progression, cost: float, currBeat: int):
        """Construct a Realization object.

        Args:
            progression (Progression): chord progression, including representations as an iterable of chords and as four parts
            cost (float): cumulative cost of this realization
            currBeat (int): number of chordal beats whose inner voices have been filled
        
        """
        self.progression = progression # TODO: do we actually need to store this as a member?
        # TODO: get first phrase (first portion from start until fermatta"
        
        self.cost = cost
        self.currBeat = currBeat # how many beats have inner voices filled in

        self.chords = self.progression.chordIterable()
        # TODO: debug
        for c in self.chords:
            print(c)

        self.figuredBass = self.progression.figureIter
        print(self.figuredBass)

    def _updateCost(self):
        """
        Updates lower bound on the cost of this inner voice realization (infinity if hard constraint is violated).

        # TODO: call in getChildren()
        
        """
        with open('costs.json') as jsonFile:
            data = json.load(jsonFile)
            if self.hasParallelFifths():
                self.cost += data["parallel fifth"]
            if hasDoubledDissonance(self.chords[self.currBeat - 1]):
                self.cost += data["doubled dissonance"]
            if not isMinimallyComplete(self.chords[self.currBeat - 1], False): #TODO: how to tell if a chord is supposed to be a 7th?
                self.cost += data["not minimally complete"]
            if not isKeyboardStyle(self.chords[self.currBeat - 1]):
                self.cost += data["not keyboard style"]

    def getCost(self) -> float:
        """
        Get lower bound on the cost associated with this realization.

        Returns:
            float: lower bound on the cost associated with this realization

        """
        return self.cost

    def getChildren(self) -> list:
        """
        Get list of realizations adjacent to this one, i.e. that realize the next chord.

        Returns: 
            list[Realization]: list of realizations adjacent to this one, i.e. that realize the next chord

        """
        children = []
        cost = 0  # TODO: figure out a way to find cost
        bass = self.progression.chordIterable()[self.currBeat].pitches[0]
        soprano = self.progression.chordIterable()[self.currBeat].pitches[-1]
        possible_chords = self._chordGenerator(bass, soprano,
                                               self.figuredBass[self.currBeat])  # all possible chords
        for c in possible_chords.getElementsByClass(chord.Chord):
            c = c.sortAscending()
            new_progression = copy.deepcopy(self.progression)  # its copying the internal progression instance
            # TODO: figure out a way to copy every instances in the object
            new_progression.chordIterable()[self.currBeat].pitches = c.pitches  # change the pitches of the chord in
            # new_progression
            children.append(Realization(new_progression, cost, self.currBeat+1))  # add the new proression to children[]
        # figure out where we are inserting next note
        # enumerate  next possible voices based on fig bass (call carson's code here)

        # for each note,
        #       insertNote
        #       call updateCost to get cost arg
        #       make copy of self and append to children
        return children

    def hasParallelFifths(self) -> bool:
        # TODO: index the last two chords in the stream
        """
        if there's a perfect fifth in the first chord
            see whether those voices also constitute a fifth in the second chord
        """
        return False

    def _insertNote(self, note: int, location) -> None:
        """
        Inserts a new note (used in getChildren)
        """
        curr_chord = self.chords[self.curr_beat]
        for interval in self._getIntervals(self.figuredBass[self.curr_beat]):
            pass
            # TODO: implement
            # 1 add note to approrpiate place in parts (self.soprano, etc.)
            # 2 add note to appriopriate place in self.chords
            # make sure edited chord is sortAscending()ed

    def _stackInterval(self, interval, chord, bass, soprano):
        """
        chord generator helper function, modifies the chord object by filling in the gap between the bass and soprano with all instances of a pitch class
        interval: a number representing the interval between the bass note and the note we are appending
        chord: a list of note objects modifying and returning by adding one additional note to it
        bass: a Note object
        soprano: a Note object
        """
        print(bass, soprano)
        temp_midi_pitch = bass.midi + interval
        while temp_midi_pitch < soprano.midi:
            chord.append(note.Note(temp_midi_pitch))
            temp_midi_pitch += 12

    def _getIntervals(self, figured_bass):
        """
        return a list of intervals based on key signature, bass, soprano and figured
            bass(it has to align with modulation of 12) the list contains only integers.
        figured_bass: a list of strings indicating figured bass, need function for it
        """
        intervals = []
        for int in figured_bass:
            chrom_itv = interval.ChromaticInterval(int)
            intervals.append(chrom_itv.mod12)
            intervals.append(12)
        return intervals

    def _chordGenerator(self, bass, soprano, figured_bass=(3, 7)):
        """
        return a Stream Object with all of the possible enumerations of chords
        bass: a Note Object representing the bass note of the chord
        soprano: a Note Object representing the soprano note of the chord
        figured_bass: a tuple with integers that indicates figured bass in semitones above the bass
        """
        ret = stream.Stream()
        intervals = self._getIntervals(figured_bass)
        # TODO: have intervals be read based on the figured bass and the key
        temp_chord = []
        for interval in intervals:
            self._stackInterval(interval, temp_chord, bass, soprano)
        for i in range(len(temp_chord)):
            for j in range(i + 1, len(temp_chord)):
                chord_to_add = chord.Chord([bass, temp_chord[i], temp_chord[j], soprano])
                ret.append(chord_to_add)
        return ret

        # make big fat chord
        # extrapolate all of the inner voices and append to new smaller chords
        # return the list of smaller chords



def hasDoubledDissonance(chord: chord.Chord) -> bool:
    """
    Returns true if the chord contains a doubled dissonance
    """
    return any([chord.hasRepeatedChordStep(step) for step in [2, 4, 7]])


def isMinimallyComplete(chord: chord.Chord, isSeventh: bool) -> bool:
    """
    Returns true if the root, third, and seventh (if indicated) are present
    """
    if isSeventh:
        return chord.root() != None and chord.third != None and chord.seventh != None
    return chord.root() != None and chord.third != None


def isKeyboardStyle(chord: chord.Chord) -> bool:
    """
    Returns true if the soprano is no more than an octave above the tenor
    TODO: Requires 4 notes sorted?
    """
    sortedChord = chord.sortAscending()  # todo: sort in place or require beforehand?
    tenor = sortedChord.pitches[1]
    soprano = sortedChord.pitches[3]
    return interval.Interval(tenor, soprano).semitones <= 12
