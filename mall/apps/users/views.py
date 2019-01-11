from random import randint

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from users.models import User
from users.serializer import RegiserUserSerializer


class RegisterUsernameCountAPView(APIView):

    '''
    获取用户的个数
    GET /users/username/(?p<username>\w{5,20})/count/

    '''
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        context = {
            'count':count,
            'username':username,
        }
        return Response(context)


#查询手机号的个数
class RegisterPhoneCountAPIView(APIView):

    def get(self,request,mobile):

        count = User.objects.filter(mobile=mobile).count()
        context = {
            'count':count,
            'phone':mobile,
        }

        return Response(context)

#生成图片验证码
class RegisterImageCodeView(APIView):

    def get(self,request,image_code_id):

        #创建图片和验证码　
        text,image = captcha.generate_captcha()
        #通过redis保存验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,60,text)
        #将图片返回　　注意　图片是　二进制的
        return HttpResponse(image,content_type='image/jpeg')
#用户注册
class RegiserUserAPIView(APIView):

    def post(self,request):
        #１．接收数据
        data = request.data
        #２．校验数据
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)







