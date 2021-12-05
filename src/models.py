from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DBMixin:
    timestamp = None

    @classmethod
    def get_or_create(cls, session, **kwargs):
        symbol = kwargs.get('symbol')
        exchange = kwargs.get('exchange')
        timestamp = kwargs.get('timestamp')
        instance = session.query(cls).filter_by(symbol=symbol, exchange=exchange, timestamp=timestamp).first()
        if instance:
            return session
        else:
            instance = cls(**kwargs)
            session.add(instance)
            return session

    @classmethod
    def get_last(cls, session, limit=50):
        return session.query(cls).order_by(cls.timestamp.desc()).limit(limit).all()


class Bars(Base, DBMixin):
    __tablename__ = 'bars'
    __table_args__ = (
        UniqueConstraint('symbol', 'exchange', 'timestamp', name='uix_bars_symbol_timestamp'),
    )

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10))
    exchange = Column(String(10))
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    timestamp = Column(DateTime)
    trade_count = Column(Integer)
    vwap = Column(Float)

# from peewee import Model, FloatField, CharField, IntegerField, DateTimeField, CompositeKey
#
# from src.settings import db
#
#
# class BaseModel(Model):
#     """Base model class"""
#
#     class Meta:
#         database = db
#
#
# class BarModel(BaseModel):
#     symbol = CharField()
#     exchange = CharField()
#     high = FloatField()
#     low = FloatField()
#     open = FloatField()
#     close = FloatField()
#     timestamp = DateTimeField()
#     volume = FloatField()
#     trade_count = IntegerField()
#     vwap = FloatField()
#
#     class Meta:
#         primary_key = CompositeKey('symbol', 'exchange', 'timestamp')
#
#
# class QuoteModel(BaseModel):
#     ask_size = FloatField(default=0.0)
#     ask_price = FloatField(default=0.0)
#     bid_price = FloatField(default=0.0)
#     bid_size = FloatField(default=0.0)
#     exchange = CharField()
#     symbol = CharField()
#     timestamp = DateTimeField()
#
#
# class TradeModel(BaseModel):
#     id = IntegerField(primary_key=True)
#     price = FloatField()
#     size = FloatField()
#     symbol = CharField()
#     takerside = CharField()
#     timestamp = DateTimeField()
