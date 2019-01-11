from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mall import settings
from oauth.models import OAuthQQUser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from oauth.serializers import OAuthQQUserSerializer
# from oauth.serializers import UserCenterInfoSerializer
from oauth.utils import generic_opne_id, generic_token

'''
当用户点击ｑｑ按钮的时候　回发送一个请求
我们后端返回给他一个ｕｒｌ（ｕｒｌ是前端根据文档拼接出来的）

'''
#链接ｑｑ登陆页面　将所需的参数传入导入的ｑｑ类中初始化

class OAuthQQURLAPIView(APIView):

    def get(self,request):

        '''
        qq模块中封装的内容
            def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径

        :param request:
        :return:
        '''
        state='/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        auth_url = oauth.get_qq_url()

        return Response({'auth_url':auth_url})
'''
1.用户同意登陆授权，这个时候　会返回一个ｃｏｄｅ
２．我们有了ｃｏｄｅ　换取ｔｏｋｎｅ
３．有了ｔｏｋｅｎ我们在获取ｏｐｅｎｉｄ

'''
class OAuthQQUserAPIView(APIView):

    def get(self,request):
        params = request.query_params
        #获取前端页面返回来的ｃｏｄｅ
        code = params.get('code')
        print(code)
        #对ｃｏｄｅ进行判断
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        #用ｃｏｄｅ换取ｔｏｋｅｎ
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        )
        token = oauth.get_access_token(code)
        #3.用ｔｏｋｅｎ换openid
        openid = oauth.get_open_id(token)
        #4.openid 是此网站上唯一对应的用户身份的标示
        # 网站可将ｉｄ进行储存便于用户下次登陆时辨识其身份
        '''
        获取openid 分为两种情况
        １．之前绑定过的
        ２．用户之前没有绑定过的
        根据ｏｐｅｎｉｄ查询数据

        '''
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)


        except OAuthQQUser.DoesNotExist:
            '''#用户不存在，　
            #绑定也应该有一个时效,
            对加except OAuthQQUser.DoesNotExist:密openid 的步骤进行抽取
            '''
            # #创建一个序列化器　secret_key秘钥
            # #expires_in 过期时间　单位是秒
            # s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
            # #组织数据
            # data = {
            #     'openid':openid
            # }
            # #３．让序列化器对数据进行处理
            # token = s.dumps(data)
            token = generic_opne_id(openid)

            print('打印token'+token)


            return Response({'access_token':token})

        else:
            # 存在　应该让用户登陆
            #抽取获取ｔｏｋｅｎ功能

            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)
            # token = generic_token(qquser.user)

            return Response({
                'token':token,
                'username':qquser.user.username,
                'openid':qquser.user.id
            })

    def post(self,request):
        #获取数据
        data = request.data
        #校验数据
        serializer = OAuthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        #保存校验数据　并接收
        user = serializer.save()
        print(user)
        token = generic_token(user)
        print(token)

        #返回相应
        response = Response({
            'token':token,
            'user_id':user.id,
            'username':user.username

        })
        return request

# class UserCerterInfoAPIView(APIView):
#
#     #添加　权限　必须是登陆用户才可以访问
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#         #获取用户信息
#
#         user = request.user
#         #将模型转化字典Ｊｓｏｎ
#         serializer = UserCenterInfoSerializer(user)
#         #３．返回相应
#         return Response(serializer.data)



# class UserCenterInfoAPIView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

