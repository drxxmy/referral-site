import random
import time

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api import serializers

from .models import AuthCode, User


class RequestCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"error": "Необходимо указать номер телефона"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Имитируем задержку
        time.sleep(random.randint(1, 2))

        # Генерируем 4-значный код
        code = str(random.randint(1000, 9999))

        # Сохраняем код
        AuthCode.objects.create(phone_number=phone_number, code=code)

        return Response({"status": "success", "message": "Код отправлен"})


class VerifyCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        code = request.data.get("code")
        if not phone_number:
            return Response({"error": "Необходимо указать номер телефона"})

        if not code:
            return Response({"error": "Необходимо указать код подтверждения"})

        try:
            auth_code = AuthCode.objects.get(
                phone_number=phone_number, code=code, is_used=False
            )
            auth_code.is_used = True
            auth_code.save()
        except AuthCode.DoesNotExist:
            return Response(
                {"error": "Неверный код или код уже использован"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ищем или создаем пользователя
        user, created = User.objects.get_or_create(phone_number=phone_number)

        # Генерация JWT токена
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": "success",
                "token": str(refresh.access_token),
                "is_new_user": created,
            }
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserProfileSerializer(request.user)
        return Response(serializer.data)


class ActivateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.ActivateInviteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invite_code = serializer.validated_data["invite_code"]

        # Проверяем что пользователь еще не активировал инвайт
        if request.user.activated_invite:
            return Response(
                {"error": "Инвайт уже был активирован"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ищем пользователя с таким инвайт-кодом
        try:
            inviter = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response({"error": "Инвайт-код не найден"})

        # Проверяем на активацию собственного кода
        if inviter == request.user:
            return Response({"error": "Нельзя активировать собственный инвайт-код"})

        # Активируем инвайт-код
        request.user.activated_invite = inviter
        request.user.save()

        return Response({"status": "success", "message": "Инвайт-код активирован"})
