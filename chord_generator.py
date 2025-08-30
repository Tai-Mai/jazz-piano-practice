from enum import Enum
import os
import random
import argparse
import time
import wave
from piper import PiperVoice

type semitones = int
type wholetones = int


class Mode(Enum):
    """Modes described as semitone deltas relative to a major scale"""

    lydian = [0, 0, 0, 1, 0, 0, 0]
    ionian = [0, 0, 0, 0, 0, 0, 0]
    mixolydian = [0, 0, 0, 0, 0, 0, -1]
    dorian = [0, 0, -1, 0, 0, 0, -1]
    aeolian = [0, 0, -1, 0, 0, -1, -1]
    phrygian = [0, -1, -1, 0, 0, -1, -1]
    locrian = [0, -1, -1, 0, -1, -1, -1]
    major = ionian
    minor = aeolian
    harmonic_minor = [0, 0, -1, 0, 0, -1, 0]
    melodic_minor = [0, 0, -1, 0, 0, 0, 0]


MAJOR_KEY_SIGNATURES: dict[str, tuple[int, str]] = {
    "C": (0, ""),
    "G": (1, "#"),
    "D": (2, "#"),
    "A": (3, "#"),
    "E": (4, "#"),
    "B": (5, "#"),
    "F#": (6, "#"),
    "C#": (7, "#"),
    "F": (1, "b"),
    "Bb": (2, "b"),
    "Eb": (3, "b"),
    "Ab": (4, "b"),
    "Db": (5, "b"),
    "Gb": (6, "b"),
    "Cb": (7, "b"),
}


semitones_to_accidental: dict[semitones, str] = {
    -2: "bb",
    -1: "b",
    0: "",
    1: "#",
    2: "x",
}


def _apply_mode_to_scale(
    scale: list[str],
    mode: Mode,
) -> list[str]:
    for scale_degree in range(len(scale)):
        mode_delta: semitones = mode.value[scale_degree]
        semitone_sum: int = (
            scale[scale_degree].count("#") - scale[scale_degree].count("b") + mode_delta
        )
        accidental: str = semitones_to_accidental[semitone_sum]
        scale[scale_degree] = scale[scale_degree][0] + accidental

    return scale


def get_scale(root: str, mode: Mode) -> list[str]:
    """
    Returns the scale of a key. Excepting keys written as, e.g., "Cmaj", "Bbmin", etc.
    Starts off with the major scale starting at `root`, then modifies the scale degrees according to the mode if necessary.
    """
    C_MAJOR: list[str] = ["C", "D", "E", "F", "G", "A", "B"]

    num_vorzeichen: int
    vorzeichen: str
    num_vorzeichen, vorzeichen = MAJOR_KEY_SIGNATURES[root]

    # sharps start at F#, flats at Bb
    vorzeichen_starting_index: int = 3 if vorzeichen == "#" else 6

    PERFECT_FIFTH: wholetones = 4
    PERFECT_FOURTH: wholetones = 3
    OCTAVE: wholetones = 7

    vorzeichen_interval = PERFECT_FIFTH if vorzeichen == "#" else PERFECT_FOURTH
    scale = C_MAJOR.copy()
    for i in range(num_vorzeichen):
        scale[(vorzeichen_starting_index + (i * vorzeichen_interval)) % OCTAVE] += vorzeichen

    root_index: int = scale.index(root)
    scale = scale[root_index:] + scale[:root_index]

    return _apply_mode_to_scale(scale, mode)


def get_random_chord():
    letters: list[str] = ["C", "D", "E", "F", "G", "A", "B"]
    qualities: list[str] = ["maj7", "min7", "7", "dim7", "m7b5"]
    incidentals: list[str] = ["#", "b", ""]
    chord: str = random.choice(letters) + random.choice(incidentals) + random.choice(qualities)
    return chord


