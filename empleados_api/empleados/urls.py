# empleados/urls.py
from django.urls import path
from .views import EmpleadoListCreateView, EmpleadoDetailView, ExportarEmpleadosS3View

urlpatterns = [
    # Ruta alternativa para clientes que esperan /crear/
    path('crear/', EmpleadoListCreateView.as_view(), name='empleados_create'),
    path('', EmpleadoListCreateView.as_view(), name='empleados_list_create'),
    path('exportar-s3/', ExportarEmpleadosS3View.as_view(), name='exportar_empleados_s3'),
    path('<int:pk>/', EmpleadoDetailView.as_view(), name='empleado_detail'),
]
