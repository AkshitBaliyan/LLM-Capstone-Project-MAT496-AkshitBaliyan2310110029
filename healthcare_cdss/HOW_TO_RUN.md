# How to Run Healthcare CDSS

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
cd healthcare_cdss
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Set Up API Keys
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
```

Edit `.env` and add your API keys:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
LANGSMITH_API_KEY=lsv2_pt_your-key-here
```

Get API keys from:
- Anthropic: https://console.anthropic.com/
- LangSmith: https://smith.langchain.com/

### 3. Run the Application

**Option A: Web UI (Recommended)**
```bash
streamlit run app.py
```
Open browser to `http://localhost:8501`

**Option B: Command Line Demo**
```bash
python demo.py
```

**Option C: Single Test Case**
```bash
python main.py
```

---

## 📱 Using the Streamlit Web UI

### Starting the UI
```bash
cd healthcare_cdss
streamlit run app.py
```

The web interface will open at `http://localhost:8501`

### Features

**1. Demo Cases** (Quickest way to test)
- Select "Use Demo Case" in sidebar
- Choose from 4 pre-loaded scenarios:
  - URI (Routine) - Common cold/flu
  - Cardiac Emergency - Chest pain emergency
  - Pediatric - Child with sore throat
  - Geriatric - Elderly with dizziness
- Click "Run Clinical Analysis"
- View results in ~30 seconds

**2. Manual Input** (Custom cases)
- Select "Manual Input" in sidebar
- Fill in patient demographics
- Add chief complaint
- Enter symptoms (1-10)
- Add vital signs
- Click "Run Clinical Analysis"

### What You'll See

The UI displays:
- ✅ Differential diagnosis (top 5 conditions)
- ✅ Probability scores for each diagnosis
- ✅ Clinical reasoning
- ✅ Recommended diagnostic tests
- ✅ Safety alerts and red flags
- ✅ Evidence sources from medical literature
- ✅ Human review requirements

---

## 💻 Command Line Options

### Run Demo Script (All 4 Cases)
```bash
python demo.py
```

Shows comprehensive analysis of all demo cases:
- Upper Respiratory Infection
- Cardiac Emergency
- Pediatric case
- Geriatric case

### Run Single Case
```bash
python main.py
```

Analyzes a single URI (fever/cough) case

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 🔧 Troubleshooting

### "Module not found" Error
```
ImportError: No module named 'langgraph'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### "API Key not found" Error
```
Error: ANTHROPIC_API_KEY not found
```
**Solution:**
1. Create `.env` file in `healthcare_cdss/` directory
2. Add: `ANTHROPIC_API_KEY=your-key-here`
3. Restart the application

### Streamlit Won't Start
```bash
# Reinstall streamlit
pip install --upgrade streamlit

# Check if port 8501 is in use
streamlit run app.py --server.port 8502
```

### LangSmith Not Tracing
Check `.env` file has:
```
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your-key-here
LANGCHAIN_PROJECT=healthcare-cdss
```

---

## 📊 Understanding the Output

### Differential Diagnosis Example
```
1. Upper Respiratory Tract Infection (85% probability)
   Reasoning: Classic symptoms of fever, cough, and fatigue...
   Recommended Tests: Chest X-ray, CBC with differential
```

### Safety Alerts
```
🚨 CARDIAC EMERGENCY: crushing chest pain radiating to left arm
⚠️  PEDIATRIC PATIENT (Age: 8) - Age-appropriate dosing required
```

### Human Review Flags
```
⚕️ HUMAN REVIEW REQUIRED
Reasons:
- Emergency condition detected
- Cardiac symptoms requiring immediate evaluation
```

---

## 🎥 For Video Demonstration

### Option 1: Web UI Demo (Recommended for Video)
```bash
streamlit run app.py
```

1. Show the clean web interface
2. Select a demo case (Cardiac Emergency is impressive)
3. Click "Run Clinical Analysis"
4. Show results appearing in real-time
5. Expand different sections to show detail

### Option 2: Command Line Demo
```bash
python demo.py
```

Shows all 4 cases with detailed output

---

## 🌐 Running on Different Machines

### Clone from GitHub
```bash
git clone https://github.com/AkshitBaliyan/LLM-Capstone-Project-MAT496-AkshitBaliyan2310110029.git
cd LLM-Capstone-Project-MAT496-AkshitBaliyan2310110029/healthcare_cdss
```

### Follow 3-Step Quick Start
See top of this document

---

## 🔐 Security Notes

- **Never commit** `.env` file (it's in `.gitignore`)
- API keys are **private** - don't share
- `.env.example` shows format but has no real keys

---

## ⚡ Performance Tips

- First run takes longer (LLM warmup)
- Subsequent runs are faster
- Literature search adds 5-10 seconds
- Complex cases take longer than simple ones

---

## 📈 Monitoring in LangSmith

After running analysis:

1. Go to https://smith.langchain.com/
2. Navigate to project: `healthcare-cdss`
3. See all workflow traces with:
   - Node execution times
   - LLM prompts and responses
   - Tool calls
   - Complete state evolution

---

## 🎯 Quick Validation Checklist

To verify everything works:

- [ ] `pip install -r requirements.txt` completes
- [ ] `.env` file created with API keys
- [ ] `streamlit run app.py` starts without errors
- [ ] Can run demo case and see results
- [ ] `python demo.py` runs successfully
- [ ] `pytest tests/` all pass

---

**Need Help?** Check:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed installation
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Code usage examples
- [TESTING.md](TESTING.md) - Running tests
- [README.md](README.md) - Project overview

---

**🎉 You're ready to run the Healthcare CDSS!**

Start with: `streamlit run app.py` for the best experience.
