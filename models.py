from sqlalchemy import Column,Integer,String,Float,Date,Text,DateTime,Boolean,ForeignKey
from database import Base
from datetime import datetime
class User(Base):
 __tablename__='users'; id=Column(Integer,primary_key=True); name=Column(String,nullable=False); email=Column(String,unique=True,index=True); password_hash=Column(String); role=Column(String,default='Employee'); employee_id=Column(String); is_active=Column(Boolean,default=True)
class Employee(Base):
 __tablename__='employees'; id=Column(Integer,primary_key=True); employee_id=Column(String,unique=True,index=True); name=Column(String); email=Column(String); gender=Column(String); department=Column(String); role=Column(String); manager=Column(String); location=Column(String); hire_date=Column(Date); annual_gross=Column(Float,default=0); performance=Column(Float,default=0); engagement=Column(Float,default=0); utilisation=Column(Float,default=0); leave_balance=Column(Float,default=0); retention_risk=Column(String,default='Low'); status=Column(String,default='Active')
class Project(Base):
 __tablename__='projects'; id=Column(Integer,primary_key=True); project_id=Column(String,unique=True); name=Column(String); client=Column(String); manager=Column(String); sector=Column(String); start_date=Column(Date); due_date=Column(Date); contract_value=Column(Float,default=0); budget=Column(Float,default=0); cost_to_date=Column(Float,default=0); completion=Column(Float,default=0); schedule=Column(String,default='Green'); risk=Column(String,default='Low'); status=Column(String,default='In Progress')
class ProjectTask(Base):
 __tablename__='project_tasks'; id=Column(Integer,primary_key=True); project_id=Column(Integer,ForeignKey('projects.id')); title=Column(String); owner=Column(String); priority=Column(String,default='Medium'); status=Column(String,default='To Do'); due_date=Column(Date); progress=Column(Float,default=0); notes=Column(Text)
class FinanceMonth(Base):
 __tablename__='finance_months'; id=Column(Integer,primary_key=True); month=Column(Date); type=Column(String); revenue=Column(Float); direct_costs=Column(Float); operating_expenses=Column(Float); closing_cash=Column(Float); accounts_receivable=Column(Float); accounts_payable=Column(Float); dso=Column(Integer); budget_revenue=Column(Float)
class Invoice(Base):
 __tablename__='invoices'; id=Column(Integer,primary_key=True); invoice_no=Column(String,unique=True); client=Column(String); project=Column(String); issue_date=Column(Date); due_date=Column(Date); amount=Column(Float,default=0); paid_amount=Column(Float,default=0); status=Column(String,default='Draft'); notes=Column(Text)
class PayrollRecord(Base):
 __tablename__='payroll_records'; id=Column(Integer,primary_key=True); payroll_id=Column(String,unique=True); employee_id=Column(String); employee_name=Column(String); period=Column(String); basic=Column(Float); allowances=Column(Float); overtime=Column(Float); bonus=Column(Float); deductions=Column(Float); net_pay=Column(Float); status=Column(String,default='Draft')
class TimeEntry(Base):
 __tablename__='time_entries'; id=Column(Integer,primary_key=True); employee_id=Column(String); employee_name=Column(String); project=Column(String); work_date=Column(Date); hours=Column(Float); activity=Column(String); billable=Column(Boolean,default=True); status=Column(String,default='Submitted')
class Opportunity(Base):
 __tablename__='opportunities'; id=Column(Integer,primary_key=True); opportunity_id=Column(String,unique=True); client=Column(String); sector=Column(String); owner=Column(String); opportunity=Column(String); stage=Column(String); probability=Column(Float); potential_value=Column(Float); expected_close=Column(Date); account_health=Column(String); csat=Column(Float); ar_balance=Column(Float); days_outstanding=Column(Integer)
class PurchaseOrder(Base):
 __tablename__='purchase_orders'; id=Column(Integer,primary_key=True); po_no=Column(String,unique=True); vendor=Column(String); category=Column(String); project_department=Column(String); requester=Column(String); order_date=Column(Date); required_date=Column(Date); value=Column(Float); paid=Column(Float); delivery_status=Column(String); quality=Column(String); approval_status=Column(String); vendor_risk=Column(String); approver=Column(String); approval_note=Column(Text)
