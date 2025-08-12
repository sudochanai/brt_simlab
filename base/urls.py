from django.urls import path

from .views import get_notes, create_note, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('notes/', get_notes),
    path('notes/create/', create_note),

]
