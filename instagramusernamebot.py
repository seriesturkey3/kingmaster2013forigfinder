import streamlit as st
import instaloader
import requests
import random
import string
import os
import json
import time
import io
from datetime import datetime
from PIL import Image
import pandas as pd
import base64

# Set page configuration
st.set_page_config(
    page_title="Instagram Bot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with sea blue accents
def apply_custom_css():
    st.markdown("""
    <style>
    /* Dark theme with sea blue accents */
    .stApp {
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #0077B6;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0096c7;
    }
    .stTextInput>div>div>input {
        background-color: #1F1F1F;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #1F1F1F;
        color: white;
    }
    .stSelectbox>div>div>select {
        background-color: #1F1F1F;
        color: white;
    }
    .stHeader {
        color: #0077B6;
    }
    .stSubheader {
        color: #0096c7;
    }
    .profile-card {
        background-color: #1F1F1F;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        padding: 10px;
        color: #0077B6;
        font-size: 0.8rem;
    }
    .highlight {
        color: #0096c7;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F1F1F;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0077B6;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
apply_custom_css()

# Initialize session state variables
if 'instaloader' not in st.session_state:
    st.session_state.instaloader = instaloader.Instaloader()
if 'bulk_results' not in st.session_state:
    st.session_state.bulk_results = []

# Title and description
st.title("Instagram Bot")
st.markdown("A powerful tool for Instagram profile information and username tools")

# Create tabs
tabs = st.tabs(["Profile Info", "Username Tools", "Bulk Fetching"])

# Profile Info Tab
with tabs[0]:
    st.subheader("Profile Information")
    
    username = st.text_input("Enter Instagram Username", key="profile_username")
    
    if st.button("Fetch Profile", key="fetch_profile_button"):
        if username:
            with st.spinner("Fetching profile information..."):
                try:
                    # Get profile information
                    profile = instaloader.Profile.from_username(st.session_state.instaloader.context, username)
                    
                    # Create two columns for layout
                    col1, col2 = st.columns([1, 2])
                    
                    # Display profile picture in the first column
                    with col1:
                        try:
                            response = requests.get(profile.profile_pic_url)
                            img = Image.open(io.BytesIO(response.content))
                            st.image(img, width=200, caption=f"@{profile.username}")
                        except Exception as e:
                            st.error(f"Error loading profile picture: {str(e)}")
                    
                    # Display profile information in the second column
                    with col2:
                        st.markdown(f"<div class='profile-card'>", unsafe_allow_html=True)
                        st.markdown(f"<h3 class='highlight'>@{profile.username}</h3>", unsafe_allow_html=True)
                        st.markdown(f"**Full Name:** {profile.full_name}")
                        
                        if profile.biography:
                            st.markdown("**Biography:**")
                            st.markdown(f"<div style='background-color:#2A2A2A; padding:10px; border-radius:5px;'>{profile.biography}</div>", unsafe_allow_html=True)
                        
                        if profile.external_url:
                            st.markdown(f"**Website:** [{profile.external_url}]({profile.external_url})")
                        
                        # Create metrics for followers, following, and posts
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        metrics_col1.metric("Followers", f"{profile.followers:,}")
                        metrics_col2.metric("Following", f"{profile.followees:,}")
                        metrics_col3.metric("Posts", f"{profile.mediacount:,}")
                        
                        # Additional information
                        info_col1, info_col2 = st.columns(2)
                        info_col1.markdown(f"**Private Account:** {'Yes' if profile.is_private else 'No'}")
                        info_col2.markdown(f"**Verified:** {'Yes' if profile.is_verified else 'No'}")
                        
                        if profile.is_business_account:
                            st.markdown(f"**Business Account:** Yes")
                            if hasattr(profile, 'business_category_name') and profile.business_category_name:
                                st.markdown(f"**Category:** {profile.business_category_name}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                except instaloader.exceptions.ProfileNotExistsException:
                    st.error(f"Profile '{username}' does not exist.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a username")

# Username Tools Tab
with tabs[1]:
    st.subheader("Username Tools")
    
    # Create two columns for layout
    col1, col2 = st.columns(2)
    
    # Username Checker (left column)
    with col1:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("### Check Username Availability")
        
        check_username = st.text_input("Enter username to check", key="check_username")
        
        if st.button("Check Availability", key="check_button"):
            if check_username:
                with st.spinner("Checking username availability..."):
                    try:
                        try:
                            profile = instaloader.Profile.from_username(st.session_state.instaloader.context, check_username)
                            st.error(f"Username '{check_username}' is already taken by:")
                            st.markdown(f"**Full Name:** {profile.full_name}")
                            st.markdown(f"**Followers:** {profile.followers:,}")
                            if profile.is_verified:
                                st.markdown("**Account Status:** ✓ Verified")
                        except instaloader.exceptions.ProfileNotExistsException:
                            st.success(f"Username '{check_username}' appears to be available!")
                            st.info("Note: Instagram may still reject this username based on their policies.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a username to check")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Username Generator (right column)
    with col2:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("### Generate Username Suggestions")
        
        base_word = st.text_input("Base Word (optional)", key="base_word")
        num_suggestions = st.slider("Number of Suggestions", min_value=1, max_value=20, value=5)
        
        if st.button("Generate Usernames", key="generate_button"):
            with st.spinner("Generating username suggestions..."):
                # Common suffixes and prefixes
                suffixes = ["_official", "_real", "the_", "_", ".", "__", "official", "real"]
                prefixes = ["the", "real", "official", "its", "im", "i_am"]
                
                suggestions = []
                
                # Generate random usernames
                for _ in range(num_suggestions):
                    if base_word:
                        # Use the base word
                        choice = random.randint(1, 4)
                        if choice == 1:
                            # Add random suffix
                            suffix = random.choice(suffixes)
                            username = base_word + suffix
                        elif choice == 2:
                            # Add random prefix
                            prefix = random.choice(prefixes)
                            username = prefix + "_" + base_word
                        elif choice == 3:
                            # Add random numbers
                            numbers = ''.join(random.choices(string.digits, k=random.randint(2, 4)))
                            username = base_word + numbers
                        else:
                            # Mix of letters and base word
                            letters = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 4)))
                            username = base_word + "_" + letters
                    else:
                        # Generate completely random username
                        length = random.randint(5, 12)
                        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
                    
                    suggestions.append(username)
                
                # Display generated usernames
                st.markdown("#### Generated Usernames:")
                
                # Create a DataFrame for better display
                df = pd.DataFrame({"Username": suggestions})
                
                # Display the DataFrame
                st.dataframe(df, hide_index=True)
                
                # Add a selectbox to choose a username to check
                selected_username = st.selectbox(
                    "Select a username to check availability:",
                    [""] + suggestions
                )
                
                if selected_username and st.button("Check Selected Username"):
                    with st.spinner(f"Checking {selected_username}..."):
                        try:
                            try:
                                profile = instaloader.Profile.from_username(st.session_state.instaloader.context, selected_username)
                                st.error(f"Username '{selected_username}' is already taken.")
                            except instaloader.exceptions.ProfileNotExistsException:
                                st.success(f"Username '{selected_username}' appears to be available!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

# Bulk Fetching Tab
with tabs[2]:
    st.subheader("Bulk Profile Fetching")
    
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("Enter usernames (one per line):")
    
    # Text area for usernames - Fixed the empty label issue
    bulk_usernames = st.text_area("Usernames", height=150, key="bulk_usernames")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Fetch Profiles", key="fetch_bulk_button"):
            usernames = [u.strip() for u in bulk_usernames.split('\n') if u.strip()]
            
            if usernames:
                st.session_state.bulk_results = []
                progress_bar = st.progress(0)
                
                for i, username in enumerate(usernames):
                    with st.spinner(f"Fetching {username}... ({i+1}/{len(usernames)})"):
                        try:
                            profile = instaloader.Profile.from_username(st.session_state.instaloader.context, username)
                            
                            # Format profile information
                            info = {
                                "username": profile.username,
                                "full_name": profile.full_name,
                                "followers": profile.followers,
                                "following": profile.followees,
                                "posts": profile.mediacount,
                                "private": profile.is_private,
                                "verified": profile.is_verified,
                                "status": "success"
                            }
                            
                            st.session_state.bulk_results.append(info)
                            
                        except instaloader.exceptions.ProfileNotExistsException:
                            info = {
                                "username": username,
                                "status": "not_found",
                                "error": "Profile does not exist"
                            }
                            st.session_state.bulk_results.append(info)
                            
                        except Exception as e:
                            info = {
                                "username": username,
                                "status": "error",
                                "error": str(e)
                            }
                            st.session_state.bulk_results.append(info)
                        
                        # Update progress bar
                        progress_bar.progress((i + 1) / len(usernames))
                        
                        # Add a small delay to avoid rate limiting
                        time.sleep(1)
                
                st.success(f"Completed fetching {len(usernames)} profiles!")
            else:
                st.warning("Please enter at least one username")
    
    with col2:
        if st.button("Export Results", key="export_button"):
            if st.session_state.bulk_results:
                # Convert results to DataFrame
                df = pd.DataFrame(st.session_state.bulk_results)
                
                # Convert DataFrame to CSV
                csv = df.to_csv(index=False)
                
                # Create a download button
                b64 = base64.b64encode(csv.encode()).decode()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"instagram_profiles_{timestamp}.csv"
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No results to export")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.bulk_results:
        st.markdown("### Results")
        
        # Create tabs for different views
        result_tabs = st.tabs(["Table View", "Card View"])
        
        with result_tabs[0]:
            # Table view
            df = pd.DataFrame(st.session_state.bulk_results)
            st.dataframe(df, use_container_width=True)
        
        with result_tabs[1]:
            # Card view
            for result in st.session_state.bulk_results:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                
                if result["status"] == "success":
                    st.markdown(f"<h3 class='highlight'>@{result['username']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**Full Name:** {result['full_name']}")
                    
                    # Create metrics for followers, following, and posts
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    metrics_col1.metric("Followers", f"{result['followers']:,}")
                    metrics_col2.metric("Following", f"{result['following']:,}")
                    metrics_col3.metric("Posts", f"{result['posts']:,}")
                    
                    # Additional information
                    info_col1, info_col2 = st.columns(2)
                    info_col1.markdown(f"**Private Account:** {'Yes' if result['private'] else 'No'}")
                    info_col2.markdown(f"**Verified:** {'Yes' if result['verified'] else 'No'}")
                
                elif result["status"] == "not_found":
                    st.markdown(f"<h3>@{result['username']}</h3>", unsafe_allow_html=True)
                    st.error("Profile does not exist")
                
                else:
                    st.markdown(f"<h3>@{result['username']}</h3>", unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                
                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Made by [KingMaster2013]</div>", unsafe_allow_html=True)
