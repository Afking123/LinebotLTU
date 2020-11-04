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
                if event.message.text=="圖片地圖":
                    message = ImagemapSendMessage(
                    base_url='https://i.imgur.com/PCYD9ml.jpg',
                    alt_text='MHW',
                    base_size=BaseSize(width=768,height=432),
                    actions=[
                        URIImagemapAction(
                            link_uri="https://www.monsterhunter.com/world-iceborne/hk/",
                            area=ImagemapArea(
                                x=0,y=0,width=384,height=432
                            )
                        ),
                        URIImagemapAction(
                            link_uri="https://forum.gamer.com.tw/A.php?bsn=5786",
                            area=ImagemapArea(
                                x=384,y=0,width=384,height=432
                            )
                        )
                    ]
                )
                elif event.message.text=="圖片木馬":
                    message = TemplateSendMessage(
                    alt_text='圖片木馬',
                    template=ImageCarouselTemplate(
                    columns=[
                        ImageCarouselColumn(
                            image_url='https://imgur.com/REejfPZ.jpg',
                            action=PostbackTemplateAction(
                                label='碎龍',
                                data='action=buy&itemid=1'
                            )
                        ),
                        ImageCarouselColumn(
                            image_url='https://imgur.com/2wB5aG4.jpg',
                            action=PostbackTemplateAction(
                                label='斬龍',
                                data='action=buy&itemid=2',
                                uri='https://imgur.com/2wB5aG4.jpg'
                            )
                        )
                    ]
                )
                )
                line_bot_api.reply_message(event.reply_token,message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# Create your views here.
