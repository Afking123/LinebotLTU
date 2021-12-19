from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from .scraper import rent591
from math import radians, cos, sin, asin, sqrt
import pymysql
import pymysql.cursors
import numpy as np

def haversine(lon1, lat1, lon2, lat2):#計算距離的函式,經度lon,緯度lat
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def bodymessage(landlord,ping,rent,tel,address):
    k=('''{
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "'''+landlord+'''",
            "weight": "bold",
            "size": "xl",
            "margin": "lg"
          },
          {
            "type": "text",
            "text": "[坪數] '''+ping+'''",
            "margin": "sm",
            "weight": "regular",
            "style": "normal",
            "decoration": "none",
            "color": "#7F7F7F"
          },
          {
            "type": "text",
            "text": "[房租] '''+rent+'''",
            "color": "#7F7F7F"
          },
          {
            "type": "text",
            "text": "[電話] '''+tel+'''"
          },
          {
            "type": "text",
            "text": "[地址] '''+address+'''",
            "color": "#575555"
          },
          {
            "type": "separator",
            "color": "#696969"
          },'''
    )
    return k
def flexmessageframe(text1,text2):
    z=('''{
            "type": "bubble",
            "body": '''+
            text1.strip(',')+text2
            +'''
                ],
                "borderWidth": "bold",
                "cornerRadius": "none",
                "offsetTop": "none",
                "offsetBottom": "none",
                "offsetStart": "none",
                "paddingAll": "md",
                "paddingTop": "sm",
                "paddingBottom": "lg",
                "paddingStart": "md",
                "spacing": "none"
            }
        }'''
    )
    return z
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        print(body)
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent): # 如果有訊息事件
                if event.message.type=='location':#如果回傳為座標訊息
                    # get user lat and lon
                    ulat = event.message.latitude#lat緯度
                    ulon = event.message.longitude#lon經度
                    db = pymysql.connect(host='us-cdbr-east-04.cleardb.com', port=3306, user='b39d8fa6dd08de', passwd='e2b8b154', db='heroku_d34613fc10f0366', charset='utf8')
                    cursor = db.cursor()
                    cursor.execute("SELECT 房東姓名,坪數,房租,房東電話,租屋住址,經度E,緯度N FROM heroku_d34613fc10f0366.mapa")
                    row = cursor.fetchone()
                    page=0
                    list1=[]
                    i=0
                    text1=""
                    text2=""
                    while row: #判斷兩點距離若小於0.5km就將row資料存進list1
                        if haversine(ulon,ulat,row[5],row[6])<0.5:
                            list1.append(row)
                        row = cursor.fetchone()#使row輸出下一行資料列
                    a = np.array(list1)
                    list1len = a.shape[0]#list1len=list1有多少項目,int用來去小數點
                    if list1len == 0:
                        message=TextSendMessage(text='附近沒有租屋')
                    elif list1len >5:
                        while i<5:
                            text1=text1+bodymessage(list1[i][0],list1[i][1],list1[i][2],list1[i][3],list1[i][4])
                            i=i+1
                        message = FlexSendMessage(
                            alt_text='附近租戶',
                            contents=eval(flexmessageframe(text1,']}]}]}]}')),
                                quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="下一頁",text=('page,'+str(page+1)+','+str(ulon)+','+str(ulat))))])
                                )
                    else:
                        while i<list1len:
                            text1=text1+bodymessage(list1[i][0],list1[i][1],list1[i][2],list1[i][3],list1[i][4])
                            i=i+1
                        for l in range(list1len-1):
                                    text2=text2+']}'
                        message = FlexSendMessage(
                            alt_text='附近租戶',
                            contents=eval(flexmessageframe(text1,text2)),#可修改模組達到帶query 的 httprequest
                                quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="下一頁",text=('page,'+str(page+1)+','+str(ulon)+','+str(ulat))))])
                                )
                elif event.message.type=='text':#如果回傳為文字訊息
                    if event.message.text=="租屋地圖":
                        message = ImagemapSendMessage(
                        base_url='https://i.imgur.com/SwgBzhf.jpg',
                        alt_text='server_imagemap',
                        base_size=BaseSize(width=1353,height=718),
                        actions=[
                            URIImagemapAction(
                                link_uri="https://dashboard.heroku.com/",
                                area=ImagemapArea(
                                    x=359,y=359,width=676.5,height=359
                                )
                            ),
                            URIImagemapAction(
                                link_uri="https://developers.line.biz/zh-hant/",
                                area=ImagemapArea(
                                    x=359,y=0,width=676.5,height=359
                                )
                            ),
                            URIImagemapAction(
                                link_uri="https://code.visualstudio.com/",
                                area=ImagemapArea(
                                    x=0,y=0,width=676.5,height=359
                                )
                            ),
                            URIImagemapAction(
                                link_uri="https://git-scm.com/",
                                area=ImagemapArea(
                                    x=0,y=359,width=676.5,height=359
                                )
                            )
                        ]
                    )
                    elif 'page' in event.message.text:
                        db = pymysql.connect(host='us-cdbr-east-04.cleardb.com', port=3306, user='b39d8fa6dd08de', passwd='e2b8b154', db='heroku_d34613fc10f0366', charset='utf8')
                        cursor = db.cursor()
                        cursor.execute("SELECT 房東姓名,坪數,房租,房東電話,租屋住址,經度E,緯度N FROM heroku_d34613fc10f0366.mapa")
                        row = cursor.fetchone()
                        list1=[]
                        text1=''
                        text2=''
                        page=int((event.message.text).split(',')[1])+1#第1頁為0~4第2頁為5~10
                        ulon=float((event.message.text).split(',')[2])#以逗號切割回傳字串中的經緯度
                        ulat=float((event.message.text).split(',')[3])
                        while row: #判斷兩點距離若小於0.5km就將row資料存進list1
                            if haversine(ulon,ulat,row[5],row[6])<0.5:
                                list1.append(row)
                            row = cursor.fetchone()#使row輸出下一行資料列
                        a = np.array(list1)
                        list1len = a.shape[0]#list1len=list1有多少項目
                        if list1len%5==0:#算出page的上限為pagelimit , int用來去小數點
                            pagelimit=int(list1len/5)
                        else :
                            pagelimit=int(list1len/5+1)
                        if page==pagelimit:#如果page==上限(最後一頁),判斷要輸出5個一行還是湊不滿5個的最後幾行
                            if list1len%5 != 0:
                                i = list1len%5#i是要跑的行數
                                j = list1len-i#j是從第幾行開始跑
                                for k in range(j,j+i):
                                    text1=text1+bodymessage(list1[k][0],list1[k][1],list1[k][2],list1[k][3],list1[k][4])
                                for l in range(i-1):
                                    text2=text2+']}'
                                print(text1+text2)
                                message = FlexSendMessage(
                                    alt_text='附近租戶',
                                    contents=eval(flexmessageframe(str(text1),str(text2))),
                                    quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="下一頁",text=('page,'+str(page+1)+','+str(ulon)+','+str(ulat))))]))
                            else:
                                i = 5
                                j= page*5
                                for k in range(j,j+i):
                                    text1=text1+bodymessage(list1[k][0],list1[k][1],list1[k][2],list1[k][3],list1[k][4])
                                message = FlexSendMessage(
                                    alt_text='附近租戶',
                                    contents=eval(flexmessageframe(text1,']}]}]}]}')),
                                    quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="下一頁",text=('page,'+str(page+1)+','+str(ulon)+','+str(ulat))))]))
                        elif page<pagelimit:#如果page還不是最後一頁輸出page*5之後的5頁
                            print(page,pagelimit,list1len)
                            i = 5
                            j = page*5-1
                            for k in range(j,j+i):
                                text1=text1+bodymessage(list1[k][0],list1[k][1],list1[k][2],list1[k][3],list1[k][4])
                            message = FlexSendMessage(
                                alt_text='附近租戶',
                                contents=eval(flexmessageframe(text1,']}]}]}]}')),
                                quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="下一頁",text=('page,'+str(page+1)+','+str(ulon)+','+str(ulat))))]))
                        elif page>pagelimit:#page>最後一頁就回傳沒有下一頁
                            message = TextSendMessage(text='沒有下一頁了')
                    elif event.message.text == "租屋區域":
                        message = TemplateSendMessage(
                        alt_text='租屋區域',
                        template=CarouselTemplate(
                            columns=[
                                CarouselColumn(
                                    thumbnail_image_url='https://imgur.com/UNZbyY9.jpg',
                                    title='網頁區域A區',
                                    text='LTU租屋網',
                                    actions=[
                                        URITemplateAction(
                                            label='查看地圖',
                                            uri='https://yuc27883.github.io/LTU/MAP/mapa.html'
                                        )
                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url='https://imgur.com/cRU7bQK.jpg',
                                    title='網頁區域B區',
                                    text='LTU租屋網',
                                    actions=[
                                        URITemplateAction(
                                            label='查看地圖',
                                            uri='https://yuc27883.github.io/LTU/MAP/mapb.html'
                                        )
                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url='https://imgur.com/G2wmOf6.jpg',
                                    title='網頁區域C區',
                                    text='LTU租屋網',
                                    actions=[
                                        URITemplateAction(
                                            label='查看地圖',
                                            uri='https://yuc27883.github.io/LTU/MAP/mapc.html'
                                        )
                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url='https://imgur.com/C5pOXb7.jpg',
                                    title='網頁區域D區',
                                    text='LTU租屋網',
                                    actions=[
                                        URITemplateAction(
                                            label='查看地圖',
                                            uri='https://yuc27883.github.io/LTU/MAP/mapd.html'
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                    elif event.message.text in ["台北市","新北市","基隆市","宜蘭縣","新竹市","新竹縣","桃園市","苗栗縣","台中市","彰化縣","南投縣","嘉義市","嘉義縣","雲林縣","台南市","高雄市","澎湖縣","金門縣","屏東縣","台東縣","花蓮縣","連江縣"]:
                        rent = rent591(event.message.text)
                        message = TextSendMessage(text=rent.scrape())
                    elif event.message.text=='http://203.217.122.53/Member/Login':
                        message = TextSendMessage(text='點擊網址進入我們的登入頁面')
                    else:
                        message = TextSendMessage(text='查詢租屋地圖的方法\n方法一\n請在文字欄輸入『 租屋區域 』\n方法二\n按下選單中間的Map按鈕\n┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉\n快速查詢附近物件及房東資訊\n點選下方 ✚ 號 ➡️按下位置資訊➡️按下分享')
                line_bot_api.reply_message(event.reply_token,message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# Create your views here.