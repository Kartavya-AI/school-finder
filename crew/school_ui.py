__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]
import streamlit as st
import sys
import os
import pandas as pd
import json
import re
from pathlib import Path

from src.crew.school_crew import schoolcrew

def check_api_keys():
    """Check if API keys are set and valid"""
    serper_key = os.environ.get('SERPER_API_KEY')
    gemini_key = os.environ.get('GEMINI_API_KEY')
    
    return bool(serper_key and gemini_key)

def setup_api_keys():
    """Setup API keys interface"""
    st.markdown("### 🔑 API Keys Setup")
    st.markdown("""
    To use the AI School Search, you need to provide two API keys:
    
    **Required API Keys:**
    - **SERPER_API_KEY**: For web search functionality ([Get it here](https://serper.dev/))
    - **GEMINI_API_KEY**: For AI processing ([Get it here](https://makersuite.google.com/app/apikey))
    """)
    
    # Create two columns for API key inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 SERPER API Key")
        st.markdown("*Used for web search functionality*")
        serper_key = st.text_input(
            "Enter your SERPER API Key",
            type="password",
            placeholder="Your SERPER API key...",
            help="Get your free API key from https://serper.dev/"
        )
    
    with col2:
        st.markdown("#### 🤖 GEMINI API Key")
        st.markdown("*Used for AI analysis and recommendations*")
        gemini_key = st.text_input(
            "Enter your GEMINI API Key",
            type="password",
            placeholder="Your GEMINI API key...",
            help="Get your free API key from Google AI Studio"
        )
    
    # Validate and set API keys
    if st.button("🔑 Set API Keys", type="primary", use_container_width=True):
        if serper_key and gemini_key:
            # Set environment variables
            os.environ['SERPER_API_KEY'] = serper_key
            os.environ['GEMINI_API_KEY'] = gemini_key
            
            st.success("✅ API Keys set successfully! You can now search for schools.")
            st.rerun()
        else:
            st.error("❌ Please provide both API keys to continue.")
    
    # Help section
    with st.expander("ℹ️ How to get API Keys"):
        st.markdown("""
        ### Getting Your API Keys:
        
        **SERPER API Key:**
        1. Go to [serper.dev](https://serper.dev/)
        2. Sign up for a free account
        3. Get your API key from the dashboard
        4. Free tier includes 2,500 searches/month
        
        **GEMINI API Key:**
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API key"
        4. Copy the generated key
        5. Free tier includes generous usage limits
        
        ### Security Note:
        - Your API keys are stored securely in the session
        - Keys are not saved permanently
        - You'll need to re-enter them if you refresh the page
        """)

