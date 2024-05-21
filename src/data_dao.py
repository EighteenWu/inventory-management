from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from data_model import Part, OperationLog
from datetime import datetime
import configparser

# 创建一个ConfigParser对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini')

# 获取配置文件中的值
db_host = config.get('Database', 'db_host')
db_port = config.getint('Database', 'db_port')  # 如果值是整数，可以使用getint()
db_name = config.get('Database', 'db_name')
db_user = config.get('Database', 'db_user')
db_password = config.get('Database', 'db_password')
engine = create_engine(F'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
Session = sessionmaker(bind=engine)


class PartDAO:
    def add_part(self, part):
        session = Session(bind=engine)
        session.add(part)
        session.commit()
        session.close()

    def get_part_by_drawing_number(self, drawing_number):
        session = Session()
        part = session.query(Part).filter_by(product_drawing_number=drawing_number).first()
        session.close()
        return part

    # 根据图号,产品名称,更改时间范围查找
    def query_data_by_condition(self, drawing_number=None, name=None, start_time=None, end_time=None,
                                log_callback=None):
        session = Session()
        query = session.query(Part)
        if drawing_number:
            query = query.filter(Part.product_drawing_number.like(f'%{drawing_number}%'))
        if name:
            query = query.filter(Part.name.like(f'%{drawing_number}%'))
        if start_time:
            query = query.filter(Part.update_time >= start_time)
        if end_time:
            query = query.filter(Part.update_time <= end_time)
        query = query.filter(Part.update_time <= end_time)
        # if log_callback:
        #     log_callback(f'Executing query: {query}\n Query values:{drawing_number},{name},{start_time},{end_time}')
        parts = query.all()
        session.close()
        return parts

    def update_part_quantity(self, drawing_number, new_quantity):
        session = Session()
        part = session.query(Part).filter_by(product_drawing_number=drawing_number).first()
        if part:
            # 更改时间为当前时间
            part.update_time = datetime.now().strftime('%Y-%m-%d')
            part.inventory_quantity = new_quantity
            session.commit()
        session.close()

    def delete_part_by_drawing_number(self, drawing_number):
        session = Session()
        part = session.query(Part).filter_by(product_drawing_number=drawing_number).first()
        if part:
            session.delete(part)
            session.commit()
        session.close()

    # 查找所有数据
    def query_all_data(self):
        session = Session()
        parts = session.query(Part).all()
        session.close()
        return parts

    def batch_delete(self, drawing_numbers, log_callback):
        session = Session()
        session.query(Part).filter(Part.product_drawing_number.in_(drawing_numbers)).delete(synchronize_session=False)
        if log_callback:
            log_callback(f'Deleting parts with drawing numbers: {drawing_numbers}')
        session.commit()
        session.close()

    def update_part(self, part):
        session = Session()
        # 更改时间为当前时间
        part.update_time = datetime.now().strftime('%Y-%m-%d')
        session.merge(part)
        session.commit()
        session.close()


class OperationLogDAO:
    def add_operation_log(self, log):
        session = Session()
        session.add(log)
        session.commit()
        session.close()

    def get_logs_by_drawing_number(self, drawing_number):
        session = Session()
        logs = session.query(OperationLog).filter_by(product_drawing_number=drawing_number).all()
        session.close()
        return logs

    def delete_logs_by_drawing_number(self, drawing_number):
        session = Session()
        session.query(OperationLog).filter_by(product_drawing_number=drawing_number).delete()
        session.commit()
        session.close()
