from rest_framework import viewsets,status,generics
from .serializers import RegisterationSerializer,LoginSerializer,ChangePasswordSerializer,EmailChangeSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer


# Create your views here.
class RegisterationViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterationSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post')
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        refresh = RefreshToken.for_user(user)
        res = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response({
            'refresh': res['refresh'],
            'access': res['access'],
        }, status=status.HTTP_201_CREATED)
    
            
class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post')
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
class RefreshViewset(viewsets.ViewSet,TokenRefreshView):
    http_method_names = ('post')
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data,
            status=status.HTTP_200_OK)
    
class UserDetailsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user  # the authenticated user
        serializer = CustomUserSerializer(user)  # Serialize user data
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return user details

    def get_queryset(self):
        return CustomUserSerializer.objects.filter(user=self.request.user)

    
    def retrieve(self, request, *args, **kwargs):
        profile = self.get_queryset().first()  # Get the user's profile
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Profile updated successfully!"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data,context={'request': request})
        
        if serializer.is_valid():
            # Check old password
            user = request.user
          
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):
    def put(self, request):
        user = request.user
        serializer = EmailChangeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            new_email = serializer.validated_data['new_email']

            # Update the user's email
            user.email = new_email
            user.save()

            return Response({"message": "Email updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)