def get_chord_quality_of_scale_degree(scale_degree: int, mode: Mode = Mode.ionian) -> str:
    """0-based scale_degree! Not 1-based like in convention in music theory"""

    # semitone intervals from the root, starting with the root
    MAJOR_SCALE: list[semitones] = [0, 2, 4, 5, 7, 9, 11]

    mode_scale: list[semitones] = MAJOR_SCALE.copy()

    OCTAVE: wholetones = 7

    for i in range(len(mode_scale)):
        # apply mode semitone deltas to the major scale
        mode_scale[i] += mode.value[i % OCTAVE]

    third_index: int = scale_degree + 2
    fifth_index: int = scale_degree + 4
    seventh_index: int = scale_degree + 6
    third: semitones = (
        (third_index // 7) * 12 + mode_scale[(third_index) % OCTAVE] - mode_scale[scale_degree]
    )
    fifth: semitones = (
        (fifth_index // 7) * 12 + mode_scale[(fifth_index) % OCTAVE] - mode_scale[scale_degree]
    )
    seventh: semitones = (
        (seventh_index // 7) * 12 + mode_scale[(seventh_index) % OCTAVE] - mode_scale[scale_degree]
    )

    MINOR_THIRD: semitones = 3
    MAJOR_THIRD: semitones = 4
    PERFECT_FIFTH: semitones = 7
    AUGMENTED_FIFTH: semitones = 8
    DIMINISHED_FIFTH: semitones = 6
    MAJOR_SEVENTH: semitones = 11
    MINOR_SEVENTH: semitones = 10
    DIMINISHED_SEVENTH: semitones = 9

    chord_quality: str = ""

    if third == MAJOR_THIRD:
        if fifth == AUGMENTED_FIFTH:
            chord_quality += "aug"

        if seventh == MAJOR_SEVENTH:
            chord_quality += "maj7"
        elif seventh == MINOR_SEVENTH:
            chord_quality += "7"
    if third == MINOR_THIRD:
        if fifth == PERFECT_FIFTH:
            chord_quality += "min"
            if seventh == MAJOR_SEVENTH:
                chord_quality += "maj7"
            elif seventh == MINOR_SEVENTH:
                chord_quality += "7"

        elif fifth == DIMINISHED_FIFTH:
            if seventh == MINOR_SEVENTH:
                chord_quality = "m7b5"
            elif seventh == DIMINISHED_SEVENTH:
                chord_quality = "dim7"

    return chord_quality


def tts(message: str) -> None:
    voice = PiperVoice.load("./en_US-hfc_female-medium.onnx")
    with wave.open(filename := "temp.wav", "wb") as wav_file:
        voice.synthesize_wav(message, wav_file)

    os.system(f"paplay {filename}")


def pronounce_chord(chord: str) -> None:
    chord_pronouncable = (
        chord.replace("A", "A-")
        .replace("#", " sharp")
        .replace("b", " flat")
        .replace("min", " minor")
        .replace("maj", " major")
        .replace("dim", " diminished")
        .replace("m7 flat5", " half-diminished")
        .replace("aug", " augmented")
        .replace("7", " seven")
    )
    tts(chord_pronouncable)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Random Chord Generator",
        description="Generates a random chord for practicing chord voicings",
    )
    parser.add_argument(
        "-r",
        "--root",
        type=str,
        default=None,
        help="Scale root. When left empty, chords are generated chromatically instead of diatonically.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="major",
        help="Desired mode. Requires passing a `--root`. Includes `major` and `minor` and the 7 church modes.",
    )
    parser.add_argument("-s", "--seconds", type=float, default=3, help="Time to play the chord")
    args = parser.parse_args()

    if args.root:
        scale: list[str] = get_scale(root=args.root.upper(), mode=(mode := Mode[args.mode]))

        last_scale_degree: int = -1

        while True:
            scale_degree = random.choice(range(len(scale)))

            if scale_degree == last_scale_degree:
                continue

            question: str = f"{scale_degree + 1} of {args.root} {args.mode}"
            print(question)
            tts(question)
            time.sleep(args.seconds)

            chord = scale[scale_degree] + get_chord_quality_of_scale_degree(
                scale_degree=scale_degree, mode=mode
            )
            print(chord)
            pronounce_chord(chord)
            time.sleep(args.seconds / 2)

            last_scale_degree = scale_degree

    else:
        last_chord: str = ""

        while True:
            chord: str = get_random_chord()
            if chord == last_chord:
                continue

            print(chord)
            pronounce_chord(chord)
            time.sleep(args.seconds)

            last_chord = chord
