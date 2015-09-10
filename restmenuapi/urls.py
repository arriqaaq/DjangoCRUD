from django.conf.urls import patterns, url
from restmenuapi import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^add_restaurant/$', views.newRestaurantItem, name='add_restaurant'),
        url(r'^edit_restaurant/(?P<restaurant_id>[\w\-]+)/$', views.editRestaurantItem, name='edit_restaurant'),
        url(r'^delete_restaurant/(?P<restaurant_id>[\w\-]+)/$', views.deleteRestaurantItem, name='delete_restaurant'),
        url(r'^menu/(?P<restaurant_id>[\w\-]+)/$', views.restaurantMenu, name='menu'),
        url(r'^add_menu/(?P<restaurant_id>[\w\-]+)/$', views.newMenuItem, name='newmenu'),
        url(r'^edit_menu/(?P<menu_id>[\w\-]+)/$', views.editMenuItem, name='edit_menu'),
        url(r'^test/$', views.restaurantJson, name='test'),
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
)
