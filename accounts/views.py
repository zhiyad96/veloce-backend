from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLoginserializer,UserRegisterserializer
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
import requests
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication





        #===================== google login view ==============
        
        
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token required"}, status=400)

        google_response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )

        if google_response.status_code != 200:
            return Response({"error": "Invalid token"}, status=400)

        data = google_response.json()
        if data.get("aud") != "1057639794290-p47jbkpidvecn1kmv7k7nqdpgdvnapev.apps.googleusercontent.com":
            return Response({"error": "Invalid audience"}, status=400)

        email = data.get("email")
        name=data.get("given_name")
        if not email:
            return Response({"error": "Email not found"}, status=400)

        user,_ = User.objects.get_or_create(
            email=email,
            defaults={"username": name}
        )
        
        if not user.is_active:
            return Response({"error": "User is blocked"}, status=403)
        
        refresh=RefreshToken.for_user(user)

        response= Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email,
        })
        
        
        access=refresh.access_token
        response= Response({
        "refresh":str(refresh),
        "access":str(refresh.access_token)
        })
        response.set_cookie(
        key="access_token",
        value=str(access),
        httponly=True,
        secure=False,
        samesite="Lax",
        path="/",
        max_age=60 * 15
        )
            
        response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=False,
                    samesite="Lax",
                    path="/",
                    max_age=60 * 60 * 24 * 7
                )
        return response
        
        
            # ========================== logi section ======================

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer=UserLoginserializer(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data["email"]
            password=serializer.validated_data["password"]
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            user=authenticate(username=user_obj.username,password=password)
            
            
            if user :
                refresh=RefreshToken.for_user(user)
                access=refresh.access_token
                response= Response({
                "refresh":str(refresh),
                "access":str(refresh.access_token)
                })
                response.set_cookie(
                    key="access_token",
                    value=str(access),
                    httponly=True,
                    secure=False,
                    samesite="Lax",
                    path="/",
                    max_age=60 * 15
                )
            
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=False,
                    samesite="Lax",
                    path="/",
                    max_age=60 * 60 * 24 * 7
                )
                return response
            return Response({
                "error":"invalid  credentials"
                },status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        # ==============================registration section =======================
        
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer=UserRegisterserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    # ========================== User list section ================
    
class UserDetailView(APIView):
    
    def get(self, request, id=None):
        
        if id:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserRegisterserializer(user)
            return Response(serializer.data)
        
        user=User.objects.all()
        serializer=UserRegisterserializer(user,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
    def patch(self, request, id):
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({"error": "user not found"},status=status.HTTP_404_NOT_FOUND)
            serializer = UserRegisterserializer(user,data=request.data,partial=True )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "user not found"},status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "user deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
    
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserRegisterserializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
   
#    ================================== logout section=========================
   
class Logout(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    
    
    
class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
       
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)

            new_access_token = str(refresh.access_token)

            response = Response(
                {"message": "Access token refreshed"},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=False,     
                samesite="Lax",   
                path="/",
                max_age=60 * 15   
            )

            return response

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
            
            
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        serializer = UserRegisterserializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
            
        
    # ============================  cookies jwt authenication ==================
    
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get("access_token")
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token