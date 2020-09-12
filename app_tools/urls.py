from django.urls import path
from . import views

app_name = 'app_tools'

urlpatterns =[
    path('',views.ToolsOverview.as_view(),name='tools_overview'),
    path('tools1/',views.Tool1.as_view(),name='tools1'),
    path('tools2/',views.Tool2.as_view(),name='tools2'),
    path('tools3/',views.Tool3.as_view(),name='tools3'),
    path('tools4/',views.Tool4.as_view(),name='tools4'),
    path('tools5/',views.Tool5.as_view(),name='tools5'),
    path('tools1/tools1_result',views.tools1_result,name='tools1_result'),
    path('tools2/tools2_result_return', views.tools2_result_return, name='tools2_result_return'),
    path('tools2/tools2_result_risk', views.tools2_result_risk, name='tools2_result_risk'),
    path('tools3/tools3_result',views.tools3_result,name='tools3_result'),
    path('tools4/tools4_result',views.tools4_result,name='tools4_result'),
    path('tools5/tools5_result',views.tools5_result,name='tools5_result')

]
