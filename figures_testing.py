from progression import Progression
import music21
from music21 import note, chord, tie
import json

def main():
    c = Progression('chorale_012_separate_parts.musicxml', chordify=True)
    print(c.measure(3)[0][0].expressions)
    print(c.measure(3)[0])
    print(c.chordIterable()[16])
    print(c.chordIterable()[16])
    print(len(c.chordIterable()))
    print(c.fermataIndices)
    print(c.chordIterable())
    print(len(c.figureIter))


   # for i, ch in enumerate(c.chordIterable()):
   #     n = ch.notes[0] #should be bass note
   #     if n.tie:
   #         if isinstance(n.tie, type(tie.Tie('start'))):
   #             if ch.notes[-1] != c.chordIterable()[i+1].notes[-1] and n.tie.type == 'start':
   #                 fig = c.figureIter[i]
   #                 c.figureIter.insert(i, fig)                               


    print(c.figureIter)
    print(len(c.figureIter))
    for chord in c.chordIterable():
        print(chord)
    #c.showTwoParts()
   
if __name__ == "__main__":
    main()
