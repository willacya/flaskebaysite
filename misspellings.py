import numpy as np
import pandas as pd

keyboard = np.array([['q','w','e','r','t','y','u','i','o','p'],
                    ['a','s','d','f','g','h','j','k','l','.'],
                    ['.','z','x','c','v','b','n','m','.','.']])

keys = {'q':[0,0],
        'w':[0,1],
        'e':[0,2],
        'r':[0,3],
        't':[0,4],
        'y':[0,5],
        'u':[0,6],
        'i':[0,7],
        'o':[0,8],
        'p':[0,9],
        'a':[1,0],
        's':[1,1],
        'd':[1,2],
        'f':[1,3],
        'g':[1,4],
        'h':[1,5],
        'j':[1,6],
        'k':[1,7],
        'l':[1,8],
        '.':[1,9],
        '.':[2,0],
        'z':[2,1],
        'x':[2,2],
        'c':[2,3],
        'v':[2,4],
        'b':[2,5],
        'n':[2,6],
        'm':[2,7],
        '.':[2,8],
        '.':[2,9]}

def misspelled_words(word):
    misspellings = []
    for e,i in enumerate(word):
        if i == " ":
            misspellings.append(word[:e] + word[e+1:])
        else:
            for j in [-1,0,1]:
                for k in [-1,0,1]:
                    try:
                        if keys[i][0] + j <= 2 and keys[i][0] + j >= 0 and keys[i][1] + k <= 9 and keys[i][1] + k >= 0:
                            if keyboard[keys[i][0] + j, keys[i][1] + k] != '.':
                                letter = keyboard[keys[i][0] + j, keys[i][1] + k]
                                misspellings.append(word[:e] + letter + word[e+1:])
                    except:
                        pass

            if e < len(word)-1:
                misspellings.append(word[:e] + word[e+1] + word[e] + word[e+2:])
                misspellings.append(word[:e+1] + word[e+2:])

            misspellings.append(word[:e] + i + word[e:])

    x = []
    for i in list(set(misspellings)):
        if i[0] == word[0] and i[-1] == word[-1] and len(word) > 2:
                x.append(i)
    return x

def split_words(word):
    words = word.split(" ")
    misspellings = []
    if len(words) > 1:
        for e, i in enumerate(words):
            for j in misspelled_words(i):
                x = "" if e == 0 else " "
                y = "" if e == len(words)-1 else " "
                misspellings.append(" ".join(words[:e]) + x + j + y + " ".join(words[e+1:]))
    else:
        for i in misspelled_words(words[0]):
            misspellings.append(i)

    return misspellings


def split_misspelled_keywords(word):

    counter = 0
    sub_total_words = []
    total_words = []

    for i in split_words(word):
        if i != word:
            if counter + len(i) + 1 > 298:
                total_words.append("(" + ",".join(sub_total_words) + ")")
                counter = len(i) + 1
                sub_total_words = []
                sub_total_words.append(i)
            else:
                counter += len(i) + 1
                sub_total_words.append(i)

    total_words.append("(" + ",".join(sub_total_words) + ")")

    return total_words

