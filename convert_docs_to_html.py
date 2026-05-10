#!/usr/bin/env python3
"""
Convert markdown documentation to modularized HTML structure.
Generates docs-html/ with index.html and organized subdirectories.
"""

import os
import re
from pathlib import Path
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension


def get_html_template(title, content, breadcrumb=""):
    """Generate HTML template with Bootstrap 5 styling."""
    breadcrumb_html = f"""
    <nav aria-label="breadcrumb" class="mt-3">
        <ol class="breadcrumb">
            {breadcrumb}
        </ol>
    </nav>
    """ if breadcrumb else ""
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Cell Classification Pipeline</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
        }}
        
        body {{
            background-color: #f8f9fa;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        main {{
            flex: 1;
        }}
        
        .navbar-brand {{
            font-size: 1.5rem;
            font-weight: bold;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        
        header .breadcrumb {{
            background: transparent;
            padding: 1rem 0 0 0;
        }}
        
        header .breadcrumb-item {{
            color: rgba(255, 255, 255, 0.8);
        }}
        
        header .breadcrumb-item.active {{
            color: white;
        }}
        
        header .breadcrumb-item a {{
            color: white;
        }}
        
        header .breadcrumb-item a:hover {{
            text-decoration: underline;
        }}
        
        .content {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin: 2rem 0;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary-color);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }}
        
        h1 {{
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }}
        
        h2 {{
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.3rem;
        }}
        
        table {{
            margin: 1.5rem 0;
        }}
        
        table thead {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        table tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        code {{
            color: #d63384;
            background-color: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        pre code {{
            color: #333;
            padding: 0;
            background: none;
        }}
        
        blockquote {{
            border-left: 4px solid var(--primary-color);
            padding-left: 1.5rem;
            margin: 1.5rem 0;
            color: #666;
            font-style: italic;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            margin: 1.5rem 0;
            border-radius: 5px;
        }}
        
        a {{
            color: var(--primary-color);
        }}
        
        a:hover {{
            color: var(--secondary-color);
        }}
        
        footer {{
            background-color: white;
            border-top: 1px solid #e0e0e0;
            padding: 1.5rem 0;
            text-align: center;
            color: #666;
            margin-top: auto;
        }}
        
        .back-link {{
            margin-bottom: 1.5rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🔬 Cell Classification Pipeline</h1>
            <p>Data Mining University - Pre-processing Documentation</p>
            {breadcrumb_html}
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="back-link">
                <a href="index.html" class="btn btn-secondary btn-sm">
                    <i class="bi bi-arrow-left"></i> Back to Index
                </a>
            </div>
            <div class="content">
                {content}
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p class="mb-0">Generated from Markdown Documentation | Last Updated: May 2026</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def get_index_template(sections):
    """Generate index.html template with Bootstrap 5."""
    sections_html = ""
    for section_name, docs in sections.items():
        sections_html += f"""
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-gradient text-white">
                    <h5 class="card-title mb-0">{section_name}</h5>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
"""
        for doc in docs:
            sections_html += f'                        <li class="mb-2"><i class="bi bi-arrow-right text-primary"></i> <a href="{doc["path"]}" class="text-decoration-none">{doc["title"]}</a></li>\n'
        sections_html += """
                    </ul>
                </div>
            </div>
        </div>
"""
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cell Classification Pipeline - Documentation Index</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
        }}
        
        body {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        main {{
            flex: 1;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 3rem 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 3rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            font-weight: bold;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.95;
        }}
        
        .intro {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 3rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .intro h2 {{
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}
        
        .stat-item {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 5px;
            text-align: center;
        }}
        
        .stat-item .number {{
            font-size: 1.8rem;
            font-weight: bold;
        }}
        
        .stat-item .label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .card {{
            transition: transform 0.3s, box-shadow 0.3s;
            border-top: 4px solid var(--primary-color);
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2) !important;
        }}
        
        .card-header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        }}
        
        .card-title {{
            font-size: 1.3rem;
            font-weight: 600;
        }}
        
        .card a {{
            color: var(--primary-color);
        }}
        
        .card a:hover {{
            color: var(--secondary-color);
            text-decoration: underline;
        }}
        
        footer {{
            background-color: white;
            border-top: 1px solid #e0e0e0;
            padding: 1.5rem 0;
            text-align: center;
            color: #666;
            margin-top: auto;
        }}
        
        .bg-gradient {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🔬 Cell Classification Pipeline</h1>
            <p>Data Mining University - Pre-processing Documentation</p>
        </div>
    </header>
    
    <main>
        <div class="container my-5">
            <div class="intro">
                <h2>📚 Welcome to the Documentation</h2>
                <p>This comprehensive guide covers the entire preprocessing pipeline for blood cell anomaly classification. 
                Navigate through the sections below to explore different aspects of numeric processing, categorical handling, 
                feature engineering, and model training.</p>
                
                <div class="row g-3 mt-2">
                    <div class="col-sm-6">
                        <div class="stat-item">
                            <div class="number">{sum(len(docs) for docs in sections.values())}</div>
                            <div class="label">Total Documents</div>
                        </div>
                    </div>
                    <div class="col-sm-6">
                        <div class="stat-item">
                            <div class="number">{len(sections)}</div>
                            <div class="label">Sections</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                {sections_html}
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p class="mb-0"><i class="bi bi-link-45deg"></i> Last Updated: May 2026 | Cell Classification Pipeline v1.0.0</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def convert_markdown_to_html(md_content):
    """Convert markdown to HTML with extensions."""
    md = markdown.Markdown(extensions=[
        TableExtension(),
        TocExtension(toc_depth=2),
        CodeHiliteExtension(),
        'extra',
        'nl2br'
    ])
    return md.convert(md_content)


def process_docs():
    """Process all markdown files in docs/ and convert to HTML."""
    docs_path = Path("/Users/phuchoang/Local_Document/data-mining-university/docs")
    output_path = Path("/Users/phuchoang/Local_Document/data-mining-university/docs-html")
    
    # Create output directory
    output_path.mkdir(exist_ok=True)
    
    # Track all documents for index
    all_sections = {}
    
    # Main documents in docs root
    main_docs = list(docs_path.glob("*.md"))
    all_sections["Main Documentation"] = []
    
    for md_file in sorted(main_docs):
        print(f"Converting {md_file.name}...")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = convert_markdown_to_html(md_content)
        title = md_file.stem.replace('-', ' ').title()
        
        # Generate breadcrumb
        breadcrumb = f'<a href="index.html">Home</a> <span>/</span> <span>{title}</span>'
        
        html = get_html_template(title, html_content, breadcrumb)
        
        output_file = output_path / f"{md_file.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        all_sections["Main Documentation"].append({
            "title": title,
            "path": f"{md_file.stem}.html"
        })
    
    # Process subdirectories
    subdirs = {
        "category": "Categorical Processing",
        "numeric": "Numeric Processing",
        "visualize": "Visualization & Analysis"
    }
    
    for subdir_name, section_label in subdirs.items():
        subdir_path = docs_path / subdir_name
        if not subdir_path.exists():
            continue
        
        # Create output subdirectory
        output_subdir = output_path / subdir_name
        output_subdir.mkdir(exist_ok=True)
        
        all_sections[section_label] = []
        
        # Process markdown files
        for md_file in sorted(subdir_path.glob("*.md")):
            print(f"Converting {subdir_name}/{md_file.name}...")
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = convert_markdown_to_html(md_content)
            title = md_file.stem.replace('-', ' ').title()
            
            # Generate breadcrumb
            breadcrumb = f'<a href="../index.html">Home</a> <span>/</span> <a href="../index.html">{section_label}</a> <span>/</span> <span>{title}</span>'
            
            html = get_html_template(title, html_content, breadcrumb)
            
            output_file = output_subdir / f"{md_file.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            all_sections[section_label].append({
                "title": title,
                "path": f"{subdir_name}/{md_file.stem}.html"
            })
        
        # Process notebook files (just reference them)
        for nb_file in sorted(subdir_path.glob("*.ipynb")):
            print(f"Referencing {subdir_name}/{nb_file.name}...")
            all_sections[section_label].append({
                "title": nb_file.stem.replace('_', ' ').title() + " (Notebook)",
                "path": f"../docs/{subdir_name}/{nb_file.name}"
            })
    
    # Generate index.html
    print("Generating index.html...")
    index_html = get_index_template(all_sections)
    with open(output_path / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"\n✅ Conversion complete!")
    print(f"📁 Output saved to: {output_path}")
    print(f"🌐 Open this file to view: {output_path / 'index.html'}")


if __name__ == "__main__":
    try:
        process_docs()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
