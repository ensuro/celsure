from rest_framework import serializers

from .models import Policy


class PolicySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "imei",
            "status",
            "email",
            "data",
        ]
        read_only_fields = ["status"]
