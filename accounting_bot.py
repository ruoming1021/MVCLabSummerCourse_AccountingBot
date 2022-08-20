import os
import re
import json
import random
from dotenv import load_dotenv
from pyquery import PyQuery
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from influxdb import InfluxDBClient
class DB():
    def __init__(self, ip, port, user, password, db_name):
        self.client = InfluxDBClient(ip, port, user, password, db_name)
        print('Influx DB init.....')

    def insertData(self, data):
        """
        [data] should be a list of datapoint JSON,
        "measurement": means table name in db
        "tags": you can add some tag as key
        "fields": data that you want to store
        """
        if self.client.write_points(data):
            return True
        else:
            print('Falied to write data')
            return False

    def queryData(self, query):
        """
        [query] should be a SQL like query string
        """
        return self.client.query(query)
    def delete(self):
        return self.client.query('drop measurement accounting_items')
        #return self.client.query('drop measurement accounting_items where \"time\" == \'2022-08-19T16:34:54.769434Z\' ') 
# Init a Influx DB and connect to it
db = DB('0.0.0.0', 8086, 'root', '', 'accounting_db')

load_dotenv()


CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

app = FastAPI()

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

'''
For first testing, you can comment the code below after you check your linebot can send you the message below
'''
CHANNEL_ID = os.getenv('LINE_UID')
my_event = ['#anya','#math','#note', '#report','#delete','#sum']
my_emoji = [
    [{'index':0, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'042'}],
    [{'index':0, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'054'}],
    [{'index':0, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'087'}]
]
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    recieve_message = str(event.message.text).split(' ')
    case_ = recieve_message[0].lower().strip()
    print("re_message = ",recieve_message)
    print("case_ = ",case_)
    if re.match(my_event[0], case_):
        id = random.randint(1, 40)
        url = f"https://spy-family.net/assets/img/special/anya/{id}.png"
        My_LineBotAPI.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
        )
    elif re.match(my_event[1], case_):
        #message = TextSendMessage(text= event.message.text)
        #num = re.sub('[a-zA-z!@#$%^&_= ]','',message.text)
        #if num.find("+")+1 >len(num)-1 or num.find("-")+1 >len(num)-1 or num.find("*")+1 >len(num)-1 or num.find("/")+1 >len(num)-1:    
        message = ''
        for i in range(1,len(recieve_message)):
            message = message +  recieve_message[i]
        print("#############",message)
        if re.findall('[a-zA-z!@#$%^&_]',message):
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text = "輸入包含非數值!!")
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text = eval(str(message)))
            )
    elif re.match(my_event[2], case_):
        # cmd: #note [事件] [+/-] [錢]
        if len(recieve_message) != 4:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text = "輸入格式錯誤!!")
            )
            return
        event_ = recieve_message[1]
        op = recieve_message[2]
        money = int(recieve_message[3])
        # process +/-
        if op == '-':
            money *= -1
        # get user id
        user_id = event.source.user_id

        # build data
        data = [
            {
                "measurement" : "accounting_items",
                "tags": {
                    "user": str(user_id),
                    # "category" : "food"
                },
                "fields":{
                    "event": str(event_),
                    "money": money
                }
            }
        ]
        if db.insertData(data):
            # successed
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Write to DB Successfully!"
                )
            )
    elif re.match(my_event[3], case_):
        # get user id
        user_id = event.source.user_id
        query_str = """
        select * from accounting_items 
        """
        result = db.queryData(query_str)
        print("################",result)
        points = result.get_points(tags={'user': str(user_id)})
        reply_text = ''
        for i, point in enumerate(points):
            time = point['time']
            event_ = point['event']
            money = point['money']
            reply_text += f'[{i}] -> [{time}] : {event_}   {money}\n'
        if len(reply_text) > 0:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply_text
                )
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="No data"
                )
            )
    elif re.match(my_event[4], case_):
        delete_ = recieve_message[1]
        #print("############",delete_)
        if delete_ == 'all':
            db.delete()
            #delete  all successed
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text= "Delete All Successfully"
                )
            )
        else:
            user_id = event.source.user_id
            query_str = """
            select * from accounting_items
            """
            result = db.queryData(query_str)
            points = result.get_points(tags={'user': str(user_id)})
            temp_time = []
            for i, point in enumerate(points):
                print("---------------------------------",i,point)
                del_item = point['time']
                temp_time.append(del_item)
                if i == int(delete_):
                    output = point['event']
                #if str(i) == delete_: #
                    #del_item = point['time']
                    #print("############",del_item)
                    #del_time = del_item.split('.')
            #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",temp_time[0])
            if int(delete_) == 0:
                db.queryData(f"DELETE FROM accounting_items WHERE time < '{temp_time[int(delete_)+1]}' - 1ms")
            elif int(delete_) == len(temp_time)-1:
                db.queryData(f"DELETE FROM accounting_items WHERE time > '{temp_time[int(delete_)-1]}' + 1ms")
            else:
                db.queryData(f"DELETE FROM accounting_items WHERE time > '{temp_time[int(delete_)-1]}' + 1ms and time < '{temp_time[int(delete_)+1]}' - 1ms")

            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text= f"Delete {output} Successfully"
                )
            )
    elif re.match(my_event[5],case_):
        #answer = db.queryData("SELECT sum(money) FROM accounting_items WHERE time > now() - 1d")
        query_str = """
            select * from accounting_items where time > now() - 1d 
        """
        user_id = event.source.user_id
        #points_sum = answer.get_points(tags={'user': str(user_id)})
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        temp_m = []
        for i, point in enumerate(points):
            del_item = point['money']
            temp_m.append(del_item)
        total = 0
        for i in temp_m:
            total += i
        My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text= f"今天共花費 : {total} 元"
                )
            )
    else:
        # Unkown command
        reply_emoji = random.choice(my_emoji)
        command_describtion = '$ Use command #anya , #math , #note , #report , #delete'
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=command_describtion,
                emojis=reply_emoji
            )
        )

class My_Sticker:
    def __init__(self, p_id: str, s_id: str):
        self.type = 'sticker'
        self.packageID = p_id
        self.stickerID = s_id

my_sticker = [My_Sticker(p_id='446', s_id='1995'), My_Sticker(p_id='446', s_id='2012'),
     My_Sticker(p_id='446', s_id='2024'), My_Sticker(p_id='446', s_id='2027'),
     My_Sticker(p_id='6325', s_id='10979923'), My_Sticker(p_id='789', s_id='10877'),
     My_Sticker(p_id='6362', s_id='11087938'), My_Sticker(p_id='789', s_id='10885'),
     My_Sticker(p_id='6136', s_id='10551391'),
     ]

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    # Random choice a sticker from my_sticker list
    ran_sticker = random.choice(my_sticker)
    # Reply Sticker Message
    My_LineBotAPI.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id= ran_sticker.packageID,
            sticker_id= ran_sticker.stickerID
        )
    )



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='count:app', reload=True, host='0.0.0.0', port=1234)