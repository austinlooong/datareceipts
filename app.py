import streamlit as st
import zipfile
import io
import json
import pandas as pd
from collections import Counter
from datetime import datetime

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

watch_history = []
search_history = []
google_search_history = []
location_pings = []
semantic_visits = 0

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

        # --- Parse YouTube Watch History ---
        if relevant_files['YouTube Watch History']:
            for fname in relevant_files['YouTube Watch History']:
                with z.open(fname) as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            watch_history.extend(data)
                    except Exception as e:
                        st.warning(f"Could not parse {fname}: {e}")

        # --- Parse YouTube Search History ---
        if relevant_files['YouTube Search History']:
            for fname in relevant_files['YouTube Search History']:
                with z.open(fname) as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            search_history.extend(data)
                    except Exception as e:
                        st.warning(f"Could not parse {fname}: {e}")

        # --- Parse Google Search History ---
        if relevant_files['Google Search History']:
            for fname in relevant_files['Google Search History']:
                with z.open(fname) as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            google_search_history.extend(data)
                    except Exception as e:
                        st.warning(f"Could not parse {fname}: {e}")

        # --- Parse Location History Records.json ---
        for fname in relevant_files['Location History']:
            if 'records.json' in fname.lower():
                with z.open(fname) as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            location_pings.extend(data)
                        elif isinstance(data, dict) and 'locations' in data:
                            location_pings.extend(data['locations'])
                    except Exception as e:
                        st.warning(f"Could not parse {fname}: {e}")

        # --- Parse Semantic Location History ---
        for fname in relevant_files['Location History']:
            if 'semantic location history' in fname.lower() and fname.lower().endswith('.json'):
                with z.open(fname) as f:
                    try:
                        data = json.load(f)
                        # Each file is a dict with 'timelineObjects' key
                        if isinstance(data, dict) and 'timelineObjects' in data:
                            for obj in data['timelineObjects']:
                                if 'placeVisit' in obj:
                                    semantic_visits += 1
                    except Exception as e:
                        st.warning(f"Could not parse {fname}: {e}")

        # --- Analyze Watch History ---
        if watch_history:
            st.header("YouTube Watch History Analysis")
            total_watched = len(watch_history)
            st.write(f"**Total videos watched:** {total_watched}")
            # Most active hour
            hours = []
            for entry in watch_history:
                t = entry.get("time")
                if t:
                    try:
                        dt = datetime.fromisoformat(t.replace('Z', '+00:00'))
                        hours.append(dt.hour)
                    except Exception:
                        pass
            if hours:
                most_common_hour = Counter(hours).most_common(1)[0][0]
                st.write(f"**Most active YouTube hour:** {most_common_hour}:00")
            else:
                st.write("Could not determine most active hour.")
            # Estimated value
            value_watch = total_watched * 0.08
            st.write(f"**Estimated value generated (watch history):** ${value_watch:.2f}")
        else:
            st.info("No YouTube Watch History found or could not be parsed.")

        # --- Analyze Search History ---
        if search_history:
            st.header("YouTube Search History Analysis")
            total_searches = len(search_history)
            st.write(f"**Total YouTube searches:** {total_searches}")
            queries = [entry.get("query") for entry in search_history if entry.get("query")]
            unique_queries = set(queries)
            st.write(f"**Number of unique searches:** {len(unique_queries)}")
            value_search = total_searches * 0.03
            st.write(f"**Estimated value generated (search history):** ${value_search:.2f}")
        else:
            st.info("No YouTube Search History found or could not be parsed.")

        # --- Analyze Google Search History ---
        if google_search_history:
            st.header("Google Search History Analysis")
            # Extract queries from entries where title starts with 'Searched for'
            queries = []
            for entry in google_search_history:
                title = entry.get("title", "")
                if title.startswith("Searched for"):
                    # Extract the query after 'Searched for '
                    query = title.replace("Searched for ", "", 1)
                    queries.append(query)
            total_searches = len(queries)
            st.write(f"**Total Google searches:** {total_searches}")
            unique_queries = set(queries)
            st.write(f"**Number of unique Google searches:** {len(unique_queries)}")
            value_search = total_searches * 0.03
            st.write(f"**Estimated value generated (Google search history):** ${value_search:.2f}")
        else:
            st.info("No Google Search History found or could not be parsed.")

        # --- Analyze Location Data ---
        if location_pings or semantic_visits:
            st.header("Location History Analysis")
            st.write(f"**Total location pings (Records.json):** {len(location_pings)}")
            st.write(f"**Total place visits (Semantic Location History):** {semantic_visits}")
            value_location = len(location_pings) * 0.01 + semantic_visits * 0.01
            st.write(f"**Estimated value generated (location history):** ${value_location:.2f}")
        else:
            st.info("No Location History found or could not be parsed.")
