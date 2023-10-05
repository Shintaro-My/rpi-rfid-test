
# 導入手順

```sh
sudo raspi-config
```
`3 Interface Options`の`I5 I2C`を`Enable`にする。

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
