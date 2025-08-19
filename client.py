import grpc
import pyaudio # PyAudioをインポート
from proto import greeter_pb2
from proto import greeter_pb2_grpc

# ▼▼▼ マイクと音声データの設定 ▼▼▼
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 1024 # PyAudioで読み取るチャンクサイズ
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

def generate_audio_chunks():
    """マイクから音声を読み込み、チャンクごとにyieldするジェネレータ関数"""
    audio = pyaudio.PyAudio()
    
    # マイク入力用のストリームを開く
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)
    
    print("マイク入力のストリーミングを開始しました... (Ctrl+Cで終了)")
    
    try:
        while True:
            # マイクから音声データを読み取る
            data = stream.read(CHUNK_SIZE)
            # 読み取ったデータをAudioChunkメッセージとしてyieldする
            yield greeter_pb2.AudioChunk(data=data)
            
    except KeyboardInterrupt:
        # Ctrl+Cが押されたらループを抜ける
        print("ストリーミングを停止します。")
    finally:
        # ストリームとPyAudioをクリーンアップ
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("リソースを解放しました。")


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = greeter_pb2_grpc.GreeterStub(channel)
        
        print("音声ストリーミングを開始します...")
        
        # マイク入力用のジェネレータを渡してStreamAudioメソッドを呼び出す
        audio_generator = generate_audio_chunks()
        response = stub.StreamAudio(audio_generator)
        
        print("\nサーバーからの応答:")
        print(f"  - ステータス: {response.status}")
        print(f"  - 受信合計バイト数: {response.received_bytes}")

if __name__ == '__main__':
    run()