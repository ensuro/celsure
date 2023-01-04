import os

from celery import Celery
from celery.signals import task_failure

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celsure.settings")

app = Celery("celsure")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

if bool(os.environ.get("CELERY_WORKER_RUNNING", False)):
    import rollbar
    from django.conf import settings

    rollbar.init(**settings.ROLLBAR)

    def celery_base_data_hook(request, data):
        data["framework"] = "celery"

    rollbar.BASE_DATA_HOOK = celery_base_data_hook

    @task_failure.connect
    def handle_task_failure(**kw):
        rollbar.report_exc_info(extra_data=kw)


@app.task(bind=True)
def debug_task(self, fail=False):
    print(f"Request: {self.request!r}")

    if fail:
        raise RuntimeError("Testing notifications pipeline on celery")
