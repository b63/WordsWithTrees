from enum import Enum
from threading import Thread
from queue import Queue

from flask import current_app, g, Flask, cli

from ..graphics.cli import render_tree
from ..graphics.render import Renderer

# global object to hold rendering jobs that need to be rendered
__queue = None
# counter to keep track of rendering jobs
__job_counter = 0
# list to keep track of jobs that have been completed
__jobs_finished = []
# global thread instance
__thread = Queue(1)


def init_queue():
    """
    Initialing global variables that keep track of rendering jobs.
    """
    global __queue
    global __job_counter
    global __jobs_finished

    if __queue is None:
        __queue = Queue()
        __job_counter = 0
        __jobs_finished = []


def _get_queue() -> Queue:
    """
    Returns global :class:`Queue` object that keeps track of pending and ongoing jobs/tasks.
    :return: queue of tasks
    """
    global __queue
    if __queue is None:
        init_queue()
    return __queue


def _get_job_count():
    """
    Returns global counter for job ids.
    :return: current value of counter
    """
    global __job_counter
    return __job_counter


def _increment_job_counter():
    """
    Increments global job counter by one.
    :return: the new value of global job counter
    """

    global __job_counter
    __job_counter += 1
    return __job_counter


def _get_finished_jobs():
    """
    Returns global list object that keeps track of finished rendering tasks.
    :return: list of finished tasks.
    """
    global __jobs_finished
    return __jobs_finished


def _thread_count():
    """
    Returns the number of background threads currently active rendering tiles.
    :return: number of active threads rendering tiles
    """
    global __thread
    return __thread.qsize()


def _set_thread(t):
    """
    Adds the passed in thread instance to the global queue keeping track of active threads `__thread`. Pass `None`
    for :param:`t` to empty the queue.

    :param t: thread to add to queue; since there should only be one active thread rendering the tiles, will raise
        exception since max size of queue is 1. `None` to empty the queue.
    """
    global __thread
    if t:
        __thread.put_nowait(t)
    else:
        __thread.get_nowait()


class JobState(Enum):
    """
    Enum to represent the state of a task.
    """
    NOT_STARTED = 0
    RUNNING = 1
    DONE = 2
    ERROR = 3


class RenderJob:
    """
    Holds information needed in order to carry out the rendering of the branches/tree. In particular, the `tree_id` and
    zoom levels.
    """
    def __init__(self, tree_id, zoom_levels):
        """
        Create instance of :class:`RenderJob` with tree-id `tree_id` and zoom levels given by `zoom_levels`. Leaving
        :param:`zoom_levels` as `None` will result in all zoom levels being rendered (See :class:`Renderer`)

        :param tree_id: id of tree entry
        :param zoom_levels: list of zoom levels at which to render the branches; `None` corresponds to all possible zoom
            levels.
        """
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
        """
        Initialize id of this job with current value of global job counter and set job state to `RUNNING`.
        """
        self.__id = _get_job_count()
        _increment_job_counter()
        self.__state = JobState.RUNNING

    def done(self):
        self.__state = JobState.DONE

    def error(self):
        self.__state = JobState.ERROR


def _handle_render_jobs():
    """
    Keeps rendering branches at requested zoom levels until global queue of jobs is empty.
    """
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
    """
    Runnable that calls `_handle_render_jobs` with application context.
    """
    def __init__(self, app: Flask):
        super().__init__()
        self.__app = app

    def run(self):
        with self.__app.app_context():
            _handle_render_jobs()
        _set_thread(None)


def _start_thread():
    q = _get_queue()

    if q.empty():
        return

    t = RenderThread(current_app._get_current_object())
    t.start()
    _set_thread(t)


def render(zooms=None):
    """
    Render the application tree (tree entry with tree-id given in application configuration under `TREE_ID`) at zoom
    levels specified in `zooms`.
    :param zooms: list of zoom levels to render the tree. Valid zoom levels can be found in `ZOOM_LEVELS` member of
        :class:`Renderer`. A value of `None` corresponds to all possible zoom levels.

    :return: the job id of the resulting job. The rendering of the branches at the requested zoom levels will have
        completed once :meth:`last_render_job` returns an id greater that id of this job.
    """
    global __job_counter
    q = _get_queue()
    tree_id = current_app.config['TREE_ID']

    size = q.qsize()
    min_job_id = _get_job_count()

    if size < 2:
        job = RenderJob(tree_id, zooms)
        q.put_nowait(job)

        # there should be only one thread doing the rendering
        if size == 0 and _thread_count() == 0:
            _start_thread()

    return min_job_id


def last_render_job():
    """
    Returns the id of the last finished job. If the id of a job is smaller than or equal to the value returned by this
    function, then the job has effectively been completed.

    :return: job-id of the last finished rendering job, `-1` if none has yet to complete
    """
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
