from fastapi import FastAPI,Request,Form,Depends,UploadFile,File,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func,or_
from database import Base,engine,SessionLocal
from models import *
from auth import verify_password,make_session,read_session
from datetime import date,datetime
import os,sys,subprocess,uuid,shutil
BASE_DIR=os.path.dirname(os.path.abspath(__file__)); UPLOAD_DIR=os.path.join(BASE_DIR,'uploads'); os.makedirs(UPLOAD_DIR,exist_ok=True)
Base.metadata.create_all(bind=engine)
_check=SessionLocal(); _needs_seed=_check.query(User).count()==0; _check.close()
if _needs_seed: subprocess.run([sys.executable,os.path.join(BASE_DIR,'seed.py')],check=True)
app=FastAPI(title='Tera Projekt Management Platform',version='4.0'); app.mount('/static',StaticFiles(directory=os.path.join(BASE_DIR,'static')),name='static'); templates=Jinja2Templates(directory=os.path.join(BASE_DIR,'templates'))
def db_session():
 db=SessionLocal()
 try: yield db
 finally: db.close()
def money(v): return f'GH₵ {float(v or 0):,.0f}'
def pct(v): return f'{float(v or 0)*100:.1f}%'
def ddate(v): return v.strftime('%d %b %Y') if v else '—'
def initials(n): return ''.join(x[0] for x in (n or 'TP').split()[:2]).upper()
templates.env.globals.update(money=money,pct=pct,ddate=ddate,initials=initials,today=date.today())
def user_of(request,db):
 uid=read_session(request.cookies.get('tera_session')); return db.get(User,uid) if uid else None
PERMS={'Administrator':{'*'},'Managing Director':{'*'},'HR Manager':{'dashboard','hr','payroll','timesheets','approvals','documents','audit'},'Finance Manager':{'dashboard','finance','payroll','invoices','procurement','approvals','documents','audit'},'Project Manager':{'dashboard','projects','design','site','timesheets','procurement','approvals','documents','actions','risks'},'Employee':{'selfservice','timesheets','approvals','documents'}}
def allowed(user,area): return bool(user and ('*' in PERMS.get(user.role,set()) or area in PERMS.get(user.role,set())))
def require(request,db,area):
 u=user_of(request,db)
 if not u: return None
 if not allowed(u,area): raise HTTPException(403,'You do not have permission to access this area.')
 return u
def audit(db,u,action,etype,eref,details=''): db.add(AuditLog(actor=u.name if u else 'System',action=action,entity_type=etype,entity_ref=eref,details=details))
def ctx(request,db,u,title,active,**kw):
 pending=db.query(LeaveRequest).filter(LeaveRequest.status=='Pending').count()+db.query(ExpenseClaim).filter(ExpenseClaim.status=='Pending').count()+db.query(PurchaseOrder).filter(PurchaseOrder.approval_status=='Pending').count()
 notes=db.query(Notification).filter(Notification.user_email==u.email,Notification.is_read==False).count()
 return {'request':request,'user':u,'title':title,'active':active,'pending_approvals':pending,'notifications':notes,'permissions':PERMS.get(u.role,set()),**kw}
@app.get('/login',response_class=HTMLResponse)
def login_page(request:Request): return templates.TemplateResponse('login.html',{'request':request,'error':None})
@app.post('/login')
def login(request:Request,email:str=Form(...),password:str=Form(...),db:Session=Depends(db_session)):
 u=db.query(User).filter(func.lower(User.email)==email.lower()).first()
 if not u or not verify_password(password,u.password_hash): return templates.TemplateResponse('login.html',{'request':request,'error':'Invalid email or password.'},status_code=401)
 r=RedirectResponse('/',303); r.set_cookie('tera_session',make_session(u.id),httponly=True,samesite='lax',secure=os.getenv('COOKIE_SECURE','0')=='1'); return r
@app.get('/logout')
def logout():
 r=RedirectResponse('/login',303); r.delete_cookie('tera_session'); return r
