from django.contrib import admin
from django.urls import path
from api.views import AnalyzeTextView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/analyze/", AnalyzeTextView.as_view()),
]
