import grpc
from concurrent import futures
import wave
import whisper
import pyaudio # get_sample_sizeのため

from proto import greeter_pb2
from proto import greeter_pb2_grpc

class TranscriberService(greeter_pb2_grpc.TranscriberServicer):
    def __init__(self):
        self.model = whisper.load_model("base")
        self.p_audio = pyaudio.PyAudio() # PyAudioを初期化
        print("文字起こし。")

    def Transcribe(self, request, context):
        
        # 受信した音声データをWAVファイルとして保存
        wav_file_path = "temp_audio_for_whisper.wav"
        with wave.open(wav_file_path, 'wb') as wf:
            wf.setnchannels(request.channels)
            wf.setsampwidth(self.p_audio.get_sample_size(request.format))
            wf.setframerate(request.rate)
            wf.writeframes(request.data)
        
            #self.play_audio(wav_file_path)
        # Whisperで文字起こし
        result = self.model.transcribe(wav_file_path, fp16=False, language="ja")
        transcribed_text = result["text"]
        
        print(f" {transcribed_text}")
        
        # 結果をGoサーバーに返す
        return greeter_pb2.TranscriptionReply(text=transcribed_text)
        
    def play_audio(self, file_path):
        """指定されたWAVファイルを再生する関数"""
        print(f"受信した音声ファイル ({file_path}) を再生します...")
        try:
            wf = wave.open(file_path, 'rb')
            stream = self.p_audio.open(
                format=self.p_audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            chunk = 1024
            data = wf.readframes(chunk)
            while data:
                stream.write(data)
                data = wf.readframes(chunk)

            stream.stop_stream()
            stream.close()
            print("再生が完了しました。")
        except Exception as e:
            print(f"音声の再生中にエラーが発生しました: {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_TranscriberServicer_to_server(TranscriberService(), server)
    server.add_insecure_port('[::]:50052') # ★ Goサーバーとは別のポートで待機
    print("Whisperサーバーがポート 50052 で待機中です。")
    server.start()
    server.wait_for_termination()
    

if __name__ == '__main__':
    serve()
    