"""systrader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from quantylab.systrader.creon import bridge_django

urlpatterns = [
    path('admin/', admin.site.urls),
    path('connection', bridge_django.handle_connection),
    path('stockcodes', bridge_django.handle_stockcodes),
    path('stockstatus', bridge_django.handle_stockstatus),
    path('stockcandles', bridge_django.handle_stockcandles),
    path('marketcandles', bridge_django.handle_marketcandles),
    path('stockfeatures', bridge_django.handle_stockfeatures),
    path('short', bridge_django.handle_short), 
    path('investorbuysell', bridge_django.handle_investorbuysell), 
    path('marketcap', bridge_django.handle_marketcap), 
]
