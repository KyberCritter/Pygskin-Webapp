# pygskin_webapp/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def my_periodic_task():
    logger.info("This task runs periodically without any credentials!")
