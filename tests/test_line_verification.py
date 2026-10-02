# -*- coding: utf-8 -*-
"""The Whisper round-trip gate has to fold spelling and still catch a substituted word.

Whisper transcribes Haryanvi through a Hindi model, so it rewrites the dialect's spelling on
every single line — गाड्डी->गाड़ी, सै->है, हॉर्न->होरन. If the gate flags those, the real defect
drowns in noise and gets waved through. If it folds too much, it stops catching anything.

Both defects below are real: Veo read `पहचाण` as "पैर पैन" (meaningless, regenerated), and read
`पाछै` ("behind") as "अच्छे" ("fine"), which destroyed the line the whole horror story turned on.
edge-tts's sentence-initial `चाय` -> "चाहे" is the third.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from verify_lines import _matched, _norm


class TestSpellingIsFolded:
    def test_haryanvi_double_consonant_reads_as_nukta(self):
        assert _matched("गाड्डी", ["गाड़ी"])

    def test_haryanvi_sai_reads_as_hindi_hai(self):
        assert _matched("सै", ["है"])

    def test_conjunct_is_spelled_out(self):
        assert _matched("हॉर्न...", ["होरन"])

    def test_vowel_length_and_nasal_marks_do_not_matter(self):
        assert _matched("तू", ["तु"])
        assert _matched("सूं", ["सूँ"])

    def test_trailing_danda_is_not_part_of_the_word(self):
        assert _matched("जा।", ["जा"])

    def test_haryanvi_vowel_spelling_of_the_same_word(self):
        # क्यूँ and क्यों are the same word written for Haryanvi and for Hindi
        assert _matched("क्यूँ", ["क्यों"])

    def test_retroflex_la_is_written_as_plain_la(self):
        # काळू is the Haryanvi spelling of the name Whisper returns as कालू
        assert _matched("काळू", ["कालू"])

    def test_whisper_splitting_one_word_into_two_is_not_a_misread(self):
        assert _matched("खरीदी", ["खरीद", "दी"])

    def test_haryanvi_va_glide_folds(self):
        # बतावूँ carries the vowel as a matra after a व glide; Hindi spells it ऊ outright
        assert _matched("बतावूँ", ["बताऊं"])


class TestRealMisreadsAreStillCaught:
    def test_pehchaan_read_as_pair_pain(self):
        assert not _matched("पहचाण", ["पैर", "पैन"])

    def test_paachhai_read_as_acche(self):
        assert not _matched("पाछै", ["अच्छे"])

    def test_chai_read_as_chahe(self):
        assert not _matched("चाय", ["चाहे"])

    def test_an_entirely_different_noun_is_caught(self):
        assert not _matched("गाड्डी", ["कुत्ता"])
        assert not _matched("जमीन", ["मकान"])

    def test_a_near_rhyme_is_still_caught(self):
        # the folding rules must not go so far that रोटियाँ and गाड़ियाँ collapse together
        assert not _matched("रोटियाँ", ["गाड़ियाँ"])


class TestNumbersAreWrittenAsNumerals:
    def test_char_hazaar_comes_back_as_4000(self):
        # Whisper writes numerals; "चार हज़ार रोटियाँ" transcribes as "4000 रोटियां"
        assert _matched("चार", ["4000", "रोटियां"])
        assert _matched("हज़ार", ["4000", "रोटियां"])

    def test_a_number_word_with_no_numeral_anywhere_is_still_checked(self):
        assert not _matched("चार", ["पाँच", "रोटियां"])


class TestEnglishLoanwordsCrossScripts:
    def test_devanagari_loanword_returned_in_latin(self):
        # the line spells the English words in Devanagari; Whisper hands them back in Latin
        heard = "Southwest वही मेरा bedroom है".split()
        assert _matched("साउथ-वेस्ट।", heard)
        assert _matched("बेडरूम", heard)

    def test_a_latin_word_in_the_transcript_does_not_excuse_an_unrelated_word(self):
        assert not _matched("रोटियाँ", ["bedroom", "है"])


class TestLatinWordsAreNotComparable:
    def test_wifi_transliterated_to_devanagari_is_not_a_misread(self):
        # Whisper writes "वाईफाई" for "WiFi" — correct, and impossible to compare across scripts
        assert _matched("WiFi", ["मम्मी", "जी", "वाईफाई", "का", "पासवर्ड"])

    def test_a_latin_word_never_blocks_assembly(self):
        assert _matched("Follow", ["फॉलो"])


def test_norm_is_stable_for_a_word_with_nothing_to_fold():
    assert _norm("मेरी") == "मेरी"
