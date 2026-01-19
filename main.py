import streamlit as st
import os
import json
from firecrawl import FirecrawlApp
import openai
from dotenv import load_dotenv

load_dotenv()

# streamlit configuration

st.set_page_config(
    page_title= "AI Scraper", #btw title changed here at 2:31pm 19/1/2026
    page_icon= "🤖",
    layout= "wide"
)

#API key setup

try:
    firecrawl_api_key = os.environ["FIRECRAWL_API_KEY"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    st.error("API Keys not found! Please create a .env file and set them keys")
    st.stop()


##Core app functionality

def scrape_content(url):
    """ Uses Firecrawl to scrape the main content from a URL"""
    if not url:
        return None
    try:
        app = FirecrawlApp(api_key=firecrawl_api_key)
        #use .scrape() to specify mkdown format
        scraped_data = app.scrape(url, formats=["markdown"])
        #access the mkdown with dot notation
        return scraped_data.markdown
    except Exception as e:
        st.error(f" failed to scrape the url {e} ")
        return None
    
    

def analyze_content_with_llm(content):
    """uses the LLM to summarize, categorize, and analyze sentiment """
    if not content:
        return None
    try:
        system_prompt = """
        you are an expert content analyst. Analyze the provided text and return a JSON object with three keys:
        1. 'summary' : Give a concise summary, don't make it too short and not too long, like make it give all the things you got to know as a summarized whole.
        2. 'category' : The most relevant category (e.g., 'Technology', 'Finance', 'Neutral')
        3. 'sentiment' : The overall sentiment ('Positive', 'Negative', 'Neutral)

        """
        response = openai.chat.completions.create(

            model="gpt-4o",
            response_format={"type" : "json_object"},
            messages= [
                {"role" : "system", "content" : system_prompt},
                {"role" : "user", "content" : content}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f" failed to analyze content with the llm {e}")
        return None
    

# streamlit UI

st.title(" On Demand website analyzer")
st.markdown(" enter a url to scrape ")

url_input = st.text_input(" enter the url to analyze", placeholder="https://example.com/article")


if st.button(" Analyze URL", type="primary"):
    if url_input:
        with st.spinner("scraping the website with firecrawl..."):
            scraped_markdown = scrape_content(url_input)

        if scraped_markdown:
            st.success("scraping successful nice")
            with st.spinner("AI is analyzing the content..."):
                analysis_result = analyze_content_with_llm(scraped_markdown)

            if analysis_result:
                st.success("Analysis Complete cuh!")
                st.subheader("Analysis Results")

                col1, col2 = st.columns(2)
                col1.info(f"**Category** {analysis_result.get('category', 'N/A')}")
                col2.info(f"**Sentiment** {analysis_result.get('sentiment', 'N/A')}")

                st.subheader("Summary ")
                st.write(analysis_result.get('summary', 'could not get summary'))

                with st.expander("View raw scraped markdown"):
                    st.markdown(scraped_markdown)

    else:
        st.warning(" please enter a url to analzye")
