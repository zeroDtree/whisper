from TTS.api import TTS
import torch

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cpu"

""" List available 🐸TTS models"""
# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# generate speech by cloning a voice using default settings
speaker_wav = "xinwen.wav"
tts.tts_to_file(
    text="我花了很长时间才开发出声音， 现在有了声音，我不会再沉默了。",
    file_path="output_" + speaker_wav,
    speaker_wav=speaker_wav,
    language="zh",
)
