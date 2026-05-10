# 📚 Cell Classification Pipeline - HTML Documentation

This directory contains the modularized HTML version of the Data Mining University preprocessing pipeline documentation.

## 📁 Structure

```
docs-html/
├── index.html                           # Main entry point (open this file)
├── categorical-processing.html          # Categorical features guide
├── numeric-processing.html              # Numeric features guide
├── model_training.html                  # Model training documentation
├── modular_programming_guide.html       # Programming best practices
│
├── category/                            # Categorical processing details
│   ├── detail_Categorical&Numberical.html
│   └── detail_CrossFeatureInteration.html
│
├── numeric/                             # Numeric processing details
│   ├── advanced-numeric-processing.html
│   ├── detail_1.html
│   ├── detail_2.html
│   ├── detail_3.html
│   ├── detail_5.html
│   └── NhomA.png, NhomB.png, NhomC.png, NhomD.png  # Reference images
│
└── visualize/                           # Jupyter notebooks for visualization
    ├── KTDL_DoAn_TienXuLy_01.ipynb
    └── visualizeByGroup.ipynb
```

## 🚀 Getting Started

### Option 1: Open in Browser (Recommended)
```bash
# On macOS
open docs-html/index.html

# On Linux
xdg-open docs-html/index.html

# On Windows
start docs-html\index.html
```

### Option 2: Using Python HTTP Server
```bash
cd docs-html
python3 -m http.server 8000
# Then open http://localhost:8000 in your browser
```

### Option 3: Using Node.js HTTP Server
```bash
cd docs-html
npx http-server
# Then open http://localhost:8080 in your browser
```

## 📖 Navigation

- **Home Page (index.html)**: Displays all available sections with quick links
- **Breadcrumb Navigation**: Each page shows your current location
- **Back to Index**: Every page has a link to return to the main index
- **Section Cards**: Organize documents by topic

## 📑 Content Organization

### Main Documentation
- **Categorical Processing**: Guide for encoding categorical variables
- **Numeric Processing**: Handling numeric features and outliers
- **Model Training**: Training and evaluating 6 classification models
- **Modular Programming**: Best practices for team collaboration

### Detailed Sections

#### Categorical Processing Details (`category/`)
- Cross-feature interactions
- Group-wise statistics
- Encoding strategies

#### Numeric Processing Details (`numeric/`)
- Advanced processing techniques
- Feature group analysis (Groups A, B, C, D)
- Distribution analysis with visualizations

#### Visualization (`visualize/`)
- Interactive Jupyter notebooks
- Data exploration and analysis
- Distribution plots by group

## 🎨 Features

✅ **Responsive Design**: Works on desktop, tablet, and mobile  
✅ **Search-Friendly**: Well-structured HTML for easy indexing  
✅ **Beautiful Typography**: Gradient headers, clean layout  
✅ **Table Support**: Markdown tables converted with styling  
✅ **Code Highlighting**: Syntax-highlighted code blocks  
✅ **Math Support**: Mathematical equations in markdown  
✅ **Navigation Breadcrumbs**: Know your location at all times  

## 🔧 Customization

### Modify Styling
The CSS is embedded in each HTML file. To customize:
1. Open `index.html` in a text editor
2. Modify the CSS in the `<style>` section
3. Repeat for other HTML files as needed

### Update Content
To add or modify documentation:
1. Update the markdown files in `../docs/`
2. Run the conversion script: `python3 ../convert_docs_to_html.py`
3. The HTML files will be regenerated automatically

## 📝 Regenerating HTML

To regenerate all HTML files after updating markdown:

```bash
cd /Users/phuchoang/Local_Document/data-mining-university
python3 convert_docs_to_html.py
```

**Requirements**: 
- Python 3.6+
- `markdown` package: `pip install markdown`

## 🌐 Deployment

### Deploy to GitHub Pages
```bash
# Copy docs-html to gh-pages branch or docs folder
git add docs-html/
git commit -m "Update HTML documentation"
git push origin main
```

### Deploy to Web Server
```bash
# Copy entire docs-html folder to your web server
scp -r docs-html/ username@server:/var/www/html/pipeline-docs
```

## 📞 Support

For issues or improvements:
1. Check the markdown source files in `../docs/`
2. Update as needed
3. Regenerate HTML using the conversion script
4. Commit changes to git

---

**Generated**: May 2026  
**Pipeline Version**: 1.0.0  
**Last Updated**: May 10, 2026
