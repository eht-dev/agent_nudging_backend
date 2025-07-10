from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
import enum

load_dotenv()

Base = declarative_base()

class TemplateStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    duration_weeks = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)

class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    progress_percent = Column(DECIMAL(5,2), default=0.00)
    last_activity = Column(DateTime, default=datetime.utcnow)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student")
    course = relationship("Course")

class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    points = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course")

class Submission(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    score = Column(DECIMAL(5,2))
    status = Column(String(20), default='submitted')
    
    student = relationship("Student")
    assignment = relationship("Assignment")

class NudgeLog(Base):
    __tablename__ = 'nudges_log'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    nudge_type = Column(String(50))
    message = Column(Text)
    channel = Column(String(20))
    sent_at = Column(DateTime, default=datetime.utcnow)
    opened_at = Column(DateTime)
    action_taken = Column(Boolean, default=False)
    
    student = relationship("Student")

class AgentConfiguration(Base):
    __tablename__ = 'agent_configurations'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(200), nullable=False)
    agent_type = Column(String(100), nullable=False)
    database_config = Column(Text)  # JSON
    query_config = Column(Text)     # JSON
    template_config = Column(Text)  # JSON
    schedule_config = Column(Text)  # JSON
    channel_config = Column(Text)   # JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime)
    next_run = Column(DateTime)

class AgentExecution(Base):
    __tablename__ = 'agent_executions'
    
    id = Column(Integer, primary_key=True)
    agent_config_id = Column(Integer, ForeignKey('agent_configurations.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(50), default='running')
    items_processed = Column(Integer, default=0)
    actions_taken = Column(Integer, default=0)
    execution_log = Column(Text)
    
    agent_config = relationship("AgentConfiguration")

class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    
    id = Column(Integer, primary_key=True)
    template_name = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    template_type = Column(String(100))
    status = Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT)
    created_by_agent = Column(String(100))
    variables = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseConnection(Base):
    __tablename__ = 'database_connections'
    
    id = Column(Integer, primary_key=True)
    connection_name = Column(String(200), nullable=False)
    database_type = Column(String(50), nullable=False)
    connection_string = Column(String(500), nullable=False)
    schema_cache = Column(Text)  # JSON
    last_schema_refresh = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
