from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from agents.models import Agent


class DeviceTokenAuthentication(BaseAuthentication):
    """Authenticate agents via device token passed in Authorization header."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split('Bearer ')[1].strip()
        if not token:
            return None

        try:
            agent = Agent.objects.get(device_token=token, is_active=True)
        except Agent.DoesNotExist:
            raise AuthenticationFailed('Invalid or expired token.')

        return (agent, token)
