import re
import dns.resolver
import socket
import smtplib

from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from core import serializers


class CheckEmail(APIView):
    authentication_classes = (TokenAuthentication, )
    serializer_class = serializers.CheckEmail

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        addressToVerify = email
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)

        try:
            if match is None:
                print('Bad Syntax in ' + addressToVerify)
                raise ValueError('Bad Syntax')

            # Step 2: Getting MX record
            # Pull domain name from email address
            domain_name = email.split('@')[1]

            # get the MX record for the domain
            records = dns.resolver.query(domain_name, 'MX')
            mxRecord = records[0].exchange
            mxRecord = str(mxRecord)

            # Step 3: ping email server
            # check if the email address exists

            # Get local server hostname
            host = socket.gethostname()

            # SMTP lib setup (use debug level for full output)
            server = smtplib.SMTP()
            server.set_debuglevel(0)

            # SMTP Conversation
            server.connect(mxRecord)
            server.helo(host)
            server.mail('me@domain.com')
            code, message = server.rcpt(str(addressToVerify))
            server.quit()

            # Assume 250 as Success
            if code == 250:
                return Response(data=email, status=status.HTTP_200_OK)
            else:
                raise ValueError()

        except Exception:

            return Response(data={'error': "Email doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
