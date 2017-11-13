import dns.resolver
import socket
import smtplib

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from core import serializers

STATUS_SMTP_SUCCESS = 250


class CheckEmail(APIView):
    authentication_classes = (TokenAuthentication, )
    serializer_class = serializers.CheckEmail

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        if self.verify_email(email):
            return Response(data=email, status=status.HTTP_200_OK)
        else:
            return Response(data={'error': "Email doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

    def verify_email(self, email):
        domain_name = email.split('@')[1]

        records = dns.resolver.query(domain_name, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)

        host = socket.gethostname()

        server = smtplib.SMTP()
        server.set_debuglevel(0)

        server.connect(mxRecord)
        server.helo(host)
        server.mail(settings.EMAIL_FOR_CHECK)
        code, message = server.rcpt(str(email))
        server.quit()

        if code == STATUS_SMTP_SUCCESS:
            answer = True
        else:
            answer = False

        return answer
