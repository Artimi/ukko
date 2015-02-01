from celery import Celery

app = Celery('roihunter_recommendations',
             broker='redis://localhost',
             backend='redis://localhost',
             include=['ukko.celery_tasks'])

if __name__ == '__main__':
    app.start()
