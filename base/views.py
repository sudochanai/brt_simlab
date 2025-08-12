from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer 

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            # Call the original TokenObtainPairView to get the tokens
            response = super().post(request, *args, **kwargs)
            tokens = response.data  
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            # Create a fresh response object
            res = Response({"success": True}, status=status.HTTP_200_OK)

            # Store tokens in cookies
            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  
                samesite='Strict'
            )
            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True, 
                samesite='Strict'
            )

            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            if 'refresh' not in request.data:
                refresh_token = request.COOKIES.get('refresh_token')
                if not refresh_token:
                    return Response(
                        {"success": False, "message": "Refresh token missing"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                data = request.data.copy()
                data['refresh'] = refresh_token
                request._full_data = data

            response = super().post(request, *args, **kwargs)
            access_token = response.data.get('access')

            res = Response({"success": True}, status=status.HTTP_200_OK)
            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True, 
                samesite='Strict',
            )
            return res

        except Exception:
            return Response(
                {"success": False, "message": "Token refresh failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view(['POST'])
def logout(request):
    res = Response({"success": True}, status=status.HTTP_200_OK)
    res.delete_cookie('access_token')
    res.delete_cookie('refresh_token')
    return res



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notes(request):
    notes = Note.objects.filter(owner=request.user)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note(request):
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
