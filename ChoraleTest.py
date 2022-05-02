from Chorale import Chorale

def main():
    c = Chorale('chorale_006_separate_parts.musicxml', chordify=True)
    c.show()

    chordChorale = c.chordify()
    chordChorale.show()

    for chord in c.chordIterable():
        print(chord)
    
    for measure in c:
        print(measure)

if __name__ == "__main__":
    main()
