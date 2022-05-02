import music21
from progression import Progression

def change_arr_idx_0(arr):
    arr[0] = 1

if __name__ == '__main__':
    # arr = [2,2,2]
    # change_arr_idx_0(arr)
    # print(arr)
    c = Progression('chorale_012_separate_parts.musicxml', chordify=True)
    for sth in c.progression:
        print(sth)