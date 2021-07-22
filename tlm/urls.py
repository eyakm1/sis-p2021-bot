"""Django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from tlm.requests_handler import (
    add_submissions,
    confirm_send,
    confirm_delete,
    waiting,
    delete,
    update_assignee,
    update_status,
)

urlpatterns = [
    path('submissions/', add_submissions),
    path('submissions/<int:submission_id>/confirm/send/', confirm_send),
    path('submissions/<int:submission_id>/confirm/delete/', confirm_delete),
    path('waiting/', waiting),
    path('to_delete/', delete),
    path('submissions/<int:submission_id>/status/', update_status),
    path('submissions/<int:submission_id>/assignee/', update_assignee)
]
