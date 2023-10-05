
# 故障した場合

### 本体などのハードが損傷した場合
　Raspberry Pi本体が壊れた場合は、同じバージョンのRaspberry Pi Zero Wであれば、micro SDを付け直すだけで問題ない。もし廃版になるなどで新しいバージョン（例: `Raspberry Pi Zero 2 W`）を使う必要がある時は、後述の`導入手順（フルバージョン）`に従ってソフトも入れ直す必要がある。

　本体に接続している各種コンポーネントが壊れた場合は、以下の部品を必要数用意し、予備の基板に実装あるいは接続する。　
 部品名 | 個数 | メモ
:---- |:----:| :----
 [M5Stack用WS1850S搭載 RFID 2ユニット](https://www.switch-science.com/products/8301) | 1 | - 
 カーボン抵抗6.8KΩ | 2 | - 
 1N4007 | 1 | - 
 2SC1815 | 1 | -
 ピンヘッダ (20x2) | 1 | 20x1を2個でもよい
 [電子ブザー 12mm UDP-05LFPN](https://akizukidenshi.com/catalog/g/gP-09704/) | 1 | -
 [5V小型リレー 接点容量: 2A 946H-1C-5D](https://akizukidenshi.com/catalog/g/gP-07342/) | 1 | -
 [2色LED 赤・黄緑5mm カソードコモン](https://akizukidenshi.com/catalog/g/gI-06314/) | 1 | -
 [基板取付用LANコネクタ(モジュラージャック)(RJ-45)](https://akizukidenshi.com/catalog/g/gC-00159/) | 1 | 高さ調整のため、リーダー側には取り付けない。またピンの幅が若干狭いので、ピンの先をペンチなどで少し折り曲げてから取り付けること。 

※予備の基板が無い場合は、本プロジェクト内にある`OfficeDoorManagement.zip`をダウンロードし、基板メーカーに注文すること。

# 導入手順（フルバージョン）

### 0. Raspberry Pi Zero W
　Raspberry Pi OS Liteを`Raspberry Pi Imager`などでmicro SDに書き込み、挿入する。

### 1. I2Cを有効化する
```sh
sudo raspi-config
```
`3 Interface Options`の`I5 I2C`を`Enable`にする。

### 2. 自動ドア認証と周辺プログラムをインストールする
```sh
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git pip libmagic1

pip install mfrc522_i2c rpi.gpio ipget websocket-server websockets questionary

git clone https://github.com/billw2/rpi-clone.git 
cd rpi-clone
sudo cp rpi-clone rpi-clone-setup /usr/local/sbin
cd ../

git clone https://github.com/Shintaro-My/rpi-rfid-test.git
cd rpi-rfid-test
chmod 755 task.sh && chmod 755 detect.sh && chmod 755 server.sh && chmod 755 shutdown.sh
cd ../
```

### 3. 自動実行のセットアップを行う

```sh
sudo nano /etc/rc.local
```
`exit 0`の直前にプログラムを実行するコマンドを記述する。
```sh
cd /home/pi/rpi-rfid-test
bash task.sh

exit 0
```

----

# RFID（RC522）についての備忘録

* 記録領域は計1024バイトで、0 - 15番までの計16個のセクターで分割されている。
* セクターはそれぞれ64バイトで、さらに0 - 3番までの計4個（各16バイト）のブロックで分割されている。
* ブロックが基本的なデータ保存単位になるため、16バイトを超えるデータを記録する場合は複数回に分けて保存する必要がある。
* セクター0の0番目のブロックは、RFIDの識別に用いられるため、書き込み不可。
* 全セクターの3番目のブロックは、セクターの管理に用いられるため、書き込み不可。書き込むとそれ以降のセクターも壊れる。
  * セクター2の管理ブロックに謝って書き込み、セクター0と1しか使えなくなったRFタグがある。
* 基本的には0番（セクター0は除く）と1・2番ブロックに書き込みが可能なので、実質的な記憶領域は752バイトである。
* ここまでに出てきたセクターという区分は説明を容易にするためのものであり、実際にはブロックの区分しかない。
  * 0 - 63番のブロック。「セクター2の0番目のブロック」は8番ブロック（4 * 2 + 0）ということになる。
* ここまでの説明はあくまで考察の域を出ないものであるので、使用する前に記録領域の全読み出しをするべき。

# ~~自動起動~~
*  ~~`/home/pi/.config/lxsession/LXDE-pi/autostart`に、`lxterminal -e [app_dir]/autostart.sh`を追記する。~~
  * ~~事前にシェルスクリプトは`chmod 755 [app_dir]/autostart.sh`で実行権限を渡しておく。~~
