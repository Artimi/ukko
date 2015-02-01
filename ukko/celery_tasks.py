from celery_app import app
import ukko
from .rcpparser import RCPParser
from .problem import Problem
from .garth import GARTH
from celery import chord
from celery.utils.log import get_task_logger
import redis
import os.path

logger = get_task_logger(__name__)
c = redis.StrictRedis()

@app.task
def compute_instance(filename, test_run_id):
    rcpparser = RCPParser()
    problem_dict = rcpparser(filename)
    problem = Problem(problem_dict)
    g = GARTH(problem)
    g.run()
    best_dict = {
        'makespan': g.best.makespan,
        'schedule': str(g.best)
    }
    key = "test_run:{}:{}".format(os.path.basename(filename), test_run_id)
    c.lpush(key, g.best.makespan)
    return best_dict


@app.task
def compute_instance_multiple(filename):
    test_run_id = c.incr('test_run_id')
    header = [compute_instance.s(filename, test_run_id) for i in xrange(2)]
    callback = process_run_results.s(filename)
    chord(header)(callback)


@app.task
def process_run_results(result, filename):
    logger.info("Filename %s, results %s", filename, result)
    result_makespan = [d['makespan'] for d in result]
    best_key = 'mybest:'.format(os.path.basename(filename))
    best_makespan = min(result_makespan)
    best_schedule = ''
    for d in result:
        if d['makespan'] == best_makespan:
            best_schedule = d['schedule']
            break
    c.hset(best_key, 'makespan', best_makespan)
    c.hset(best_key, 'schedule', best_schedule)




