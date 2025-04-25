from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, Customer, Agent, Ticket, Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role", "profile_picture")
        read_only_fields = ("id",)
    
    def create(self, validated_data):
        # pop off password, handle hashing
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class RegisterSerializer(serializers.Serializer):
    user = UserSerializer()
    # optionally let clients pick role, but usually fixed:
    role = serializers.ChoiceField(choices=[Role.CUSTOMER, Role.AGENT])

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_data["role"] = validated_data["role"]
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)

        if user.role == Role.CUSTOMER:
            profile = Customer.objects.create(user=user)
        else:
            # import Agent lazily to avoid circular
            from .models import Agent 
            profile = Agent.objects.create(user=user, **self.context.get("agent_defaults", {}))

        return {"user": user, "profile": profile}
    
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name")


class CustomerSerializer(serializers.ModelSerializer):
    # nest the user so client can provide username/email/password/role
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ("id", "user", "solved_issues", "is_paid")
        read_only_fields = ("id", "solved_issues")

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # ensure role is CUSTOMER
        user_data["role"] = Role.CUSTOMER
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Agent
        fields = (
            "id",
            "user",
            "department",
            "current_customers",
            "max_customers",
            "is_available",
        )
        read_only_fields = ("id", "current_customers")

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # ensure role is AGENT
        user_data["role"] = Role.AGENT
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        agent = Agent.objects.create(user=user, **validated_data)
        return agent


class TicketSerializer(serializers.ModelSerializer):
    # show nested customer and agent by ID
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    agent = serializers.PrimaryKeyRelatedField(
        queryset=Agent.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "ticket_id",
            "customer",
            "agent",
            "issue_title",
            "issue_desc",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "ticket_id", "created_at")
