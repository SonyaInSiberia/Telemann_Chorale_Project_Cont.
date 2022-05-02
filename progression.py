from music21 import note, pitch, stream, converter, harmony, noteworthy, clef, duration, meter, key, interval, scale, expressions, tie
from music21.figuredBass import *
import copy
from bs4 import BeautifulSoup
from bs4.element import Tag
from itertools import islice
import collections
from birdseye import eye
class Progression:
    
    def __init__(self, progressionFile, chordify=False):
        """requires a .musicxml file containing only bass & soprano parts;
       returns a progression stream containing inserted alto and tenor voices,
       with time/key info intialized via context from the rest of the progression.
       If chordify=True is passed in, the returned progression will be an iterable of
       chords (otherwise, it will just be the 4 distinct parts)

       Some display-related functions currently assume that functions which edit the chordified chorale also edit the corresponding
       part objects (self.soprano, self.alto, self.tenor. self.bass), even if this happens after a solution is determined. 
       """
        self.progression = converter.parse(progressionFile)

        #labeling individual parts:
        self.soprano = self.progression.parts[0] 
        self.bass = self.progression.parts[1]

        self.fermataIndices = self.findFermatas()  #quick solution for segmenting phrases 

        #insert the inner voices
        self.alto = Progression.createPartFromTemplate(self.soprano, 'Alto') #fills with rests
        #tenor = createPartFromTemplate(bass, 'Tenor', 'G3') #fills with G3 (just because)
        self.tenor = Progression.createPartFromTemplate(self.bass, 'Tenor')

        self.progression.remove(self.bass)
        self.progression.append(self.alto)
        self.progression.append(self.tenor)
        self.progression.append(self.bass)

        #now soprano is progression.parts[0]; bass is progression.parts(3)
        self.initializeInnerVoices()

        self.progressionFourParts = self.progression

        self.isChordified = chordify
        if chordify:
            self.progression = self.progression.chordify()
        
        self.figureIter = self.parseFigures(progressionFile)


    # def __getattr__(self, attr):
    #     return getattr(self.progression, attr)

    def __iter__(self):
        return iter(self.progression)

    #TODO: proxy in other dunders as necessary: 
    # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
    #https://github.com/cuthbertLab/music21/blob/master/music21/stream/base.py

    def showFourParts(self):
        self.progressionFourParts.show()
    
    def showTwoParts(self):
        combinedStaves = self.progressionFourParts.partsToVoices(voiceAllocation=2)
        combinedStaves.parts[1].insert(0, clef.BassClef())
        combinedStaves.show()

    def initializeInnerVoices(self):
        """requires a progression with inner voices inserted; 
        adds visual time/key signatures to that progression 
        (only adds in the initial time/key for now)
        """
        soprano = self.progression.parts[0] 
        alto = self.progression.parts[1]
        tenor = self.progression.parts[2]
        bass = self.progression.parts[3]

        tenor.insert(0, clef.BassClef()) #0 is the duration offset

        ts = copy.deepcopy(self.progression[meter.TimeSignature].first())
        print(self.progression[meter.TimeSignature].first())
        ks = copy.deepcopy(self.progression[key.KeySignature].first())

        for part in self.progression.parts:
            part.measure(1).insert(0, ts)
            part.measure(1).insert(0, ks)

    @staticmethod
    def createPartFromTemplate(templatePart, partName, fillWithNote='|'):
      """
      quick way to currently initialize a new part as a deep copy of templatePart, 
      then modify relevant member variables and fill said new part
      with whole rests. templatePart should have a structure analogous to 
      that produced by converter.parse(<one_of_our_progressions>.musicxml) and accessed
      via one_of_our_progressions.parts[i], where i is the parts staff number (0-indexed)
      TODO: read in and display figured bass
      """

      part = copy.deepcopy(templatePart) #a bit janky, but safest way for now to keep the parts' structures' uniform
      for i in range(len(templatePart.getElementsByClass(stream.Measure))):
        part.getElementsByClass(stream.Measure)[i].clear() #get read of each measures' contents but NOT the measure itself
        if(fillWithNote == '|'):
          part.measure(i + 1).repeatAppend(note.Rest(type='whole'), 1) #part.measure() is 1-indexed
        else:
          part.measure(i + 1).repeatAppend(note.Note(fillWithNote, type='whole'), 1)
      part.partName = partName
      part.id = partName
      part.partAbbreviation = partName[0] + '.'

      return part

    def chordIterable(self):
        """given (requires) self to be a chordified progression (see createProgression),
           returns an chord iterable, e.g., 

           for chord in <myProgression>.chordIterable():
               #do stuff
        
           if self is not chordified, just prints a short warning for now
        """
        if not self.isChordified:
            print("warning: progression is not chordified! (using chordified copy)")
        return self.progression.recurse().getElementsByClass('Chord')

    def findFermatas(self):
        """iterates over the bass part and grabs the locations of all the fermatas. 
        Returns a list of indices into self.chordIterable() where fermatas occur,
        inclusive (e.g., if output[1] == 16, then self.chordIterable[16] contains a fermata"""
        output = []
        for i, n in enumerate(self.bass.flatten().getElementsByClass(note.Note)):
            if n.expressions:
                for exp in n.expressions:
                    if isinstance(exp, expressions.Fermata):
                        output.append(i)
        return output



    @staticmethod
    def standardizeFigure(figure):
        """fills in the redundant blanks left by fb notation. for example, give (6) returns (3, 6)
        not really accounting for 7th chords yet, except perhaps incidentally
        (incomplete)"""

        hasAccidental = False

        if(figure[0] == '6' and len(figure) == 1):
            figure.insert(0, 3)
            figure = [6 if x=='6' else x for x in figure]

        figure = checkSevenths(figure)

        if "sharp" in figure or "backslash" in figure: #then adjust the third
            figure = ['#' if x=="sharp" or x=="backslash" else x for x in figure] #backslash suffix is same as raising third
            hasAccidental = True

        if("flat") in figure:
            figure = ['b' if x=="flat" else x for x in figure] 
            hasAccidental = True
        
        if("natural") in figure:
            figure = ['n' if x=="natural" else x for x in figure] 
            hasAccidental = True

        if not hasAccidental:
            return tuple(map(int, figure))

        elif len(figure) > 1: #implying figure is a heterogenous combination of interval numbers & accidentals
            figure = [int(x) if x.isdigit() else x for x in figure]
            return figure

        else:
            figure.append(5)
            return tuple(figure) #case where just one accidental is given for now (so add in the fifth)

    def str2tuple(self, s: str):
        result = []
        it = iter(s)
        for i, ch in enumerate(it):
            if ch == 's':
                result.append(s[i:i+6])
                i += 6
                consume(it, 6) #skip ahead in the iteration
            elif ch == 'b':
                result.append(s[i:i+10])
                i += 10
                consume(it, 10)
            elif ch == 'n':
                result.append(s[i:i+7])
                i += 7 
                consume(it, 7)
            elif ch == 'f':
                result.append(s[i:i+4])
                i += 4
                consume(it, 4)
            elif ch.isdigit():
                result.append(ch)
        result = self.standardizeFigure(result)
        return tuple(result)

    @eye
    def getFigures(self, file):
        """parses musicxml for figures and stores them as tuples in a list coindexed with the chord iterable"""
        with open(file) as fp:
            soup = BeautifulSoup(fp, 'lxml')

            bass = soup.find('part', id='P2') #P2 is bass

            result = []
            nextFig = ""

            #print(len(self.chordIterable()))
            
            for measure in bass.children:
                if isinstance(measure, Tag):
                    for item in measure.contents:

                        if item.name == 'figured-bass':

                            nextFig += (item.get_text().strip()) #handle figured-bass, prefix, postfix, suffix cases
                        elif item.name == 'note':
                            if(nextFig):
                                result.append(self.str2tuple(nextFig))
                            else: #append 3 5 as long as 'note' isn't actually a rest (if no rests in piece could just be results.append(3, 5))
                                append = True
                                for i in item.contents:
                                    if i.name == 'rest':
                                        append = False 
                                if append:
                                    result.append((3, 5))
                            nextFig = ""

            return result

    def correctTransposedKeyAwareOffset(self, pitch, key): #if the bass note has an accidental transposePitchKeyAware will be off by one; this should fix that
        #match-case sadly too new to risk using
        if not pitch.accidental or pitch.accidental.alter == 0.0: #(natural) — note that a pitch with no accidental does not have alter==0, but alter is None
            if key.sharps > 0: #then we compensate in the same way we did for flat
                return 1
            elif key.sharps < 0: #then we compensate in the same way we did for sharp
                return -1 
        elif pitch.accidental.alter == 1.0: #(sharp)   #then key-aware transposition will 'correct' down a semitone and we must compensate
            return -1 
        elif pitch.accidental.alter == -1.0: #(flat)
            return 1

        return 0 

    def parseFigures(self, file):
        untranslatedFigs = self.getFigures(file)
        self.writeVisualFigures(untranslatedFigs)
        translatedFigs = []
        #get the key (TODO: ACCOUNT FOR MID-CHORALE KEY SIGNATURE CHANGES)
        keyInference = self.progression.analyze('key')
        k = keyInference
        print("Figure parsing inferring key: ", k)
        nextInterpretation = 0
        while k.sharps != self.progression[key.KeySignature].first().sharps:
                #i.e., k assumed the wrong key
                print("Figured bass parser inferred an incorrect keysig. Trying again.")
                k = keyInference[nextInterpretation+1] #try the next most probable key
                nextInterpretation += 1
        
        for i, n in enumerate(self.bass.flatten().getElementsByClass(note.Note)):
            #i is an index into figured bass list, n is a note object
            figure = untranslatedFigs[i]
            intervals = []
            p = pitch.Pitch(n.nameWithOctave) #turns note object into pitch object so we can use pitch-specific functions

            for num in figure:
                if not isAccidental(num):
                    int = interval.GenericInterval(num) #e.g., just a '6th' in a vacuum
                    upperNote = int.transposePitchKeyAware(p, k, inPlace=False) #create phantom note a <num> above the bass
                    chromaticInt = interval.notesToChromatic(n, upperNote)
                    
                    if(k.accidentalByStep(p.step) != p.accidental): #i.e., if p has an accidental not already assigned by the key sig
                        chromaticInt.semitones += self.correctTransposedKeyAwareOffset(p, k) #if the bass note has an accidental transposePitchKeyAware will be off by one; this should fix that

                    intervals.append(chromaticInt.semitones)
                    
                else: #have to do some different stuff when dealing with accidental
                    int = interval.GenericInterval(3) #gonna be a 3rd no matter what
                    upperNote = int.transposePitchKeyAware(p, k, inPlace=False) #create phantom note a <num> above the bass
                    chromaticInt = interval.notesToChromatic(n, upperNote)
                    #match-case
                    if(num == '#'):
                        chromaticInt.semitones += 1
                    elif(num == 'b'):
                        chromaticInt.semitones -= 1
                    elif(num == 'n'):
                        #e.g., if key sig has sharps, we want natural to flatten the default chr. interval by a semitone
                        #note that we dealt with the opposite case above with correctTransposedKeyAwareOffset, hence the -=
                        chromaticInt.semitones -= self.correctTransposedKeyAwareOffset(p, k) 
                    else:
                        print("parseFigures(): bad accidental given")
                    intervals.append(chromaticInt.semitones)
                    


            translatedFigs.append(tuple(intervals))
 
        self.checkOneToManyOffsets(translatedFigs)
        return translatedFigs

    def checkOneToManyOffsets(self, figureIter):
        """searches for cases where a one-to-many ratio exists between soprano and bass and inserts
        figures to account for the coindexing invariant"""
        for i, ch in enumerate(self.chordIterable()):
            n = ch.notes[0] #should be bass note
            if n.tie:
                if isinstance(n.tie, type(tie.Tie('start'))):
                    if ch.notes[-1] != self.chordIterable()[i+1].notes[-1] and n.tie.type == 'start':
                        fig = figureIter[i]
                        figureIter.insert(i, fig)        

    def writeVisualFigures(self, figList):
        """( TODO: )since music21 does not yet read figures from input files, it follows that to have figures
        displayed in the output score when calling show() we must add them into the musicxml file
        ourselves. this function does so by making them lyrics, just like Finale :) 
        
        Takes in a list of explicit key-aware intervals (e.g., the output from getFigures)
        so far not sure how suspensions will work, not explicitly considering 7th chords yet either
        
        in general, at some point we'll have to work on inserting figure nodes into the output xmltree
        where they actually belong"""
        prettyFigs = []
        
        for figure in figList:
            prettyFig = []
            for symbol in figure:
                if symbol != 3 and symbol != 5:
                    prettyFig.append(str(symbol) + "\n\n\n")

            prettyFigs.append(prettyFig)
        
        for i, n in enumerate(self.bass.flatten().getElementsByClass(note.Note)):
            n.addLyric(prettyFigs[i])
        

def checkSevenths(figure):
    """checks if a figure represents a 7th chord, then addresses some common cases if it is. 
    does not yet address 7th chords containing accidentals"""
    #root position
    if(figure[0] == '7' and len(figure) == 1):
        figure.insert(0, 3)
        figure.insert(1, 5)
        figure = [7 if x=='7' else x for x in figure]
    #first inversion
    if(figure[0] == '6' and figure[1] == '5'):
        figure.insert(0, 3)
        figure = [6 if x=='6' else x for x in figure]
        figure = [5 if x=='5' else x for x in figure]
    #second inversion
    if(figure[0] == '4' and figure[1] == '3'):
        figure.insert(2, 6)
        figure = [4 if x=='4' else x for x in figure]
        figure = [3 if x=='3' else x for x in figure]
    #third inversion
    if(figure[0] == '4' and figure[1] == '2'):
        figure.insert(2, 6)
        figure = [4 if x=='4' else x for x in figure]
        figure = [2 if x=='2' else x for x in figure]
    return figure

def consume(iterator, n):
    "Helper function to advance an iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

def isAccidental(figure): 
    if '#' == figure or 'b' == figure or 'n' == figure:
        return True
    else:
        return False