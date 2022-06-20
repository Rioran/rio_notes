"""Functions for wave generation & transformation."""


def generate_wave_sine(timeline: np.array, frequency: float):
    """Transform linear array into sine wave.

    Parameters:
        timeline: np.array
            array with linear rising values
        frequency: float
            note frequency

    Returns:
        np.array
            calculated transformation
    """
    return np.sin(2 * np.pi * frequency * timeline)


def generate_wave_square(timeline: np.array, frequency: float):
    """Transform linear array into square wave.

    Parameters:
        timeline: np.array
            array with linear rising values
        frequency: float
            note frequency

    Returns:
        np.array
            calculated transformation
    """
    return timeline // (1 / frequency) % 2 * 2 - 1


def generate_wave_triangular(timeline: np.array, frequency: float):
    """Transform linear array into triangular wave.

    Parameters:
        timeline: np.array
            array with linear rising values
        frequency: float
            note frequency

    Returns:
        np.array
            calculated transformation
    """
    raw_triangle = timeline % (2 / frequency) * frequency - 1
    return np.absolute(raw_triangle) * 2 - 1


def generate_wave_saw(timeline: np.array, frequency: float):
    """Transform linear array into saw wave.

    Parameters:
        timeline: np.array
            array with linear rising values
        frequency: float
            note frequency

    Returns:
        np.array
            calculated transformation
    """
    return timeline % (2 / frequency) * frequency - 1


def generate_wave_backsaw(timeline: np.array, frequency: float):
    """Transform linear array into backsaw wave.

    Parameters:
        timeline: np.array
            array with linear rising values
        frequency: float
            note frequency

    Returns:
        np.array
            calculated transformation
    """
    return -timeline % (2 / frequency) * frequency - 1


WAVE_FUNCTIONS = MappingProxyType({
    'sin': generate_wave_sine,
    'square': generate_wave_square,
    'triangular': generate_wave_triangular,
    'saw': generate_wave_saw,
    'backsaw': generate_wave_backsaw,
})


def apply_linearity(array, start_ratio, end_ratio):
    """Transform linear array values with ratios.

    Parameters:
        array: np.array
            array with linear rising values
        start_ratio: float
            starting multiplier
        end_ratio: float
            starting multiplier

    Returns:
        np.array
            calculated transformation
    """
    multipliers = np.linspace(start_ratio, end_ratio, num=len(array))
    return array * multipliers