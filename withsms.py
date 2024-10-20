import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pickle
import os
import streamlit_authenticator as stauth
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

USER_DATA_FILE = 'user_scheme.pkl'

# File paths
USER_PROFILES_FILE = 'user.csv'
SCHEMES_FILE = 'ds1.csv'



# Load user data using pickle
def load_user_data():
    if os.path.exists(USER_DATA_FILE) and os.path.getsize(USER_DATA_FILE) > 0:  # Check if file exists and is not empty
        with open(USER_DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return []  # Return empty list if file does not exist or is empty



# Initialize files if they don't exist
def initialize_files():
    if not os.path.isfile(USER_PROFILES_FILE):
        pd.DataFrame(columns=['username', 'gender','age', 'state','income', 'student', 'married', 'email','phone']).to_csv(USER_PROFILES_FILE,
                                                                                                    index=False)
    if not os.path.isfile(SCHEMES_FILE):
        pd.DataFrame(
            columns=['NAME', 'STATE', 'GENDER', 'START AGE', 'END AGE', 'INCOME', 'STUDENT', 'MARRIED']).to_csv(
            SCHEMES_FILE, index=False)


initialize_files()

# Temporary dictionaries to store user credentials
#user_db = {'user': 'pass','pradeep':'123'}
admin_credentials = {'admin': 'admin123'}
user_interactions = []  # To track user interactions

# Set page config
st.set_page_config(page_title="GovSchemes", page_icon="🏛️", layout="wide")


def save_user_data(user_data):
    with open(USER_DATA_FILE, 'wb') as f:
        pickle.dump(user_data, f)


def authenticate_user(username, password):
    user_data = load_user_data()
    for user in user_data:
        if user['username'] == username and user['password'] == password:
            return True, user
    return False, None

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_phone_number, message_body):
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=''
    )
    


