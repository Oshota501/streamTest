import wave
import sys

import pyaudio

CHUNK = 1024

if len(sys.argv) < 2:
    print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
    sys.exit(-1)

with wave.open(sys.argv[1], 'rb') as wf:
    # PyAudioをインスタンス化し、PortAudioシステムリソースを初期化する (1)
    p = pyaudio.PyAudio()

    # ストリームを開く (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # WAVEファイルのサンプルを再生する (3)
    while len(data := wf.readframes(CHUNK)):  # `:=`はPython 3.8 以降が必要 
        stream.write(data)

    # ストリームを閉じる (4)
    stream.close()

    # PortAudioシステムリソースを解放する (5)
    p.terminate()

