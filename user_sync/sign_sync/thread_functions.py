from threading import Thread


class ThreadWorker(Thread):
    def __init__(self, queue, func):
        """
        This function initialized the thread
        :param queue: list[]
        :param func: def()
        """
        Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self.func = func

    def run(self):
        """
        This function runs the tread and adds it to the queue
        """
        while True:
            user = self.queue.get()
            try:
                self.func(user)
            finally:
                self.queue.task_done()
