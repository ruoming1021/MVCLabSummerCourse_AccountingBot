# MVCLabSummerCourse_AccountingBot

### Install InfluxDB(1.X) with apt

    sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
    sudo echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
    sudo apt update
    sudo apt install influxdb

### Start InfluxDB service

    sudo systemctl enable influxdb
    sudo systemctl start influxdb
    sudo service influxdb start

### How to run
* **Step 1: Install Python Packages**
    * > pip install -r requirements.txt
* **Step 2: Editing `.env.sample` and save as `.env`**

You should not let people know your  LINE_TOKEN,LINE_SECRET,LINE_UID 


    LINE_TOKEN = Your Line Token
    LINE_SECRET = Your Line Secret
    LINE_UID = Your Line UID

* **Step 3: Run ngrok**
    * > ngrok http 1234
* **Step 4: Webhook settings (you should setting everytime when you run ngrok)**

![未命名](https://user-images.githubusercontent.com/43459716/185759616-ece8b044-ebcf-4389-8dfd-bcd84141f2b5.png)

* **Step 5: Run `accounting_bot.py`**
    * The port used in main.py is '1234'
    * > python3 accounting_bot.py


### Function
- command
  - `#anya`                                      -> Random AnyaImage
  - `#math [a] [+-*/] [b] (a,b can be negative)` -> 四則運算
  - `Sticker` ->                                 -> Random sticker
  - `#note [事件] [+/-] [錢]`                     -> 新增記帳資料
  - `#report`                                    -> 顯示目前記帳資料
  - `#delete [i]`                                -> 刪除第i筆資料
  - `#sum`                                       -> 結算24小時前的帳
  
 
 
