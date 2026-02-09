from . import views
from django.urls import path

urlpatterns=[
    path("",views.indexpage,name="index"),
    path("home-public/",views.homepage,name="home_public"),
    path('match/', views.match_public, name='match'),
    path('match_simp/', views.match , name='match_simp'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how-it-works'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='sign-up'),
    path("home/", views.home_view, name="home"),
    path('profile/', views.profile_view, name='profile'),
    path('chat/', views.chat_view, name='chat'),
    path("schedule/", views.schedule_view, name="schedule"),
    path("quiz/", views.quiz_view, name="quiz"),
    path('send-request/', views.send_request_view, name='send_request'),
    path('about_m/',views.about_m,name="about_m"),
    path('requests/', views.request_view, name='requests'),
    path('requests/accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('requests/decline/<int:request_id>/', views.decline_request, name='decline_request'),
    path("quiz/data/", views.quiz_data, name="quiz_data"),
    path("quiz/save/", views.save_quiz_result, name="save_quiz"),
    path("chat/messages/<int:buddy_id>/", views.get_messages, name="get_messages"),
]