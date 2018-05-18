from django.urls import path
from . import views

urlpatterns = [
    path('<int:fund_code>', views.showfund),
]