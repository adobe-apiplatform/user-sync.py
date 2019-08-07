from user_sync.helper import JobStats


class PostSyncConnector:

    def __init__(self, **kwargs):
        self.post_sync = kwargs['post_sync']
        self.umapi_info = kwargs['umapi_info']
        self.umapi_connectors = kwargs['umapi_connectors']
        self.directory_groups = kwargs['directory_groups']
        self.directory_connector = kwargs['directory_connector']
        self.logger = kwargs['logger']

        # self.post_sync_modules = ConfigLoader(self.post_sync).get_post_sync_modules()
        # self.post_sync_connectors = ConfigLoader(self.post_sync).get_post_sync_options()

        self.run_post_sync_modules()

    def run_post_sync_modules(self):
        for each_module in self.post_sync:
            job_stats = JobStats(name='Post Sync Module: ' + each_module)
            job_stats.log_start(self.logger)
            job_stats.log_end(self.logger)
