# Jazz Piano Practice Scripts

Some dumb little script(s) I wrote to help me practice jazz piano.
Might make a proper front-end at some point if I'm feeling cute.
Wanted to learn some front-end anyway.

## Chord Generator

This script produces text-to-speech (TTS) of chord names, either from a specific
scale, or just chromatic chords, so that I can practice finding chord voicings
on the piano more quickly.

The script has two use cases at the moment:

1. Generate random chromatic chords
2. Generate random chords from a specific key/scale/mode

For the TTS library, I chose [`piper-tts`](https://github.com/OHF-Voice/piper1-gpl)
because it sounds good enough, it's light-weight and actively developed
(unlike Coqui TTS) and it's offline, free and thus not susceptible to API rate limits
(unlike Google TTS and other AI-based cloud-hosted solutions).

### Setup

1. Clone this repo
2. Download a TTS voice to the repo's root by following [`piper-tts`'s Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md). I recommend `en_US-hfc_female-medium`:

   ```bash
   uv run -m piper.download_voices en_US-hfc_female-medium
   ```

   or if you don't use `uv` (you should), optionally set up a virtual
   environment and run

   ```bash
   pip install piper-tts
   python3 -m piper.download_voices en_US-hfc_female-medium
   ```

### Usage

```bash
uv run chord_generator.py
```

or

```bash
python chord_generator.py
```

- Optional CLI arguments
  - `-h`/`--help`: Show help about these CLI arguments
  - `-r`/`--r`: Root of the scale you want to practice. If left empty, chords
    are generated chromatically instead of diatonic to a key.
  - `-m`/`--mode`: Mode/scale you want to practice. Includes the seven
    church modes, as well as `major`, `minor`, `melodic_minor` and `harmonic_minor`.
    Requires `--root`.
  - `-s`/`--seconds`: How many seconds to wait before generating the next chord.
