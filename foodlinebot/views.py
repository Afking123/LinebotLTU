from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
 
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
                else:
                    message = TextSendMessage(text='請輸入租屋地圖,租屋區域或位置')
                line_bot_api.reply_message(event.reply_token,message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# Create your views here.
