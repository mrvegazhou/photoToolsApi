# -*- coding: utf-8 -*-
import six
from datetime import datetime, timedelta

from flask_apscheduler import APScheduler as _BaseAPScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.executors.base import MaxInstancesReachedError
from apscheduler.events import (JobSubmissionEvent, EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES)
from apscheduler.util import (timedelta_seconds, TIMEOUT_MAX)
from ..config.sys_config import config
from ..cache.redisLock import RedisLock

# 重写APScheduler，实现上下文管理机制，小优化功能也可以不要。对于任务函数涉及数据库操作有用
# 操作db需要app，而定时器在后台运行实际上是找不到app的，需要push一个app context给它，让它在上下文里面工作
class APScheduler(_BaseAPScheduler):

    def run_job(self, id, jobstore=None):
        with self.app.app_context():
            super().run_job(id=id, jobstore=jobstore)

ENV = config['env']
CONFIG = config[ENV]

job_defaults = {
    #是否合并执行任务默认为True
    'coalesce': True,
    'max_instances': 1,
    #添加允许容错的时间
    'misfire_grace_time': 60,
    #将任务持久化至数据库中时，此参数必须添加，值为True。并且id值必须有。不然当程序重新启动时，任务会被重复添加
    'replace_existing': True
}
# 设置定时任务运行的线程和进程，可选配置
executors = {
    'default': ThreadPoolExecutor(CONFIG.SCHEDULER_EXECUTORS),  # 默认线程数
    'processpool': ProcessPoolExecutor(4)  # 默认进程
}
# host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, db=CONFIG.REDIS_DB, password=CONFIG.REDIS_PASSWORD
redisJobStore = RedisJobStore(**CONFIG.SCHEDULER_JOBSTORES)
jobstores = {
    'redis': redisJobStore
}


#: constant indicating a scheduler's stopped state
STATE_STOPPED = 0
#: constant indicating a scheduler's running state (started and processing jobs)
STATE_RUNNING = 1
#: constant indicating a scheduler's paused state (started but not processing jobs)
STATE_PAUSED = 2

class DistributedBackgroundScheduler(BackgroundScheduler):
    _redis_client = None
    _lock_timeoout = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.redis_client = redis_client
        # self.lock_timeoout = lock_timeoout

    @property
    def redis_client(self):
        return self._redis_client

    @redis_client.setter
    def redis_client(self, redis_client):
        self._redis_client = redis_client

    @property
    def lock_timeoout(self):
        return self._lock_timeoout

    @lock_timeoout.setter
    def lock_timeoout(self, lock_timeoout):
        self._lock_timeoout = lock_timeoout

    def _process_jobs(self):
        """
        重写_process_jobs，使用redis分布式锁解决分布式问题
        Iterates through jobs in every jobstore, starts jobs that are due and figures out how long
        to wait for the next round.
        If the ``get_due_jobs()`` call raises an exception, a new wakeup is scheduled in at least
        ``jobstore_retry_interval`` seconds.
        """
        if self.state == STATE_PAUSED:
            self._logger.debug('Scheduler is paused -- not processing jobs')
            return None

        self._logger.debug('Looking for jobs to run')
        now = datetime.now(self.timezone)
        next_wakeup_time = None
        events = []
        with self._jobstores_lock:
            for jobstore_alias, jobstore in six.iteritems(self._jobstores):
                try:
                    due_jobs = jobstore.get_due_jobs(now)
                except Exception as e:
                    # Schedule a wakeup at least in jobstore_retry_interval seconds
                    self._logger.warning('Error getting due jobs from job store %r: %s',
                                         jobstore_alias, e)
                    retry_wakeup_time = now + timedelta(seconds=self.jobstore_retry_interval)
                    if not next_wakeup_time or next_wakeup_time > retry_wakeup_time:
                        next_wakeup_time = retry_wakeup_time

                    continue

                for job in due_jobs:
                    # 获取分布式锁
                    key = 'jobs' + job.id
                    print("self.lock_timeoout:", self.lock_timeoout)
                    with RedisLock(redis_client=self.redis_client, lock_key=key, lock_timeoout=self.lock_timeoout) as lock:
                        if lock:
                            # Look up the job's executor
                            try:
                                executor = self._lookup_executor(job.executor)
                            except BaseException:
                                self._logger.error(
                                    'Executor lookup ("%s") failed for job "%s" -- removing it from the '
                                    'job store', job.executor, job)
                                self.remove_job(job.id, jobstore_alias)
                                continue

                            run_times = job._get_run_times(now)
                            run_times = run_times[-1:] if run_times and job.coalesce else run_times
                            if run_times:
                                try:
                                    executor.submit_job(job, run_times)
                                except MaxInstancesReachedError:
                                    self._logger.warning(
                                        'Execution of job "%s" skipped: maximum number of running '
                                        'instances reached (%d)', job, job.max_instances)
                                    event = JobSubmissionEvent(EVENT_JOB_MAX_INSTANCES, job.id,
                                                               jobstore_alias, run_times)
                                    events.append(event)
                                except BaseException:
                                    self._logger.exception('Error submitting job "%s" to executor "%s"',
                                                           job, job.executor)
                                else:
                                    event = JobSubmissionEvent(EVENT_JOB_SUBMITTED, job.id, jobstore_alias,
                                                               run_times)
                                    events.append(event)

                                # Update the job if it has a next execution time.
                                # Otherwise remove it from the job store.
                                job_next_run = job.trigger.get_next_fire_time(run_times[-1], now)
                                if job_next_run:
                                    job._modify(next_run_time=job_next_run)
                                    jobstore.update_job(job)
                                else:
                                    self.remove_job(job.id, jobstore_alias)
                # Set a new next wakeup time if there isn't one yet or
                # the jobstore has an even earlier one
                jobstore_next_run_time = jobstore.get_next_run_time()
                if jobstore_next_run_time and (next_wakeup_time is None or
                                               jobstore_next_run_time < next_wakeup_time):
                    next_wakeup_time = jobstore_next_run_time.astimezone(self.timezone)

        # Dispatch collected events
        for event in events:
            self._dispatch_event(event)

        # Determine the delay until this method should be called again
        if self.state == STATE_PAUSED:
            wait_seconds = None
            self._logger.debug('Scheduler is paused; waiting until resume() is called')
        elif next_wakeup_time is None:
            wait_seconds = None
            self._logger.debug('No jobs; waiting until a job is added')
        else:
            wait_seconds = min(max(timedelta_seconds(next_wakeup_time - now), 0), TIMEOUT_MAX)
            self._logger.debug('Next wakeup is due at %s (in %f seconds)', next_wakeup_time,
                               wait_seconds)

        return wait_seconds

bgs = DistributedBackgroundScheduler(timezone=CONFIG.SCHEDULER_TIMEZONE, jobstores=jobstores, job_defaults=job_defaults, executors=executors)
scheduler = APScheduler(bgs)
redisJobStore.remove_all_jobs()