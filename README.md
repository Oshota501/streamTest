# 今適当に書いたのでもしかしたら間違っているかも...
```zsh
git clone https://github.com/Oshota501/streamTest.git
# 仮想環境を作ります。使うライブラリは頑張って解読してください。
python3 -m venv .venv
source .venv/bin/activate

pip3 install numpy
# homebrewはmacのみだったりするので気をつけてください。OSに合わせてください。
brew install portaudio
pip3 install pip
pip install pyaudio
pip3 install websockets

#　ここからWhisperを実装。サーバーのみ実装でOK
pip install git+https://github.com/openai/whisper.git
brew install ffmpeg
#　ここでffmpegの実装方法はOSによって異なります。以下を参照してください。
# https://github.com/openai/whisper/blob/main/README.md
# 多分真ん中くらいにinstallの一覧表みたいなんがあります。
```
---
# 起動について
二つターミナル開いてそれでそれぞれ仮想環境に入ってserver.pyとclient.pyを起動してください。これはラズパイを使うと**client.pyサイドがラズパイ**で処理する環境ということにするつもりです。
