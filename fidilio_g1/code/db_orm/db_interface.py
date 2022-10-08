import datetime
import pandas as pd
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Text,
                        Column, Boolean, Time,
                        ForeignKey, PrimaryKeyConstraint,
                        Float)
from sqlalchemy import or_, and_


Base = declarative_base()


class DBManager:

    def __init__(self, user, password, host, db) -> None:
        self.engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}/{db}')
        self.inspector = inspect(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def bulk_create(self, tb_cls, kwargs_list: list):
        with self.Session() as session:
            session.begin()
            try:
                session.add_all([tb_cls(**kwarg) for kwarg in kwargs_list])
            except:
                session.rollback()
                raise
            else:
                session.commit()
            session.close()

    def create(self, tb_cls, kwargs):
        with self.Session() as session:
            session.begin()
            try:
                session.add(tb_cls(**kwargs))
            except:
                session.rollback()
                raise
            else:
                session.commit()
            session.close()

    def query(self, tb_cls):
        self.session.close()
        return self.session.query(tb_cls)

    def values(self, queryset, *cols):
        all_cols = queryset[0].__table__.columns.keys()
        return [{col: getattr(obj, col) for col in cols} for obj in queryset] if cols else\
            [{col: getattr(obj, col) for col in all_cols} for obj in queryset]

    def get_df(self, values):
        return pd.DataFrame(values)


class Cafe(Base):
    __tablename__ = 'cafe'
    cafe_id = Column(Integer, primary_key=True, autoincrement=True)
    cafe_name = Column('cafe_name', String(64))
    city = Column('city', String(64))
    province = Column('province', String(64))
    phone_number = Column('phone_number', String(64))
    cost = Column(Integer)
    work_start = Column(Time, nullable=True)
    work_end = Column(Time, nullable=True)
    rate = Column(Float)

    def __repr__(self):
        return '<Cafe %r>' % (self.cafe_name)


class CafeAddress(Base):
    __tablename__ = 'cafe_address'
    __table_args__ = (
        PrimaryKeyConstraint('cafe_id'), {},
    )
    cafe_id = Column(Integer, ForeignKey('cafe.cafe_id'))
    cafe_address = Column(String(256))
    lat = Column(String(32))
    lng = Column(String(32))


class CafeFeatures(Base):
    __tablename__ = 'cafe_features'
    __table_args__ = (
        PrimaryKeyConstraint('cafe_id'), {},
    )
    cafe_id = Column(Integer, ForeignKey('cafe.cafe_id'))
    hookah = Column(Boolean, default=False)
    internet = Column(Boolean, default=False)
    delivery = Column(Boolean, default=False)
    smoking = Column(Boolean, default=False)
    open_space = Column(Boolean, default=False)
    live_music = Column(Boolean, default=False)
    parking = Column(Boolean, default=False)
    pos = Column(Boolean, default=False)


class CafeRating(Base):
    __tablename__ = 'cafe_rating'
    __table_args__ = (
        PrimaryKeyConstraint('cafe_id'), {},
    )
    cafe_id = Column(Integer, ForeignKey('cafe.cafe_id'))
    food_quality = Column(Integer)
    service_quality = Column(Integer)
    cost = Column(Integer)
    cost_value = Column(Integer)
    environment = Column(Integer)


if __name__ == '__main__':
    # dbm.session : session object
    # user = 'user_group1'
    # password = 'AWsWrGBjjyrA_group1'
    # host = '45.139.10.138:80'
    # db = 'group1'
    dbm = DBManager('amir_quera', 'quera', '127.0.0.1', 'group1')
    # simple filters
    # returns all the Cafes for a specific author
    lCafes = dbm.query(Cafe).filter_by(cafe_id=1)

    # more complex filters
    # returns all the Cafes with cost <3. Note we use filter, not filter_by
    lCafes = dbm.query(Cafe).filter(Cafe.cost < 3)

    # filters can be combined
    lCafes = dbm.query(Cafe).filter_by(cafe_id=1).filter(
        Cafe.cost < 25)  # all Cafes by a specific author, with cost<20

    # logical operations can be used in filters
    from sqlalchemy import or_
    # returns all Cafes  that cost less than 3 OR are being promoted
    lCafes = dbm.query(Cafe).filter(
        or_(Cafe.cost < 3, Cafe.city == 'Tehran'))
    lCafes = dbm.query(Cafe).filter(
        and_(Cafe.cost < 3, Cafe.city == 'Tehran'))

    # ordering
    from sqlalchemy import desc
    dbm.query(Cafe).order_by(Cafe.cost)  # get all Cafes ordered by cost
    # get all Cafes ordered by cost descending
    dbm.query(Cafe).order_by(desc(Cafe.cost))

    # other useful things
    dbm.query(Cafe).count()  # returns the number of Cafes
    dbm.query(Cafe).limit(5).all()  # return at most 5 Cafes
    dbm.query(Cafe).first()  # return the first Cafe only or None
    dbm.query(Cafe).get(2)  # return the Cafe with primary key = 2, or None

    # delete rows
    dbm.session.query(Cafe).filter(Cafe.cafe_name == 'Leo').delete()
    dbm.session.commit()

    objs = dbm.query(Cafe).all()
    # query set values
    values = dbm.values(objs, 'city')
    values = dbm.values(objs)
    # get df
    cafe_df = dbm.get_df(values)

    # dbm.create(Cafe, {
    #     'cafe_name': 'Ketab',
    #     'city': 'Isfahan',
    #     'province': 'Abas Abad',
    #     'cost': 4,
    # })
    # dbm.bulk_create(Cafe,[dict(
    #     cafe_name='yooo', city='Munich',
    #     province='Bavaria', cost=i)for i in range(1,5)])

    # update rows
    dbm.session.query(Cafe).filter(Cafe.cafe_name == 'Leo').update(
        {Cafe.cost: 20}, synchronize_session=False)
    dbm.session.commit()  # Important!
