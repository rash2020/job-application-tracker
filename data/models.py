from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, Text

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = 'job_applications'

    id = Column(Integer, primary_key=True)
    company = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    date_applied = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<JobApplication(company={self.company}, position={self.position}, date={self.date_applied}, status={self.status})>"
