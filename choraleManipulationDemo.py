from music21 import note, pitch, stream, converter, harmony, noteworthy, clef, duration
from music21.figuredBass import *
import copy
  
"""
    putting links here because they can be hard to find in the docs
    Interval: https://web.mit.edu/music21/doc/usersGuide/usersGuide_18_intervals.html
    Harmony: https://web.mit.edu/music21/doc/moduleReference/moduleHarmony.html (contains figures)
    voices: https://web.mit.edu/music21/doc/moduleReference/moduleStreamBase.html#music21.stream.base.Stream.voices
     also see https://web.mit.edu/music21/doc/moduleReference/moduleStreamBase.html#voice
    parts to voices: https://web.mit.edu/music21/doc/moduleReference/moduleStreamBase.html#music21.stream.base.Score.partsToVoices
    if easiest we could be keep SATB on independent staves, then concatenate into voices on a grand staff at the end:
    score: https://web.mit.edu/music21/doc/moduleReference/moduleStreamBase.html#music21.stream.base.Score
    Part: http://web.mit.edu/music21/doc/moduleReference/moduleStreamBase.html#music21.stream.base.Part
"""

def createPartFromTemplate(templatePart, partName, fillWithNote='|'):
  """
  quick way to currently initialize a new part as a deep copy of templatePart, 
  then modify relevant member variables and fill said new part
  with whole rests. templatePart should have a structure analogous to 
  that produced by converter.parse(<one_of_our_chorales>.musicxml) and accessed
  via one_of_our_chorales.parts[i], where i is the parts staff number (0-indexed)
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


def main():

#example of showing output (from the entire chorale to individual notes), 
#creating/inserting new parts into chorale — i.e., inner voices — into the chorale,
#editing those parts, 
#and compressing the expanded chorale (4 staves) back into its original format

# parse chorale #6: https://web.mit.edu/music21/doc/usersGuide/usersGuide_04_stream1.html#usersguide-04-stream1 
  chorale = converter.parse('chorale_006_separate_parts.musicxml')
      #The Stream object and its subclasses (Score, Part, Measure) are the fundamental containers for music21 objects 
      #such as Note, Chord, Clef, TimeSignature objects. Syntax is that of a list of lists of lists ... of lists

  #accessing individual parts:
  soprano = chorale.parts[0] 
  bass = chorale.parts[1]

  #accessing & displaying the first measure, then first note of the Bass in measure 1:
    #(note that measures are 1-indexed in this format)
  bass.measure(1).show()
  bass.measure(1).getElementsByClass(note.Note)[0].show() 

  #display outer voices individually
  soprano.show()
  bass.show()

  #display the outer voices together
  chorale.show()

  #insert the inner voices
  alto = createPartFromTemplate(soprano, 'Alto')
  tenor = createPartFromTemplate(bass, 'Tenor', 'G3')
  tenor.insert(0, clef.BassClef()) #0 is the duration offset
  
  chorale.remove(bass)
  chorale.append(alto)
  chorale.append(tenor)
  chorale.append(bass)

  #adjust the inner voices
  #alto.repeatAppend(note.Note('G'), 4)
  tNote = tenor.flatten().getElementsByClass(note.Note)[0]
  tNote.transpose('M3', inPlace=True)

  chorale.show() #now shows four staves

  #compress voices back into two staves
  combinedStaves = chorale.partsToVoices(voiceAllocation=2)
  print(len(combinedStaves.parts)) #expected 2
  combinedStaves.parts[1].insert(0, clef.BassClef())
  combinedStaves.show()


if __name__ == "__main__":
    main()