@app.get('/',response_class=HTMLResponse)
def dashboard(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'dashboard' if user_of(request,db) and user_of(request,db).role!='Employee' else 'selfservice')
 if not u: return RedirectResponse('/login',303)
 if u.role=='Employee': return RedirectResponse('/me',303)
 latest=db.query(FinanceMonth).filter(FinanceMonth.type=='Actual').order_by(FinanceMonth.month.desc()).first(); projects=db.query(Project).all(); emps=db.query(Employee).filter(Employee.status=='Active').all(); opps=db.query(Opportunity).all(); risks=db.query(Risk).all(); inv=db.query(Invoice).all()
 gp=latest.revenue-latest.direct_costs; op=gp-latest.operating_expenses
 briefs=db.query(DesignBrief).all(); visits=db.query(SiteVisit).all(); specs=db.query(MaterialSpecification).all(); clients=db.query(Client).all(); kpis={'revenue':latest.revenue,'margin':op/latest.revenue if latest.revenue else 0,'cash':latest.closing_cash,'headcount':len(emps),'pipeline':sum(o.potential_value*o.probability for o in opps),'at_risk':sum(1 for p in projects if p.status=='At Risk'),'critical':sum(1 for r in risks if r.rating in ['Critical','High']),'overdue':sum(i.amount-i.paid_amount for i in inv if i.status=='Overdue'),'design_approval':sum(1 for b in briefs if b.client_approval=='Approved')/len(briefs) if briefs else 0,'quality':sum(v.quality_score for v in visits)/len(visits) if visits else 0,'spec_value':sum(s.quantity*s.unit_cost for s in specs),'client_sat':sum(c.satisfaction for c in clients)/len(clients) if clients else 0}
 return templates.TemplateResponse('dashboard.html',ctx(request,db,u,'Executive Command Center','dashboard',kpis=kpis,projects=projects[:5],risks=risks[:5],actions=db.query(ManagementAction).order_by(ManagementAction.due_date).limit(5).all(),briefs=briefs,visits=visits,months=[x.month.strftime('%b') for x in db.query(FinanceMonth).order_by(FinanceMonth.month).all()],revenues=[x.revenue for x in db.query(FinanceMonth).order_by(FinanceMonth.month).all()]))
@app.get('/me',response_class=HTMLResponse)
def me(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'selfservice')
 if not u:return RedirectResponse('/login',303)
 emp=db.query(Employee).filter(Employee.employee_id==u.employee_id).first(); leaves=db.query(LeaveRequest).filter(LeaveRequest.employee_id==u.employee_id).order_by(LeaveRequest.id.desc()).all(); times=db.query(TimeEntry).filter(TimeEntry.employee_id==u.employee_id).order_by(TimeEntry.work_date.desc()).limit(10).all(); expenses=db.query(ExpenseClaim).filter(ExpenseClaim.employee_id==u.employee_id).all()
 return templates.TemplateResponse('selfservice.html',ctx(request,db,u,'My Workspace','selfservice',emp=emp,leaves=leaves,times=times,expenses=expenses))
@app.get('/hr',response_class=HTMLResponse)
def hr(request:Request,q:str='',db:Session=Depends(db_session)):
 u=require(request,db,'hr')
 if not u:return RedirectResponse('/login',303)
 query=db.query(Employee); query=query.filter(or_(Employee.name.ilike(f'%{q}%'),Employee.department.ilike(f'%{q}%'),Employee.role.ilike(f'%{q}%'))) if q else query
 rows=query.order_by(Employee.name).all(); return templates.TemplateResponse('hr.html',ctx(request,db,u,'People & Culture','hr',rows=rows,q=q,headcount=len(rows),engagement=sum(x.engagement for x in rows)/len(rows),high=sum(x.retention_risk=='High' for x in rows)))
@app.get('/hr/{eid}',response_class=HTMLResponse)
def employee_detail(eid:str,request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'hr'); emp=db.query(Employee).filter(Employee.employee_id==eid).first()
 if not u:return RedirectResponse('/login',303)
 if not emp: raise HTTPException(404)
 docs=db.query(DocumentRecord).filter(DocumentRecord.entity_type=='Employee',DocumentRecord.entity_ref==eid).all(); pay=db.query(PayrollRecord).filter(PayrollRecord.employee_id==eid).all(); times=db.query(TimeEntry).filter(TimeEntry.employee_id==eid).all()
 return templates.TemplateResponse('employee_detail.html',ctx(request,db,u,emp.name,'hr',emp=emp,docs=docs,pay=pay,times=times))
