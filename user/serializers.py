from .models import CustomUser
from rest_framework import serializers
from .forms import UserForm
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError



class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # Assuming public_id is the user ID

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','last_name','first_name']
        
from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class RegisterationSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        # Ensure that first_name, last_name, and username are provided
        if not data.get('first_name'):
            raise serializers.ValidationError("First name is required")
        if not data.get('last_name'):
            raise serializers.ValidationError("Last name is required")
        if not data.get('username'):
            raise serializers.ValidationError("Username is required")

        # Check if passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        
        return data

    def create(self, validated_data):
        # Create user with validated data
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],  # create_user handles password hashing
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user


User = get_user_model()

class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

   
    def validate(self, attrs):
        data = {}
        email = attrs.get('email')
        password = attrs.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = self.get_token(user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            data['user'] = CustomUserSerializer(user).data
            return data
        else:
            raise ValidationError('Invalid email/password')

        return data

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
       
        # Check if the new password and confirm new password match.
     
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New password and Confirm password do not match.")
        return data
    def validate_old_password(self, value):
        # Validate the old password
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    confirm_new_email = serializers.EmailField(required=True)
    current_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        new_email = data.get('new_email')
        confirm_new_email = data.get('confirm_new_email')
        current_password = data.get('current_password')

        # Check if the current password is correct
        if not user.check_password(current_password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        # Check if the new email matches the confirm email
        if new_email != confirm_new_email:
            raise serializers.ValidationError({"email_mismatch": "New email and confirm email do not match."})

        # Optionally, check if the email is already in use by another user
        if user.__class__.objects.filter(email=new_email).exists():
            raise serializers.ValidationError({"email_exists": "This email is already in use."})

        return data
