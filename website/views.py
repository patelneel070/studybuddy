from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import StudyBuddyRequest, Profile, User
from django.shortcuts import get_object_or_404, redirect
import csv
import os
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import QuizResult
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from chat.models import ChatMessage   



def indexpage(request):
    return render(request,'index.html')
def homepage(request):
    return render(request,'home-public.html')
from django.contrib.auth.decorators import login_required

def match_public(request):
    return render(request, "match-public.html")


@login_required(login_url='login')
def match(request):
    profile = Profile.objects.get(user=request.user)
    other_profiles = Profile.objects.exclude(user=request.user)

    compatible_buddies = []

    for buddy in other_profiles:
        shared_subjects = []

        if buddy.subjects and profile.subjects:
            for subject in buddy.subjects:
                if subject in profile.subjects:
                    buddy_level = (
                        buddy.levels.get(subject, "Beginner")
                        if buddy.levels else "Beginner"
                    )
                    shared_subjects.append({
                        "subject": subject,
                        "level": buddy_level
                    })

        if shared_subjects:
            compatible_buddies.append({
                "id": buddy.user.id,
                "name": buddy.user.username,
                "shared_subjects": shared_subjects
            })

    return render(request, "match.html", {
        "profile": profile,
        "buddies": compatible_buddies
    })

@login_required
def about_m(request):
    return render(request,'about_m.html')

def about(request):
    return render(request, 'about.html')

def how_it_works(request):
    return render(request, 'how-it-works.html')



def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('sign-up')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('sign-up')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)   
        return redirect('home')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, "login.html")

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")   
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

# -------- PROTECTED --------



@login_required
def profile_view(request):
    print("METHOD:", request.method)
    print("POST:", request.POST)
    profile, created = Profile.objects.get_or_create(user=request.user)
    subjects_list = ["Maths-1", "Data Structures", "DBMS", "Java", "Physics"]  
    levels_list = ["Beginner", "Intermediate", "Advanced"]

    if request.method == "POST":

        selected_subjects = request.POST.getlist("subjects")
        profile.subjects = selected_subjects

        levels_dict = {}
        for subject in selected_subjects:
            level_value = request.POST.get(f"level_{subject}", "Beginner")
            levels_dict[subject] = level_value
        profile.levels = levels_dict

        study_hours = request.POST.get("study_hours", 4)
        profile.study_hours = int(study_hours)

        profile.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("profile")  

    return render(request, "profile.html", {
        "profile": profile,
        "subjects_list": subjects_list,
        "levels_list": levels_list,
    })

@login_required
def schedule_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
        print("LOGGED USER:", request.user.username)
        print("SUBJECTS:", profile.subjects)
    except Profile.DoesNotExist:
        profile = None
        print("NO PROFILE FOUND")

    return render(request, "schedule.html", {"profile": profile})

@login_required
def chat_view(request):
    user_profile = Profile.objects.get(user=request.user)

    
    accepted_sent = StudyBuddyRequest.objects.filter(
        sender=request.user, status="accepted"
    ).values_list("receiver", flat=True)
    accepted_received = StudyBuddyRequest.objects.filter(
        receiver=request.user, status="accepted"
    ).values_list("sender", flat=True)

    accepted_ids = list(accepted_sent) + list(accepted_received)

    accepted_buddies = Profile.objects.filter(user__id__in=accepted_ids)

    return render(request, "chat/chat.html", {"accepted_buddies": accepted_buddies})




@login_required
def quiz_view(request):
    profile = Profile.objects.get(user=request.user)

    context = {
        "user_id": request.user.id,
        "subjects": profile.subjects,      
        "levels": profile.levels,           
    }
    return render(request, "quiz.html", context)


@login_required
def send_request_view(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)

        existing_request = StudyBuddyRequest.objects.filter(
            sender=request.user,
            receiver=receiver
        ).first()

        if existing_request:
            messages.info(request, "Request already sent!")
        else:
            StudyBuddyRequest.objects.create(
                sender=request.user,
                receiver=receiver
            )
            messages.success(request, "Request sent successfully!")

        return redirect('match_simp')

@login_required
def match_view(request):
    user_profile = Profile.objects.get(user=request.user)
    all_profiles = Profile.objects.exclude(user=request.user)
    
    buddies = []

    for p in all_profiles:
        shared_subjects = []

        for subject in user_profile.subjects.all():
            if subject in p.subjects.all():
                shared_subjects.append({
                    'name': subject.name,
                    'level': subject.level  
                })

        buddies.append({
            'id': p.id,
            'name': p.user.get_full_name() or p.user.username,
            'shared_subjects': shared_subjects
        })

    sent_request_ids = [r.receiver.id for r in request.user.sent_requests.all()]

    return render(request, 'match.html', {
        'buddies': buddies,
        'sent_request_ids': sent_request_ids
    })


@login_required(login_url='login')
def request_view(request):
    pending_requests = StudyBuddyRequest.objects.filter(
        receiver=request.user,
        status='pending'
    )

    accepted_requests = StudyBuddyRequest.objects.filter(
        receiver=request.user,
        status='accepted'
    )

    return render(request, 'requests.html', {
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests
    })



@login_required(login_url='login')
def accept_request(request, request_id):
    buddy_request = get_object_or_404(
        StudyBuddyRequest,
        id=request_id,
        receiver=request.user
    )
    buddy_request.status = 'accepted'
    buddy_request.save()
    return redirect('requests')


@login_required(login_url='login')
def decline_request(request, request_id):
    buddy_request = get_object_or_404(
        StudyBuddyRequest,
        id=request_id,
        receiver=request.user
    )
    buddy_request.status = 'declined'
    buddy_request.save()
    return redirect('requests')

# views.py


def quiz_data(request):
    file_path = os.path.join(settings.BASE_DIR, "quiz_questions.csv")

    data = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            subject = row["subject"]

            if subject not in data:
                data[subject] = []

            data[subject].append({
                "q": row["question"],
                "options": [
                    row["option1"],
                    row["option2"],
                    row["option3"],
                    row["option4"],
                ],
                "correct": int(row["correct"]) - 1,
                "exp": row["explanation"]
            })

    return JsonResponse(data)

@login_required
@csrf_exempt
def save_quiz_result(request):
    print("USER:", request.user)
    if request.method == "POST":
        data = json.loads(request.body)

        QuizResult.objects.create(
            user=request.user,
            subject=data.get("subject"),
            score=data.get("score"),
            total=data.get("total"),
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})


@login_required
def home_view(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    results = QuizResult.objects.filter(
        user=request.user,
        created_at__gte=one_week_ago
    )

    if results.exists():
        avg = sum(r.percentage() for r in results) // results.count()
    else:
        avg = 0

    if avg < 40:
        level = "Beginner"
    elif avg < 70:
        level = "Intermediate"
    else:
        level = "Advanced"

    return render(request, "home.html", {
        "weekly_avg": avg,
        "progress_level": level,
    })


@login_required
def get_messages(request, buddy_id):
    user = request.user

    messages = ChatMessage.objects.filter(
        Q(sender=user.id, receiver=buddy_id) |
        Q(sender=buddy_id, receiver=user.id)
    ).order_by("timestamp")

    data = [
        {
            "sender": msg.sender.id,
            "message": msg.message,
            "timestamp": msg.timestamp.strftime("%H:%M")
        }
        for msg in messages
    ]

    return JsonResponse({"messages": data})

