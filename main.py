import os
import time
import requests
from bs4 import BeautifulSoup
import streamlit as st
from dotenv import load_dotenv

# LangChain Imports
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Load environment variables from .env
load_dotenv()

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="AI-Powered Business Research Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# Helper Functions: Robust Web Scraping & Text Loading
# ==============================================================================
def scrape_clean_url(url: str) -> Document:
    """
    Scrapes web page text cleanly, removing boilerplate, ads, navigation, and scripts.
    Includes custom headers to prevent 403 Forbidden errors common on news sites.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Strip script, style, navigation, footer, and interactive widgets
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        
        # Limit document length if unusually long
        if len(cleaned_text) > 40000:
            cleaned_text = cleaned_text[:40000]
            
        return Document(page_content=cleaned_text, metadata={"source": url})
    except Exception as e:
        return Document(page_content=f"Error loading {url}: {str(e)}", metadata={"source": url, "error": True})

def load_all_sources(company_website: str, news_urls: list[str]) -> list[Document]:
    """Loads and returns combined documents from company website and news articles."""
    all_urls = []
    if company_website.strip():
        all_urls.append(company_website.strip())
    for u in news_urls:
        if u.strip() and u.strip() not in all_urls:
            all_urls.append(u.strip())
            
    documents = []
    for url in all_urls:
        doc = scrape_clean_url(url)
        if not doc.metadata.get("error", False) and len(doc.page_content.strip()) > 50:
            documents.append(doc)
    return documents

# ==============================================================================
# Helper Functions: Automatic LLM & Embedding Setup from .env
# ==============================================================================
def get_llm_and_embeddings():
    """
    Automatically detects configured API keys from the .env file.
    Prefers Groq (free & ultra-fast) or OpenAI, Gemini.
    """
    # Check environment variable first, then fallback to Streamlit Cloud Secrets
    def fetch_secret(name):
        val = os.getenv(name, "").strip()
        if not val and hasattr(st, "secrets"):
            try:
                if name in st.secrets:
                    val = str(st.secrets[name]).strip()
            except Exception:
                pass
        return val

    groq_key = fetch_secret("GROQ_API_KEY")
    openai_key = fetch_secret("OPENAI_API_KEY")
    gemini_key = fetch_secret("GEMINI_API_KEY") or fetch_secret("GOOGLE_API_KEY")

    if groq_key:
        from langchain_groq import ChatGroq
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
        from groq import Groq

        # Auto-detect best active model on user's Groq account
        chosen_model = "openai/gpt-oss-120b"
        try:
            client = Groq(api_key=groq_key)
            available = [m.id for m in client.models.list().data]
            for candidate in [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "qwen/qwen3.8-27b",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant"
            ]:
                if candidate in available:
                    chosen_model = candidate
                    break
        except Exception:
            chosen_model = "openai/gpt-oss-120b"

        llm = ChatGroq(
            model_name=chosen_model,
            temperature=0.2,
            groq_api_key=groq_key
        )
        # FastEmbed is 100% free and runs locally
        embeddings = FastEmbedEmbeddings()
        return llm, embeddings, "Groq"

    elif openai_key:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=openai_key
        )
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai_key
        )
        return llm, embeddings, "OpenAI"

    elif gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=gemini_key
        )
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=gemini_key
        )
        return llm, embeddings, "Google Gemini"

    else:
        return None, None, None

# ==============================================================================
# Session State Initialization
# ==============================================================================
if "vectorstore" not in st.session_state:
    st.session_state["vectorstore"] = None
if "analysis_report" not in st.session_state:
    st.session_state["analysis_report"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""
if "sources_list" not in st.session_state:
    st.session_state["sources_list"] = []
if "prefilled_question" not in st.session_state:
    st.session_state["prefilled_question"] = ""

# ==============================================================================
# Sidebar: Target Company & News URLs (No API Key clutter)
# ==============================================================================
with st.sidebar:
    st.header("🏢 Target Company")
    company_name = st.text_input("Company Name", value="Tata Motors", placeholder="e.g. Tata Motors, Nvidia")
    company_website = st.text_input("Company Website", value="https://www.tatamotors.com", placeholder="https://...")
    
    st.markdown("---")
    st.header("📰 Recent News / Article URLs")
    st.caption("Provide 1 to 3 recent articles for context.")
    
    url1 = st.text_input(
        "Article URL 1",
        value="https://www.moneycontrol.com/news/business/tata-motors-mahindra-gain-certificates-for-production-linked-payouts-11281691.html"
    )
    url2 = st.text_input(
        "Article URL 2",
        value="https://www.moneycontrol.com/news/business/tata-motors-launches-punch-icng-price-starts-at-rs-7-1-lakh-11098751.html"
    )
    url3 = st.text_input(
        "Article URL 3",
        value="https://www.moneycontrol.com/news/business/stocks/buy-tata-motors-target-of-rs-743-kr-choksey-11080811.html"
    )
    
    st.markdown("---")
    analyze_btn = st.button("🚀 Analyze Company", type="primary", use_container_width=True)

# ==============================================================================
# Main Canvas: Header & Overview
# ==============================================================================
st.title("🏢 AI-Powered Business Research Assistant")
st.markdown(
    "Synthesizes company websites and market news into structured executive research: "
    "**Company Overview**, **Key Developments**, **Potential Business Challenges**, and **Targeted Solution Recommendations**."
)

# ==============================================================================
# Execution Flow: Processing & Analysis
# ==============================================================================
if analyze_btn:
    # 1. Check API Key configuration
    llm, embeddings, provider_name = get_llm_and_embeddings()
    if not llm:
        st.error("⚠️ No API key found in `.env`. Please make sure `GROQ_API_KEY` is saved in your `.env` file.")
        st.stop()
        
    if not company_name.strip():
        st.error("⚠️ Please specify the Company Name.")
        st.stop()
        
    news_urls = [u.strip() for u in [url1, url2, url3] if u.strip()]
    if not company_website.strip() and not news_urls:
        st.error("⚠️ Please provide at least the Company Website or one News URL.")
        st.stop()
        
    progress_box = st.container()
    with progress_box:
        status_text = st.empty()
        progress_bar = st.progress(5)
        
        # 1. Scrape URLs
        status_text.info(f"🔄 **Step 1/5:** Ingesting content from {company_name} website and {len(news_urls)} news sources...")
        raw_docs = load_all_sources(company_website, news_urls)
        
        if not raw_docs:
            st.error("❌ Could not extract readable content from the provided URLs. Please verify the links.")
            st.stop()
            
        progress_bar.progress(30)
        
        # 2. Text Splitting
        status_text.info(f"✂️ **Step 2/5:** Splitting documents into analytical chunks ({len(raw_docs)} documents loaded)...")
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=1000,
            chunk_overlap=150
        )
        split_docs = splitter.split_documents(raw_docs)
        progress_bar.progress(50)
        
        # 3. Vector Embeddings & FAISS Indexing
        status_text.info(f"🧠 **Step 3/5:** Indexing {len(split_docs)} chunks into FAISS vector database...")
        try:
            vectorstore = FAISS.from_documents(split_docs, embeddings)
            
            # Persist vectorstore locally
            index_path = "faiss_business_research_index"
            vectorstore.save_local(index_path)
            
            # Store in session state
            st.session_state["vectorstore"] = vectorstore
            st.session_state["company_name"] = company_name
            st.session_state["sources_list"] = [d.metadata.get("source") for d in raw_docs]
            st.session_state["chat_history"] = []
        except Exception as e:
            st.error(f"❌ Failed to build vector embeddings: {str(e)}")
            st.stop()
            
        progress_bar.progress(75)
        
        # 4. Retrieval for Business Analysis Prompt
        status_text.info("🔍 **Step 4/5:** Retrieving core strategic context for executive business analysis...")
        search_query = f"{company_name} corporate overview core products recent developments financial performance challenges strategy"
        retrieved_chunks = vectorstore.similarity_search(search_query, k=6)
        context_text = "\n\n---\n\n".join([c.page_content for c in retrieved_chunks])
        
        progress_bar.progress(85)
        
        # 5. LLM Structured Analysis
        status_text.info("💡 **Step 5/5:** Synthesizing structured business research report via LLM...")
        
        analysis_prompt = f"""
