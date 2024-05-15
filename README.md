# rio_notes
Compose WAV music using notes notation like 'd2'.

Complex usage example can be found here: https://colab.research.google.com/drive/1hX11v2cn76Shgie1vkU6z8D6seEk01cy?usp=sharing

### sound waves

There are 5 types of supported wave types:

- s - sin
- sq - square
- sw - saw
- bs - backsaw
- t - triangular

To apply a wave type use code like:

```python
from rionotes.wave_objects import Config

Config.set_wave('sq')
```

### display

To display Audio in notebooks use ipython:

```python
from IPython.display import Audio, display

from rionotes.wave_objects import SAMPLING_RATE, Track


track = Track('a2')
display(Audio(track.wave, rate=SAMPLING_RATE))
```

### ADSR

Project supports ADSR: https://en.wikipedia.org/wiki/Envelope_(music)

It is embedded into wave_objects.py file as Global Constants:

```python
ADSR_ENABLED = True
ADSR_SHARES = (0.05, 0.3, 0.9)
ADSR_LEVELS = (1.0, 1.0, 0.7)
```

Let me know if you want it to be configurable "on the go".
