import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"], p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }
        
        /* App Background */
        .stApp {
            background-color: #f8fafc;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Modern Primary Button (Main Body) */
        .stMainBlockContainer .stButton button, [data-testid="stForm"] .stButton button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
            border: none !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3) !important;
            width: 100% !important;
        }
        .stMainBlockContainer .stButton button:hover, [data-testid="stForm"] .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 15px -3px rgba(16, 185, 129, 0.4) !important;
        }
        .stMainBlockContainer .stButton button p, [data-testid="stForm"] .stButton button p {
            color: white !important;
        }

        /* Sidebar Navigation Buttons */
        [data-testid="stSidebar"] .stButton button {
            background-color: transparent !important;
            color: #475569 !important;
            border: none !important;
            box-shadow: none !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            width: 100% !important;
            margin-bottom: 0.2rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #f1f5f9 !important;
            color: #10b981 !important;
            transform: none !important;
        }
        [data-testid="stSidebar"] .stButton button p {
            color: inherit !important;
            font-size: 1.05rem !important;
            margin: 0 !important;
        }
        
        /* Text Inputs and Selectboxes */
        .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
            border-radius: 8px !important;
            border: 1px solid #cbd5e1 !important;
            padding: 0.6rem 1rem !important;
            background-color: #ffffff !important;
            color: #1e293b !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #10b981 !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #334155;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }

        /* DataFrame styling */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }

        /* Success & Error Messages */
        .stSuccess {
            background-color: #ecfdf5 !important;
            color: #065f46 !important;
            border-left: 4px solid #10b981 !important;
            border-radius: 8px;
        }
        .stError {
            background-color: #fef2f2 !important;
            color: #991b1b !important;
            border-left: 4px solid #ef4444 !important;
            border-radius: 8px;
        }
        .stInfo {
            background-color: #eff6ff !important;
            color: #1e40af !important;
            border-left: 4px solid #3b82f6 !important;
            border-radius: 8px;
        }

        /* File Uploader styling */
        [data-testid="stFileUploader"] {
            background-color: white !important;
            border: 2px dashed #cbd5e1 !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            transition: all 0.3s ease !important;
            color: #1e293b !important;
        }
        [data-testid="stFileUploader"] * {
            color: #1e293b !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #10b981 !important;
            background-color: #f0fdf4 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def card(title, content, icon=None):
    icon_html = f'<div style="font-size: 2.5rem; margin-bottom: 10px;">{icon}</div>' if icon else ''
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; height: 100%;">
            {icon_html}
            <h3 style="margin-top:0; color: #1e293b; font-size: 1.2rem;">{title}</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">{content}</p>
        </div>
    """, unsafe_allow_html=True)
