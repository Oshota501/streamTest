# 導入
- Geminiの生成してくれた構文をコピペしたら上手いこと言ったので紹介します。多少私が手作業で修正しています。
- geminiのプロンプトは次を参照してください。[こちら](https://g.co/gemini/share/e605e7942d2a)

```zsh
git clone https://github.com/Oshota501/streamTest.git
# 仮想環境を作ります。使うライブラリは頑張って解読してください。
python3 -m venv venv
source venv/bin/activate
pip install grpcio grpcio-tools


pip3 install numpy
# homebrewはmacのみだったりするので気をつけてください。OSに合わせてください。
brew install portaudio
pip3 install pip
pip install pyaudio
pip3 install websockets

#　以下サーバーのみ実装でOK

pip install git+https://github.com/openai/whisper.git
brew install protobuf
brew install ffmpeg
#　ここでffmpegの実装方法はOSによって異なります。以下を参照してください。
# https://github.com/openai/whisper/blob/main/README.md
# 多分真ん中くらいにinstallの一覧表みたいなんがあります。

# Goモジュールを初期化
go mod init grpc-go-python

# 必要なライブラリをインストール
go get google.golang.org/grpc
# go get google.golang.org/protobuf/cmd/protoc-gen-go
# go get google.golang.org/grpc/cmd/protoc-gen-go-grpc
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2
```
.zshrcファイルを開いてpathを通してください。
PATHはターミナルで`go env GOPATH `と打ってでたPATHに/binを加えてください。
```zsh
export PATH="$PATH:YOUR_GO_BIN_PATH"
```
## APIの修正
proteを変更した場合には以下をターミナルの(venv)ディレクトリ内で実行する必要がある。
```zsh
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/greeter.proto
```
またgoについてもコードを生成しなければならないので
```zsh
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    proto/greeter.proto
```

# 技術
- ゴローチン処理
  - goの機能を使って並列処理を実現しています。
  - [whisper.py](/whisper_server.py)で処理が滞ることを想定しています。
  - server関数内の以下の処理のmax_workersを変更するとスレッド数を増やせます。
  - `server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))`
- Protocol Buffers
  - [greeter.proto](/proto/greeter.proto)　ファイルを参照してください
---
- [x] whisperの文字起こし機能
- [x] goでの書き換えの実現
- [ ] サーバー構築（ビルド）
- [ ] raspberryPI
# 起動について
お使いの端末で使用するにはターミナルを3つ同時に起動する必要があります。
---
## client
- raspberryPIで実行する処理
```zsh
source venv/bin/activate
python3 client.py
```
---
## server
ターミナルその①
```zsh
python3 whisper_server.py
```
ターミナルその②
```zsh
cd /server
go main.go
```