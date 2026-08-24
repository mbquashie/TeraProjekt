from datetime import date,timedelta
from database import Base,engine,SessionLocal
from models import *
from auth import hash_password
Base.metadata.create_all(bind=engine)
db=SessionLocal()
if db.query(User).count(): db.close(); raise SystemExit
pw=hash_password('Tera2026!')
people=[
('TP-001','Elsie Amedzi','elsie@teraprojekt.com','Female','People & Culture','HR Manager','Managing Director',420000,'HR Manager'),
('TP-002','Ethel Amedzi','ethel@teraprojekt.com','Female','Architecture & Design','Lead Architect','Managing Director',540000,'Project Manager'),
('TP-003','Kojo Yankson','kojo@teraprojekt.com','Male','Architecture & Design','Senior Architect','Ethel Amedzi',480000,'Project Manager'),
('TP-004','Jerry Dwansah','jerry@teraprojekt.com','Male','Architecture & Design','Project Architect','Ethel Amedzi',420000,'Project Manager'),
('TP-005','Nana Ama Mensah','nanaama@teraprojekt.com','Female','Finance & Administration','Finance Manager','Managing Director',430000,'Finance Manager'),
('TP-006','Adjoa Owusu','adjoa@teraprojekt.com','Female','Interior Design','Interior Designer','Ethel Amedzi',240000,'Employee'),
('TP-007','Kwame Asante','kwame@teraprojekt.com','Male','Project Delivery','Projects Director','Managing Director',510000,'Project Manager'),
('TP-008','Akosua Boateng','akosua@teraprojekt.com','Female','Interior Design','Senior Interior Designer','Ethel Amedzi',330000,'Employee'),
('TP-009','Kofi Agyeman','kofi@teraprojekt.com','Male','Quantity Surveying','Senior Quantity Surveyor','Kwame Asante',310000,'Employee'),
('TP-010','Ama Serwaa','ama@teraprojekt.com','Female','Commercial','Business Development Manager','Managing Director',300000,'Employee'),
('TP-011','Yaw Osei','yaw@teraprojekt.com','Male','Finance & Administration','Senior Accountant','Nana Ama Mensah',270000,'Employee'),
('TP-012','Efua Nyarko','efua@teraprojekt.com','Female','Architecture & Design','Architect','Ethel Amedzi',300000,'Employee'),
('TP-013','Daniel Tetteh','daniel@teraprojekt.com','Male','Visualization','3D Visualizer','Ethel Amedzi',250000,'Employee'),
('TP-014','Mabel Quaye','mabel@teraprojekt.com','Female','People & Culture','HR Officer','Elsie Amedzi',190000,'Employee'),
('TP-015','Samuel Annan','samuel@teraprojekt.com','Male','Project Delivery','Site Manager','Kwame Asante',280000,'Employee'),
('TP-016','Josephine Lamptey','josephine@teraprojekt.com','Female','Client Experience','Client Experience Lead','Managing Director',280000,'Employee'),
('TP-017','Ibrahim Sulemana','ibrahim@teraprojekt.com','Male','Procurement & FF&E','Procurement Manager','Kwame Asante',300000,'Employee'),
('TP-018','Rita Koomson','rita@teraprojekt.com','Female','Finance & Administration','Admin Officer','Nana Ama Mensah',160000,'Employee')]
extra_names=['Nii Armah','Naa Dedei','Sena Agbemava','Edem Torgbor','Priscilla Aryee','Michael Nartey','Bernice Adjei','Richmond Acquah','Gifty Darko','Francis Amoako','Belinda Aidoo','Kelvin Addai','Eunice Bediako','Patrick Essel','Doreen Kusi','Emmanuel Appiah','Sheila Baah','George Antwi','Naomi Arthur','Dennis Opoku','Gloria Amponsah','Eric Sarpong','Linda Asare','Robert Kwarteng','Cynthia Ofori','Stephen Acheampong','Sandra Gyasi','David Ansong','Grace Aboagye','Philip Danso']
depts=['Architecture & Design','Interior Design','Project Delivery','Visualization','Quantity Surveying','Procurement & FF&E','Finance & Administration','Commercial','Client Experience','Operations']
roles=['Architectural Assistant','Interior Designer','Project Coordinator','BIM Technician','Quantity Surveyor','FF&E Coordinator','Accounts Officer','Business Development Executive','Client Service Executive','Site Supervisor']
for i,n in enumerate(extra_names,19): people.append((f'TP-{i:03d}',n,f'{n.lower().replace(" ",".")}@teraprojekt.com','Female' if i%2==0 else 'Male',depts[(i-19)%len(depts)],roles[(i-19)%len(roles)],['Ethel Amedzi','Kwame Asante','Elsie Amedzi','Nana Ama Mensah'][i%4],150000+(i%8)*18000,'Employee'))
for i,p in enumerate(people):
 eid,name,email,gender,dept,role,manager,gross,userrole=p
 db.add(Employee(employee_id=eid,name=name,email=email,gender=gender,department=dept,role=role,manager=manager,location='Accra' if i%5 else 'Tema',hire_date=date(2022+(i%4),1+(i%11),1+(i%25)),annual_gross=gross,performance=3.7+(i%12)/10,engagement=.76+(i%18)/100,utilisation=.72+(i%20)/100,leave_balance=8+(i%15),retention_risk='High' if i in (11,27) else ('Medium' if i%9==0 else 'Low'),status='Active'))
 db.add(User(name=name,email=email,password_hash=pw,role=userrole,employee_id=eid,is_active=True))
