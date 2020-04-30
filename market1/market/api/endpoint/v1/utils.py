from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from market.core.security import require_active_admin
from market.core.celery_app import celery_app
from market.models.user import MarketUser
from market.utils import send_test_email

router = APIRouter()


@router.post("/test-celery/", response_model=Msg, status_code=201)
def test_celery(
    msg: Msg, current_user: MarketUser = Depends(require_active_admin)
):
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=Msg, status_code=201)
def test_email(
    email_to: EmailStr, current_user: MarketUser = Depends(require_active_admin)
):
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
