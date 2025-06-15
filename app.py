import streamlit as st
import zipfile
import io
import json

st.title("Google Takeout Data Analyzer")

st.write("""
Upload your Google Takeout .zip file. This tool will extract and analyze your YouTube Watch History, YouTube Search History, Google Search History, and Location History.
""")

uploaded_file = st.file_uploader("Upload your Google Takeout .zip file", type=["zip"])

relevant_files = {
    'YouTube Watch History': [],
    'YouTube Search History': [],
    'Google Search History': [],
    'Location History': []
}

if uploaded_file:
    with zipfile.ZipFile(uploaded_file) as z:
        file_list = z.namelist()
        # Find relevant files
        for fname in file_list:
            lower = fname.lower()
            if 'youtube' in lower and 'watch' in lower and fname.endswith('.json'):
                relevant_files['YouTube Watch History'].append(fname)
            elif 'youtube' in lower and 'search' in lower and fname.endswith('.json'):
                relevant_files['YouTube Search History'].append(fname)
            elif 'search' in lower and 'my activity' in lower and fname.endswith('.json'):
                relevant_files['Google Search History'].append(fname)
            elif 'location' in lower and fname.endswith('.json'):
                relevant_files['Location History'].append(fname)
        st.subheader("Relevant JSON files found:")
        for key, files in relevant_files.items():
            st.write(f"**{key}:**")
            if files:
                for f in files:
                    st.write(f"- {f}")
            else:
                st.write("- Not found")
