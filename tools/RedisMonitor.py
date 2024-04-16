
import redis

class RedisMonitor():
    def __init__(self, connection_pool):
     self.connection_pool = connection_pool
     self.connection = None

    def __del__(self):
     try:
      self.reset()
     except:
      pass

    def reset(self):
     if self.connection:
      self.connection_pool.release(self.connection)
      self.connection = None

    def monitor(self):
     if self.connection is None:
      self.connection = self.connection_pool.get_connection(
       'monitor', None)
     self.connection.send_command("monitor")
     return self.listen()

    def parse_response(self):
     return self.connection.read_response()

    def listen(self):
     while True:
      yield self.parse_response()

if __name__ == '__main__':
    # pool = redis.ConnectionPool(host='10.89.89.219', port=6379, db=6,password="9ifiEKRaH0Ifk" ,socket_connect_timeout=10) # gs redis
    # pool = redis.ConnectionPool(host='10.89.89.109', port=6379, db=6, password="crs-huzuxxpe:ray9m%nm*",socket_connect_timeout=10)  # 主redis
    # pool = redis.ConnectionPool(host='10.89.89.203', port=6379, password="ebDN8SGFUV" )  # user api
    pool = redis.Redis(host='10.89.89.109', port=6379,  password="crs-huzuxxpe:ray9m%nm*")


    monitor = RedisMonitor(pool)
    # commands = monitor.monitor()

    # with open("redis.log", "w") as f:
    #     f.writelines('')
    for c in monitor.monitor() :
        print(c)
        with open("redis.log","a") as f:
            f.writelines(str(c)+'\n')
