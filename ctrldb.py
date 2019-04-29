from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey
import datetime
import psycopg2
import json

# dbのユーザとか読み込み
with open('token.json') as f:
    df = json.load(f)

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    text = Column(String)
    ardnotify = orm.relationship("ArdNotify")
    
    def __repr__(self):
        return "<id={}, cat={}, text={}>".format(self.id, self.category, self.text)

class ArdNotify(Base):
    __tablename__ = 'ardnotify'

    id = Column(Integer, primary_key=True)
    server_id = Column(String, ForeignKey('guild.id', onupdate='CASCADE', ondelete='CASCADE'))
    news_id = Column(Integer, ForeignKey('news.id', onupdate='CASCADE', ondelete='CASCADE'))

class Guild(Base):
    __tablename__ = 'guild'

    id = Column(String, primary_key=True)
    name = Column(String)
    prefix = Column(String)
    is_nameread = Column(Boolean, default=False)
    ardnotify = orm.relationship("ArdNotify")
    dictionaly = orm.relationship("Dictionaly")

class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String)
    speaker = Column(String)
    speed = Column(Float, default=1)
    r_range = Column(Float, default=1.1)
    pitch = Column(Float, default=1.2)

class Dictionaly(Base):
    __tablename__ = 'dictionaly'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String)
    read = Column(String)
    server_id = Column(String, ForeignKey('guild.id', onupdate='CASCADE', ondelete='CASCADE'))

class CountRequest(Base):
    __tablename__ = 'countrequest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    hour = Column(Integer)
    count = Column(Integer, default = 0)

class Sessions(Base):
    __tablename__ = 'sessions'

    date_time = Column(DateTime, primary_key=True)
    now_sessions = Column(Integer)
    max_sessions = Column(Integer, default = 0)

url = 'postgresql+psycopg2://{}:{}@{}/{}'.format(df['db_user'], df['password'], df['host'], df['db_name'])
engine = create_engine(url)

def main():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()

Session = orm.sessionmaker(bind=engine)
session = Session()

def get_guild(guild_id):
    guilds = session.query(Guild).filter_by(id=guild_id).one_or_none()

    return guilds