
# 故障した場合

### 本体などのハードが損傷した場合
　Raspberry Pi本体が壊れた場合は、同じバージョン（`Raspberry Pi Zero W`あるいは`WH`）であれば、micro SDを付け直すだけで問題ない。もし廃版になるなどで新しいバージョン（例: [`Raspberry Pi Zero 2 W`](https://www.switch-science.com/products/7600)）を使う必要がある場合は、後述の[ソフト導入手順](#ソフト導入手順)に従ってソフトも入れ直す必要がある。

　本体に接続している各種コンポーネントが壊れた場合は、以下の部品を必要数用意し、予備の基板に実装あるいは接続する。　
 部品名 | 個数 | メモ
:---- |:----:| :----
 [M5Stack用WS1850S搭載 RFID 2ユニット](https://www.switch-science.com/products/8301) | 1 | - 
 [電子ブザー 12mm UDP-05LFPN](https://akizukidenshi.com/catalog/g/gP-09704/) | 1 | -
 [HY2.0mm 4Pソケット サイド型](https://www.amazon.co.jp/dp/B09CP5K8XT) | 1 | -
 [5V小型リレー 接点容量: 2A 946H-1C-5D](https://akizukidenshi.com/catalog/g/gP-07342/) | 1 | -
 [2色LED 赤・黄緑5mm カソードコモン](https://akizukidenshi.com/catalog/g/gI-06314/) | 1 | -
 1N4007 | 1 | リレーの逆起電力対策。向きに注意。 
 2SC1815 | 1 | リレー駆動用のトランジスタ。
 カーボン抵抗6.8KΩ | 2 | - 
 ピンソケット (20x2) | 1 | 下向きに付けることに注意。はんだ付け後、飛び出したピンはなるべく短く切ること。線材のはんだ付けの位置を間違えないこと。
 [基板取付用LANコネクタ(モジュラージャック)(RJ-45)](https://akizukidenshi.com/catalog/g/gC-00159/) | 1 | 高さ調整のため、リーダー側には取り付けない。またピンの幅が若干狭いので、ピンの先をペンチなどで少し折り曲げてから取り付けること。 

※ 予備の基板が無い場合は、本プロジェクト内にある[`OfficeDoorManagement.zip`](/OfficeDoorManagement.zip?raw=1)をダウンロードし、基板メーカーに注文すること。

### ソフト（micro SD）が損傷した場合
　バックアップのmicro SDがある場合は差し直すだけでよい。バックアップが無い場合は、後述の[ソフト導入手順](#ソフト導入手順)に従って初期設定を行う。

　定期的にバックアップは行うこと。


# ソフト導入手順

### 0. Raspberry Pi Zero W
　`Raspberry Pi OS Lite`を[Raspberry Pi Imager](https://www.raspberrypi.com/software/)でmicro SDに書き込み、挿入する。ImagerのOS詳細設定でSSHを有効化しておく。Wi-Fiの設定も可能だが、IP固定はこの時点ではできないので、IP固定などを行わないと繋げられないWi-Fiの場合は設定しない。

> [!NOTE]
> * SSHを有効化する > パスワード認証を行う
> * ユーザー名: pi
> * パスワード: raspberry
>  * （絶対に忘れないように）
> * Wi-Fiを設定する
>  * Wi-Fiを使う国: JP

　「USB Type-Aのメス-メス変換器」と「USB Type-B to Aケーブル」を使うことで、本体にUSB機器を繋ぐことができる。普段はバックアップ用のmicro SDを繋いでおくが、こちらにキーボード、そしてmini HDMI端子を変換器越しにモニターに繋ぐことで、簡単に以下のセットアップが行える。

　事前にWi-Fiの設定が行えているのであれば、SSHでセットアップが行えるので、キーボードやモニターは不要となる。

> [!WARNING]
> IP固定を要するなどの理由よりこの時点でWi-Fi設定ができなかった場合、以下の手順でWi-Fiの手動設定を行う必要がある。
> 
> <details>
>   <summary>Wi-Fiの手動設定（ここをクリック）</summary>
> </details>

### 1. SSHとI2Cを有効化
```sh
sudo raspi-config
```
* `3 Interface Options`
  * `I2 SSH`を`Enable`にする。
  * `I5 I2C`を`Enable`にする。

### 2. 各種プログラムのインストールとセットアップ
```sh
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git python3-pip libmagic1

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

### 3. プログラムの自動実行セットアップ

```sh
sudo nano /etc/rc.local
```
`exit 0`の直前にプログラムを実行するコマンドを記述する。
```sh
cd /home/pi/rpi-rfid-test
bash task.sh

exit 0
```
※ `Ctrl+S`で保存、`Ctrl+X`でエディターを閉じる。

### 4. 本体設定ファイルの編集

```sh
sudo nano /boot/config.txt
```
末尾に以下の通りに書き込む。
```
dtoverlay=disable-bt
dtparam=act_led_gpio=27,act_led_trigger=heartbeat
```
* 未使用のBluetoothアダプタを停止（省電力化）。
* パイロットランプをGPIO27に割り振り、点灯条件を「起動中」に変更。

※ `Ctrl+S`で保存、`Ctrl+X`でエディターを閉じる。

### 5. Wi-Fiの設定

#### Wi-Fi接続情報ファイルを作成

```sh
cd rpi-rfid-test
python wpa_config.py <Wi-Fi_SSID_1> <PASSWORD_1> <Wi-Fi_SSID_2> <PASSWORD_2>
```
`python wpa_config.py`の後には`Wi-FiのSSID`・`Wi-Fiのパスワード`を半角スペースで区切って入力する。複数のWi-Fiと繋げる場合は、更に半角スペースを空けて続ける（例: `python wpa_config.py Buffalo-A-XXXX ABCD1234 elecom-XXXXXX AIUEO123`）。

#### Wi-Fi接続情報ファイルを所定の位置に配置

```sh
cat _temp.txt | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf
rm _temp.txt
```

#### （任意）IP固定化

```sh
sudo nano /etc/dhcpcd.conf
```
末尾に以下の通りに書き込む。
```
interface wlan0
```
その下に、以下の形式でIPを固定化したいWi-Fiの数だけ書き込む。

```
ssid <Wi-Fi_SSID>
static ip_address=192.168.XX.XXX/24
static routers=<IPv4のゲートウェイ>
static domain_name_servers=<DNSサーバー（優先）> <DNSサーバー（代替）>
```

例：
```
interface wlan0

ssid Buffalo-A-XXXX
static ip_address=192.168.10.111/24
static routers=192.168.10.2
static domain_name_servers=8.8.8.8 8.8.4.4

ssid elecom-XXXXXX
static ip_address=192.168.2.111/24
static routers=192.168.2.252
static domain_name_servers=200.230.230.5 220.110.130.250
```

※ `Ctrl+S`で保存、`Ctrl+X`でエディターを閉じる。


----
----

## （メモ）RFID（RC522）についての備忘録

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
