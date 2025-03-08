from rest_framework import serializers
from .models import Department, Customer, Agents, Ticket, UserDetails
from django.contrib.auth.models import User


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDetails
        # fields = ("role","profile_picture")


class Userserializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RegisterSerializer(serializers.Serializer):
    user = Userserializer()
    role = serializers.CharField(max_length=20)

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        UserDetails.objects.create(user=user, **validated_data)
        return {
            "user": user,
            "role": validated_data["role"],
        }  # Return a dictionary, not a User instance


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class AgentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agents
        fields = [
            "username",
            "created_at",
            "current_customer",
            "dept_name",
            "is_available",
            "max_customer",
            "has_capacity",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