db.add(User(name='System Administrator',email='admin@teraprojekt.com',password_hash=pw,role='Administrator',employee_id=None,is_active=True))
projects=[('PRJ-2601','Airport Residential Penthouse','Private Residence','Ethel Amedzi','Residential',3200000,2450000,.72,'Green','Low'),('PRJ-2602','Cantonments Corporate HQ','Meridian Holdings','Kojo Yankson','Corporate',4850000,3650000,.58,'Amber','Medium'),('PRJ-2603','Labone Boutique Hotel','Coastal Hospitality','Jerry Dwansah','Hospitality',6100000,4700000,.41,'Green','Medium'),('PRJ-2604','East Legon Villa','Private Residence','Ethel Amedzi','Residential',2750000,2050000,.83,'Amber','Medium'),('PRJ-2605','Ridge Executive Offices','Aseda Capital','Kojo Yankson','Corporate',3900000,2900000,.32,'Green','Low'),('PRJ-2606','Tema Showroom','Golden Coast Living','Jerry Dwansah','Retail',2100000,1580000,.66,'Red','High')]
for i,p in enumerate(projects):
 pid,name,client,mgr,sector,val,budget,comp,sched,risk=p; pr=Project(project_id=pid,name=name,client=client,manager=mgr,sector=sector,start_date=date(2026,1+i,5),due_date=date(2026,9+(i%4),20),contract_value=val,budget=budget,cost_to_date=budget*comp*.88,completion=comp,schedule=sched,risk=risk,status='At Risk' if sched=='Red' else 'In Progress'); db.add(pr); db.flush(); db.add(ProjectTask(project_id=pr.id,title='Client design approval',owner=mgr,priority='High',status='In Progress',due_date=date.today()+timedelta(days=10),progress=.5))
for m in range(1,9):
 rev=900000+m*85000; db.add(FinanceMonth(month=date(2026,m,1),type='Actual',revenue=rev,direct_costs=rev*.54,operating_expenses=rev*.23,closing_cash=1250000+m*120000,accounts_receivable=430000+m*38000,accounts_payable=260000+m*22000,dso=51-m,budget_revenue=rev*.98))
for m in range(9,13):
 rev=900000+m*85000; db.add(FinanceMonth(month=date(2026,m,1),type='Forecast',revenue=rev,direct_costs=rev*.53,operating_expenses=rev*.22,closing_cash=2100000,accounts_receivable=690000,accounts_payable=410000,dso=43,budget_revenue=rev*.97))
