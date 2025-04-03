import streamlit as st
import requests

# Flask API URL

FLASK_API_URL = "https://hackathonapi-882701280393.us-central1.run.app/analyze"  # Change this to the deployed API URL if hosted externally

def fetch_mcqs(job_desc):
    response = requests.post(FLASK_API_URL, data={'job_desc': job_desc})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch MCQs. Please try again.")
        return None

def main():
    st.title("AI-Powered Job-Specific Quiz")
    
    job_desc = st.text_area("Enter the job description:", height=150)
    
    if st.button("Generate Quiz"):
        if job_desc.strip():
            with st.spinner("Generating questions..."):
                mcq_data = fetch_mcqs(job_desc)
                if mcq_data:
                    st.session_state['mcq_questions'] = mcq_data['mcq_questions']
                    st.session_state['submitted'] = False
                    st.session_state['user_answers'] = {}
        else:
            st.warning("Please enter a job description.")
    
    if 'mcq_questions' in st.session_state and not st.session_state.get('submitted', False):
        st.subheader("Quiz")
        
        mcq_questions = st.session_state['mcq_questions']
        user_answers = {}
        
        for i, question in enumerate(mcq_questions):
            st.write(f"**Q{i+1}: {question['question']}**")
            options = question['options']
            choices = {opt['option']: opt['is_correct'] for opt in options}
            user_answers[i] = st.radio(f"Select an answer for Q{i+1}", list(choices.keys()), index=None, key=f"q{i+1}")
        
        st.session_state['user_answers'] = user_answers
        
        if st.button("Submit Quiz"):
            user_answers = st.session_state['user_answers']
            score = sum(1 for i, ans in user_answers.items() if ans is not None and any(opt['option'] == ans and opt['is_correct'] for opt in mcq_questions[i]['options']))
            total = len(mcq_questions)
            st.session_state['submitted'] = True
            st.success(f"You scored {score}/{total}!")
            
            # Reveal correct answers
            st.subheader("Correct Answers:")
            for i, question in enumerate(mcq_questions):
                correct_option = next(opt['option'] for opt in question['options'] if opt['is_correct'])
                st.write(f"**Q{i+1}: {question['question']}**")
                st.write(f"✅ Correct Answer: {correct_option}")

if __name__ == "__main__":
    main()