def recommend():
    st.title("Schemes You are eligible for")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        st.write(f"Welcome, {st.session_state['username']}!")
        if st.button("👤 Manage Profile", key="manage_profile"):
            st.session_state["page"] = "manage_profile"
        if st.button("🚪 Logout", key="logout"):
            st.session_state["logged_in"] = False
            st.session_state["page"] = "login"

    col1, col2 = st.columns(2)
    df = pd.read_csv(USER_PROFILES_FILE)
    df.set_index("username", inplace = True)

    gender = df.loc[st.session_state["username"],'gender']
    age = df.loc[st.session_state["username"],'age']
    state = df.loc[st.session_state["username"],'state']

    income = df.loc[st.session_state["username"],'income']
    student = df.loc[st.session_state["username"],'student']
    married = df.loc[st.session_state["username"],'married']
    

    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.button("🔍 Find Schemes")
    with col2:
        view_all_button = st.button("📊 View All Schemes")

    if submit_button:
        user_input = {
            'gender': gender,
            'age': age,
            'state': state,
            'income': income,
            'student': student,
            'married': married
        }

        # Load and update user profile preferences
        df_profiles = pd.read_csv(USER_PROFILES_FILE)
        #profile_preferences = df_profiles[df_profiles['username'] == st.session_state["username"]].iloc[0].to_dict()
        #for key in profile_preferences:
            #if profile_preferences[key] != 'any' and key in user_input:
                #user_input[key] = profile_preferences[key]

        df = load_data(SCHEMES_FILE)
        recommendations = recommend_schemes(user_input, df)

        if not recommendations.empty:
            st.success("Schemes you are eligible for:")
            st.dataframe(recommendations.style.highlight_max(axis=0))
        else:
            st.warning("No schemes found matching your criteria.")

        # Log user interaction
        user_interactions.append({
            'username': st.session_state["username"],
            'action': 'find_schemes',
            'details': user_input,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    if view_all_button:
        df = load_data(SCHEMES_FILE)
        st.subheader("📚 All Available Schemes")
        st.dataframe(df[['NAME', 'STATE', 'GENDER', 'START AGE', 'END AGE', 'INCOME', 'STUDENT', 'MARRIED']])

    if st.button("🔙 Back", key="back_recommendation"):
        st.session_state["page"] = "login"


def signup_user(username, password):
    user_data = load_user_data()  # Load existing user data
    
    # Check if username already exists
    for user in user_data:
        if user['username'] == username:
            return False  # Username already exists
    
    # Add new user to the existing list
    user_profile = {
        'username': username,
        'password': password
    }
    user_data.append(user_profile)  # Append new user to the list
    save_user_data(user_data)  # Save the updated user data back to pickle
    return True


def sign_up():
    st.header("🖊️ Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Choose a Username:", key="sign_up_username", help="Enter a username for your account")
        password = st.text_input("Choose a Password:", type="password", key="sign_up_password",
                                 help="Enter a password for your account")
        confirm_password = st.text_input("Confirm Password:", type="password", key="confirm_password",
                                         help="Re-enter your password for confirmation")
        submit_button = st.form_submit_button("Sign Up")
        
        if submit_button:
            if signup_user(username, password):
                # Initialize user profile
                pd.DataFrame([[username, '', '', '', '','','','','']],
                                columns=['username', 'gender','age', 'state','income', 'student', 'married', 'email','phone']).to_csv(USER_PROFILES_FILE,
                                                                                                    mode='a',
                                                                                                    header=False,
                                                                                                    index=False)
                st.success("You have successfully signed up! Please log in.")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "manage_profile"
            
            else:
                st.warning("Username already exist")

        
               
    


def login():
    st.header("🔐 Login")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username:", key="login_username", help="Enter your username")
        password = st.text_input("Password:", type="password", key="login_password", help="Enter your password")

        if st.button("🚪 Login", key="login_button"):
            authenticated, user = authenticate_user(username, password)
            if authenticated:
                st.success(F"You have successfully logged in {user['username']} !")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "recommend"
            else:
                st.error("Invalid username or password")

    with col2:
        st.write("New user?")
        if st.button("📝 Sign Up", key="signup_button"):
            st.session_state["page"] = "sign_up"

        st.write("Admin?")
        if st.button("👑 Admin Login", key="admin_button"):
            if username in admin_credentials and admin_credentials[username] == password:
                st.success("Admin login successful!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "admin_dashboard"
            else:
                st.error("Invalid admin credentials")
    


def manage_profile():
    st.header("👤 Manage Profile")
    st.write("Update your profile preferences here.")

    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Preferred Gender:", ["any", "male", "female"], key="profile_gender")
        age = st.number_input("Enter Age:", min_value=0, max_value=100, value=25)
        state = st.text_input("Preferred State:", key="profile_state", help="Enter your preferred state").lower()
        phone= st.text_input("Enter phone number:")
       
    with col2:
        income = st.number_input("Enter Annual Income:", min_value=0, value=0)
        student = st.selectbox("Student Status:", ["any", "yes", "no"], key="profile_student")
        married = st.selectbox("Marital Status:", ["any", "yes", "no"], key="profile_married")
        email = st.text_input("Email:", key="profile_email", help="Enter your email address")

    if st.button("💾 Save Profile", key="save_profile"):
        profile_data = {
            'username': st.session_state["username"],
            'gender': gender,
            'age' : age,
            'state': state,
            'income' : income,
            'student': student,
            'married': married,
            'email': email,
            'phone' : phone
        }

        #Check if the CSV file exists and read it
        if os.path.isfile(USER_PROFILES_FILE):
            df = pd.read_csv(USER_PROFILES_FILE)
            #Check if the user profile already exists and update or append accordingly
            if profile_data['username'] in df['username'].values:
                df.loc[df['username'] == profile_data['username'], ['gender','age', 'state','income', 'student', 'married', 'email','phone']] = \
                    profile_data['gender'], profile_data['age'], profile_data['state'], profile_data['income'], \
                        profile_data['student'], profile_data['married'], profile_data['email'], profile_data['phone']
            else:
                # Create DataFrame for new profile and concatenate
                new_profile_df = pd.DataFrame([profile_data])
                df = pd.concat([df, new_profile_df], ignore_index=True)
        #else:
            # Create a new DataFrame if file does not exist
            #df = pd.DataFrame([profile_data])

        df.to_csv(USER_PROFILES_FILE, index=False)
        st.success("Profile updated successfully!")

    # Add a Back button to return to the recommendation page
    if st.button("🔙 go to recommendation page", key="back_to_recommendation"):
        st.session_state["page"] = "recommend"



def add_new_scheme(scheme_name, scheme_state, gender, start_age, end_age, income, student_status, marital_status):
    # Load existing schemes
    df_schemes = pd.read_csv('ds1.csv')

    scheme_name =scheme_name 
    scheme_state = scheme_state
    gender = gender
    start_age=start_age
    end_age= end_age
    income= income
    student_status=student_status
    marital_status= marital_status

    # Create new scheme entry
    new_scheme = pd.DataFrame([{
        'NAME': scheme_name,
        'STATE': scheme_state.lower(),
        'GENDER': gender,
        'START AGE': start_age,
        'END AGE': end_age,
        'INCOME': income,
        'STUDENT': student_status,
        'MARRIED': marital_status
    }])

    # Append new scheme to the existing schemes
    df_schemes = pd.concat([df_schemes, new_scheme], ignore_index=True)
    df_schemes.to_csv('ds1.csv', index=False)

    # Load user profiles to notify them
    df_profiles = pd.read_csv('user.csv')



    # Notify users who match the new scheme criteria
    for _,profile in df_profiles.iterrows():
        #print(int(profile['age']))
        if (profile['gender'].lower() == gender.lower() and profile['state'].lower() == scheme_state.lower() and \
        int(profile['age']) >= start_age and int(profile['age'])<=end_age and (profile['student'] == student_status) and \
            (profile['married'] == marital_status)):
            #Send SMS notification
            message_body = (f"Hello {profile['username']}, a new scheme '{scheme_name}' has been added "
                                f"that might be of interest to you. Check it out!")    
                
            #profile['phone']=str(profile['phone'])
            a='+' + str(profile['phone'])
            profile['phone']=a[:len(a)-2]

            #send_sms(profile['phone'],message_body)


            st.write(f"{profile['username']} Scheme added and notification sent")

        #else:
            #st.error("notification not sent")

    


# Admin Dashboard Function
def admin_dashboard():
    st.title("Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["Add New Scheme", "User Profiles", "User Interactions"])

    with tab1:
        st.header("Add New Scheme")

        with st.form(key='scheme_form'):
            scheme_name = st.text_input("Scheme Name")
            scheme_state = st.text_input("State")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            start_age = st.number_input("Start Age", min_value=0)
            end_age = st.number_input("End Age", min_value=0)
            income =  st.number_input("Enter Annual Income:", min_value=0, value=0)
            student_status = st.selectbox("Student", ["yes", "no"])
            marital_status = st.selectbox("Married", ["yes", "no"])

            submit_button = st.form_submit_button("Add Scheme")

            if submit_button:
                if all([scheme_name, scheme_state]):
                    add_new_scheme(
                        scheme_name,
                        scheme_state,
                        gender,
                        start_age,
                        end_age,
                        income,
                        student_status,
                        marital_status
                    )
                    st.success("New scheme added")
                else:
                    st.error("Please fill out all required fields.")

    with tab2:
        st.header("User Profiles")
        df_profiles = pd.read_csv('user.csv')
        st.write(df_profiles)

    with tab3:
        st.header("User Interactions")
        st.write("Here you can manage user interactions.")


# Run the application

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['GENDER'] = df['GENDER'].str.lower()
    df['STATE'] = df['STATE'].str.lower()
    df['STUDENT'] = df['STUDENT'].str.lower()
    df['MARRIED'] = df['MARRIED'].str.lower()
    return df


def recommend_schemes(user_input, df):
    filtered_df = df.copy()
    filtered_df = filtered_df[(filtered_df['GENDER'] == user_input['gender']) | (filtered_df['GENDER'] == 'any')]
    filtered_df = filtered_df[
        (filtered_df['START AGE'] <= user_input['age']) & (filtered_df['END AGE'] >= user_input['age'])]
    filtered_df = filtered_df[(filtered_df['STATE'] == user_input['state']) | (filtered_df['STATE'] == 'central')]
    filtered_df = filtered_df[(filtered_df['INCOME'] == 0) | (filtered_df['INCOME'] >= user_input['income'])]
    filtered_df = filtered_df[(filtered_df['STUDENT'] == user_input['student']) | (filtered_df['STUDENT'] == 'any')]
    filtered_df = filtered_df[(filtered_df['MARRIED'] == user_input['married']) | (filtered_df['MARRIED'] == 'any')]
    return filtered_df[['NAME', 'STATE']]


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        login()
    elif st.session_state["page"] == "sign_up":
        sign_up()
    elif st.session_state["page"] == "manage_profile":
        manage_profile()
    elif st.session_state["page"] == "recommend" and st.session_state.get("logged_in"):
        recommend()
    elif st.session_state["page"] == "admin_dashboard" and st.session_state.get("logged_in"):
        admin_dashboard()
    else:
        st.session_state["page"] = "login"


if __name__ == "__main__":
    main()
