from imports import *

class Measurement(Base):
    __tablename__ = 'measurements'
    measurement_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    latitude = Column(Float)
    longitude = Column(Float)
    signalStrength = Column(Integer)
    downloadSpeed = Column(Float)
    uploadSpeed = Column(Float)
    ping = Column(Integer)