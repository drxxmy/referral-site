from rest_framework import serializers

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    invited_users = serializers.SerializerMethodField()
    activated_invite = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "phone_number",
            "invite_code",
            "activated_invite",
            "invited_users",
        ]  # Поля, которые будут включены в сериализованный вывод
        read_only_fields = fields

    def get_invited_users(self, obj):
        return list(
            User.objects.filter(activated_invite=obj).values_list(
                "phone_number", flat=True
            )
        )

    def get_activated_invite(self, obj):
        return obj.activated_invite.invite_code if obj.activated_invite else None


class ActivateInviteSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)
