# -*- coding: utf-8 -
from src.main.mysql.public.public import *
'''
mock_server mock服务存储表
'''


class MockServers(Base, TypeCast):

    # mock配置表
    __tablename__ = 'mock_servers'
    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    deleted_at = Column(TIMESTAMP)
    url = Column(String(255), nullable=False, comment='url地址')
    method = Column(String(25), nullable=False, comment='请求方法')
    is_available = Column(String(25), nullable=False, comment='是否启用')
    delay = Column(Integer, nullable=False, comment='延时响应时间(s)')
    resp_code = Column(Integer, nullable=False, comment='响应编码')
    remark = Column(TEXT, nullable=False, comment='接口描述')

    def mock_servers_func(self, way, *parm):
        time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
        if way == "insert":
            data = parm[0]  # data = {"url": , "method": , "is_available": , "delay": , "resp_code": , "remark": }
            add_data = MockServers(created_at=time, url=data['url'], method=data['method'],
                                   is_available=data['is_available'], delay=data['delay'], resp_code=data['resp_code'],
                                   remark=data['remark'])
            session.add(add_data)
            session.commit()
            new_data = add_data.to_dict()  # 获取添加入数据库的所有数据,并转为dict
            session.close()
            return new_data
        elif way == "delete":
            id = parm[0]
            session.query(MockServers).filter(MockServers.id == id).update({"deleted_at": time})
            session.commit()
            session.close()
        elif way == "update":
            id = parm[0]
            data = parm[1]  # data = {"url": , "method": , "is_available": , "delay": , "resp_code": , "req_remark": }
            update_data = dict({"updated_at": time}, **data)
            session.query(MockServers).filter(MockServers.id == id).update(update_data)
            session.commit()
            new_data = session.query(MockServers).filter(MockServers.id == id).first()
            session.close()
            return new_data.to_dict()
        elif way == "get":
            operation = parm[0]
            if operation == "all_info":
                t = session.query(MockServers).filter(MockServers.deleted_at == None).all()
                session.close()
                return self.to_json(t)
            elif operation == "specific_num_info":
                start = parm[1]
                num = parm[2]
                t = session.query(MockServers).filter(MockServers.deleted_at == None).offset(start).limit(num).all()
                session.close()
                return self.to_json(t)
            elif operation == "first_by_id":
                id = parm[1]
                t = session.query(MockServers).filter(MockServers.id == id, MockServers.deleted_at == None).first()
                session.close()
                return t.to_dict()
            elif operation == "first_by_url":
                url = parm[1]
                t = session.query(MockServers).filter(MockServers.url == url, MockServers.deleted_at == None).first()
                session.close()
                return t.to_dict()
            elif operation == "all_id":
                t = session.query(MockServers.id).filter(MockServers.deleted_at == None).all()
                session.close()
                return t
            elif operation == "all_url":
                t = session.query(MockServers.url).filter(MockServers.deleted_at == None).all()
                session.close()
                return t