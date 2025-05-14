import os
from datetime import datetime
import markdown2
from weasyprint import HTML

class PDFExporter:
    def __init__(self, session_name, summary_text):
        self.session_name = session_name
        self.summary_text = summary_text
        self.output_dir = os.path.join("pdf_exports")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self):
        # Convert markdown to HTML
        html_content = markdown2.markdown(self.summary_text, extras=["fenced-code-blocks"])

        # Wrap in full HTML document with minimal styling
        full_html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        margin: 2em;
                        line-height: 1.6;
                        color: #222;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 4px;
                        overflow-x: auto;
                        font-family: monospace;
                        font-size: 13px;
                        white-space: pre-wrap;
                    }}
                    code {{
                        font-family: monospace;
                        color: #c7254e;
                        background-color: #f9f2f4;
                        padding: 2px 4px;
                        border-radius: 4px;
                    }}
                    h1, h2, h3 {{
                        margin-top: 1.5em;
                    }}
                </style>
            </head>
            <body>
                <h1>Session Report: {self.session_name}</h1>
                <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
                {html_content}
            </body>
        </html>
        """

        # Export to PDF
        file_path = os.path.join(self.output_dir, f"{self.session_name}.pdf")
        HTML(string=full_html).write_pdf(file_path)

        return file_path