@app.post('/hr/{eid}/edit')
def employee_edit(eid:str,request:Request,department:str=Form(...),role:str=Form(...),manager:str=Form(''),location:str=Form('Accra'),annual_gross:float=Form(...),performance:float=Form(...),engagement:float=Form(...),retention_risk:str=Form(...),db:Session=Depends(db_session)):
 u=require(request,db,'hr'); emp=db.query(Employee).filter(Employee.employee_id==eid).first()
 if not u:return RedirectResponse('/login',303)
 emp.department=department;emp.role=role;emp.manager=manager;emp.location=location;emp.annual_gross=max(0,annual_gross);emp.performance=min(max(performance,0),5);emp.engagement=min(max(engagement,0),1);emp.retention_risk=retention_risk;audit(db,u,'Updated employee','Employee',eid,emp.name);db.commit();return RedirectResponse(f'/hr/{eid}',303)
@app.get('/projects',response_class=HTMLResponse)
def projects(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'projects')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(Project).order_by(Project.due_date).all(); return templates.TemplateResponse('projects.html',ctx(request,db,u,'Projects & PMO','projects',rows=rows,total=sum(x.contract_value for x in rows),cost=sum(x.cost_to_date for x in rows),risk=sum(x.status=='At Risk' for x in rows)))
@app.get('/projects/{pid}',response_class=HTMLResponse)
def project_detail(pid:str,request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'projects'); p=db.query(Project).filter(Project.project_id==pid).first()
 if not u:return RedirectResponse('/login',303)
 if not p: raise HTTPException(404)
 tasks=db.query(ProjectTask).filter(ProjectTask.project_id==p.id).order_by(ProjectTask.id).all(); docs=db.query(DocumentRecord).filter(DocumentRecord.entity_type=='Project',DocumentRecord.entity_ref==pid).all(); return templates.TemplateResponse('project_detail.html',ctx(request,db,u,p.name,'projects',p=p,tasks=tasks,docs=docs))
@app.post('/projects/{pid}/task')
def task_add(pid:str,request:Request,title:str=Form(...),owner:str=Form(...),priority:str=Form('Medium'),status:str=Form('To Do'),due_date:str=Form(''),db:Session=Depends(db_session)):
 u=require(request,db,'projects'); p=db.query(Project).filter(Project.project_id==pid).first()
 if not u:return RedirectResponse('/login',303)
 db.add(ProjectTask(project_id=p.id,title=title,owner=owner,priority=priority,status=status,due_date=date.fromisoformat(due_date) if due_date else None));audit(db,u,'Created task','Project',pid,title);db.commit();return RedirectResponse(f'/projects/{pid}',303)
@app.post('/tasks/{tid}/status')
def task_status(tid:int,request:Request,status:str=Form(...),db:Session=Depends(db_session)):
 u=require(request,db,'projects');t=db.get(ProjectTask,tid)
 if not u:return RedirectResponse('/login',303)
 t.status=status;t.progress=1 if status=='Done' else (.5 if status=='In Progress' else 0);db.commit();return RedirectResponse(request.headers.get('referer','/projects'),303)
@app.get('/finance',response_class=HTMLResponse)
def finance(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'finance')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(FinanceMonth).order_by(FinanceMonth.month).all(); latest=[x for x in rows if x.type=='Actual'][-1]; return templates.TemplateResponse('finance.html',ctx(request,db,u,'Finance & Performance','finance',rows=rows,latest=latest,invoices=db.query(Invoice).order_by(Invoice.due_date).all()))
@app.get('/invoices',response_class=HTMLResponse)
def invoices(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'invoices')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(Invoice).order_by(Invoice.due_date).all(); return templates.TemplateResponse('invoices.html',ctx(request,db,u,'Invoices & Receivables','invoices',rows=rows,total=sum(x.amount for x in rows),outstanding=sum(x.amount-x.paid_amount for x in rows)))
@app.post('/invoices/new')
def invoice_new(request:Request,invoice_no:str=Form(...),client:str=Form(...),project:str=Form(''),amount:float=Form(...),due_date:str=Form(...),db:Session=Depends(db_session)):
 u=require(request,db,'invoices')
 if not u:return RedirectResponse('/login',303)
 db.add(Invoice(invoice_no=invoice_no,client=client,project=project,issue_date=date.today(),due_date=date.fromisoformat(due_date),amount=max(0,amount),paid_amount=0,status='Draft'));audit(db,u,'Created invoice','Invoice',invoice_no,client);db.commit();return RedirectResponse('/invoices',303)
