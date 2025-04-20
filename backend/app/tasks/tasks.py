from .worker import celery

@celery.task(name="send_webpush_notification")
def send_webpush_notification(data):
    """
    Send a web push notification using Celery.
    """
    pass
