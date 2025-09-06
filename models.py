from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./sebi.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Advisor(Base):
    __tablename__ = "advisors"
    sr_no = Column("SR NO.", Integer)
    sebi_reg_no = Column("SEBI REGISTRATION NO", String, primary_key=True, index=True)
    name = Column("RESEARCH ANALYST NAME", String, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
