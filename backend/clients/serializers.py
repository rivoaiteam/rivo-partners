from rest_framework import serializers
from clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'client_name', 'client_phone', 'expected_mortgage_amount',
            'estimated_commission', 'commission_amount', 'status',
            'channel', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'estimated_commission', 'commission_amount',
            'status', 'channel', 'created_at', 'updated_at',
        ]


class ClientSubmitSerializer(serializers.Serializer):
    client_name = serializers.CharField(max_length=255)
    client_phone = serializers.CharField(max_length=20)
    expected_mortgage_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    consent = serializers.BooleanField()

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError('Client consent is required.')
        return value

    def validate(self, data):
        import re
        agent = self.context.get('agent')
        if not agent:
            raise serializers.ValidationError('Agent context required.')

        # Normalize phone to digits only for comparison
        client_digits = re.sub(r'\D', '', data['client_phone'])
        agent_digits = re.sub(r'\D', '', agent.phone)

        # Agent cannot refer themselves — match if digits are same or one is suffix of the other
        if client_digits == agent_digits or client_digits.endswith(agent_digits[-10:]) or agent_digits.endswith(client_digits[-10:]):
            raise serializers.ValidationError(
                {'client_phone': 'You cannot refer yourself as a client.'}
            )

        # Duplicate phone check — check with and without + prefix
        phone = data['client_phone']
        phone_variants = [phone, f'+{client_digits}', client_digits]
        if Client.objects.filter(client_phone__in=phone_variants).exists():
            raise serializers.ValidationError(
                {'client_phone': 'This client has already been referred.'}
            )

        return data
