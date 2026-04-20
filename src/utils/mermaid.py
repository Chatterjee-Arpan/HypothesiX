import html


def ensure_mermaid_flowchart(raw_text: str) -> str:
    text = (raw_text or "").strip()
    if not text:
        return "flowchart TD\n    idea[No flowchart generated]\n"
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("mermaid", "", 1).strip()
    if not text.lower().startswith(("flowchart", "graph")):
        text = f"flowchart TD\n{text}"
    return text


def mermaid_html(mermaid_text: str) -> str:
    safe = html.escape(mermaid_text)
    return f"""
    <html>
      <head>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose',
            flowchart: {{ curve: 'basis', useMaxWidth: true, htmlLabels: true }}
          }});
        </script>
        <style>
          body {{
            margin: 0;
            padding: 0;
            background: transparent;
            color: #f8fafc;
            font-family: Arial, sans-serif;
          }}
          .mermaid-wrap {{
            min-height: 500px;
            border-radius: 22px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.12);
            padding: 1rem;
          }}
          .mermaid {{
            font-size: 16px;
          }}
        </style>
      </head>
      <body>
        <div class="mermaid-wrap">
          <pre class="mermaid">{safe}</pre>
        </div>
      </body>
    </html>
    """
