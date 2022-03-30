from accounts.models import UserNotifications

def get_notifications(request):
    user = request.user
    
    if user.is_authenticated:
        notifications = UserNotifications.objects.filter(
            user_id=user).order_by('-created')[:7]
        return dict(notifications=notifications)
    else:
        return {'false': False}