You are an executive business research analyst. You have been provided with retrieved context from {company_name}'s official website and recent news articles.

Context:
{context_text}

Task:
Produce a structured, rigorous, and objective business research report for {company_name} adhering strictly to the sections below.

Format your response in Markdown using EXACTLY these 5 sections and headings:

### 🏢 Company Overview
Provide 2–3 concise sentences describing what {company_name} does, its core industry, products/services, and market presence based strictly on the supplied sources.

### 📰 Key Developments
List 3–5 bullet points highlighting the most significant recent developments, product launches, government policy incentives, or financial updates found in the sources.

### ⚠️ Potential Business Challenge
Infer ONE potential business challenge arising from these developments.
CRITICAL CONSTRAINT: Use cautious, analytical framing such as:
"The company's rapid expansion may create challenges in..." or
"Recent transitions toward new vehicle technologies could create operational friction in..."
Do NOT pretend to know confidential or undisclosed internal problems.

### 💡 Recommended Solution
From the following 5 capability areas:
1. Customer Analytics
2. Sales Analytics
3. Supply Chain Analytics
4. Process Automation
5. Data Visualization

Select EXACTLY ONE capability area that is most relevant to addressing or mitigating the identified challenge.
State the chosen area clearly, followed by 2–3 sentences explaining why it is relevant and how it helps {company_name}.

