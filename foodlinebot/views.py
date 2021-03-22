from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from .scraper import rent591
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
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
                elif event.message.text=="租屋區域":
                    message = TemplateSendMessage(
                    alt_text='租屋區域',
                    template=ImageCarouselTemplate(
                    columns=[
                        ImageCarouselColumn(
                            image_url='https://imgur.com/0GHfWpF.jpg',
                            action=PostbackTemplateAction(
                                label='A區',
                                data='action=buy&itemid=1'
                            )
                        ),
                        ImageCarouselColumn(
                            image_url='https://imgur.com/kMQ54qH.jpg',
                            action=PostbackTemplateAction(
                                label='B區',
                                data='action=buy&itemid=2',
                                uri='https://imgur.com/kMQ54qH.jpg'
                            )
                        ),
                        ImageCarouselColumn(
                            image_url='https://imgur.com/1QWQ9TZ.jpg',
                            action=PostbackTemplateAction(
                                label='c區',
                                data='action=buy&itemid=2',
                                uri='https://imgur.com/1QWQ9TZ.jpg'
                            )
                        )
                    ]
                )
                )
                elif event.message.text=='位置':
                    message = LocationSendMessage(
                        title='嶺東科大',
                        address='嶺東科技大學',
                        latitude=24.135015,
                        longitude=120.608862
                    )
                elif event.message.text=='語音':
                    message = AudioSendMessage(original_content_url='https://imgur.com/ueFHLMe.mp4',duration=10000)
                elif event.message.text=='按鈕樣板':
                    message = TemplateSendMessage(
                            alt_text='按鈕樣板',
                            template=ButtonsTemplate(
                                title='標題',
                                text='內容',
                                thumbnail_image_url='https://img.youtube.com/vi/VKMw2it8dQY/hqdefault.jpg',
                                actions=[
                                    MessageTemplateAction(
                                        label='訊息回傳',
                                        text='YOOOOOOoooooo'
                                    ),
                                    PostbackTemplateAction(
                                        label='語音',
                                        text='語音',
                                        data='B'
                                    ),
                                    URITemplateAction(
                                        label='超連結',
                                        uri='https://www.youtube.com/watch?v=VKMw2it8dQY&ab_channel=PianoFantasia-Topic'
                                    )
                                ]
                            )
                        )
                elif event.message.text=='兩按鈕樣板':
                    message = TemplateSendMessage(
                        alt_text='兩按鈕樣板',
                        template=ConfirmTemplate(
                            title='ConfirmTemplate',
                            text='有兩種按鈕選擇',
                            actions=[
                                PostbackTemplateAction(
                                    label='Y',
                                    text='確認',
                                    data='Yes'
                                ),
                                MessageTemplateAction(
                                    label='N',
                                    text='否'
                                )
                            ]
                        )
                    )
                elif event.message.text in ["台北市","新北市","基隆市","宜蘭縣","新竹市","新竹縣","桃園市","苗栗縣","台中市","彰化縣","南投縣","嘉義市","嘉義縣","雲林縣","台南市","高雄市","澎湖縣","金門縣","屏東縣","台東縣","花蓮縣","連江縣"]:
                    rent = rent591(event.message.text)
                    message = TextSendMessage(text=rent.scrape())
                else:
                    message = TextSendMessage(text='請輸入租屋地圖,租屋區域,語音,按鈕樣板,兩按鈕樣板,位置或以縣市名搜尋好房網買屋')
                line_bot_api.reply_message(event.reply_token,message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# Create your views here.
