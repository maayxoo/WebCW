import json

from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from social.models import User, Profile, Message, Hobbies
from social.templatetags.social_extras import display_message
from social.forms import LoginForm, SignupForm

appname = "Hobbies for Buddies"


def signup(request):
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            new_user = User.objects.create(username=username)
            new_user.set_password(password)
            new_user.save()
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('social:messages')

    return render(request, 'social/auth/signup.html', { 'form': SignupForm })

def login(request):

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('social:messages')

            return render(request, 'errors/error.html', {
                'error' : 'User not registered. Sign up first.'
            })

        return render(request, 'social/auth/login.html', {
            'form': form
        })

    return render(request, 'social/auth/login.html', { 'form': form })


@login_required
def friends(request):
    return render(request, 'social/pages/friends.html', { 'page': 'friends' })


@login_required
def logout(request):
    auth.logout(request)
    return redirect('social:login')


def view_profile(request, view_username):
    '''This function is only called from'''
    
    username = request.user.username
    greeting = "Your" if username == view_username else view_username + "'s"
    try:
       user = User.objects.get(username=view_username)
    except User.DoesNotExist:
       context = {
          'error' : 'User ' + view_username + ' does not exist'
       }
       return render(request, 'social/errors/error.html', context)
    context = {
        'view_user': view_username,
        'greeting': greeting,
        'profile': user.profile,
    }
    return render(request, 'social/pages/member.html', context)

@login_required
def members(request):
    user = request.user

    if 'add' in request.GET:
        friend_username = request.GET['add']
        try:
            friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            raise Http404('User does not exist')
        user.following.add(friend)
        user.save()
    if 'remove' in request.GET:
        friend_username = request.GET['remove']
        try:
            friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            raise Http404('User does not exist')
        user.following.remove(friend)
        user.save()
    if 'view' in request.GET:
        return view_profile(request, user, request.GET['view'])
    else:
        return render(request, 'social/pages/members.html', {
            'page': 'members',
            'user': user,
            'members': User.objects.exclude(username=user.username),
        })


@login_required
def profile(request):
    user = request.user

    if 'text' in request.POST and request.POST['text']:
        text = request.POST['text'][:4096]
        if user.profile:
            user.profile.text = text
            user.profile.save()
        else:
            profile = Profile(text=text)
            profile.save()
            user.profile = profile
        user.save()
    if 'email' in request.POST and request.POST['email']:
        email = request.POST['email'][:4096]
        if user.profile:
            user.profile.email = email
            user.profile.save()
        else:
            profile = Profile(email=email)
            profile.save()
            user.profile = profile
        user.save()
    if 'city' in request.POST and request.POST['city']:
        city = request.POST['city'][:4096]
        if user.profile:
            user.profile.city = city
            user.profile.save()
        else:
            profile = Profile(city=city)
            profile.save()
            user.profile = profile
        user.save()
    if 'date' in request.POST and request.POST['date']:
        date = request.POST['date'][:4096]
        if user.profile:
            user.profile.date = date
            user.profile.save()
        else:
            profile = Profile(date=date)
            profile.save()
            user.profile = profile
        user.save()
    if 'hobbies' in request.POST and request.POST['hobbies']:
        hobbies = request.POST['hobbies'][:4096]
        if user.profile:
            user.profile.hobbies = hobbies
            user.profile.save()
        else:
            profile = Profile(hobbies=hobbies)
            profile.save()
            user.profile = profile
        user.save()
    context = {
        'user': user,
        'page': 'profile',
        'profile' : user.profile,
        'session_key': request.session.session_key,
        'meta' : request.META,
    }

    return render(request, 'social/pages/profile.html', context)


@login_required
def messages_jquery(request):
    user = request.user

    if request.method == 'GET':
        if 'view' in request.GET:
            view = request.GET['view']
            try: 
                view_user = User.objects.get(username=view)
            except User.DoesNotExist:
                raise Http404('User does not exist')
            profile = view_user.profile
            m1 = Message.objects.filter(recip=view_user,public=True)
            m2 = Message.objects.filter(sender=view_user,public=True)
            m3 = Message.objects.filter(sender=user,recip=view_user)
            m4 = Message.objects.filter(sender=view_user,recip=user)
            messages = m1.union(m2,m3,m4).order_by('-time')
        else:
            view = user.username
            profile = user.profile
            m1 = Message.objects.filter(sender=user)
            m2 = Message.objects.filter(recip=user)
            messages = m1.union(m2).order_by('-time')

        context = {
            'user': user,
            'page': 'messages',
            'profile': profile,
            'view': view,
            'messages': messages,
        }

        return render(request, 'social/pages/messages-jquery.html', context)

    if request.method == 'POST':
        if 'recip' in request.POST:
            recip = request.POST['recip']
            recip_user = get_object_or_404(User, username=recip)
            text = request.POST['text'][:4095]
            pm = request.POST['pm'] == 'yes'
            message = Message.objects.create(
                sender=user,
                recip=recip_user,
                public=pm,
                time=timezone.now(),
                text=text,
            )
            return HttpResponse(display_message(message, user.username))
        else:
            raise Http404('Recip missing in POST request')


@login_required
def messages_vue(request):
    user = request.user
    view = request.GET['view'] if 'view' in request.GET else user.username

    if user.username != view:
        view_user = get_object_or_404(User, username=view)
        profile = view_user.profile
        messages = user.messages_with(view_user)
    else:
        profile = user.profile
        messages = user.messages

    vue_data = json.dumps({
        'user': user.to_dict(),
        'view': view,
        'profile': profile.to_dict() if profile else None,
        'messages': [ message.to_dict() for message in messages ],
    })

    return render(request, 'social/pages/messages-vue.html', {
        'vue_data': vue_data,
    })


@login_required
def upload_image(request):
    user = request.user

    if 'img_file' in request.FILES:
        image_file = request.FILES['img_file']
        if not user.profile:
            profile = Profile(text='')
            profile.save()
            user.profile = profile
            user.save()
        user.profile.image = image_file
        user.profile.save()
        return HttpResponse(user.profile.image.url)
    else:
        raise Http404('Image file not received')

def hobby_view(request):
    hobbies = Hobbies.objects.all()
    return render(request, 'social/pages/hobbies.html', {
        'hobbies': hobbies    
        })

def showlist(request):
    hobbies = Hobbies.objects.all()
    return render(request, 'social/base.html', {
        'hobbies': hobbies    
        })
