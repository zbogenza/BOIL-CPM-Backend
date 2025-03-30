from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, critical_path_view, bulk_create_tasks

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('critical-path/', critical_path_view),
    path('bulk-tasks/', bulk_create_tasks),
]
