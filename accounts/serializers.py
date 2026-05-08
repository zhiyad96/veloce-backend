from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User


class UserRegisterserializer(ModelSerializer):
    class Meta:
        model=User
        fields=["id","username","email","phone_number","password","role","is_active"]
        extra_kwargs={
            "password":{"write_only":True}
        }
        
        
    def create(self, validated_data):
        user= User(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            role=validated_data.get("role", "user"), 
            is_active=True
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserLoginserializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()
    
