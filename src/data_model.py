from sqlalchemy import String, Integer, Column, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Part(Base):
    def __str__(self):
        return (
            f'Part(产品序号={self.no},产品名称={self.name},产品图号={self.product_drawing_number}, update_time={self.update_time}')

    __tablename__ = 'inventoryInfo'

    no = Column('物料编号', Integer())  # 物料编号
    product_drawing_number = Column('产品图号', String(20), primary_key=True)  # 产品图号
    name = Column('产品名称', String(20))  # 名称
    inventory_quantity = Column('库存数量', Integer())  # 库存数量
    a_group_total = Column('1组', Integer())  # a组数量
    b_group_total = Column('2组', Integer())  # b组数量
    quantity_per_carton = Column('每箱数量', Integer())  # 每箱数量
    update_time = Column('上次更改日期', Date)  # 更新时间
    id = Column('id', String(99))  # id

    # 定义与 OperationLog 模型的关系
    operation_logs = relationship("OperationLog", back_populates="part")


class OperationLog(Base):
    __tablename__ = 'operation_log'

    id = Column('序号', Integer(), primary_key=True, autoincrement=True)  # 序号
    time = Column('时间', Date)  # 时间
    product_drawing_number = Column('产品图号', String(20), ForeignKey('inventoryInfo.产品图号'),
                                    primary_key=True)  # 产品图号
    operator_type = Column('操作类型', String(6))  # 操作类型
    operator_fields = Column('操作字段', String(10))  # 操作字段
    value_before_change = Column('更改前值', String(20))  # 更改前值
    changed_value = Column('更改后值', String(20))  # 更改后值

    # 定义与 Part 模型的关系
    part = relationship("Part", back_populates="operation_logs")
