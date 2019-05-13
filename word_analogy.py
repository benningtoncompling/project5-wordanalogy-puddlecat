# Project 5 by Ell Buscemi 5.11.19
# i didn't get through high school math so this is hurting me
# also i think i may be missing notes on calculating distance so i looked stuff up a bunch

import re
import math
import sys
import os
import numpy
import time


vectorFileName = sys.argv[1]
inputDirectory = sys.argv[2]
outputDirectory = sys.argv[3]
evalFile = sys.argv[4]
should_normalize = sys.argv[5]
similarity_type = sys.argv[6]


# get the data from the vector model
with open(vectorFileName, 'r', encoding='utf-8') as input:
    x = input.read()

    wordsList = re.findall(r'\b[a-z]+\b', x, re.IGNORECASE)
    floatsList = re.findall(r'\-*\d\.\d+', x, re.MULTILINE)

    wordsDictionary = {}

    index = 300
    for i in range(int(len(wordsList))):
        floatsSubList = []

        for j in range(index-300, index-1):
            floatsSubList.append(floatsList[j])

        index += 300
        wordsDictionary[wordsList[i]] = floatsSubList

    input.close()

# iterate through the files in the test set directory
with open(evalFile, 'w', encoding='utf-8') as evalOutput:
    for filename in os.listdir(inputDirectory):
        if filename.startswith('.'):
            continue
        if not filename.endswith('.txt'):
            continue
        filepath = os.path.join(inputDirectory, filename)
        outputFilepath = os.path.join(outputDirectory, filename)
        start = time.time()  # time how long it takes to do each file
        with open(filepath, 'r', encoding='utf-8') as input:
            with open(outputFilepath, 'w', encoding='utf-8') as output:
                x = input.read()

                words = re.findall(r'\b[a-z]+\b', x, re.IGNORECASE)

                # keep track of this for evaluating
                total = 0
                good = 0
                skipped = 0

                for i in range(int(len(words)/4)):
                    total += 1
                    word1 = words[i*4]
                    word2 = words[(i*4)+1]
                    word3 = words[(i*4)+2]
                    word4 = words[(i*4)+3]  # saved so we can calculate accuracy

                    if (word1 not in wordsDictionary) | (word2 not in wordsDictionary) | (word3 not in wordsDictionary):
                        skipped += 1
                        continue
                        # for now just skip words that are missing from the model, there are a lot of them though

                    # probably can condense this sort of thing onto one line? iunno
                    wordsSubList = []
                    wordsSubList.append(word1)
                    wordsSubList.append(word2)
                    wordsSubList.append(word3)

                    # ok, this is causing a lot of lag and there's probably a better way to do it but I'M A MATH IDIOT
                    if should_normalize:
                        mag = 0.0
                        for w in wordsSubList:
                            for v in wordsDictionary[w]:
                                mag += float(v)**2
                            mag = math.sqrt(mag)
                            for v in wordsDictionary[w]:
                                v = float(v)/mag

                    nparray1 = numpy.asarray(wordsDictionary[word1], dtype=float)
                    nparray2 = numpy.asarray(wordsDictionary[word2], dtype=float)
                    nparray3 = numpy.asarray(wordsDictionary[word3], dtype=float)
                    # this is the c+b-a calculation
                    nparray4 = numpy.subtract((numpy.add(nparray3, nparray2)), nparray1)

                    if similarity_type == 0:
                        # euclidean distance
                        bestDistance = 9000
                        bestDistanceWord = "NULL"

                        if should_normalize:
                            for w in wordsDictionary:
                                mag = 0.0
                                for v in wordsDictionary[w]:
                                    mag += float(v) ** 2
                                mag = math.sqrt(mag)
                                for v in wordsDictionary[w]:
                                    v = float(v) / mag

                            vector = numpy.asarray(wordsDictionary[w], dtype=float)
                            distance = numpy.linalg.norm(nparray4 - vector, 300, 0)
                            if numpy.greater(bestDistance, distance):
                                bestDistance = distance
                                bestDistanceWord = w

                    if similarity_type == 1:
                        # Manhattan distance
                        bestDistance = 9000
                        bestDistanceWord = "NULL"

                        if should_normalize:
                            for w in wordsDictionary:
                                mag = 0.0
                                for v in wordsDictionary[w]:
                                    mag += float(v) ** 2
                                mag = math.sqrt(mag)
                                for v in wordsDictionary[w]:
                                    v = float(v) / mag

                            vector = numpy.asarray(wordsDictionary[w], dtype=float)
                            distance = numpy.sum(numpy.absolute(numpy.subtract(nparray4, vector)))

                            if distance < bestDistance:
                                bestDistance = distance
                                bestDistanceWord = w

                    if similarity_type == 2:
                        # Cosine distance
                        bestDistance = 0
                        bestDistanceWord = "NULL"

                        if should_normalize:
                            for w in wordsDictionary:
                                mag = 0.0
                                for v in wordsDictionary[w]:
                                    mag += float(v) ** 2
                                mag = math.sqrt(mag)
                                for v in wordsDictionary[w]:
                                    v = float(v) / mag

                            vector = numpy.asarray(wordsDictionary[w], dtype=float)
                            distance = numpy.dot(vector, nparray4)/(numpy.linalg.norm(vector)*numpy.linalg.norm(nparray4))

                            if distance > bestDistance:
                                bestDistance = distance
                                bestDistanceWord = w

                    if bestDistanceWord == word4:
                        good += 1

                    output.write(word1 + " " + word2 + " " + word3 + " " + bestDistanceWord + "\n")

                accuracy = ((good / total) * 100)
                end = time.time()
                timed = (end - start)
                evalOutput.write("\n" + filename + "\naccuracy: " + str(accuracy) + "%\ntime: " + str(timed) + "\nskipped (due to word(s) missing from model): " + str(skipped))

                input.close()
                output.close()

    evalOutput.close()
