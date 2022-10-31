from backend_server.remote_connect import RemoteConnect
from backend_server.tasks import new_tracking, file_tracking

root_connect = RemoteConnect()
tracking_files = new_tracking(root_connect)
