import streamlit as st
from PIL import Image
import requests, json, re, io, base64, datetime, math
import pandas as pd

st.set_page_config(page_title='Construction Intelligence | Skill Wallet', page_icon='🏗️', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.4rem;max-width:1250px}.stMetric{background:#f1f5f9;padding:14px;border-radius:12px}h1,h2,h3{color:#17324d}.hero{background:linear-gradient(110deg,#123454,#187b90);padding:26px;border-radius:18px;color:white;margin-bottom:20px}.hero h1{color:white;margin:0}.hero p{color:#e3f5fb;margin:7px 0 0}</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏗️ Multimodal Construction Intelligence Platform</h1><p>AI-powered safety • Structural diagnostics • Project planning • Site advisory</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AI Settings")
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    model = st.text_input("Gemini model", value="gemini-2.5-flash", help="Use a model available to your Gemini account; model availability changes.")
    st.caption('AI mode' if api_key else '🟡 Demonstration mode — no image recognition is performed')
    st.info('Safety assessments and cost estimates are informational, not a replacement for certified engineers, site inspectors, or local compliance checks.')

def gemini(prompt, img=None):
    if not api_key: return None
    parts=[{'text':prompt}]
    if img:
        buf=io.BytesIO(); img.convert('RGB').save(buf,format='JPEG',quality=85)
        parts.append({'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(buf.getvalue()).decode()}})
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    try:
        r=requests.post(url,headers={'x-goog-api-key':api_key,'Content-Type':'application/json'},json={'contents':[{'parts':parts}],'generationConfig':{'temperature':0.2}},timeout=55)
        r.raise_for_status()
        return ''.join(p.get('text','') for p in r.json()['candidates'][0]['content']['parts'])
    except Exception as e:
        st.error(f'Gemini request failed: {e}')
        return None

def json_response(raw):
    if not raw:return None
    try:
        raw=re.sub(r'^```(?:json)?|```$','',raw.strip(),flags=re.I).strip()
        return json.loads(raw)
    except Exception:
        match=re.search(r'\{.*\}',raw,re.S)
        if match:
            try:return json.loads(match.group())
            except Exception:pass
        st.warning('AI response was not valid JSON. Displaying raw response instead.')
        st.code(raw)
        return None

def download(data,name):
    st.download_button('⬇️ Download JSON report',json.dumps(data,indent=2,ensure_ascii=False),file_name=name,mime='application/json')

def photo_input(key):
    up=st.file_uploader('Upload JPG or PNG image',type=['jpg','jpeg','png'],key=key)
    if up:
        try:
            img=Image.open(up); img.load();st.image(img,caption='Uploaded image',width=440)
            return img
        except Exception:st.error('Cannot read this image.')
    return None

tabs=st.tabs(['🦺 Safety & PPE','🧱 Crack Diagnostics','📐 Planning & Valuation','🌦️ Site Assistant'])
with tabs[0]:
    st.header('Site Safety & PPE Audit')
    st.caption('AI image inspection is available only with a working Gemini key. Demonstration output is illustrative and not based on the uploaded photo.')
    img=photo_input('ppe')
    if st.button('Analyze site safety',type='primary',key='ppego'):
        if img is None:st.warning('Upload a construction site photo first.')
        else:
            schema='Return ONLY a JSON object with keys safety_score (integer 0-100), overall_status (string), ppe_detection (object with helmets, high_visibility_vests, steel_toe_boots, safety_harnesses each set to Present, Missing, or Cannot determine), hazards (array of objects with hazard, severity [Low, Medium, High, Critical], corrective_action), summary (string). Do not claim to identify hidden details such as footwear if not visible. Use conservative uncertainty. Assess visual evidence only; OSHA and IS 456 compliance cannot be certified from a photo.'
            raw=gemini(schema,img)
            data=json_response(raw) if raw else None
            if not api_key:
                data={'mode':'DEMONSTRATION — NOT IMAGE ANALYSIS','safety_score':70,'overall_status':'Illustrative example only','ppe_detection':{x:'Not assessed' for x in ['helmets','high_visibility_vests','steel_toe_boots','safety_harnesses']},'hazards':[{'hazard':'Example: unprotected edge','severity':'High','corrective_action':'Install compliant edge protection and verify on site'}],'summary':'This is sample output. Connect Gemini for an image-based assessment.'}
            if data:
                st.metric('Safety score',f"{data.get('safety_score','N/A')}/100")
                st.write('**Status:**',data.get('overall_status','Unknown'))
                st.write('**PPE checklist**');st.json(data.get('ppe_detection',{}))
                st.write('**Hazards & corrective actions**');st.dataframe(pd.DataFrame(data.get('hazards',[])),use_container_width=True)
                st.write(data.get('summary',''))
                download(data,'site_safety_report.json')
with tabs[1]:
    st.header('Crack Diagnostics & Structural Integrity')
    img=photo_input('crack')
    st.warning('A photograph cannot reliably determine structural safety, crack depth, or precise crack width without a calibrated reference. Consult a licensed structural engineer for suspected structural damage.')
    if st.button('Analyze concrete / wall surface',type='primary'):
        if img is None:st.warning('Upload a wall or concrete photo first.')
        else:
            prompt='Return ONLY JSON with keys defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, None apparent, Uncertain), estimated_width_mm (number or null; null unless a reliable scale is visible), possible_causes (array of strings), suggested_repairs (array of strings), urgency (Low/Medium/High/Critical), limitations (string). Analyze only what is visible; never assert structural safety from a photo.'
            raw=gemini(prompt,img); data=json_response(raw) if raw else None
            if not api_key:data={'mode':'DEMONSTRATION — NOT IMAGE ANALYSIS','defect_type':'Uncertain','estimated_width_mm':None,'possible_causes':['Example: shrinkage or thermal movement'],'suggested_repairs':['Inspect and measure on site','Seek a structural engineer if cracks widen or are diagonal/stepped'],'urgency':'Requires site assessment','limitations':'Demo data; no photo analysis performed.'}
            if data:
                c1,c2=st.columns(2);c1.metric('Defect classification',data.get('defect_type','Uncertain'));c2.metric('Urgency',data.get('urgency','Uncertain'))
                st.json(data);download(data,'crack_diagnostic_report.json')
with tabs[2]:
    st.header('Planning & Real Estate Valuation')
    c1,c2,c3=st.columns(3)
    with c1:
        area=st.number_input('Built-up area (sq ft)',min_value=100.0,value=2000.0,step=100.0)
        kind=st.selectbox('Structure type',['Residential','Commercial','Industrial'])
        cost_rate=st.number_input('Construction cost (₹/sq ft)',min_value=100.0,value=2200.0,step=100.0)
    with c2:
        location=st.selectbox('Location tier',['Tier 1','Tier 2','Tier 3'])
        completion=st.slider('Project completion (%)',0,100,40)
        land_value=st.number_input('Land / plot value (₹)',min_value=0.0,value=2000000.0,step=100000.0)
    with c3:
        market_rate=st.number_input('Market value of completed built-up area (₹/sq ft)',min_value=100.0,value=4500.0,step=100.0)
        cement_factor=st.number_input('Cement requirement (bags per sq ft)',min_value=0.0,value=0.4,step=0.05,format='%.2f',help='Illustrative planning factor; replace with a quantity surveyor’s estimate.')
        steel_factor=st.number_input('Steel requirement (kg per sq ft)',min_value=0.0,value=4.0,step=0.5,help='Illustrative planning factor; replace with structural design quantities.')
    budget=area*cost_rate; incurred=budget*completion/100;remaining=budget-incurred; valuation=land_value+area*market_rate
    a,b,c,d=st.columns(4)
    a.metric('Total construction budget',f'₹{budget:,.0f}')
    b.metric('Estimated incurred cost',f'₹{incurred:,.0f}')
    c.metric('Estimated remaining cost',f'₹{remaining:,.0f}')
    d.metric('Illustrative completed market value',f'₹{valuation:,.0f}')
    st.progress(completion/100,text=f'Construction progress: {completion}%')
    st.write('**Approximate material planning quantities**')
    st.dataframe(pd.DataFrame([{'Material':'Cement','Quantity':f'{area*cement_factor:,.0f} bags'},{'Material':'Steel','Quantity':f'{area*steel_factor:,.0f} kg'}]),hide_index=True,use_container_width=True)
    st.caption('All figures are user-input-based estimates, not live market appraisals or engineering bills of quantities. Location tier and structure type are descriptive and do not silently change the rates you enter.')
    if st.button('Generate 3D rendering prompt'):
        prompt=f'Create a realistic architectural 3D visualization of a {kind.lower()} building in an Indian {location.lower()} city, approximately {area:,.0f} square feet of built-up area. Show modern, buildable materials, context, landscaping, realistic daylight, and a clear three-quarter perspective. Do not invent exact floor count or structural drawings.'
        st.code(prompt,language='text');st.caption('Copy this prompt into an architectural visualization tool; no image is generated in this app.')
    download({'structure_type':kind,'location_tier':location,'area_sqft':area,'completion_percent':completion,'budget_inr':budget,'incurred_inr':incurred,'remaining_inr':remaining,'illustrative_market_value_inr':valuation,'cement_bags_estimate':area*cement_factor,'steel_kg_estimate':area*steel_factor},'project_valuation.json')
with tabs[3]:
    st.header('Daily Site Assistant & Weather-Aware Advisory')
    weather=st.selectbox('Select observed weather condition',['Normal','High Wind','Heavy Rain','Extreme Heat'])
    advice={
        'Normal':['Conduct daily toolbox talk and PPE checks.','Inspect scaffolds, lifting equipment, and access routes.','Maintain curing and housekeeping schedules.'],
        'High Wind':['Suspend crane lifts and work at height when manufacturer/site wind limits are exceeded.','Secure loose materials, hoardings, and temporary structures.','Have the competent site supervisor reassess work before restarting.'],
        'Heavy Rain':['Suspend unsafe excavation and electrical work.','Inspect drainage, slopes, trenches, and waterlogged access.','Protect electrical equipment with appropriate isolation and weatherproofing.'],
        'Extreme Heat':['Schedule rest, shade, and drinking-water breaks.','Monitor workers for heat illness and adjust strenuous tasks.','Review concrete placement and curing plans for hot weather.']}
    for line in advice[weather]:st.info('• '+line)
    st.caption('This is a manually selected scenario, not a live weather forecast or site-specific stop-work threshold.')
    st.subheader('Construction engineering assistant')
    if 'messages' not in st.session_state:st.session_state.messages=[]
    for m in st.session_state.messages:st.chat_message(m['role']).write(m['content'])
    question=st.chat_input('Ask about construction safety, materials, cracks, or site planning…')
    if question:
        st.session_state.messages.append({'role':'user','content':question});st.chat_message('user').write(question)
        if api_key:
            history='\n'.join(f"{m['role']}: {m['content']}" for m in st.session_state.messages[-12:])
            answer=gemini('You are a cautious Indian construction engineering assistant. Provide practical general guidance, note uncertainty, do not certify structural safety, and advise qualified inspection for high-risk decisions.\n'+history)
            answer=answer or 'The AI service is unavailable. Check the API key and retry.'
        else:
            answer='DEMONSTRATION MODE: I cannot answer project-specific engineering questions without an AI key. For immediate guidance, document site conditions, follow approved drawings and local safety procedures, and consult the responsible qualified engineer for structural or safety-critical decisions.'
        st.session_state.messages.append({'role':'assistant','content':answer});st.chat_message('assistant').write(answer)
