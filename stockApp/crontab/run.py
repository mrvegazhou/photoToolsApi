# coding:utf8
import sys, os, inspect
PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(inspect.getfile(inspect.currentframe())))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from pytz import utc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from core.log.logger import get_module_logger
from stockApp.modules.dataLoader.stockData.eastIntradayData import EastIntradayData
from stockApp.modules.dataLoader.stockData.eastMarketRealTime import EastMarketRealTime


if __name__ == '__main__':

    def get_stock_codes():
        east = EastMarketRealTime()
        df = east.get_market_real_time('all_stocks')
        print(df.shape)


    def job_funcs():
        intradayData = EastIntradayData()
        intradayData.get_intraday_data()


    get_stock_codes()
    
    exit(1)


    executors = {
        'default': ThreadPoolExecutor(200),
        'processpool': ProcessPoolExecutor(10)
    }
    job_defaults = {
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 60
    }
    sched = BackgroundScheduler(job_defaults=job_defaults, timezone=utc)
    sched.add_job(job_funcs, 'cron', day_of_week='mon-fri', hour=15, minute=30,)

    def job_listener(Event):
        job = sched.get_job(Event.job_id)
        if not Event.exception:
            get_module_logger('crontab').info("job name=%s|job trigger=%s|job time=%s|retval=%s" % (job.name, job.trigger, Event.scheduled_run_time, Event.retval))
        else:
            get_module_logger('crontab').error("job name=%s|job trigger=%s|job time=%s|retval=%s" % (job.name, job.trigger, Event.scheduled_run_time, Event.retval))

    sched.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED | EVENT_JOB_MISSED)
    sched._logger = get_module_logger('crontab')
    sched.start()