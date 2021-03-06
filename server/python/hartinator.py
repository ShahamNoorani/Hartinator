# add flat keys (only minor left)
# correct doubling with inversions

from constants import allNotes, majorKeys, minorKeys, voicesInOrder, goodStartingNotes, ranges
from chord import Chord
from voice_leading import is7thResolved, isParallel5thOctave, isVoiceCrossing, isSpacingValid

import os
from random_words import RandomWords

class PartWriter:
    def __init__(self, key="C", chordProgression="I"):
        self.key = key
        self.chords = []

        self.chordProgression = chordProgression.split(" ") # convert from "I I I" to ["I", "I", "I"]

        for romanNumeral in self.chordProgression:
            self.chords.append(Chord(romanNumeral, self.key))

        sopranoLine = [""] * len(self.chords)
        altoLine = [""] * len(self.chords)
        tenorLine = [""] * len(self.chords)
        bassLine = [""] * len(self.chords)

        self.voices = {"soprano": sopranoLine, "alto": altoLine, "tenor": tenorLine, "bass": bassLine}
        
    def printAllVoices(self):
        print("Soprano: " + str(self.voices["soprano"]))
        print("Alto:    " + str(self.voices["alto"]))
        print("Tenor:   " + str(self.voices["tenor"]))
        print("Bass:    " + str(self.voices["bass"]))

    def printAllVoicesWithAccidentals(self):
        print("Soprano: " + str(self.sopranoLineWithAccidentals))
        print("Alto:    " + str(self.altoLineWithAccidentals))
        print("Tenor:   " + str(self.tenorLineWithAccidentals))
        print("Bass:    " + str(self.bassLineWithAccidentals))

    def updateAllVoicesWithAccidentals(self):
        i = 0
        for voice in voicesInOrder:
            line = []

            if self.key in majorKeys:
                keystring = majorKeys[self.key]
            else:
                keystring = minorKeys[self.key]

            for note in self.voices[voice]:
                if (note[0] + "#") in keystring:
                    line.append(note[0] + "#" + note[1])
                elif (note[0] + "b") in keystring:
                    line.append(note[0] + "b" + note[1])
                else:
                    line.append(note)

            if i == 0:
                self.sopranoLineWithAccidentals = line
            if i == 1:
                self.altoLineWithAccidentals = line
            if i == 2:
                self.tenorLineWithAccidentals = line
            if i == 3:
                self.bassLineWithAccidentals = line
            i += 1

    def followsAllVoiceLeading(self, voice, beat, newNoteIndex):
        print("beat in voice leading: " + str(beat))
        a = is7thResolved(voice, beat, newNoteIndex, self.key, self.voices) 
        b = isParallel5thOctave(voice, beat, newNoteIndex, self.voices)
        c = isVoiceCrossing(voice, beat, newNoteIndex, self.voices) 
        d = isSpacingValid(voice, beat, newNoteIndex, self.voices)

        print(str(a) + " " + str(b) + " " + str(c) + " " + str(d))
        return a and b and c and d

    def removeBadNotes(self, possibleNotes, counts, voice, chord):
        newPossibleNotes = []
        for n in possibleNotes:
            if voice == "tenor":
                if n[0] == chord.fifth[0] and counts[1] == 0: # make sure every chord member is present
                    continue
                if n[0] == chord.third[0] and counts[2] == 0: # make sure every chord memeber is present
                    continue
                if n[0] == chord.root[0] and 0 in [counts[1], counts[2]]: # make sure every chord memeber is present
                    continue
                if n[0] == chord.root[0] and counts[0] == 2:
                    continue
                if n[0] == chord.third[0] and counts[1] == 1: # prevent doubled third
                    continue
            if voice == "alto":
                if n[0] == chord.root[0] and counts[0] == 2:
                    continue
            if voice == "soprano" and chord.root == self.key:
                if n[0] != chord.root[0]:
                    continue
            newPossibleNotes.append(n)

        return newPossibleNotes

    def reorderPossibleNotes(self, possibleNotes, counts, voice, chord):
        newPossibleNotes = possibleNotes
        swapped = True
        while swapped:
            swapped = False
            for i in range(len(newPossibleNotes) - 1):
                ratingOfNote1 = self.rateNote(possibleNotes[i], counts, voice, chord)
                ratingOfNote2 = self.rateNote(possibleNotes[i + 1], counts, voice, chord)
                if ratingOfNote1 < ratingOfNote2:
                    newPossibleNotes[i], newPossibleNotes[i + 1] = newPossibleNotes[i + 1], newPossibleNotes[i]
                    swapped = False

        return newPossibleNotes

    def rateNote(self, note, counts, voice, chord):
        note = note[0]
        if voice == "soprano":
            if note == chord.root:
                return 1
            return 2
        
        if voice == "alto":
            if note == chord.root:
                return 1
            if (note == chord.fifth and counts[1] != 0) or note == chord.third:
                return 2
            return 3
        
        if voice == "tenor":
            if note == chord.root and not 0 in [counts[1], counts[2]]:
                return 1
            return 2

    def updateChordMemberFrequency(self, counts, beat, chord, voice):
        newCounts = [0, 0, 0]
        for i in voicesInOrder:
            if i == voice:
                break
            curr = self.voices[i][beat][0:1]
            if curr == chord.root[0]:
                newCounts[0] += 1
            elif curr == chord.third[0]:
                newCounts[1] += 1
            elif curr == chord.fifth[0]:
                newCounts[2] += 1
        
        return newCounts
        
    def writeBassLine(self):
        # good starting note
        lastNoteIndex = allNotes.index(goodStartingNotes["bass"])

        # write rest of bassLine
        for beat, chord in enumerate(self.chords):
            i, j = lastNoteIndex, lastNoteIndex
            while True:
                if allNotes[i] == chord.root[0:1]:
                    self.voices["bass"][beat] = allNotes[i:i+2]
                    lastNoteIndex = i
                    break
                elif allNotes[j] == chord.root[0:1]:
                    self.voices["bass"][beat] = allNotes[j:j+2]
                    lastNoteIndex = j
                    break

                # keeping pointers within range
                if i > ranges["bass"][0]:
                    i -= 2
                if j < ranges["bass"][1]:
                    j += 2
                if i <= ranges["bass"][0] and j >= ranges["bass"][1]:
                    break

    def writeLine(self, beat=0, voice="soprano", voices=""):
        if voices:
            self.voices = voices

        chord = self.chords[beat]
        possibleNotes = []
        counts = [0, 0, 0]
        
        i, j = allNotes.index(goodStartingNotes[voice]), allNotes.index(goodStartingNotes[voice])

        if beat != 0:
            i, j = allNotes.index(self.voices[voice][beat-1]), allNotes.index(self.voices[voice][beat-1])

        count = 0
        while count < 4:
            if allNotes[j] in [chord.root[0], chord.third[0], chord.fifth[0]]:
                possibleNotes.append(allNotes[j:j+2])
            if allNotes[i] in [chord.root[0], chord.third[0], chord.fifth[0]]:
                possibleNotes.append(allNotes[i:i+2])
            if i > ranges[voice][0] + 2:
                i -= 2
            if j < ranges[voice][-1] - 2:
                j += 2
            count += 1

        counts = self.updateChordMemberFrequency(counts, beat, chord, voice)
        possibleNotes = self.removeBadNotes(possibleNotes, counts, voice, chord)
        possibleNotes = self.reorderPossibleNotes(possibleNotes, counts, voice, chord)

        for n in possibleNotes:
            if "" in self.voices["tenor"] and beat < len(self.chords):
                self.voices[voice][beat] = n
                
                if voice == "tenor":
                    beat += 1
                    nextVoice = "soprano"
                else:
                    nextVoice = voicesInOrder[voicesInOrder.index(voice) + 1]

                if beat < len(self.chords):
                    self.writeLine(beat, nextVoice, self.voices)

    def printChords(self):
        for chord in self.chords:
            print(chord.root + " " + chord.third + " " + chord.fifth)

    def addOctaveAndAccidentalsForLilypond(self, note):
        result = note[0]
        if "#" in note:
            result += "is"
        elif "b" in note:
            result += "es"
        if '2' in note:
            result += ","
        elif '4' in note:
            result += "\'"
        elif '5' in note:
            result += "\'\'"
        return result + " "

    def createSheetMusicPdf(self):
        sopranoNotes, altoNotes, tenorNotes, bassNotes = "", "", "", ""

        for i in self.sopranoLineWithAccidentals:
            sopranoNotes += self.addOctaveAndAccidentalsForLilypond(i)
        for i in self.altoLineWithAccidentals:
            altoNotes += self.addOctaveAndAccidentalsForLilypond(i)
        for i in self.tenorLineWithAccidentals:
            tenorNotes += self.addOctaveAndAccidentalsForLilypond(i)
        for i in self.bassLineWithAccidentals:
            bassNotes += self.addOctaveAndAccidentalsForLilypond(i)

        self.fileName = RandomWords().random_word() + ".ly"
        fout = open(self.fileName, "w")

        if self.key in majorKeys:
            quality = "\\major"
        else:
            quality = "\\minor"
        keyAccidental = ""
        if "#" in self.key:
            keyAccidental = "is"
        if "b" in self.key:
            keyAccidental = "es"

        fileString = ""

        fileString += "global = { \\key " + self.key.lower()[0] + keyAccidental + " " + quality + " }" 
        fileString += "sopMusic = \\absolute { " + sopranoNotes.lower() + "}"
        fileString += "altoMusic = \\absolute { " + altoNotes.lower() + "}"
        fileString += "tenorMusic = \\absolute { " + tenorNotes.lower() + "}"
        fileString += "bassMusic = \\absolute { " + bassNotes.lower() + "}"
        fileString += "\\score { \\new ChoirStaff <<\\new Staff = \"women\" << \\new Voice = \"sopranos\" { \\voiceOne << \\global \\sopMusic >> }"
        fileString += "\\new Voice = \"altos\" { \\voiceTwo << \\global \\altoMusic >> } >>"
        fileString += "\\new Staff = \"men\" << \\clef bass \\new Voice = \"tenors\" { \\voiceOne << \\global \\tenorMusic >> }"
        fileString += "\\new Voice = \"basses\" { \\voiceTwo << \\global \\bassMusic >> } >> >> } \\version \"2.18.2\""
        self.fileString = fileString
        
        fout.write(fileString)
        fout.close()

        os.system("lilypond " + self.fileName)
        print("Look for a file named \'" + self.fileName[0:-3] + ".pdf" + "\'!")

    def createMidiFile(self):
        fout = open(self.fileName, "w")
        newFileString = self.fileString[0:self.fileString.index("score") + 8] + "\\midi { \\tempo 4 = 72 } " + self.fileString[self.fileString.index("score") + 8:-1] + self.fileString[-1]
        fout.write(newFileString)
        fout.close()
        os.system("lilypond " + self.fileName)

    def main(self):
        self.writeBassLine()
        self.writeLine()
        self.updateAllVoicesWithAccidentals()

if __name__ == "__main__":
    PartWriterImpl = PartWriter(
        "C", "I IV V I")
    PartWriterImpl.main()
    PartWriterImpl.printAllVoices()
    print()
    PartWriterImpl.printAllVoicesWithAccidentals()
    PartWriterImpl.createSheetMusicPdf()
    PartWriterImpl.createMidiFile()

# meme cases
#I IV vi V I IV V I ii IV V vii vi IV ii V I IV vi IV vii vi V I
