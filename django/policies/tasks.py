from celery import shared_task

from policies.models import Policy


@shared_task
def new_policy(imei):
    policy = Policy.objects.get(imei=imei)
    policy.create_policy()
    policy.save()

    return policy
