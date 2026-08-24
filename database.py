import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATABASE_URL=os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR,'tera_projekt_v3.db')}")
kwargs={'connect_args':{'check_same_thread':False}} if DATABASE_URL.startswith('sqlite') else {'pool_pre_ping':True}
engine=create_engine(DATABASE_URL, **kwargs)
SessionLocal=sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base=declarative_base()
