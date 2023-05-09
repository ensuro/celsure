from celery import shared_task

from policies.models import Policy


@shared_task
def new_policy(imei, uuid):
    policy = Policy.objects.get(imei=imei, data__uuid=uuid)
    policy.create_policy()
    policy.save()

    return policy
