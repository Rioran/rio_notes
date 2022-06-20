"""Allows creation of notes based on pure soundwaves."""
from types import MappingProxyType

import numpy as np
from IPython.display import Audio, display
from matplotlib.pyplot import figure, plot
from scipy.io import wavfile

from lib.notes import NOTES
from lib.generators import WAVE_FUNCTIONS, apply_linearity

SAMPLING_RATE = 44100  # like 44.1 KHz for MP3
DURATION = 2  # seconds
PLOT_LEN = 1000
CHART_SIZE = (15, 4)
ADSR_SHARES = (0.1, 0.3, 0.9)
ADSR_LEVELS = (1.0, 0.7, 0.6)


class Sound(object):
    """Provides topline sound operations."""

    def normalize_wave(self):
        """Reduce wave values to range 0 to 1."""
        self.wave /= np.max(np.absolute(self.wave))

    def display(self):
        """Use Jupyter feature to render interactive audio."""
        display(Audio(self.wave, rate=self._rate))

    def save(self, extension='wav'):
        """Save wave into desired extension.

        Parameters:
            extension: str
                either 'wav' or 'txt'
        """
        if extension == 'wav':
            filename = '{0}.wav'.format(self.name)
            wavfile.write(filename, self._rate, self.wave)
        if extension == 'txt':
            filename = '{0}_.txt'.format(self.name)
            np.savetxt(filename, self.wave)

    def plot(self, len_limit: int = PLOT_LEN, full=False):
        """Use Jupyter feature to render wave chart.

        Parameters:
            len_limit: int, default: PLOT_LEN
                amount of points to render
            full: bool, default: False
                whether to render full wave
        """
        if full:
            len_limit = len(self.wave)
        plot_timeline = self.timeline[:len_limit]
        plot_sound_wave = self.wave[:len_limit]
        figure(figsize=CHART_SIZE)
        plot(plot_timeline, plot_sound_wave)

    def smooth(self, wing=20, times=3):
        """Minimize value spread by applying average.

        Parameters:
            wing: int, default: 20
                value radius for mean calc
            times: int, default: 3
                how many times to apply smoothing
        """
        for _ in range(times):
            tmp_wave = self.wave[:]
            for index in range(wing, len(tmp_wave)-wing):
                neighbors = self.wave[index-wing:index+wing]
                tmp_wave[index] = np.mean(neighbors)
            self.wave = tmp_wave
        self.normalize_wave()


class Note(Sound):
    """Provides note manipulation operations."""

    wave_type: str = 'sin'
    duration: float = DURATION
    sampling_rate: int = SAMPLING_RATE

    def __init__(
        self,
        name: str,
        wave_type: str = None,
        wave: np.array = None,
        timeline: np.array = None,
    ):
        """Initiate the Note state.

        Parameters:
            name: str
                must be one of the NOTES
            wave_type: str, default = None
                must be one of the WAVE_FUNCTIONS keys
            wave: np.array, default = None
                only passed if notes combine
            timeline: np.array, default = None
                only passed if notes combine
        """
        self.name = name
        self._wave_name = wave_type
        if self._wave_name is None:
            self._wave_name = Note.wave_type
        if self._wave_name != 'mix':
            self.name = '{0}_{1}'.format(self.name, self._wave_name)
            self._note_name = name
        self._wav_file_path = '{0}.wav'.format(self.name)
        self._rate = Note.sampling_rate
        self._sound_array_len = self._rate * Note.duration
        self.timeline = timeline
        self.wave = wave
        if self.wave is None:
            self.initiate_wave()

    def __add__(self, note):
        """Add two Note's together.

        Parameters:
            note: Note
                other Note to sum up with

        Returns:
            Note
                with combined waves
        """
        name = '{0}_{1}'.format(self.name, note.name)
        wave = self.wave + note.wave
        wave_type = 'mix'
        chord = Note(name, wave_type, wave=wave, timeline=self.timeline)
        chord.normalize_wave()
        return chord

    def generate_wave(self, wave_type_function):
        """Generate a corresponding wave.

        Parameters:
            wave_type_function: callable
                specific function to make a wave.

        Returns:
            np.array
                calculated transformation
        """
        return wave_type_function(self.timeline, self.frequency)

    def initiate_wave(self):
        """Initiate the wave state."""
        self.timeline = np.linspace(
            0,
            Note.duration,
            num=self._sound_array_len,
        )
        self.timeline = self.timeline.astype(np.float64)
        self.frequency = NOTES.get(self._note_name, '0')
        self.wave = self.generate_wave(WAVE_FUNCTIONS[self._wave_name])

    def apply_adsr(self):
        """Apply ADSR: https://en.wikipedia.org/wiki/Envelope_(music) ."""
        adsr_points = [
            int(share * self._sound_array_len) for share in ADSR_SHARES
        ]
        attack, delay, sustain, release = np.split(self.wave, adsr_points)
        attack = apply_linearity(attack, 0, ADSR_LEVELS[0])
        delay = apply_linearity(delay, ADSR_LEVELS[0], ADSR_LEVELS[1])
        sustain = apply_linearity(sustain, ADSR_LEVELS[1], ADSR_LEVELS[2])
        release = apply_linearity(release, ADSR_LEVELS[2], 0)
        self.wave = np.concatenate((attack, delay, sustain, release))
        self.normalize_wave()
