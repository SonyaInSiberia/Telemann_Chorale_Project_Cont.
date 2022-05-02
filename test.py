from realization import *

c = chord.Chord(['C4', 'A4', 'E5'])
print("common name ", c.commonName)
print("root ", c.root())
print("third ", c.third)
print("fifth ", c.fifth)
print("seventh ", c.seventh)
print("is minimally complete ", isMinimallyComplete(c, False))
print("is minimally complete 7th", isMinimallyComplete(c, True))
print("\n")

c = chord.Chord(['C4', 'G4'])
print("common name ", c.commonName)
print("root ", c.root())
print("third ", c.third)
print("fifth ", c.fifth)
print("seventh ", c.seventh)
print("is minimally complete ", isMinimallyComplete(c, False))
print("\n")

c = chord.Chord(['A-3', 'B4', 'D5', 'F2'])
print(c)
print("common name ", c.commonName)
print("root ", c.root())
print("third ", c.third)
print("fifth ", c.fifth)
print("seventh ", c.seventh)
print("is minimally complete 7th", isMinimallyComplete(c, True))
print("\n")

c = chord.Chord(['C3', 'E3', 'G3', 'E4'])
print(c)
print("is keyboard style ", isKeyboardStyle(c))  
print("\n")

c = chord.Chord(['C3', 'E3', 'G3', 'G4'])
print(c)
print("is keyboard style ", isKeyboardStyle(c))  
print("\n")

# stream of notes
note1 = note.Note("C4")
note1.duration.type = 'half'
note2 = note.Note("F#4")
note3 = note.Note("B-2")

stream1 = stream.Stream()
stream1.id = 'some notes'
stream1.append(note1)
stream1.append(note2)
stream1.append(note3)

stream1.show('text')

print(stream1[-1].pitch)

# stream of chords
s = stream.Stream()
n = note.Note('C4') # qtr note default
s.append(n)

c = chord.Chord('E4 G4 C5') # qtr
s.insertIntoNoteOrChord(0.0, c)
print(s[-1])

realization = Realization(s, 0.0)
print("cost ", realization.getCost())

c2 = chord.Chord('D3 D4 A4 D5') # missing third
s.insertIntoNoteOrChord(1.0, c2)
print(s[-1])
realization.updateCost()
print("cost ", realization.getCost())

c3 = chord.Chord('E4 G4 B4 E5') # qtr
s.insertIntoNoteOrChord(2.0, c3)
print(s[-1])
realization.updateCost()
print("cost ", realization.getCost())

with open('costs.json') as json_file:
    data = json.load(json_file)
    print(data)
    print(type(data))