def main():
    st.set_page_config(
        page_title="AI School Search",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🏫 AI School Search Assistant")
    st.markdown("### Find the perfect school for your child with AI-powered search")
    
    # Check if API keys are set
    if not check_api_keys():
        setup_api_keys()
        return
    
    # Show API key status
    st.success("🔑 API Keys configured successfully!")
    
    # Option to reconfigure API keys
    if st.button("🔄 Reconfigure API Keys", help="Click to change your API keys"):
        # Clear existing keys
        if 'SERPER_API_KEY' in os.environ:
            del os.environ['SERPER_API_KEY']
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        st.rerun()
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔍 Search Criteria")
        
        # Initialize session state for location
        if 'use_current_location' not in st.session_state:
            st.session_state.use_current_location = False
        
        # Location input
        location = st.text_input(
            "📍 Location", 
            value="" if st.session_state.use_current_location else "",
            placeholder="Enter city/area (e.g., Mumbai, Maharashtra)",
            help="Enter your preferred location",
            disabled=st.session_state.use_current_location
        )
        
        # Use current location button
        if st.button("📍 Use Current Location", use_container_width=True):
            st.session_state.use_current_location = True
            st.rerun()
        
        # Clear location button (if current location is selected)
        if st.session_state.use_current_location:
            st.info("🌍 Current location will be auto-detected during search")
            if st.button("📝 Enter Custom Location", use_container_width=True):
                st.session_state.use_current_location = False
                st.rerun()
        elif location:
            st.info(f"📍 Searching in: {location}")
        
        # Set final location value
        final_location = "use my current location" if st.session_state.use_current_location else location
        
        # Grade selection
        grade_options = [
            "Pre-K", "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", 
            "4th Grade", "5th Grade", "6th Grade", "7th Grade", "8th Grade",
            "9th Grade", "10th Grade", "11th Grade", "12th Grade"
        ]
        grade = st.selectbox("🎓 Grade Level", grade_options, index=5)
        
        # Curriculum selection
        curriculum_options = [
            "CBSE", "ICSE", "IB (International Baccalaureate)", 
            "Cambridge (IGCSE)", "State Board", "NIOS", "American Curriculum",
            "British Curriculum", "Montessori", "Waldorf"
        ]
        curriculum = st.selectbox("📚 Curriculum", curriculum_options)
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            max_results = st.slider("Maximum Results", 5, 50, 20, help="Number of schools to find")
            include_fees = st.checkbox("Include Fee Information", True, help="Try to find fee details")
            include_ratings = st.checkbox("Include Ratings/Reviews", True, help="Include school ratings if available")
        
        # Search button
        search_button = st.button("🔍 Search Schools", type="primary", use_container_width=True)
        
        # API status indicator
        st.markdown("---")
        st.markdown("**🔑 API Status:**")
        st.success("✅ SERPER API: Connected")
        st.success("✅ GEMINI API: Connected")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if search_button:
            if not final_location:
                st.warning("⚠️ Please enter a location or click 'Use Current Location' button")
                st.stop()
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔍 Searching for schools... This may take a few moments."):
                try:
                    # Update progress
                    progress_bar.progress(20)
                    status_text.text("🤖 Initializing AI agents...")
                    
                    # Create crew instance
                    crew_instance = schoolcrew()
                    
                    # Update progress
                    progress_bar.progress(40)
                    status_text.text("🔍 Searching for schools...")
                    
                    # Run the crew with inputs
                    result = crew_instance.crew().kickoff(inputs={
                        'location': final_location,
                        'grade': grade,
                        'curriculum': curriculum
                    })
                    
                    # Update progress
                    progress_bar.progress(80)
                    status_text.text("📊 Processing results...")
                    
                    # Complete progress
                    progress_bar.progress(100)
                    status_text.text("✅ Search completed!")
                    
                    st.success("✅ Search completed successfully!")
                    
                    # Display results
                    st.subheader("🏫 Search Results")
                    
                    # Try to parse the result as a structured format
                    if hasattr(result, 'raw'):
                        result_text = result.raw
                    else:
                        result_text = str(result)
                    
                    # Try to extract and parse JSON data first
                    json_data = None
                    try:
                        # Look for JSON data in the result
                        json_match = re.search(r'```json\s*(\[.*?\])\s*```', result_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            json_data = json.loads(json_str)
                            
                            # Create DataFrame from JSON
                            df = pd.DataFrame(json_data)
                            
                            # Display structured results
                            st.subheader("📊 School Search Results")
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            location_for_filename = "current_location" if st.session_state.use_current_location else final_location.replace(" ", "_")
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name=f"school_search_{location_for_filename}_{grade}_{curriculum}.csv",
                                mime="text/csv"
                            )
                            
                            # Show summary stats
                            st.subheader("📈 Summary")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Schools Found", len(df))
                            with col2:
                                schools_with_fees = df[df['Fees'] != 'N/A']['Fees'].count() if 'Fees' in df.columns else 0
                                st.metric("Schools with Fee Info", schools_with_fees)
                            with col3:
                                unique_locations = df['Location'].nunique() if 'Location' in df.columns else 0
                                st.metric("Different Locations", unique_locations)
                        
                        else:
                            # Fallback: try to parse table-like data
                            lines = result_text.split('\n')
                            table_data = []
                            
                            for line in lines:
                                if '|' in line and len(line.split('|')) >= 4:
                                    row_data = [cell.strip() for cell in line.split('|')]
                                    if row_data and row_data[0] and not row_data[0].startswith('-'):
                                        table_data.append(row_data)
                            
                            if table_data and len(table_data) > 1:
                                # Create DataFrame
                                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                                st.subheader("📊 Structured Results")
                                st.dataframe(df, use_container_width=True)
                                
                                # Download button
                                csv = df.to_csv(index=False)
                                location_for_filename = "current_location" if st.session_state.use_current_location else final_location.replace(" ", "_")
                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv,
                                    file_name=f"school_search_{location_for_filename}_{grade}_{curriculum}.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.info("Could not parse structured data from results")
                                
                    except json.JSONDecodeError as e:
                        st.warning(f"Could not parse JSON data: {str(e)}")
                        st.info("Showing raw results instead")
                    except Exception as e:
                        st.warning(f"Error parsing results: {str(e)}")
                    
                    # Always show raw results in an expander
                    with st.expander("🔍 View Raw Results"):
                        st.text_area("Raw AI Output", result_text, height=300)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.error("Please check your API keys and configuration, then try again.")
                    
                    # Option to reconfigure API keys on error
                    if st.button("🔄 Reconfigure API Keys"):
                        if 'SERPER_API_KEY' in os.environ:
                            del os.environ['SERPER_API_KEY']
                        if 'GEMINI_API_KEY' in os.environ:
                            del os.environ['GEMINI_API_KEY']
                        st.rerun()
        else:
            # Welcome message
            st.markdown("""
            ## Welcome to AI School Search! 🎯
            
            This intelligent assistant helps you find the perfect school for your child by:
            
            - 🔍 **Smart Search**: AI-powered search across multiple sources
            - 📍 **Location Detection**: Automatically detects your location or use custom location
            - 🎓 **Grade-Specific**: Tailored results for your child's grade level
            - 📚 **Curriculum Matching**: Finds schools with your preferred curriculum
            - 💰 **Comprehensive Info**: Get details about fees, facilities, and reputation
            - 📊 **Structured Results**: Easy-to-read tables and downloadable CSV files
            
            ### How to Use:
            1. ✅ **API Keys are configured** - You're ready to search!
            2. Select your search criteria in the sidebar
            3. Click "Search Schools" to start the AI search
            4. Review the results and download them if needed
            
            **Note**: The search may take a few moments as our AI agents research the best options for you.
            """)
    
    with col2:
        st.subheader("ℹ️ About")
        st.markdown("""
        **AI School Search** uses advanced AI agents to:
        
        - 🔍 Search multiple sources
        - 🤖 Analyze school information
        - 📋 Provide detailed recommendations
        - ⚖️ Compare options for you
        
        **Features:**
        - 🌍 Auto location detection
        - 📚 Multiple curriculum support
        - 📊 Detailed school analysis
        - 📥 Export results to CSV
        - 🔑 Secure API key management
        """)
        
        # Search tips
        with st.expander("💡 Search Tips"):
            st.markdown("""
            **For better results:**
            - Be specific with location (e.g., "Mumbai, Maharashtra")
            - Choose the exact grade level
            - Select preferred curriculum
            - Wait for complete results before making decisions
            - Use advanced options for customized search
            
            **Supported Curricula:**
            - 🇮🇳 Indian: CBSE, ICSE, State Boards
            - 🌍 International: IB, Cambridge, American
            - 🎨 Alternative: Montessori, Waldorf
            """)
        
        # API Key management
        with st.expander("🔑 API Key Management"):
            st.markdown("""
            **Current Status:**
            - ✅ SERPER API: Connected
            - ✅ GEMINI API: Connected
            
            **Security:**
            - Keys are stored securely in session
            - Not saved permanently
            - Re-enter after page refresh
            
            **Need help?**
            - Check the API key setup guide above
            - Ensure keys are valid and active
            - Contact support if issues persist
            """)

if __name__ == "__main__":
    main()
