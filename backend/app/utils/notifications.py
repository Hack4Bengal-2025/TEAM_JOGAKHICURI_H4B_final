from pywebpush import webpush, WebPushException
import os
from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

load_dotenv()

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL")

class NotificationPayload(BaseModel):
    title: str
    body: str
    icon: Optional[HttpUrl]
    url: Optional[HttpUrl]

class PushRequest(BaseModel):
    subscription: Dict
    payload: NotificationPayload

def send_push(request: PushRequest):
    try:
        webpush(
            subscription_info=request.subscription,
            data=request.payload.model_dump_json(),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"},
        )
        return {"status": "success"}
    except WebPushException as ex:
        print("Web Push failed:", repr(ex))
        return {"status": "error", "message": str(ex)}


if __name__ == '__main__':
    message = "Manual message from python"
    subscription = {'endpoint': 'https://updates.push.services.mozilla.com/wpush/v2/gAAAAABn92QnAItTFrk3S8yWokZbT_Vwbp_f6BuN4EjvQmTmrRORQ-wqhtv5ZnPsodZubzoaA20ecINxyHYR52OuvW_ZZ5Vp7g1PdjD3eaUj0mFUrf85f1V3RtXd05DqqgaYAienTJKPU0bNn02uMQTkRtSbrmbzzasLcAiafU76UrCTOijWKHk', 'keys': {'auth': 'trFRZ8-ngYITUxFO6dP8NA', 'p256dh': 'BLgqTWWlJHSGSzaVN1qvU4EZlfe4NHhLpAA5atKRRuO7K8GhIpDVeoPcOpWbXRpsAmDxqtX-eb5lanIGLTlI2IE'}}
    request = PushRequest(
        subscription=subscription,
        payload=NotificationPayload(
            title="Hello world!",
            body="hello this is a test notification",
            url=HttpUrl('https://example.com/'),
            icon=None
        )
    )
    print(send_push(request))