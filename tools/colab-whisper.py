# Google Colab Whisper transcription script.
#
# Use when local Whisper is too slow on CPU - Colab's free tier gives you
# T4 GPU access. Paste each cell into a Colab notebook.
# (https://colab.research.google.com)

# Cell 1: Install dependencies
# !pip install openai-whisper

# Cell 2: Upload your video
# from google.colab import files
# uploaded = files.upload()

# Cell 3: Transcribe
# import whisper
# model = whisper.load_model("base")  # or "small" / "medium" / "large" with GPU
# result = model.transcribe(list(uploaded.keys())[0])

# Cell 4: Save flat transcript and download
# with open('transcript.txt', 'w', encoding='utf-8') as f:
#     f.write(result['text'])
# files.download('transcript.txt')

# Cell 5: (optional) Save timestamped transcript
# with open('transcript-with-timestamps.txt', 'w', encoding='utf-8') as f:
#     for seg in result['segments']:
#         f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}\n")
# files.download('transcript-with-timestamps.txt')
