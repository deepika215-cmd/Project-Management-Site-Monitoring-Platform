from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.database import Base
class ProjectStatusHistory(Base):
    __tablename__='project_status_history'
    id=Column(Integer,primary_key=True,index=True)
    project_id=Column(Integer,ForeignKey('projects.id'),nullable=False)
    old_status=Column(String(50),nullable=True)
    new_status=Column(String(50),nullable=False)
    changed_by=Column(Integer,ForeignKey('users.id'),nullable=False)
    changed_at=Column(DateTime,default=datetime.utcnow,nullable=False)
