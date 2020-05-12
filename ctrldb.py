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
    dictionaly = orm.relationship("GuildSetting")

class GuildSetting(Base):
    __tablename__ = 'guildsetting'

    server_id = Column(String, ForeignKey('guild.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    bot_id = Column(String, primary_key=True)
    prefix = Column(String)
    is_nameread = Column(Boolean, default=False)
    is_whitelist = Column(Boolean, default=False)
    readlimit = Column(Integer, default=40)

class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String)
    speaker = Column(String)
    speed = Column(Float, default=1)
    r_range = Column(Float, default=1.1)
    pitch = Column(Float, default=1.2)

class DailyUser(Base):
    __tablename__ = 'dailyuser'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    u_id = Column(String)

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
session.execute("SET search_path TO public")

def add_news(cat, mess):
    news = News(category=cat, text=mess)

    session.add(news)
    session.commit()
    session.close()

def get_news():
    news = session.query(News)

    return news

def add_notify(news_id, guild_id):
    notified = ArdNotify(server_id=guild_id ,news_id=news_id)

    session.add(notified)
    session.commit()
    session.close()

def get_notify(guild_id):
    notifications = session.query(ArdNotify).filter_by(server_id=guild_id)

    return notifications

def add_guild(guild_id, prefix, bot_id):
    dguild = GuildSetting(server_id=guild_id, prefix=prefix, bot_id=bot_id)
    session.add(dguild)
    session.commit()

def add_guild_name(guild_id, name):
    guild = Guild(id=guild_id, name=name)
    session.add(guild)
    session.commit()
    session.close()

def set_prefix(guild_id, prefix, bot_id):
    guild = session.query(GuildSetting).filter_by(server_id=guild_id, bot_id=bot_id).one()
    guild.prefix = prefix

    session.commit()
    session.close()

def set_guild_name(guild_id, guild_name):
    guild = session.query(Guild).filter_by(id=guild_id).one()
    guild.name = guild_name

    session.commit()
    session.close()

def get_guild_name(guild_id):
    guild = session.query(Guild).filter_by(id=guild_id).one_or_none()

    return guild

def set_readlimit(guild_id, bot_id, limitnum):
    guild = session.query(GuildSetting).filter_by(server_id=guild_id, bot_id=bot_id).one_or_none()
    guild.readlimit = limitnum

    session.commit()
    session.close()
    return limitnum

def get_guild(guild_id, bot_id):
    guilds = session.query(GuildSetting).filter_by(server_id=guild_id, bot_id=bot_id).one_or_none()

    return guilds

def add_user(user_id, name, speaker):
    user = User(id=user_id, name=name, speaker=speaker)

    session.add(user)
    session.commit()
    session.close()

def set_user(user_id, speaker):
    user = session.query(User).filter_by(id=user_id).one()
    user.speaker = speaker

    session.commit()
    session.close()

def get_user(user_id):
    users = session.query(User).filter_by(id=user_id).one_or_none()

    return users

def add_dict(word, read, server_id):
    dictionary = session.query(Dictionaly).filter_by(word=word, server_id=server_id).one_or_none()
    if isinstance(dictionary, type(None)):
        dictionary = Dictionaly(word=word, read=read, server_id=server_id)

        session.add(dictionary)
        session.commit()
        session.close()
    else:
        set_dict(read, dictionary)

def set_dict(read, dictionary):
    dictionary.read = read

    session.commit()
    session.close()

def get_dict(server_id):
    dictionary = session.query(Dictionaly).filter_by(server_id=server_id)

    return dictionary

def del_dict(id, str_id):
    found_dict = session.query(Dictionaly).filter_by(id=id, server_id=str_id).one_or_none()
    
    if isinstance(found_dict, type(None)):
        return None
    else:
        session.delete(found_dict)
        session.commit()
        session.close()
        return True

def search_dict(str_id, word):
    found_dict = session.query(Dictionaly).filter_by(word=word, server_id=str_id).one_or_none()

    return found_dict

def del_all_dict(str_id):
    session.query(Dictionaly).filter_by(server_id=str_id).delete()
    session.commit()
    session.close()

def set_nameread(is_read, guild_id, bot_id):
    found_guild = session.query(GuildSetting).filter_by(server_id=guild_id, bot_id=bot_id).one_or_none()
    if isinstance(found_guild, type(None)):
        return None
    else:
        found_guild.is_nameread = is_read
        session.commit()
        session.close()
        return 0

def set_whitelist(is_white, guild_id, bot_id):
    found_guild = session.query(GuildSetting).filter_by(server_id=guild_id, bot_id=bot_id).one_or_none()

    if isinstance(found_guild, type(None)):
        return None
    else:
        found_guild.is_whitelist = is_white
        session.commit()
        session.close()

def set_readspeed(prm, id):
    found_user = session.query(User).filter_by(id=id).one_or_none()

    if isinstance(found_user, type(None)):
        return None
    else:
        found_user.speed = prm
        session.commit()
        session.close()

def set_readrange(prm, id):
    found_user = session.query(User).filter_by(id=id).one_or_none()

    if isinstance(found_user, type(None)):
        return None
    else:
        found_user.r_range = prm
        session.commit()
        session.close()

def set_readpitch(prm, id):
    found_user = session.query(User).filter_by(id=id).one_or_none()

    if isinstance(found_user, type(None)):
        return None
    else:
        found_user.pitch = prm
        session.commit()
        session.close()

def set_reqcount(date, time):
    found_rec = session.query(CountRequest).filter_by(date = date, hour = time).one_or_none()

    if isinstance(found_rec, type(None)):
        get_recs = session.query(CountRequest.hour).filter_by(date = date).all()
        recs = list()
        for rec in get_recs:
            recs.append(rec.hour)
        zero_cts = list()
        for i in range(0, time+1):
            if not i in recs:
                zero_ct = CountRequest(date = date, hour = i)
                zero_cts.append(zero_ct)
        session.add_all(zero_cts)
        session.commit()
        session.close()

        found_rec = session.query(CountRequest).filter_by(date = date, hour = time).one()
    
    found_rec.count += 1
    session.commit()
    session.close()

def set_session(dt, ss_num):
    found_data = session.query(Sessions).filter_by(date_time=dt).one_or_none()

    if found_data is None:
        new_data = Sessions(date_time = dt, now_sessions = ss_num)
        session.add(new_data)
        session.commit()
        session.close()

        found_data = session.query(Sessions).filter_by(date_time=dt).one_or_none()
    
    found_data.now_sessions = ss_num
    if found_data.max_sessions < ss_num:
        found_data.max_sessions = ss_num
    
    session.commit()
    session.close()

def add_daily_user(date, uid):
    new_data = DailyUser(date=date, u_id=uid)
    session.add(new_data)
    session.commit()
    session.close()

def get_daily_user(date):
    data = session.query(DailyUser).filter_by(date=date)

    return data

def move_guild():
    detas = session.query(Guild)

    for deta in detas:
        new = GuildSetting(server_id=deta.id, bot_id='518899666637553667', prefix=deta.prefix, is_nameread=deta.is_nameread)
        session.add(new)

    session.commit()
    session.close()