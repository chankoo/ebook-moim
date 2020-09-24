# from celery.schedules import crontab

broker_url = 'redis://localhost:6379/0'
broker_transport_options = {'visibility_timeout': 3600}
timezone = 'Asia/Seoul'
task_ignore_result = True
# beat_schedule = {
#     'test_celery_okay': {
#         'task': 'tasks.test_celery_okay',
#         'schedule': crontab(minute=47, hour=8),
#     },
# }
