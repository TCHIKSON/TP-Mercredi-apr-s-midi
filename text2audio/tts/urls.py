from django.urls import path

from tts import views

urlpatterns = [
    path("say/", views.SayView.as_view(), name="say"),
]
