import numpy as np
import wave
import pyaudio
import socket
import threading

class MixedSoundStreamClient(threading.Thread):
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 12345
    def a ():
        __path__
    # wav_filenameは不要になったので、コンストラクタから削除
    def __init__(self, server_host=None, server_port=None):
        threading.Thread.__init__(self)

        
        # 引数が指定されていればその値を、なければクラス変数のデフォルト値を使用
        self.SERVER_HOST = server_host if server_host is not None else self.DEFAULT_HOST
        self.SERVER_PORT = int(server_port) if server_port is not None else self.DEFAULT_PORT
        # self.WAV_FILENAME = wav_filename # 不要

    def run(self):
        audio = pyaudio.PyAudio()
        # wav_file = wave.open(self.WAV_FILENAME, 'rb') # 不要

        FORMAT = pyaudio.paInt16
        # WAV_CHANNELS = wav_file.getnchannels() # 不要
        RATE = 44100  # 一般的なレートに固定 (WAVファイルに依存しないように)
        CHUNK = 4096
        MIC_CHANNELS = 1

        mic_stream = audio.open(format=FORMAT,
                            channels=MIC_CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # サーバに接続
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.SERVER_HOST, self.SERVER_PORT))

            # サーバにオーディオプロパティを送信
            sock.send("{},{},{},{}".format(FORMAT, MIC_CHANNELS, RATE, CHUNK).encode('utf-8'))

            # 受信再生スレッドを起動
            playback_thread = threading.Thread(target=self.playback_stream, args=(audio, sock, FORMAT, MIC_CHANNELS, RATE, CHUNK))
            playback_thread.daemon = True
            playback_thread.start()

            # メインループ（送信）
            while True:
                # wav_data = wav_file.readframes(CHUNK) # 不要
                mic_data = mic_stream.read(CHUNK)
                # if wav_data == b'': # 不要
                #     wav_file.rewind() # 不要
                #     wav_data = wav_file.readframes(CHUNK) # 不要
                
                # ミキシング処理をせず、マイクのデータを直接送信する
                # mixed = self.mix_sound(wav_data, mic_data, MIC_CHANNELS, CHUNK, 0.5, 0.5) # 不要
                if mic_data is not None:
                    sock.sendall(mic_data) # mic_dataを直接送信

        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()

    # サーバから受信した音声を再生 (この関数は変更なし)
    def playback_stream(self, audio, sock, format, channels, rate, chunk):
        stream = audio.open(format=format,
                            channels=channels,
                            rate=rate,
                            output=True,
                            frames_per_buffer=chunk)
        try:
            while True:
                data = sock.recv(chunk * 2)  # 16bit=2byte
                if not data:
                    break
                stream.write(data)
        finally:
            stream.stop_stream()
            stream.close()

    # mix_sound関数は使わなくなったので、削除してもOK
    # def mix_sound(self, data1, data2, channels, frames_per_buffer, volume1, volume2):
    #     ...

if __name__ == '__main__':
    # "wavs/collectathon.wav"を渡す必要がなくなった
    mss_client = MixedSoundStreamClient()
    mss_client.start()
    mss_client.join()
