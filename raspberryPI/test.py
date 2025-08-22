from adafruit_rgb_display.ili9341 import ILI9341

from busio import SPI
from digitalio import DigitalInOut
import board

from PIL import Image, ImageDraw, ImageFont

# ピンの構成
cs_pin = DigitalInOut(board.D2)
dc_pin = DigitalInOut(board.D24)
rst_pin = DigitalInOut(board.D23)

# SPIバスを設定
spi = SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# ILI9341ディスプレイのインスタンスを作成
disp = ILI9341(
    spi,
    cs=cs_pin, dc=dc_pin, rst=rst_pin,
    width=240, height=320,
    rotation=90,
    baudrate=24000000
)

# イメージサイズを定義
IMAGE_SIZE = (disp.height, disp.width)

# フォントを定義
FONT_NOTO = ImageFont.truetype("NotoSansCJK-Regular.ttc", 18)

# 色を定義
COLOR_WHITE = (255, 255, 255)

# 黒背景を作成
image = Image.new("RGB", IMAGE_SIZE, (0, 0, 0))

# テキストを描画
draw = ImageDraw.Draw(image)
text = """\
こんにちは
私はRaspberry Piです!
"""
for i, line in enumerate(text.split("\n")):
    draw.text((0, 24*i), line, font=FONT_NOTO, fill=COLOR_WHITE)

# ディスプレイに表示
disp.image(image)