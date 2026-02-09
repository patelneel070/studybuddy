from website.models import Match

def users_are_matched(user_a, user_b):
    return Match.objects.filter(
        accepted=True
    ).filter(
        (models.Q(user1=user_a) & models.Q(user2=user_b)) |
        (models.Q(user1=user_b) & models.Q(user2=user_a))
    ).exists()
