# ThatsMyAI

A desktop personal assistant powered by GPT-4. This AI sidekick remembers your conversations, exports clean session summaries as PDFs, and runs entirely from your machine — no browser needed.

---

## Features

- Chat with a personalized GPT-4 assistant
- Remembers your past conversations (locally stored)
- Automatically names and saves each chat session
- Export summarized chat sessions to styled PDF reports
- Clean, simple PyQt6 interface
- Markdown support for code, lists, and formatting

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/EvanRPavone/ThatsMyAI.git
cd ThatsMyAI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the root folder:

```
OPENAI_API_KEY=your-key-here
```

---

## Usage

Run the app:

```bash
python3 -m app.launcher
```

- On first launch, you'll be guided through a setup wizard.
- Chat history is stored in `memory/`
- Exported PDFs are saved in `pdf_exports/`

---

## Project Structure

```
app/
  ├── UI/               # GUI files
  ├── config/           # Personality and user info
  ├── memory/           # Saved chat sessions
  ├── pdf_exports/      # Generated PDFs
  ├── logs/             # Error logs
  └── launcher.py       # Entry point
```

---

## Built With

- [OpenAI API](https://platform.openai.com/)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [WeasyPrint](https://weasyprint.org/) (for PDF rendering)
- [markdown2](https://github.com/trentm/python-markdown2)

---

## License

MIT License — use freely and modify to fit your needs.

---

## Author

[Evan Pavone](https://github.com/EvanRPavone)
