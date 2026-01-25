# 📄 Document Vision AI

An AI-powered tool that extracts structured data from invoices, receipts, and salary slips using OpenAI's Vision API. Automatically exports extracted data to Excel for easy processing.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## ✨ Features

- **Multi-Format Support** - Process PDF, PNG, JPG, and other image formats
- **AI-Powered Extraction** - Uses GPT-4 Vision for intelligent data extraction
- **Structured Output** - Extracts specific fields like date, amount, vendor, etc.
- **Batch Processing** - Process multiple documents at once
- **Excel Export** - Automatically exports to formatted Excel spreadsheets
- **High Accuracy** - Handles various document layouts and languages

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core Language |
| OpenAI API | Vision AI |
| Pandas | Data Processing |
| Pillow | Image Processing |
| pdf2image | PDF Conversion |

## 📁 Project Structure

```
document-vision-ai/
├── main.py                  # CLI entry point
├── extractor/
│   ├── __init__.py
│   ├── vision_ai.py         # OpenAI Vision integration
│   ├── document_parser.py   # Document parsing logic
│   └── schemas.py           # Data schemas
├── utils/
│   ├── __init__.py
│   ├── image_utils.py       # Image processing utilities
│   └── export.py            # Excel export functions
├── sample_docs/             # Sample documents for testing
├── output/                  # Exported Excel files
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/EhtishamProAI/document-vision-ai.git
cd document-vision-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the extractor
python main.py --input sample_docs/ --output output/
```

## 📖 Usage Examples

### Extract from single invoice
```python
from extractor import DocumentExtractor

extractor = DocumentExtractor()
data = extractor.extract("invoice.pdf")
print(data)
```

### Batch process multiple documents
```python
from extractor import DocumentExtractor

extractor = DocumentExtractor()
results = extractor.batch_extract("documents/", output_excel="results.xlsx")
```

## 📊 Extracted Fields

### Invoice Fields
| Field | Description |
|-------|-------------|
| `invoice_number` | Unique invoice identifier |
| `date` | Invoice date |
| `vendor_name` | Seller/vendor name |
| `vendor_address` | Seller address |
| `total_amount` | Total invoice amount |
| `tax_amount` | Tax/VAT amount |
| `line_items` | List of items with quantities and prices |

### Receipt Fields
| Field | Description |
|-------|-------------|
| `store_name` | Store/merchant name |
| `date` | Transaction date |
| `items` | Purchased items |
| `subtotal` | Subtotal before tax |
| `tax` | Tax amount |
| `total` | Total amount |

## 👨‍💻 Author

**Ehtisham Ashraf**  
Senior AI Software Engineer | AI & Automation Specialist

- GitHub: [@EhtishamProAI](https://github.com/EhtishamProAI)
- Email: kingehtsham0@gmail.com
