from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class VisitLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"Visit to {request.path} by {request.user if request.user.is_authenticated else 'Anonymous'}")