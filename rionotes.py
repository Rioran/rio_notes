"""Allows creation of notes based on pure soundwaves."""
import numpy as np
from IPython.display import Audio, display
from matplotlib.pyplot import figure, plot
from scipy.io import wavfile

from lib.generators import (
    WAVE_FUNCTIONS,
    apply_linearity,
    normalize_wave,
    random_shift,
)
from lib.notes import NOTES

BPM = 144
SAMPLING_RATE = 44100  # like 44.1 KHz for MP3
NOTE_LENGTH = SAMPLING_RATE * 60 / BPM
NOTE_DURATION = NOTE_LENGTH / SAMPLING_RATE
CHART_SIZE = (15, 4)
# t triangular, s sine, sq square, sw saw, bs backsaw
WAVE_TYPE = 't'
# About ADSR: https://en.wikipedia.org/wiki/Envelope_(music)
ADSR_ENABLED = True
ADSR_SHARES = (0.05, 0.3, 0.9)
ADSR_LEVELS = (1.0, 1.0, 0.7)


def reset_cashes():
    """Reset cashes for production classes waves."""
    for entity in (Chord, Note, Timeline):
        entity.wave_cash = {0: 0}


class Track(object):
    """Combined chords into long tracks."""

    def __init__(self, notes: str):
        """Initiate Track instance.

        Parameters:
            notes: str
                text with notes representations,
                could look like g3*g4*b4*d4+g3*g4*b4*d4
                newlines allowed + for concatenation,
                * for sound over sound
        """
        notes = notes.strip().replace('\n', '+')
        chords_list = notes.split('+')
        chords = [Chord(chord) for chord in chords_list]
        self.wave = sum(chords)

    def display(self):
        """Use Jupyter feature to render interactive audio."""
        display(Audio(self.wave, rate=SAMPLING_RATE))

    def save(self, path: str = 'demo.wav'):
        """Save wave into wav file.

        Parameters:
            path: str, default: 'demo.wav'
                where and how your track will be saved
        """
        wavfile.write(path, SAMPLING_RATE, self.wave)

    def plot(self, times: int = 1, full=False):
        """Use Jupyter feature to render wave chart.

        Parameters:
            times: int, default: 1
                how many notes to render
            full: bool, default: False
                whether to render full wave
        """
        if full:
            len_limit = len(self.wave)
            plot_timeline = Timeline(int(len(self.wave) / NOTE_LENGTH))
        else:
            len_limit = times * NOTE_LENGTH
            plot_timeline = Timeline(times)
        plot_sound_wave = self.wave[:len_limit]
        figure(figsize=CHART_SIZE)
        plot(plot_timeline, plot_sound_wave)

    def smooth(self, times=1, wing=10):
        """Minimize value spread by applying average.

        Parameters:
            times: int, default: 3
                how many times to apply smoothing
            wing: int, default: 20
                value radius for mean calc
        """
        for _ in range(times):
            tmp_wave = self.wave[:]
            for index in range(wing, len(tmp_wave)-wing):
                neighbors = self.wave[index - wing:index + wing]
                tmp_wave[index] = np.mean(neighbors)
            self.wave = tmp_wave
        self.wave = normalize_wave(self.wave)

    def distort(self, distance: float = 0.05):
        """Distort value with spread inside given range.

        Parameters:
            distance: float, default: 0.05
                new value will be multiplied by random value in 1 +/- range
        """
        self.wave = random_shift(self.wave)
        self.wave = normalize_wave(self.wave)


class Chord(object):
    """Combined notes."""

    wave_cash = {'': 0}

    def __init__(self, text):
        """Initiate Chord instance.

        Parameters:
            text: str
                text with notes representations,
                could look like g3*g4*b4*d4---
                where '-' stands for repetition
        """
        self.text = text
        label, *tail = text.split('-')
        if text in Chord.wave_cash:
            self.wave = Chord.wave_cash.get(text, 0)
            return
        times = len(tail) + 1
        note_list = label.split('*')
        notes = [Note(note, times) for note in note_list]
        self.wave = sum(notes)
        if ADSR_ENABLED:
            self.apply_adsr()
        Chord.wave_cash[text] = normalize_wave(self.wave)
        self.wave = Chord.wave_cash[text]

    def __add__(self, other):
        """Add chords together to get a longer wave (Track).

        Parameters:
            other: Chord
                Just other chord

        Returns:
            Chord
                with concatenated sound wave.
        """
        chord = Chord('0', 0)
        chord.wave = np.concatenate((self.wave, other.wave))
        return chord

    def apply_adsr(self):
        """Apply ADSR: https://en.wikipedia.org/wiki/Envelope_(music) ."""
        adsr_points = [
            int(share * len(self.wave)) for share in ADSR_SHARES
        ]
        attack, delay, sustain, release = np.split(self.wave, adsr_points)
        attack = apply_linearity(attack, 0, ADSR_LEVELS[0])
        delay = apply_linearity(delay, ADSR_LEVELS[0], ADSR_LEVELS[1])
        sustain = apply_linearity(sustain, ADSR_LEVELS[1], ADSR_LEVELS[2])
        release = apply_linearity(release, ADSR_LEVELS[2], 0)
        self.wave = np.concatenate((attack, delay, sustain, release))


class Note(object):
    """Single note defined by pitch and times length (bpm)."""

    wave_cash = {'': 0}

    def __init__(self, note: str, times: int):
        """Initiate Note instance.

        Parameters:
            note: str
                specific note to work with, like as4
            times: int
                defines the length of the note
        """
        label = '{0}-{1}'.format(note, times)
        self.times = times
        if label in Note.wave_cash:
            self.wave = Note.wave_cash.get(label, 0)
            return
        timeline = Timeline(times).wave
        frequency = NOTES.get(note, '0')
        wave = WAVE_FUNCTIONS[WAVE_TYPE](timeline, frequency)
        Note.wave_cash[label] = wave
        self.wave = wave

    def __add__(self, other):
        """Add notes together to get a Chord-like wave.

        Parameters:
            other: Note
                Just other note

        Returns:
            Note
                with combined sounds.
        """
        note = Note('0', self.times)
        note.wave = self.wave + other.wave
        return note


class Timeline(object):
    """Collection of arrays to speed-up generation of objects."""

    wave_cash = {'': 0}

    def __init__(self, times: int = 1):
        """Initiate Timeline instance.

        Parameters:
            times: int
                defines the length of the Timeline based on bpm
        """
        if times in Timeline.wave_cash:
            self.wave = Timeline.wave_cash.get(times, 0)
            return
        wave = np.linspace(0, NOTE_DURATION, num=NOTE_LENGTH)
        Timeline.wave_cash[times] = wave.astype(np.float64)
        self.wave = Timeline.wave_cash[times]
