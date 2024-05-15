# rio_notes
Compose WAV music using notes notation like 'd2'.

### display

To display Audio in notebooks use ipython:

```python
from IPython.display import Audio, display

from rionotes.wave_objects import SAMPLING_RATE, Track


track = Track('a2')
display(Audio(track.wave, rate=SAMPLING_RATE))
```
