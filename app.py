import json
import os
import re
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='LearnLoop AI · V2', page_icon='🎓', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp {background: radial-gradient(circle at 80% 0%, #172c49 0%, #0b1424 48%, #090e19 100%); color:#eaf1ff}
.block-container {padding-top:2rem;max-width:1150px}
[data-testid="stSidebar"] {background:#101b2d}
h1,h2,h3 {letter-spacing:-.035em}
.hero {padding:24px 28px;border:1px solid #324963;border-radius:22px;background:linear-gradient(110deg,#19345b,#182339);margin-bottom:18px}
.hero h1 {margin:0;color:#fff;font-size:2.6rem}.hero p{color:#c5d7f3;margin:8px 0 0}
.tag{display:inline-block;border-radius:30px;background:#28547a;color:#c9f1ff;padding:5px 12px;font-size:12px}
[data-testid="stMetric"]{background:#14253b;padding:14px;border-radius:14px;border:1px solid #29405d}
.stButton button[kind="primary"] {background:#38a7f6;color:#081423;border-radius:12px}
</style>''', unsafe_allow_html=True)

DEMO = {
 'Photosynthesis': {'lesson':'Plants absorb sunlight using chlorophyll in chloroplasts. They use carbon dioxide and water to produce glucose, releasing oxygen.', 'question':'What absorbs light energy in photosynthesis?', 'choices':['Chlorophyll','Oxygen','Roots','Glucose'],'correct':0,'why':'Chlorophyll is the pigment that captures light.'},
 "Newton's Laws": {'lesson':"Newton's first law describes inertia: motion stays unchanged unless a net external force acts. The second law is F = ma, and the third describes equal and opposite forces.", 'question':'Which expression represents Newton’s second law?', 'choices':['F = ma','E = mc²','V = IR','p = mv²'],'correct':0,'why':'Net force equals mass times acceleration.'},
 'Fractions': {'lesson':'A fraction describes part of a whole. To add fractions, find a common denominator, add numerators, then simplify.', 'question':'What is 1/2 + 1/4?', 'choices':['1/4','2/6','3/4','1/8'],'correct':2,'why':'1/2 is 2/4, and 2/4 + 1/4 = 3/4.'},
}

def init():
 for key, value in {'messages':[], 'results':[], 'quiz':None, 'quiz_done':False, 'lesson':'', 'topic':'Photosynthesis', 'mode':'Demo (no key needed)'}.items():
  if key not in st.session_state: st.session_state[key]=value
init()

def get_key():
 key=os.getenv('GEMINI_API_KEY','').strip()
 if key: return key
 try: return str(st.secrets.get('GEMINI_API_KEY','')).strip()
 except Exception: return ''

def ai(prompt, system):
 from google import genai
 from google.genai import types
 client=genai.Client(api_key=get_key())
 response=client.models.generate_content(model='gemini-3.5-flash-lite',contents=prompt,config=types.GenerateContentConfig(system_instruction=system,temperature=0.5,max_output_tokens=850))
 if not response.text: raise ValueError('AI returned an empty response. Try again.')
 return response.text.strip()

def fallback_explain(topic):
 if topic in DEMO: return DEMO[topic]['lesson']
 return f'Demo mode has prepared lessons for {", ".join(DEMO)}. Add a Gemini API key in the sidebar to study “{topic}” with live AI.'

def explain(topic, level):
 if st.session_state.mode.startswith('Demo'): return fallback_explain(topic)
 return ai(f'Explain {topic} to a {level} learner in about 130 words. Include one real-world analogy and one check-for-understanding question.', 'You are LearnLoop, a supportive and accurate educational tutor. Encourage understanding, do not claim you performed actions you did not perform.')

def make_quiz(topic, level):
 if st.session_state.mode.startswith('Demo'):
  d=DEMO.get(topic, DEMO['Photosynthesis'])
  return {'question':d['question'],'choices':d['choices'],'correct_index':d['correct'],'explanation':d['why'],'topic':topic}
 raw=ai(f'Create ONE {level} multiple choice question about {topic}. Return ONLY JSON with keys question (string), choices (array of exactly 4 strings), correct_index (integer 0-3), explanation (string).', 'You create clear, factual study questions. Output valid JSON only, no markdown.')
 raw=re.sub(r'^```(?:json)?\s*|\s*```$', '',raw.strip(),flags=re.I)
 data=json.loads(raw)
 if not isinstance(data.get('choices'),list) or len(data['choices'])!=4 or not isinstance(data.get('correct_index'),int) or not 0<=data['correct_index']<=3: raise ValueError('Quiz response format invalid. Please retry.')
 for k in ('question','explanation'): 
  if not isinstance(data.get(k),str): raise ValueError('Quiz response incomplete. Please retry.')
 data['topic']=topic
 return data

def chat_answer(question,topic,level):
 if st.session_state.mode.startswith('Demo'):
  return fallback_explain(topic)+'\n\nDemo mode: enable Gemini in the sidebar for a personalized response to your question.'
 history='\n'.join(f"{m['role']}: {m['content']}" for m in st.session_state.messages[-8:])
 return ai(f'Current topic: {topic}\nStudent level: {level}\nConversation:\n{history}\nStudent: {question}', 'You are LearnLoop, a concise patient study coach. Prefer hints and short explanations. Avoid collecting personal information.')

with st.sidebar:
 st.markdown('### 🎓 LearnLoop AI')
 st.caption('Your learning command center')
 st.session_state.mode=st.radio('Engine', ['Demo (no key needed)','Gemini AI (API key required)'],index=0 if st.session_state.mode.startswith('Demo') else 1)
 key=get_key()
 if st.session_state.mode.startswith('Gemini'):
  if key: st.success('API key found — AI mode ready')
  else: st.warning('No API key found. Follow SETUP_GUIDE.md to configure one.')
 st.divider()
 topic=st.text_input('Study topic',value=st.session_state.topic,help='Try Photosynthesis, Fractions, or any topic in Gemini mode').strip() or 'Photosynthesis'
 st.session_state.topic=topic
 level=st.select_slider('Learning level',options=['Beginner','Intermediate','Advanced'],value='Beginner')
 st.caption('Demo mode supports Photosynthesis, Newton’s Laws, and Fractions.')
 st.divider()
 if st.button('🧹 Reset current session',use_container_width=True):
  for k in ('messages','results','quiz','quiz_done','lesson'): st.session_state.pop(k,None)
  st.rerun()
 st.caption('Privacy: study questions sent in Gemini mode go to the API provider. Avoid personal or sensitive details.')

st.markdown('<div class="hero"><span class="tag">ALEXA+-INSPIRED · SIMULATED EXPERIENCE</span><h1>LearnLoop AI ✨</h1><p>Learn a concept. Test your understanding. Build a smarter revision plan.</p></div>',unsafe_allow_html=True)
correct=sum(r['correct'] for r in st.session_state.results)
attempts=len(st.session_state.results)
c1,c2,c3=st.columns(3)
c1.metric('Questions answered',attempts)
c2.metric('Correct',correct)
c3.metric('Accuracy',f'{correct/attempts:.0%}' if attempts else '—')

tab1,tab2,tab3,tab4=st.tabs(['💬 AI Tutor','🧠 Quiz Studio','📅 Revision Planner','🎬 Demo Guide'])
with tab1:
 st.subheader('Ask, explore, understand')
 if st.button('✨ Explain my topic',type='primary'):
  try:
   with st.spinner('Preparing your lesson...'): st.session_state.lesson=explain(topic,level)
  except Exception as exc: st.error(f'Could not generate lesson: {exc}')
 if st.session_state.lesson: st.info(st.session_state.lesson)
 for msg in st.session_state.messages:
  with st.chat_message(msg['role']): st.markdown(msg['content'])
 question=st.chat_input('Ask a question about your topic…')
 if question:
  try:
   with st.spinner('Thinking...'): answer=chat_answer(question,topic,level)
   st.session_state.messages.extend([{'role':'user','content':question},{'role':'assistant','content':answer}])
   st.rerun()
  except Exception as exc: st.error(f'Chat failed: {exc}')
with tab2:
 st.subheader('Practice one question at a time')
 if st.button('🎲 Generate a new quiz',type='primary'):
  try:
   with st.spinner('Building your quiz...'): st.session_state.quiz=make_quiz(topic,level)
   st.session_state.quiz_done=False
  except Exception as exc: st.error(f'Quiz generation failed: {exc}')
 q=st.session_state.quiz
 if q:
  st.markdown(f"**{q['question']}**")
  if not st.session_state.quiz_done:
   with st.form('quiz_answer'):
    choice=st.radio('Choose an answer',list(range(4)),format_func=lambda i:q['choices'][i],index=None)
    submit=st.form_submit_button('Check answer',type='primary')
   if submit:
    if choice is None: st.warning('Select an answer first.')
    else:
     good=choice==q['correct_index']
     st.session_state.results.append({'topic':q['topic'],'correct':good,'when':datetime.now().isoformat(timespec='seconds'),'question':q['question']})
     st.session_state.quiz_done=True
     st.rerun()
  else:
   last=st.session_state.results[-1]
   if last['correct']: st.success('Correct! Well done.')
   else: st.warning(f"Keep practicing. Correct answer: {q['choices'][q['correct_index']]}")
   st.info(q['explanation'])
   st.caption('Generate a new quiz to continue.')
with tab3:
 st.subheader('Your personalized revision plan')
 if not attempts: st.info('Take a quiz first. Your revision plan will appear here.')
 else:
  topics=sorted(set(r['topic'] for r in st.session_state.results))
  for name in topics:
   records=[r for r in st.session_state.results if r['topic']==name]
   hits=sum(r['correct'] for r in records)
   rate=hits/len(records)
   st.markdown(f'**{name}** — {hits}/{len(records)} correct')
   st.progress(rate)
   if rate<0.7: st.warning('Priority: Review the explanation, then try another question tomorrow.')
   else: st.success('Good progress: Revisit this topic in 3 days.')
  st.caption('Revision recommendations are simple rule-based suggestions, not a clinical or educational assessment.')
  st.download_button('⬇️ Export progress (JSON)',data=json.dumps(st.session_state.results,indent=2),file_name='learnloop-progress.json',mime='application/json')
with tab4:
 st.subheader('90-second demo script')
 st.markdown('''1. **0–15s:** Introduce LearnLoop as an Alexa+-inspired *simulation*.
2. **15–35s:** Ask the tutor to explain photosynthesis.
3. **35–65s:** Generate and answer a quiz; deliberately miss one answer.
4. **65–80s:** Show how the revision plan prioritizes that topic.
5. **80–90s:** Mention Gemini AI, honest limitations, and future Alexa+ integration.''')
 st.caption('This project does not connect to an Alexa device or the official Alexa+ API.')
