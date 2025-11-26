import streamlit as st
from deepresearch.crew import Deepresearch
from datetime import datetime
import sys
import os
import re

# Ensure the src directory is in the python path so imports work correctly
# when running from the root directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Deep Research Agent", layout="wide")

st.title("🕵️‍♂️ Deep Research Agent")
st.markdown("Generate comprehensive research reports using AI agents.")

with st.sidebar:
    st.header("Configuration")
    topic = st.text_input("Enter the topic to research:", "AI LLMs")
    st.info("This tool uses CrewAI to research and report on the specified topic.")


class StreamlitOutputStream:
    def __init__(self, container):
        self.container = container
        self.buffer = ""
        self.ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def write(self, data):
        # Filter out ANSI codes
        clean_data = self.ansi_escape.sub("", data)
        self.buffer += clean_data
        self.container.code(self.buffer, language="text")

    def flush(self):
        pass


if st.button("Run Research", type="primary"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        # Create tabs for better organization
        tab1, tab2 = st.tabs(["📊 Report", "⚙️ Execution Log"])

        with tab2:
            st.write("Initializing agents...")
            log_container = st.empty()

        # Capture stdout
        original_stdout = sys.stdout
        sys.stdout = StreamlitOutputStream(log_container)

        result = None
        try:
            with st.spinner(
                f"Running research on '{topic}'... This may take a few minutes."
            ):
                inputs = {"topic": topic, "current_year": str(datetime.now().year)}

                # Initialize the crew
                deep_research_crew = Deepresearch()
                crew = deep_research_crew.crew()

                # Run the crew
                result = crew.kickoff(inputs=inputs)

        except Exception as e:
            # Restore stdout before printing error
            sys.stdout = original_stdout
            st.error(f"An error occurred: {e}")

        finally:
            # Restore stdout
            sys.stdout = original_stdout

        if result:
            with tab1:
                st.success("Research completed successfully!")
                st.markdown(result)

                # Check if report.md exists and offer it for download
                # We check the current working directory for the report
                if os.path.exists("report.md"):
                    with open("report.md", "r") as f:
                        report_content = f.read()
                        st.download_button(
                            label="Download Report",
                            data=report_content,
                            file_name="report.md",
                            mime="text/markdown",
                        )