class Asset(Base):
 __tablename__='assets'; id=Column(Integer,primary_key=True); asset_id=Column(String,unique=True); name=Column(String); category=Column(String); location=Column(String); custodian=Column(String); cost=Column(Float); current_value=Column(Float); condition=Column(String); utilisation=Column(Float); downtime_days=Column(Integer); status=Column(String); action=Column(String)
class Risk(Base):
 __tablename__='risks'; id=Column(Integer,primary_key=True); risk_id=Column(String,unique=True); area=Column(String); risk=Column(Text); owner=Column(String); likelihood=Column(Integer); impact=Column(Integer); rating=Column(String); control=Column(Text); control_status=Column(String); residual_rating=Column(String); due_date=Column(Date)
class ManagementAction(Base):
 __tablename__='management_actions'; id=Column(Integer,primary_key=True); action_id=Column(String,unique=True); priority=Column(String); area=Column(String); action=Column(Text); owner=Column(String); due_date=Column(Date); status=Column(String); progress=Column(Float); expected_benefit=Column(Text)
class LeaveRequest(Base):
 __tablename__='leave_requests'; id=Column(Integer,primary_key=True); request_id=Column(String,unique=True); employee_id=Column(String); employee_name=Column(String); leave_type=Column(String); start_date=Column(Date); end_date=Column(Date); days=Column(Float); reason=Column(Text); approver=Column(String); status=Column(String,default='Pending'); created_by=Column(String)
class ExpenseClaim(Base):
 __tablename__='expense_claims'; id=Column(Integer,primary_key=True); claim_id=Column(String,unique=True); employee_id=Column(String); employee_name=Column(String); category=Column(String); project=Column(String); amount=Column(Float); expense_date=Column(Date); description=Column(Text); approver=Column(String); status=Column(String,default='Pending')
class DocumentRecord(Base):
 __tablename__='documents'; id=Column(Integer,primary_key=True); document_id=Column(String,unique=True); title=Column(String); entity_type=Column(String); entity_ref=Column(String); category=Column(String); file_name=Column(String); file_path=Column(String); uploaded_by=Column(String); uploaded_at=Column(DateTime,default=datetime.utcnow)
class Notification(Base):
 __tablename__='notifications'; id=Column(Integer,primary_key=True); user_email=Column(String,index=True); title=Column(String); message=Column(Text); level=Column(String,default='info'); is_read=Column(Boolean,default=False)
class AuditLog(Base):
 __tablename__='audit_logs'; id=Column(Integer,primary_key=True); actor=Column(String); action=Column(String); entity_type=Column(String); entity_ref=Column(String); details=Column(Text); created_at=Column(DateTime,default=datetime.utcnow)
class DesignBrief(Base):
 __tablename__='design_briefs'; id=Column(Integer,primary_key=True); brief_id=Column(String,unique=True); project_id=Column(String,index=True); client=Column(String); design_lead=Column(String); style_direction=Column(String); spaces=Column(String); budget_band=Column(Float); status=Column(String,default='Discovery'); concept_due=Column(Date); client_approval=Column(String,default='Pending'); notes=Column(Text)
class MaterialSpecification(Base):
 __tablename__='material_specs'; id=Column(Integer,primary_key=True); spec_id=Column(String,unique=True); project_id=Column(String,index=True); room_zone=Column(String); category=Column(String); item=Column(String); supplier=Column(String); unit=Column(String); quantity=Column(Float); unit_cost=Column(Float); lead_time_days=Column(Integer); approval_status=Column(String,default='Pending'); procurement_status=Column(String,default='Not Ordered')
class SiteVisit(Base):
 __tablename__='site_visits'; id=Column(Integer,primary_key=True); visit_id=Column(String,unique=True); project_id=Column(String,index=True); visit_date=Column(Date); architect=Column(String); site_stage=Column(String); progress_pct=Column(Float); quality_score=Column(Float); safety_status=Column(String); snag_count=Column(Integer); critical_issue=Column(Text); next_action=Column(Text)
class Client(Base):
 __tablename__='clients'; id=Column(Integer,primary_key=True); client_id=Column(String,unique=True); name=Column(String); contact_person=Column(String); email=Column(String); phone=Column(String); sector=Column(String); relationship_owner=Column(String); lifetime_value=Column(Float,default=0); active_projects=Column(Integer,default=0); satisfaction=Column(Float,default=0); health=Column(String,default='Green')
