# empleados/urls.py
from django.urls import path
from .views import EmpleadoListCreateView, EmpleadoDetailView

urlpatterns = [
    # Ruta alternativa para clientes que esperan /crear/
    path('crear/', EmpleadoListCreateView.as_view(), name='empleados_create'),
    path('', EmpleadoListCreateView.as_view(), name='empleados_list_create'),
    path('<int:pk>/', EmpleadoDetailView.as_view(), name='empleado_detail'),
]