@app.get('/payroll',response_class=HTMLResponse)
def payroll(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'payroll')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(PayrollRecord).order_by(PayrollRecord.employee_name).all(); return templates.TemplateResponse('payroll.html',ctx(request,db,u,'Payroll','payroll',rows=rows,gross=sum(x.basic+x.allowances+x.overtime+x.bonus for x in rows),net=sum(x.net_pay for x in rows)))
@app.get('/timesheets',response_class=HTMLResponse)
def timesheets(request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 if not allowed(u,'timesheets'): raise HTTPException(403)
 q=db.query(TimeEntry); q=q.filter(TimeEntry.employee_id==u.employee_id) if u.role=='Employee' else q; rows=q.order_by(TimeEntry.work_date.desc()).all(); return templates.TemplateResponse('timesheets.html',ctx(request,db,u,'Timesheets','timesheets',rows=rows,total=sum(x.hours for x in rows)))
@app.post('/timesheets/new')
def time_new(request:Request,project:str=Form(...),work_date:str=Form(...),hours:float=Form(...),activity:str=Form(...),db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 emp=db.query(Employee).filter(Employee.employee_id==u.employee_id).first() if u.employee_id else None; db.add(TimeEntry(employee_id=u.employee_id or 'ADMIN',employee_name=emp.name if emp else u.name,project=project,work_date=date.fromisoformat(work_date),hours=min(max(hours,0),24),activity=activity,billable=True,status='Submitted'));audit(db,u,'Submitted time','TimeEntry',project,f'{hours} hours');db.commit();return RedirectResponse('/timesheets',303)
@app.get('/crm',response_class=HTMLResponse)
def crm(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'dashboard')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(Opportunity).order_by(Opportunity.expected_close).all(); return templates.TemplateResponse('crm.html',ctx(request,db,u,'Commercial & CRM','crm',rows=rows,pipeline=sum(x.potential_value for x in rows),weighted=sum(x.potential_value*x.probability for x in rows)))
@app.get('/procurement',response_class=HTMLResponse)
def procurement(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'procurement')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(PurchaseOrder).order_by(PurchaseOrder.required_date).all(); return templates.TemplateResponse('procurement.html',ctx(request,db,u,'Procurement & Vendors','procurement',rows=rows,total=sum(x.value for x in rows)))
@app.post('/procurement/{poid}/{decision}')
def po_decision(poid:int,decision:str,request:Request,note:str=Form(''),db:Session=Depends(db_session)):
 u=require(request,db,'approvals'); po=db.get(PurchaseOrder,poid)
 if not u:return RedirectResponse('/login',303)
 if decision in ['Approved','Rejected']: po.approval_status=decision;po.approver=u.name;po.approval_note=note;audit(db,u,f'PO {decision.lower()}','PurchaseOrder',po.po_no,money(po.value));db.commit()
 return RedirectResponse('/procurement',303)
@app.get('/assets',response_class=HTMLResponse)
def assets(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'dashboard')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(Asset).all(); return templates.TemplateResponse('assets.html',ctx(request,db,u,'Assets & Operations','assets',rows=rows,cost=sum(x.cost for x in rows),value=sum(x.current_value for x in rows)))
@app.get('/risks',response_class=HTMLResponse)
def risks(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'risks')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(Risk).all(); return templates.TemplateResponse('risks.html',ctx(request,db,u,'Risk & Compliance','risks',rows=rows,critical=sum(x.rating in ['Critical','High'] for x in rows)))
@app.get('/actions',response_class=HTMLResponse)
def actions(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'actions')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(ManagementAction).all(); return templates.TemplateResponse('actions.html',ctx(request,db,u,'Management Actions','actions',rows=rows))
@app.get('/approvals',response_class=HTMLResponse)
def approvals(request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 leaves=db.query(LeaveRequest); expenses=db.query(ExpenseClaim); pos=db.query(PurchaseOrder).filter(PurchaseOrder.approval_status=='Pending')
 if u.role=='Employee': leaves=leaves.filter(LeaveRequest.employee_id==u.employee_id); expenses=expenses.filter(ExpenseClaim.employee_id==u.employee_id); pos=pos.filter(PurchaseOrder.id==-1)
 return templates.TemplateResponse('approvals.html',ctx(request,db,u,'Approvals & Requests','approvals',leaves=leaves.all(),expenses=expenses.all(),pos=pos.all()))
@app.post('/approvals/leave/{iid}/{decision}')
def leave_decision(iid:int,decision:str,request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db); item=db.get(LeaveRequest,iid)
 if not u:return RedirectResponse('/login',303)
 if decision in ['Approved','Rejected'] and u.role!='Employee': item.status=decision;audit(db,u,f'Leave {decision.lower()}','Leave',item.request_id,item.employee_name);db.commit()
 return RedirectResponse('/approvals',303)
@app.post('/approvals/expense/{iid}/{decision}')
def expense_decision(iid:int,decision:str,request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db); item=db.get(ExpenseClaim,iid)
 if not u:return RedirectResponse('/login',303)
 if decision in ['Approved','Rejected'] and u.role!='Employee': item.status=decision;audit(db,u,f'Expense {decision.lower()}','Expense',item.claim_id,money(item.amount));db.commit()
 return RedirectResponse('/approvals',303)
@app.post('/requests/leave')
def leave_new(request:Request,leave_type:str=Form(...),start_date:str=Form(...),end_date:str=Form(...),reason:str=Form(''),db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 emp=db.query(Employee).filter(Employee.employee_id==u.employee_id).first(); s=date.fromisoformat(start_date);e=date.fromisoformat(end_date);days=(e-s).days+1;rid='LV-'+datetime.now().strftime('%y%m%d%H%M%S');db.add(LeaveRequest(request_id=rid,employee_id=u.employee_id,employee_name=emp.name if emp else u.name,leave_type=leave_type,start_date=s,end_date=e,days=days,reason=reason,approver=emp.manager if emp else '',created_by=u.name));audit(db,u,'Requested leave','Leave',rid,f'{days} days');db.commit();return RedirectResponse('/approvals',303)
@app.get('/documents',response_class=HTMLResponse)
def documents(request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 rows=db.query(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc()).all(); return templates.TemplateResponse('documents.html',ctx(request,db,u,'Document Center','documents',rows=rows))
@app.post('/documents/upload')
def upload_doc(request:Request,title:str=Form(...),entity_type:str=Form(...),entity_ref:str=Form(...),category:str=Form('General'),file:UploadFile=File(...),db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u:return RedirectResponse('/login',303)
 ext=os.path.splitext(file.filename or '')[1][:10]; safe=f'{uuid.uuid4().hex}{ext}'; path=os.path.join(UPLOAD_DIR,safe)
 with open(path,'wb') as out: shutil.copyfileobj(file.file,out)
 did='DOC-'+uuid.uuid4().hex[:8].upper();db.add(DocumentRecord(document_id=did,title=title,entity_type=entity_type,entity_ref=entity_ref,category=category,file_name=file.filename,file_path=safe,uploaded_by=u.name));audit(db,u,'Uploaded document','Document',did,file.filename);db.commit();return RedirectResponse('/documents',303)
@app.get('/documents/{did}/download')
def download_doc(did:str,request:Request,db:Session=Depends(db_session)):
 u=user_of(request,db);d=db.query(DocumentRecord).filter(DocumentRecord.document_id==did).first()
 if not u:return RedirectResponse('/login',303)
 if not d:raise HTTPException(404)
 return FileResponse(os.path.join(UPLOAD_DIR,d.file_path),filename=d.file_name)
@app.get('/audit',response_class=HTMLResponse)
def audit_page(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'audit')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(AuditLog).order_by(AuditLog.id.desc()).limit(200).all();return templates.TemplateResponse('audit.html',ctx(request,db,u,'Audit Trail','audit',rows=rows))
@app.get('/settings',response_class=HTMLResponse)
def settings(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'dashboard')
 if not u:return RedirectResponse('/login',303)
 return templates.TemplateResponse('settings.html',ctx(request,db,u,'System & Deployment','settings',db_url='PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite',microsoft_enabled=bool(os.getenv('MICROSOFT_CLIENT_ID'))))
@app.get('/auth/microsoft')
def microsoft_auth():
 if not os.getenv('MICROSOFT_CLIENT_ID'): return HTMLResponse('<h2>Microsoft Entra ID is not configured.</h2><p>Set MICROSOFT_CLIENT_ID, MICROSOFT_TENANT_ID and MICROSOFT_CLIENT_SECRET in your production environment.</p>',503)
 return HTMLResponse('<h2>Microsoft Entra ID configuration detected.</h2><p>Complete OAuth callback wiring using your registered application credentials.</p>')
@app.get('/design',response_class=HTMLResponse)
def design_studio(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'design' if user_of(request,db) and user_of(request,db).role=='Project Manager' else 'dashboard')
 if not u:return RedirectResponse('/login',303)
 briefs=db.query(DesignBrief).order_by(DesignBrief.concept_due).all(); specs=db.query(MaterialSpecification).order_by(MaterialSpecification.project_id).all(); clients=db.query(Client).all()
 spec_value=sum(x.quantity*x.unit_cost for x in specs); approved=sum(x.client_approval=='Approved' for x in briefs); pending=sum(x.client_approval!='Approved' for x in briefs)
 return templates.TemplateResponse('design.html',ctx(request,db,u,'Design Studio','design',briefs=briefs,specs=specs,clients=clients,spec_value=spec_value,approved=approved,pending=pending))
@app.post('/design/brief/new')
def design_brief_new(request:Request,project_id:str=Form(...),client:str=Form(...),design_lead:str=Form(...),style_direction:str=Form(...),spaces:str=Form(...),budget_band:float=Form(...),concept_due:str=Form(...),db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u or not (allowed(u,'projects') or '*' in PERMS.get(u.role,set())): raise HTTPException(403)
 bid='DB-'+datetime.now().strftime('%y%m%d%H%M%S'); db.add(DesignBrief(brief_id=bid,project_id=project_id,client=client,design_lead=design_lead,style_direction=style_direction,spaces=spaces,budget_band=budget_band,status='Discovery',concept_due=date.fromisoformat(concept_due),client_approval='Pending')); audit(db,u,'Created design brief','DesignBrief',bid,project_id); db.commit(); return RedirectResponse('/design',303)
@app.get('/site',response_class=HTMLResponse)
def site_control(request:Request,db:Session=Depends(db_session)):
 u=require(request,db,'site' if user_of(request,db) and user_of(request,db).role=='Project Manager' else 'dashboard')
 if not u:return RedirectResponse('/login',303)
 rows=db.query(SiteVisit).order_by(SiteVisit.visit_date.desc()).all(); return templates.TemplateResponse('site.html',ctx(request,db,u,'Site & Installation Control','site',rows=rows,quality=sum(x.quality_score for x in rows)/len(rows) if rows else 0,snags=sum(x.snag_count for x in rows),amber=sum(x.safety_status!='Green' for x in rows)))
@app.post('/site/new')
def site_new(request:Request,project_id:str=Form(...),visit_date:str=Form(...),architect:str=Form(...),site_stage:str=Form(...),progress_pct:float=Form(...),quality_score:float=Form(...),safety_status:str=Form(...),snag_count:int=Form(...),critical_issue:str=Form(''),next_action:str=Form(''),db:Session=Depends(db_session)):
 u=user_of(request,db)
 if not u or not (allowed(u,'projects') or '*' in PERMS.get(u.role,set())): raise HTTPException(403)
 vid='SV-'+datetime.now().strftime('%y%m%d%H%M%S'); db.add(SiteVisit(visit_id=vid,project_id=project_id,visit_date=date.fromisoformat(visit_date),architect=architect,site_stage=site_stage,progress_pct=min(max(progress_pct,0),1),quality_score=min(max(quality_score,0),5),safety_status=safety_status,snag_count=max(snag_count,0),critical_issue=critical_issue,next_action=next_action)); audit(db,u,'Logged site visit','SiteVisit',vid,project_id); db.commit(); return RedirectResponse('/site',303)
@app.get('/api/health')
def health(db:Session=Depends(db_session)): return {'status':'ok','application':'Tera Projekt Management Platform','version':'4.0','database':'connected','employees':db.query(Employee).count(),'projects':db.query(Project).count()}