for i,(client,opp,val,prob) in enumerate([('Meridian Holdings','Regional office redesign',2600000,.75),('Coastal Hospitality','Beach resort interiors',5200000,.55),('Aseda Capital','Executive floor fit-out',1800000,.8),('Golden Coast Living','Showroom rollout',3400000,.4)],1): db.add(Opportunity(opportunity_id=f'OP-{400+i}',client=client,sector='Property',owner='Ama Serwaa',opportunity=opp,stage='Proposal',probability=prob,potential_value=val,expected_close=date.today()+timedelta(days=20*i),account_health='Green',csat=.9,ar_balance=90000*i,days_outstanding=18+i*7))
for i,p in enumerate(projects[:4],1): db.add(DesignBrief(brief_id=f'DB-{i:03d}',project_id=p[0],client=p[2],design_lead=p[3],style_direction=['Contemporary African Luxury','Warm Minimalism','Modern Coastal','Timeless Contemporary'][i-1],spaces='Reception, living, bedrooms, executive areas',budget_band=p[5]*.35,status='Concept Design',concept_due=date.today()+timedelta(days=7*i),client_approval='Approved' if i<3 else 'Pending',notes=''))
for i,p in enumerate(projects[:5],1): db.add(SiteVisit(visit_id=f'SV-{i:03d}',project_id=p[0],visit_date=date.today()-timedelta(days=i*5),architect=p[3],site_stage='Installation',progress_pct=p[7],quality_score=4.2+(i%4)/10,safety_status='Green' if i!=4 else 'Amber',snag_count=i*3,critical_issue='',next_action='Close priority snags and confirm client walkthrough'))
for i,p in enumerate(projects[:5],1): db.add(MaterialSpecification(spec_id=f'SP-{i:03d}',project_id=p[0],room_zone='Main Area',category='FF&E',item=['Custom sofa','Feature lighting','Stone finish','Executive desk','Window treatment'][i-1],supplier='Approved Vendor',unit='item',quantity=2+i,unit_cost=8500*i,lead_time_days=21+i*4,approval_status='Approved' if i<4 else 'Pending',procurement_status='Ordered' if i<3 else 'Not Ordered'))
for i,p in enumerate(projects[:4],1): db.add(Client(client_id=f'CL-{i:03d}',name=p[2],contact_person='Client Representative',email=f'client{i}@example.com',phone='+233 20 000 0000',sector=p[4],relationship_owner='Josephine Lamptey',lifetime_value=p[5],active_projects=1,satisfaction=.88+i*.015,health='Green'))
for i,p in enumerate(projects[:4],1): db.add(Invoice(invoice_no=f'INV-26-{i:03d}',client=p[2],project=p[1],issue_date=date.today()-timedelta(days=25*i),due_date=date.today()+timedelta(days=15-i*8),amount=p[5]*.18,paid_amount=p[5]*(.10 if i<3 else .03),status='Overdue' if i==4 else 'Issued',notes='Project milestone invoice'))
for i in range(1,6): db.add(PurchaseOrder(po_no=f'PO-26-{80+i}',vendor=f'Approved Design Vendor {i}',category='FF&E',project_department=projects[(i-1)%len(projects)][1],requester='Ibrahim Sulemana',order_date=date.today()-timedelta(days=8*i),required_date=date.today()+timedelta(days=12*i),value=65000*i,paid=20000*i,delivery_status='Pending',quality='Good',approval_status='Pending' if i%2 else 'Approved',vendor_risk='Low',approver='',approval_note=''))
for i in range(1,5): db.add(Risk(risk_id=f'RSK-{i:02d}',area=['Projects','Finance','People','Procurement'][i-1],risk=['Client approval delay','Receivable concentration','Design talent retention','Imported FF&E lead time'][i-1],owner=['Ethel Amedzi','Nana Ama Mensah','Elsie Amedzi','Ibrahim Sulemana'][i-1],likelihood=3,impact=4,rating='High' if i<3 else 'Medium',control='Weekly management review',control_status='In Progress',residual_rating='Medium',due_date=date.today()+timedelta(days=14*i)))
for i in range(1,5): db.add(ManagementAction(action_id=f'ACT-{100+i}',priority='High' if i<3 else 'Medium',area=['Design','Finance','HR','Procurement'][i-1],action=['Close Cantonments concept approval','Accelerate overdue collections','Complete architect succession plan','Confirm long-lead FF&E orders'][i-1],owner=['Ethel Amedzi','Nana Ama Mensah','Elsie Amedzi','Ibrahim Sulemana'][i-1],due_date=date.today()+timedelta(days=7*i),status='In Progress',progress=.35+i*.1,expected_benefit='Protect delivery and client experience'))
for i,e in enumerate(people):
 basic=e[7]/12*.72; allow=e[7]/12*.18; ded=e[7]/12*.08; db.add(PayrollRecord(payroll_id=f'PAY-2608-{i+1:03d}',employee_id=e[0],employee_name=e[1],period='Aug 2026',basic=basic,allowances=allow,overtime=0,bonus=0,deductions=ded,net_pay=basic+allow-ded,status='Processed'))
db.add(LeaveRequest(request_id='LV-260801',employee_id='TP-006',employee_name='Adjoa Owusu',leave_type='Annual Leave',start_date=date.today()+timedelta(days=10),end_date=date.today()+timedelta(days=12),days=3,reason='Personal leave',approver='Ethel Amedzi',status='Pending',created_by='Adjoa Owusu'))
db.add(Notification(user_email='elsie@teraprojekt.com',title='People review due',message='Monthly people and retention review is ready.',level='info',is_read=False))
db.commit(); db.close(); print('Tera Projekt demo data seeded.')
