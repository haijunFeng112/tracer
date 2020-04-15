import redis
class Redis_Store:
    #创建数据库连接池
    pool = redis.ConnectionPool(host='127.0.0.1',port=6379,password='foobared',encoding='utf-8')
    #去连接池获取一个连接
    conn = redis.Redis(connection_pool=pool)

    def setCode(self,phone_number,code):
        self.conn.set(phone_number,code,ex=60)

    def getCode(self,phone_number):
        value = self.conn.get(phone_number)
        return value
