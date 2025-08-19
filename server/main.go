package main

import (
	"bytes"
	"context"
	"io"
	"log"
	"net"
	"time"

	pb "grpc-go-python/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// 音声プロパティの定義 (Pythonクライアントと合わせる)
const (
	sampleRate      = 44100
	channels        = 1
	bitDepth        = 2 // 16-bit PCM = 2 bytes
	bufferSeconds   = 6
	bytesPerSecond  = sampleRate * channels * bitDepth
	bufferThreshold = bytesPerSecond * bufferSeconds
)

type server struct {
	pb.UnimplementedGreeterServer
}

func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	return &pb.HelloReply{Message: "Hello, " + in.GetName()}, nil
}

func (s *server) StreamAudio(stream pb.Greeter_StreamAudioServer) error {
	log.Println("音声ストリームの受信を開始しました。")
	var audioBuffer bytes.Buffer

	for {
		chunk, err := stream.Recv()
		if err == io.EOF {
			// ストリーム終了時、残りのバッファがあれば処理
			if audioBuffer.Len() > 0 {
				go sendToWhisperServer(audioBuffer.Bytes())
			}
			return stream.SendAndClose(&pb.AudioReply{Status: "Stream finished"})
		}
		if err != nil {
			log.Printf("ストリーム受信中にエラー発生: %v", err)
			return err
		}

		audioBuffer.Write(chunk.GetData())

		// バッファが6秒分溜まったかチェック
		if audioBuffer.Len() >= bufferThreshold {
			log.Printf("バッファが6秒分 (%d バイト) 溜まりました。Whisperサーバーに送信します。", audioBuffer.Len())

			// Whisperサーバーへの送信処理をゴルーチンで非同期に実行
			go sendToWhisperServer(audioBuffer.Bytes())

			// バッファをリセット
			audioBuffer.Reset()
		}
	}
}

// Whisperサーバーに音声データを送信する関数
func sendToWhisperServer(data []byte) {
	// gRPCクライアントとしてWhisperサーバーに接続
	conn, err := grpc.Dial("localhost:50052", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Printf("Whisperサーバーへの接続に失敗: %v", err)
		return
	}
	defer conn.Close()

	client := pb.NewTranscriberClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*30) // タイムアウト設定
	defer cancel()

	// AudioDataメッセージを作成して送信
	req := &pb.AudioData{
		Data:     data,
		Format:   8, // pyaudio.paInt16
		Channels: channels,
		Rate:     sampleRate,
	}

	res, err := client.Transcribe(ctx, req)
	if err != nil {
		log.Printf("文字起こしリクエストに失敗: %v", err)
		return
	}

	log.Printf("Whisperサーバーからの応答: %s", res.GetText())
	// res.GetText()でwhisperからの応答が得られます
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("ポートのリッスンに失敗: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	log.Printf("Goサーバーがポート 50051 で待機中...")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("サーバーの起動に失敗: %v", err)
	}
}
