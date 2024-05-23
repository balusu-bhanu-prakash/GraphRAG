import streamlit as st
from neo4j import GraphDatabase
from langchain_google_genai import ChatGoogleGenerativeAI


# Function for the authentication page
def authentication_page():
    st.title("Authentication")

    # Get user inputs for authentication
    graph_db_url = st.text_input("Your graph database URL")
    password = st.text_input("Enter your password", type="password")
    google_api_key = st.text_input("Enter your Gemini API key", type="password")

    if st.button("Submit"):
        if graph_db_url and password and google_api_key:
            # Save the inputs in the session state
            st.session_state.graph_db_url = graph_db_url
            st.session_state.password = password
            st.session_state.google_api_key = google_api_key
            # Navigate to the prompt page
            st.session_state.page = "prompt_page"
        else:
            st.error("Please fill in all the fields")

    if "graph_db_url" in st.session_state and "password" in st.session_state:
        try:
            with GraphDatabase.driver(
                st.session_state.graph_db_url, auth=("neo4j", st.session_state.password)
            ) as driver:
                driver.verify_connectivity()
                st.session_state.driver = driver
        except Exception as e:
            st.error(f"Error connecting to the database: {e}")


# Function for the prompt page
def prompt_page():
    st.title("Enter Your Prompt")

    # Display user inputs for verification (optional)
    st.write(f"Graph DB URL: {st.session_state.graph_db_url}")
    # st.write(f"Google API Key: {st.session_state.google_api_key}")

    # Get user prompt or query
    prompt = st.text_input("Enter your prompt")

    if st.button("Submit"):
        if prompt:
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro", google_api_key=st.session_state.google_api_key
            )
            query = prompt
            result = llm.invoke("Write a cypher query where I need you to " + query)
            # Cleaning to output for a CYPHER query
            cypher_query = result.content.split("```cypher")[1].split("```")[0].strip()
            print(cypher_query)

            try:
                with st.session_state.driver.session() as session:
                    results = session.run(cypher_query)
                    st.code(cypher_query, language="cypher")
            except Exception as e:
                st.error(f"Error executing the query: {e}")
        else:
            st.error("Please enter a prompt or query")


# Main function to control page navigation
def main():
    if "page" not in st.session_state:
        st.session_state.page = "authentication_page"

    if st.session_state.page == "authentication_page":
        authentication_page()
    elif st.session_state.page == "prompt_page":
        prompt_page()


# Run the app
if __name__ == "__main__":
    main()
