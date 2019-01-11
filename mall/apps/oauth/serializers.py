from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import check_access_token
from users.models import User


class OAuthQQUserSerializer(serializers.Serializer):

    '''
    qq登陆创建用户用序列化器
    '''
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号',regex='r^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):

        #检验access_token mobile password sms_code

        access_token = attrs['access_token']
        #平身份获取ｏｐｅｎｉｄ
        openid = check_access_token(access_token)

        if openid is None:
            raise serializers.ValidationError('openid 错误')

        attrs['openid']=openid

        mobile = attrs.get('mobile')
        password = attrs['password']
        attrs_sms_code = attrs.get('sms_code')
        # 链接ｒｅｄｉｓ
        from django_redis import get_redis_connection
        # 获取redis 保存中的验证码
        redis_conn = get_redis_connection('code')
        redis_sms = redis_conn.get('sms_' + mobile)

        # 判断验证码是否有值
        if redis_sms is None:
            raise serializers.ValidationError('验证码过过期')
        # 最好删除验证码
        redis_conn.delete('sms_' + mobile)
        if redis_sms.decode()!= attrs_sms_code:
            # if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')

        #对手机号进行判断
        try:
            user = User.objects.get(mobile = mobile)
        except User.DoesNotExist:
            # 如果没有注册要对用户进行注册
            pass
        else:
            #说明注册过了　需要对密码进行验证
            if not user.check_password(['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user']=user
            # attrs["openid"]=openid
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        qquser = OAuthQQUser.objects.create(
            user = user,
            openid = validated_data['openid'],
        )
        return qquser

# class UserCenterInfoSerializer(serializers):
#     class Meta:
#         model = User
#         fields = ('id','username','mobile','email','emil_active')




