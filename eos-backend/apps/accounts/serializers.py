"""
Accounts Serializers - User and Authentication API
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, TenantMembership, AgencyMembership, ClientMembership,
    UserNotificationPreference
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.CharField(read_only=True)
    tenant_memberships_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'role', 'is_client_portal_user',
            'language', 'timezone', 'is_active', 'is_staff',
            'two_factor_enabled', 'tenant_memberships_count',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login',
            'is_staff', 'is_superuser'
        ]

    def get_tenant_memberships_count(self, obj):
        return obj.tenant_memberships.count()


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for User list."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone',
            'role', 'language', 'timezone'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar',
            'language', 'timezone'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login."""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


class TenantMembershipSerializer(serializers.ModelSerializer):
    """Serializer for TenantMembership model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = TenantMembership
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'tenant', 'tenant_name', 'role', 'is_default', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AgencyMembershipSerializer(serializers.ModelSerializer):
    """Serializer for AgencyMembership model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)

    class Meta:
        model = AgencyMembership
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'agency', 'agency_name', 'role', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClientMembershipSerializer(serializers.ModelSerializer):
    """Serializer for ClientMembership model."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = ClientMembership
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'client', 'client_name', 'role',
            'can_approve', 'can_view_financials', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserNotificationPreference model."""
    class Meta:
        model = UserNotificationPreference
        fields = [
            'email_campaign_status', 'email_approval_required',
            'email_approval_completed', 'email_budget_alerts',
            'email_weekly_summary',
            'inapp_campaign_status', 'inapp_approval_required',
            'inapp_comments'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed serializer for user profile with memberships."""
    full_name = serializers.CharField(read_only=True)
    tenant_memberships = TenantMembershipSerializer(many=True, read_only=True)
    agency_memberships = AgencyMembershipSerializer(many=True, read_only=True)
    client_memberships = ClientMembershipSerializer(many=True, read_only=True)
    notification_preferences = UserNotificationPreferenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'role', 'is_client_portal_user',
            'language', 'timezone', 'is_active',
            'two_factor_enabled',
            'tenant_memberships', 'agency_memberships', 'client_memberships',
            'notification_preferences',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'email', 'created_at', 'updated_at', 'last_login'
        ]
