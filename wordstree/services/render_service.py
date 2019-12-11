from enum import Enum
from threading import Thread
from queue import Queue

from flask import current_app, g, Flask, cli

from ..graphics.cli import render_tree
from ..graphics.render import Renderer

__queue = None
__job_counter = 0
__jobs_finished = []


def init_queue():
    global __queue
    global __job_counter
    global __jobs_finished

    if __queue is None:
        __queue = Queue()
        __job_counter = 0
        __jobs_finished = []


def _get_queue() -> Queue:
    global __queue
    if __queue is None:
        init_queue()
    return __queue


def _get_job_count():
    global __job_counter
    return __job_counter


def _increment_job_counter():
    global __job_counter
    __job_counter += 1
    return __job_counter


def _get_finished_jobs():
    global __jobs_finished
    return __jobs_finished


class JobState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    DONE = 2
    ERROR = 3


class RenderJob:
    def __init__(self, tree_id, zoom_levels):
        self.__id = None
        self.__tree_id = tree_id

        if zoom_levels is None:
            zoom_levels = []
        self.__zoom_levels = zoom_levels
        self.__state = JobState.NOT_STARTED

    @property
    def id(self):
        return self.__id

    @property
    def tree_id(self):
        return self.__tree_id

    @property
    def zoom_levels(self):
        return self.__zoom_levels

    @property
    def state(self):
        return self.__state

    def started(self):
        self.__id = _get_job_count()
        _increment_job_counter()
        self.__state = JobState.RUNNING

    def done(self):
        self.__state = JobState.DONE

    def error(self):
        self.__state = JobState.ERROR


def _handle_render_jobs():
    q = _get_queue()

    size = q.qsize()
    while size > 0:
        job = q.get()

        job.started()
        max_zoom = len(Renderer.ZOOM_LEVELS) - 1
        if not job.zoom_levels or len(job.zoom_levels) == 0:
            # render_tree cli commands expects arguments as a string of integers '1,2,3 ..etc'
            zooms = ','.join([str(i) for i in range(max_zoom + 1)])
        else:
            zooms = ','.join(job.zoom_levels)

        tree_id = job.tree_id

        try:
            current_app.cli.get_command(current_app.app_context(), 'render')\
                .main(args=['-z', zooms, '-f', 'db:{}'.format(tree_id)])
        except SystemExit as e:
            pass

        job.done()
        q.task_done()
        _get_finished_jobs().append(job)

        size = q.qsize()


class RenderThread(Thread):
    def __init__(self, app: Flask):
        super().__init__()
        self.__app = app

    def run(self):
        with self.__app.app_context():
            _handle_render_jobs()


def _start_thread():
    q = _get_queue()

    if q.empty():
        return

    t = RenderThread(current_app._get_current_object())
    t.start()


def render(zooms=None):
    global __job_counter
    q = _get_queue()
    tree_id = current_app.config['TREE_ID']

    size = q.qsize()
    min_job_id = _get_job_count()

    if size < 2:
        job = RenderJob(tree_id, zooms)
        q.put_nowait(job)

        # there should be only one thread doing the rendering
        if size == 0:
            _start_thread()

    return min_job_id


def last_render_job():
    global __queue

    if __queue is None:
        return -1

    finished = _get_finished_jobs()
    size = len(finished)
    if size < 1:
        return -1
    else:
        last_job = finished[-1]
        return last_job.id