### 📚 Evidence / Sources
List the source URLs or reference points that substantiate this analysis.
"""
        try:
            response = llm.invoke(analysis_prompt)
            st.session_state["analysis_report"] = response.content
        except Exception as e:
            st.error(f"❌ LLM Analysis generation failed: {str(e)}")
            st.stop()
            
        progress_bar.progress(100)
        status_text.success("✅ Business research analysis successfully completed!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()

# ==============================================================================
# Display Section: Structured Research Report (Adaptive to Dark & Light Modes)
# ==============================================================================
if st.session_state["analysis_report"]:
    st.markdown(f"## 📋 Executive Research Report: {st.session_state.get('company_name', 'Target Company')}")
    
    report_content = st.session_state["analysis_report"]
    
    # Parse and render formatted report cards using native theme-adaptive containers
    sections = report_content.split("### ")
    
    for section in sections:
        if not section.strip():
            continue
        header, *body = section.split("\n", 1)
        header = header.strip()
        body_text = body[0].strip() if body else ""
        
        if "Company Overview" in header:
            with st.container(border=True):
                st.subheader("🏢 Company Overview")
                st.markdown(body_text)
            
        elif "Key Developments" in header:
            with st.container(border=True):
                st.subheader("📰 Key Developments")
                st.markdown(body_text)
            
        elif "Potential Business Challenge" in header:
            with st.container(border=True):
                st.subheader("⚠️ Potential Business Challenge")
                st.markdown(body_text)
            
        elif "Recommended Solution" in header:
            with st.container(border=True):
                st.subheader("💡 Recommended Solution")
                st.markdown(body_text)
            
        elif "Evidence" in header or "Sources" in header:
            with st.container(border=True):
                st.subheader("📚 Evidence / Sources")
                st.markdown(body_text)
                if st.session_state.get("sources_list"):
                    st.markdown("**Indexed Source URLs:**")
                    for src in set(st.session_state["sources_list"]):
                        st.markdown(f"- [{src}]({src})")
        else:
            with st.container(border=True):
                st.subheader(header)
                st.markdown(body_text)

    st.markdown("---")

    # ==============================================================================
    # Chatbot Section: "Ask AI about this company"
    # ==============================================================================
    st.subheader("💬 Ask AI about this company")
    st.caption("Ask follow-up questions powered by the same FAISS vector index and retrieval pipeline.")
    
    # Quick question suggestions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❓ Why did you identify this challenge?", use_container_width=True):
            st.session_state["prefilled_question"] = "Why did you identify this as a potential business challenge, and what evidence supports it?"
    with col2:
        if st.button("❓ Which article supports the solution?", use_container_width=True):
            st.session_state["prefilled_question"] = "Which specific article or source supports the recommended solution area?"
    with col3:
        if st.button("❓ What other developments did you find?", use_container_width=True):
            st.session_state["prefilled_question"] = "What other notable business developments or details did you find in the sources?"

    # User question input
    user_query = st.text_input(
        "Your Question:",
        value=st.session_state.get("prefilled_question", ""),
        placeholder="e.g. How does government policy affect their current strategy?",
        key="qa_input"
    )
    
    ask_button = st.button("Submit Question", type="primary")
    
    if ask_button and user_query.strip():
        llm, _, _ = get_llm_and_embeddings()
        if not llm:
            st.error("No API key found in `.env`.")
        elif st.session_state["vectorstore"] is None:
            st.warning("Please analyze a company first to build the knowledge base.")
        else:
            with st.spinner("Retrieving relevant evidence and synthesizing answer..."):
                try:
                    retriever = st.session_state["vectorstore"].as_retriever(search_kwargs={"k": 4})
                    relevant_chunks = retriever.invoke(user_query)
                    
                    context_block = "\n\n".join([f"Source: {c.metadata.get('source')}\nContent: {c.page_content}" for c in relevant_chunks])
                    
                    qa_prompt = f"""
