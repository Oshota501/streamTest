import pyaudio
import socket
import threading
import whisper
import wave
import numpy as np

class MixedSoundStreamServer(threading.Thread):
    def __init__(self, server_host, server_port):
        threading.Thread.__init__(self)
        self.SERVER_HOST = server_host
        self.SERVER_PORT = int(server_port)

    def run(self):
        audio = pyaudio.PyAudio()
        print("サーバーが起動するまでお待ちください。")
        print("Whisperモデルをロード中です... (base)")
        model = whisper.load_model("base")
        print("モデルのロードが完了しました。")
        # サーバーソケット生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind((self.SERVER_HOST, self.SERVER_PORT))
            print("サーバー起動")
            server_sock.listen(1)

            audio = pyaudio.PyAudio()
            audio_buffer = b'' # wavファイルに積み重ねるための変数
            loop_count = 0     # 何回分でひとまとまりにするかを処理するためのカウント

            # クライアントと接続
            client_sock, _ = server_sock.accept()
            with client_sock:
                print("接続検知")
                # クライアントからオーディオプロパティを受信
                settings_list = client_sock.recv(256).decode('utf-8').split(",")
                FORMAT = int(settings_list[0])
                CHANNELS = int(settings_list[1])
                RATE = int(settings_list[2])
                CHUNK = int(settings_list[3])

                # オーディオ出力ストリーム生成 
                stream = audio.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    output=True,
                                    frames_per_buffer=CHUNK)

                # メインループ
                while True:
                    # クライアントから音データを受信
                    data = client_sock.recv(CHUNK)
                    audio_buffer += data # バッファに音声データを溜める
                    loop_count += 1
                    # ここでwavを積み重ねる処理を書きます。
                    # (5秒 * 44100Hz) / 1024フレーム ≈ 215回
                    if loop_count >= 215:
                        print("バッファが溜まったので文字起こしを実行します...")
                        
                        # ★★★ ポイント1: WAVファイルとしてヘッダー付きで保存 ★★★
                        wav_file_path = "received_audio.wav"
                        with wave.open(wav_file_path, 'wb') as wf:
                            wf.setnchannels(CHANNELS)
                            wf.setsampwidth(audio.get_sample_size(FORMAT))
                            wf.setframerate(RATE)
                            wf.writeframes(audio_buffer)
                        
                        # Whisperで文字起こし
                        # fp16=FalseはCPUで動かす場合に推奨
                        result = model.transcribe(wav_file_path, fp16=False, language="ja")

                        if result["text"]:
                            print("-----------------------------------------")
                            print("文字起こし結果:", result["text"])
                            print("-----------------------------------------")

                        # バッファとカウンターをリセット
                        audio_buffer = b''
                        loop_count = 0
                    # 切断処理
                    if not data:
                        break

                    # オーディオ出力ストリームにデータ書き込み
                    stream.write(data)
    
        # 終了処理
        stream.stop_stream()
        stream.close()

        audio.terminate()

if __name__ == '__main__':
    mss_server = MixedSoundStreamServer("localhost", 12345)
    mss_server.start()
    mss_server.join()

