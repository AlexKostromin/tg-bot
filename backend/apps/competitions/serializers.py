from rest_framework import serializers
from .models import Competition, VoterTimeSlot

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'


class VoterTimeSlotSerializer(serializers.ModelSerializer):
    """Сериализатор для временных слотов судей"""
    voter_display = serializers.SerializerMethodField()
    competition_display = serializers.SerializerMethodField()
    
    class Meta:
        model = VoterTimeSlot
        fields = [
            'id', 'competition', 'competition_display', 'voter', 'voter_display',
            'slot_date', 'start_time', 'end_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_voter_display(self, obj):
        return f"{obj.voter.first_name} {obj.voter.last_name}"
    
    def get_competition_display(self, obj):
        return obj.competition.name