You are an executive business research assistant answering questions about {st.session_state.get('company_name', 'the company')}.
Answer the question based STRICTLY on the retrieved context below. 
If the answer cannot be determined from the context, state that clearly rather than hallucinating.
Always cite the specific source URL(s) that provided the information.

Context:
{context_block}

Question:
{user_query}

Provide a clear, detailed answer followed by a 'Sources Used' section listing the URLs.
"""
                    answer = llm.invoke(qa_prompt).content
                    
                    # Save to chat history
                    st.session_state["chat_history"].append({
                        "question": user_query,
                        "answer": answer,
                        "sources": list(set([c.metadata.get("source") for c in relevant_chunks if c.metadata.get("source")]))
                    })
                    
                    # Clear prefilled state
                    st.session_state["prefilled_question"] = ""
                    
                except Exception as e:
                    st.error(f"Error answering question: {str(e)}")

    # Display Chat History
    if st.session_state["chat_history"]:
        st.markdown("#### Conversation History")
        for idx, chat in enumerate(reversed(st.session_state["chat_history"])):
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.markdown(chat["answer"])
                if chat["sources"]:
                    st.caption(f"Sources cited: {', '.join(chat['sources'])}")
            st.markdown("---")

else:
    # Helpful starting guide when app first opens
    st.info("👈 Enter the company details and recent article URLs in the sidebar, then click **'🚀 Analyze Company'** to generate your executive report.")
    
    st.markdown("""
    #### How It Works:
    1. **Data Ingestion**: Scrapes the official company website and 1–3 recent market news articles.
    2. **Text Chunking**: Partitions long-form unstructured web text into clean semantic segments.
    3. **Vector Embeddings & FAISS**: Builds an in-memory vector database indexed for high-precision similarity search.
    4. **Automated Business Report**:
       - 🏢 **Company Overview** (Industry, products, market footprint)
       - 📰 **Key Developments** (Milestones, product launches, subsidies)
       - ⚠️ **Potential Business Challenge** (Inferred cautiously without speculation)
       - 💡 **Recommended Solution** (Customer Analytics, Sales Analytics, Supply Chain Analytics, Process Automation, or Data Visualization)
       - 📚 **Evidence / Sources** (Direct URL attribution)
    5. **Interactive Q&A**: Continue inquiring about the company with the RAG-powered chatbot.
    """)
