"""
VividCrowd 子应用模块
"""
from backend.apps.chat.app import chat_app
from backend.apps.celebrity.app import celebrity_app
from backend.apps.customer_service.app import customer_service_app

__all__ = ["chat_app", "celebrity_app", "customer_service_app"]
