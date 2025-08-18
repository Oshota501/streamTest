import numpy as np
import wave
import pyaudio
import socket
import threading

class MixedSoundStreamClient(threading.Thread):
    def __init__(self, server_host, server_port, wav_filename):
        threading.Thread.__init__(self)
        self.SERVER_HOST = server_host
        self.SERVER_PORT = int(server_port)
        self.WAV_FILENAME = wav_filename

    def run(self):
        audio = pyaudio.PyAudio()
        wav_file = wave.open(self.WAV_FILENAME, 'rb')

        FORMAT = pyaudio.paInt16
        WAV_CHANNELS = wav_file.getnchannels()
        RATE = wav_file.getframerate()
        CHUNK = 1024
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
                wav_data = wav_file.readframes(CHUNK)
                mic_data = mic_stream.read(CHUNK)
                if wav_data == b'':
                    wav_file.rewind()
                    wav_data = wav_file.readframes(CHUNK)
                mixed = self.mix_sound(wav_data, mic_data, MIC_CHANNELS, CHUNK, 0.5, 0.5)
                if mixed is not None:
                    sock.sendall(mixed)

        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()

    # サーバから受信した音声を再生
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

    def mix_sound(self, data1, data2, channels, frames_per_buffer, volume1, volume2):
        if volume1 + volume2 > 1.0:
            return None
        decoded_data1 = np.frombuffer(data1, np.int16).copy()
        decoded_data2 = np.frombuffer(data2, np.int16).copy()
        decoded_data1.resize(channels * frames_per_buffer, refcheck=False)
        decoded_data2.resize(channels * frames_per_buffer, refcheck=False)
        return (decoded_data1 * volume1 + decoded_data2 * volume2).astype(np.int16).tobytes()

if __name__ == '__main__':
    mss_client = MixedSoundStreamClient("localhost", 12345, "wavs/collectathon.wav")
    mss_client.start()
    mss_client.join()
