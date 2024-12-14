from rest_framework import serializers
from .models import User, Chat, Summary

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        write_only_fields = ["password"]
        
    def create(self, validated_data):
        user = User(username = validated_data["username"], email = validated_data["email"] )
        user.set_password(validated_data["password"])
        user.save()
        return user
        
class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "user", "chat"]
        read_only_fields = ["id","user"]
        
        
class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ["id","user", "summary"]
        read_only_fields = ["id","user"]