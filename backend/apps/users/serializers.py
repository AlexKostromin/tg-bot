from rest_framework import serializers
from .models import User, RegistrationRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegistrationRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для заявок на регистрацию"""
    user_display = serializers.SerializerMethodField()
    competition_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistrationRequest
        fields = [
            'id', 'user', 'user_display', 'competition', 'competition_display',
            'role', 'status', 'user_first_name', 'user_last_name', 'user_email',
            'user_phone', 'created_at', 'reviewed_at', 'reviewed_by', 'rejection_reason'
        ]
        read_only_fields = ['id', 'created_at', 'reviewed_at', 'reviewed_by']
    
    def get_user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_competition_display(self, obj):
        return obj.competition.name
