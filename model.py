from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine('postgresql://localhost:5432/ofashion', echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit=False,
                                      autoflush=False))
Base = declarative_base()
Base.query = session.query_property()

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class User(Base):
	__tablename__="users"

	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False, index=True)
	email = Column(String(64), nullable =False)
	password = Column(String(64), nullable=False)
	location_id = Column(Integer, ForeignKey('locations.id'))
	location = relationship("Location", backref=backref("users"))

class Picture(Base):
	__tablename__="pictures"
	id = Column (Integer, primary_key=True)
	filename = Column(String, nullable=False, unique=True)
	notes = Column(String, nullable=True)
	style = Column(String, nullable=False)
	user_id = Column(Integer, ForeignKey('users.id'))
	location_id = Column(Integer, ForeignKey('locations.id'))

	user = relationship("User", backref=backref("pictures", order_by=id))
	location = relationship("Location", backref=backref("pictures"))

class Location(Base):
	__tablename__="locations"
	id = Column(Integer, primary_key=True)
	location_name = Column(String,nullable=False)

# class Avatar(Base):
# 	__table__="avatars"
# 	id = Column (Integer, primary_key=True)
# 	filename = Column(String, nullable=False, unique=True)
# 	user_id = Column(Integer, ForeignKey('users.id'))
# 	user = relationship("User", backref=backref("profile_pics", order_by=id))

# def connect():
    # global ENGINE
    # global Session

    # ENGINE = create_engine("sqlite:///temp.db", echo=True)
    # Session = sessionmaker(bind=ENGINE)

    # return Session()

# Base.metadata.create_all(engine)
# print 'below create all'


def main():
    pass

if __name__ == "__main__":
    main()

