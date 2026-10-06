# 🏢 AI-Powered Business Research Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-powered-business-research-agent.streamlit.app/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=flat&logo=streamlit)](https://ai-powered-business-research-agent.streamlit.app/)

> 🚀 **Live Application:** [https://ai-powered-business-research-agent.streamlit.app/](https://ai-powered-business-research-agent.streamlit.app/)

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
          Document Loader  (Custom Scraper with Header Validation)
                 ▼
          Text Splitter   (Recursive Character Text Splitter)
                 ▼
        Vector Embeddings (FastEmbed Dense Vectors)
                 ▼
          FAISS Vector DB (In-Memory Similarity Index)
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
                LLM       (Groq / Llama High-Performance Inference)
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
* **Company Name** (e.g., `Tata Motors`, `Nvidia`, `Apple`)
* **Company Website** (e.g., `https://www.tatamotors.com`)
* **1–3 Recent News / Article URLs** (e.g., financial news, press releases, market coverage)

### 2. Automatic Executive Analysis
Once you click **`[ 🚀 Analyze Company ]`**, the system ingests the sources and produces:
* 🏢 **Company Overview**: 2–3 concise sentences summarizing the enterprise, primary industry, and core product lines.
* 📰 **Key Developments**: 3–5 bullet points detailing major product launches, regulatory updates, or financial milestones.
* ⚠️ **Potential Business Challenge**: An objective, carefully framed operational or market risk inferred from the developments (*e.g., "The company's rapid expansion may create challenges in..."*).
* 💡 **Recommended Solution**: Selects **ONE** capability area from a curated business suite:
  1. *Customer Analytics*
  2. *Sales Analytics*
  3. *Supply Chain Analytics*
  4. *Process Automation*
  5. *Data Visualization*
  accompanied by a 2–3 sentence justification explaining how it addresses the identified challenge.
* 📚 **Evidence / Sources**: Direct attribution and clickable URLs substantiating the analysis.

### 3. Interactive Follow-up Chatbot
At the bottom of the analysis, users can continue exploring the data:
* *"Why did you identify this as a potential challenge?"*
* *"Which article supports the recommendation?"*
* *"What other developments did you find?"*

Answers are retrieved in real-time from the same FAISS vector index with source citations.

---

## 📁 Repository Structure

```text
AI-Powered-Business-Research-Assistant/
├── notebooks/
│   └── 1_business_research_rag_pipeline.ipynb   # Interactive step-by-step pipeline walkthrough
├── main.py                                      # Streamlit interactive web application
├── requirements.txt                             # Python dependencies (Python 3.10 - 3.13)
├── .env.example                                 # Environment variable template
├── .gitignore                                   # Git ignore rules for keys, cache, and indices
└── README.md                                    # Project documentation & architecture overview
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AnanyaKastiya/AI-Powered-Business-Research-Assistant.git
cd AI-Powered-Business-Research-Assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your Environment
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Add your API key to `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```
*(Get a free Groq API key in seconds at [console.groq.com/keys](https://console.groq.com/keys))*

---

## 🖥️ Running the Application

### 🌐 Live Web Application
Try the deployed application in your browser:
👉 **[https://ai-powered-business-research-agent.streamlit.app/](https://ai-powered-business-research-agent.streamlit.app/)**

### 💻 Running Locally
```bash
python -m streamlit run main.py
```
Open your browser at `http://localhost:8501`.

### 2. Run the Interactive Jupyter Notebook
To experiment with each pipeline step individually:
```bash
jupyter notebook notebooks/1_business_research_rag_pipeline.ipynb
```

---

## 🧪 Demo Example: Tata Motors

1. Enter Company Name: `Tata Motors`
2. Enter Company Website: `https://www.tatamotors.com`
3. Provide recent article URLs:
   - `https://www.moneycontrol.com/news/business/tata-motors-mahindra-gain-certificates-for-production-linked-payouts-11281691.html`
   - `https://www.moneycontrol.com/news/business/tata-motors-launches-punch-icng-price-starts-at-rs-7-1-lakh-11098751.html`
   - `https://www.moneycontrol.com/news/business/stocks/buy-tata-motors-target-of-rs-743-kr-choksey-11080811.html`
4. Click **`[ 🚀 Analyze Company ]`** to generate the executive report.
5. Inquire about the company using the follow-up Q&A chatbox.
