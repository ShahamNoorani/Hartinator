import unittest

from hartinator import PartWriter
from constants import allNotes

class TestPartWriter(unittest.TestCase):
    def testVoiceCrossing(self):
        testObject = PartWriter("C", "I V I")
        testObject.voices["bass"] = ["C3", "G3", "C4", "D4"]
        testObject.voices["tenor"] = ["E3", "G3", "E3"]
        newNoteIndex = allNotes.index("F3")
        self.assertTrue(testObject.isVoiceCrossing("tenor", 2, newNoteIndex))

    def testIsParallelFifthOctave(self):
        testObject = PartWriter("C", "I V")
        testObject.voices["soprano"] = ["D5", "C5"]
        testObject.voices["alto"] = ["G4"] # F4
        testObject.voices["tenor"] = ["C3"] # C3
        testObject.voices["bass"] = ["C2", "C2"]
        self.assertTrue(testObject.isParallel5thOctave("alto", 1, allNotes.index("F4")))
        self.assertFalse(testObject.isParallel5thOctave("tenor", 1, allNotes.index("C3")))

    def testIs7thResolved(self):
        testObject = PartWriter("C", "I V")
        testObject.voices["soprano"] = ["B4"]
        testObject.voices["bass"] = ["B3"]
        self.assertTrue(testObject.is7thResolved("soprano", 1, allNotes.index("C5")))
        self.assertFalse(testObject.is7thResolved("bass", 1, allNotes.index("A3")))

    def testIsSpacingValid(self):
        testObject = PartWriter("C", "I V")
        testObject.voices["soprano"] = ["C5"] # F4
        testObject.voices["alto"] = ["B3"] # F4
        testObject.voices["tenor"] = ["G3"] # C3
        self.assertFalse(testObject.isSpacingValid("alto", 0, allNotes.index("B3")))
        self.assertTrue(testObject.isSpacingValid("tenor", 0, allNotes.index("G3")))


if __name__ == '__main__':
    unittest.main()