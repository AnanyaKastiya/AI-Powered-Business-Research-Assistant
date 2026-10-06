# 🏢 AI-Powered Business Research Assistant

An intelligent, retrieval-augmented business analysis assistant that takes a company website and recent market articles, indexes them into a FAISS vector database, and generates an executive research report with company overviews, key developments, potential business challenges, and targeted capability recommendations—followed by an interactive follow-up Q&A chatbot.

---

## 📌 Technical Architecture

```text
               INPUT
                 │
       ┌─────────┴─────────┐
       │                   │
Company Website        News URLs
       │                   │
       └─────────┬─────────┘
                 ▼
          Document Loader
                 ▼
          Text Splitter
                 ▼
        Vector Embeddings
                 ▼
          FAISS Vector DB
                 │
       ┌─────────┴─────────┐
       │                   │
Structured Analysis    User Question
       │                   │
       ▼                   ▼
   Retriever           Retriever
       │                   │
       └─────────┬─────────┘
                 ▼
                LLM
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
Business Insight     Q&A Response
       │                   │
       ▼                   ▼
Streamlit Report      Source URLs
```

---

## 🚀 Key Features & Output

### 1. User Inputs
* **Company Name** (e.g., `Tata Motors`)
* **Company Website** (e.g., `https://www.tatamotors.com`)
* **1–3 News / Article URLs** (e.g., Moneycontrol, Reuters, Bloomberg, etc.)

### 2. Automatic Executive Analysis
Once you click **[ 🚀 Analyze Company ]**, the system processes the sources and generates:
* 🏢 **Company Overview**: 2–3 sentences summarizing the firm, core industries, and offerings.
* 📰 **Key Developments**: 3–5 bullet points highlighting major recent milestones, launches, or policies.
* ⚠️ **Potential Business Challenge**: One carefully framed potential challenge inferred from recent developments (using balanced language like *"The company's rapid expansion may create challenges in..."*).
* 💡 **Recommended Solution**: Selects **ONE** capability area from a curated set:
  1. *Customer Analytics*
  2. *Sales Analytics*
  3. *Supply Chain Analytics*
  4. *Process Automation*
  5. *Data Visualization*
  accompanied by 2–3 sentences explaining why it is relevant to the identified challenge.
* 📚 **Evidence / Sources**: Direct attribution and clickable URLs supporting the findings.

### 3. Interactive Follow-up Chatbot
At the bottom of the analysis, users can continue asking questions:
* *"Why did you identify this as a potential challenge?"*
* *"Which article supports the recommendation?"*
* *"What other developments did you find?"*

Answers are grounded strictly in the same FAISS vector database with cited sources.

---

## 🧠 Comparison with Codebasics Tutorial

| Dimension | Original Codebasics Project | AI-Powered Business Research Assistant |
|---|---|---|
| **Objective** | Generic news article Q&A tool (RockyBot) | Structured executive business research assistant |
| **Inputs** | 3 Article URLs | Company Name + Company Website + 1–3 News URLs |
| **Pipeline Core** | Streamlit + LangChain + Embeddings + FAISS + LLM | **Retained**: Same proven RAG foundation |
| **Post-Indexing Action** | Blank question box | **Automated Business Intelligence Analysis** |
| **Strategic Reasoning** | None | Infer business challenges & recommend targeted capability area |
| **Model Flexibility** | Hardcoded legacy OpenAI | **OpenAI, Groq (Llama 3), Google Gemini, and Grok (xAI)** |
| **Local / Free Support** | Requires paid OpenAI key | Free local embedding support (FastEmbed) + Free Groq tier |
| **Follow-up Chat** | Standalone Q&A | Integrated conversational exploration grounded in same index |

### Interview Talking Point
> *"I retained the standard RAG pipeline for retrieving information from company and news sources, but extended the application from simple question answering into a structured business research assistant that automatically converts the retrieved information into a company overview, key developments, a potential business challenge, and a relevant solution recommendation."*

---

## ⚙️ Installation & Setup

### 1. Clone or Open Project
```bash
cd AI-Powered_Business_Research_Agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your preferred key. You can also paste the key directly in the Streamlit web interface!

#### How to Obtain an API Key:
* **Option A: OpenAI (Recommended)**
  * Go to: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  * Sign in, create a new secret key (`sk-...`), and paste into `OPENAI_API_KEY`.
* **Option B: Groq (Free & Ultra Fast Meta Llama 3)**
  * Go to: [https://console.groq.com/keys](https://console.groq.com/keys)
  * Sign in (free with Google/GitHub), generate key (`gsk_...`), and paste into `GROQ_API_KEY`.
* **Option C: Google Gemini**
  * Go to: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
  * Sign in and create key, and paste into `GEMINI_API_KEY`.
* **Option D: xAI (Grok)**
  * Go to: [https://console.x.ai](https://console.x.ai)
  * Generate an API key (`xai-...`) and paste into `XAI_API_KEY`.

---

## 🖥️ Running the Application

Launch the Streamlit web dashboard:
```bash
python -m streamlit run main.py
```

### Quick Demo with Tata Motors:
1. Open the app in your browser (usually `http://localhost:8501`).
2. Company Name: `Tata Motors`
3. Company Website: `https://www.tatamotors.com`
4. Pre-filled URLs:
   - `https://www.moneycontrol.com/news/business/tata-motors-mahindra-gain-certificates-for-production-linked-payouts-11281691.html`
   - `https://www.moneycontrol.com/news/business/tata-motors-launches-punch-icng-price-starts-at-rs-7-1-lakh-11098751.html`
   - `https://www.moneycontrol.com/news/business/stocks/buy-tata-motors-target-of-rs-743-kr-choksey-11080811.html`
5. Select your AI provider in the sidebar, paste your API key (if not in `.env`), and click **`[ 🚀 Analyze Company ]`**.
6. Review the generated executive cards and test follow-up questions at the bottom!

---

## 📁 Project Structure

```text
AI-Powered_Business_Research_Agent/
├── main.py              # Main Streamlit application with ingestion, FAISS RAG, and UI
├── requirements.txt     # Python dependencies compatible with Python 3.10 - 3.13
├── .env.example         # Template for environment variables and API keys
├── .env                 # Local file storing your secret keys (git ignored)
└── README.md            # Comprehensive project documentation & architecture guide
```
