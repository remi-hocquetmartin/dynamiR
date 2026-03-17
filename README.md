# DynamiR - microRNA Binding Site Analysis Tool

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A comprehensive graphical tool for identifying microRNA binding sites on target mRNA sequences using multiple analysis modes.

</div>

## 🔬 Overview

DynamiR is a bioinformatics application designed to analyze microRNA (miRNA) binding sites on messenger RNA (mRNA) sequences. It provides three complementary analysis modes to support different research workflows:

- **Matching Mode**: Direct alignment of a user-provided microRNA against a target mRNA
- **Dynamite Mode**: High-throughput screening of entire miRNA database against target mRNA

## ✨ Features

- 🎯 **Three Analysis Modes**: Flexible workflows for different research needs
- 🧬 **Multiple Input Formats**: Support for FASTA, GenBank, and direct sequence entry
- 🔄 **Database Integration**: NCBI GenBank access for remote sequence retrieval
- 📊 **Detailed Results**: Watson-Crick pairing, wobble pairing analysis, and binding statistics
- ⚡ **Threading Support**: Non-blocking UI for long-running analyses
- 💾 **Export Results**: Save analysis results to file
- 🖥️ **Intuitive GUI**: Clean, tabbed interface built with Tkinter

## 📋 Requirements

- Python 3.7 or higher
- BioPython (>=1.75)
- Tkinter (usually included with Python)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dynamiR.git
cd dynamiR
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python projet.py
```

## 📖 Usage

### Video Demonstration
Watch this video to see DynamiR in action:
[![DynamiR Demo](https://img.youtube.com/vi/Xs2eHMujGWI/0.jpg)](https://www.youtube.com/watch?v=Xs2eHMujGWI)

### Matching Mode
Direct microRNA-to-mRNA binding analysis:
1. Enter a microRNA sequence (database ID, file, or direct input)
2. Enter a target mRNA sequence (GenBank ID, file, or direct input)
3. Specify seed region (e.g., positions 2-7)
4. Click "Parse" to run analysis
5. Results show all binding sites with detailed pairing information

### Dynamite Mode
Scan entire miRNA database against target mRNA:
1. Enter target mRNA sequence
2. Specify seed region
3. Click "Parse" to run analysis (~5-10 seconds)
4. Results show all microRNAs with binding affinity

### BLAST Mode
Sequence homology searching:
1. Enter query mRNA sequence
2. Specify identity threshold
3. Click "Parse" to run BLAST search
4. Results displayed with E-values and alignment metrics

## 🏗️ Project Structure

```
dynamiR/
├── projet.py               # Main entry point
├── gui_frontend.py         # Main GUI window
├── backend/                # Core algorithms
│   └── stub_backend.py     # Matching, Dynamite, and BLAST implementations
├── ui/                     # User interface components
│   ├── matching_tab.py     # Matching mode UI
│   ├── dynamite_tab.py     # Dynamite mode UI
│   ├── blast_tab.py        # BLAST mode UI
│   ├── loading_popup.py    # Loading indicator widget
│   └── widgets.py          # Reusable UI components
├── utils/                  # Utility functions
│   ├── file_readers.py     # Sequence file I/O
│   └── parsers.py          # Text parsing utilities
├── data/                   # Data files and databases
├── requirements.txt        # Python dependencies
├── setup.py               # Package installation configuration
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md              # This file
```

## 🔧 Configuration

### Sequence Format Support

**FASTA Format (.fa, .fasta)**
```
>sequence_name
AUGCAUGCAUGC...
```

**GenBank Format (.gb, .gbk)**
- Fully annotated sequences from NCBI
- Automatic metadata extraction
- Remote retrieval by GenBank ID

**Direct Entry**
- Paste sequences directly into input fields
- Automatic T→U conversion (DNA to RNA)

### Seed Region Specification
- Format: `start-end` (e.g., `2-7`)
- Defines critical binding region for perfect Watson-Crick pairing
- Outside seed region: wobble pairs acceptable

## 📊 Algorithm Details

### Watson-Crick Pairing
Standard base pairs with full binding stability:
- A-U (adenine-uracil)
- C-G (cytosine-guanine)

### Wobble Pairing
Non-standard but functional pair:
- G-U (guanine-uracil) - partial binding stability

### Scoring
- Full score: Watson-Crick pairs
- Half score: Wobble pairs
- Binding percentage: Score / microRNA length × 100

## 🔄 Workflow

1. **Sequence Acquisition**
   - From file (automatic format detection)
   - From NCBI database (via GenBank ID)
   - Direct text entry

2. **Preprocessing**
   - Uppercase conversion
   - DNA→RNA conversion (T→U)
   - Reverse complement for microRNA

3. **Alignment**
   - Position-by-position comparison
   - Seed region validation
   - Supplementary pairing detection

4. **Result Compilation**
   - Binding site identification
   - Statistics calculation
   - Visual representation formatting

## 💡 Use Cases

### Research
- Validate predicted microRNA targets
- Discover novel miRNA-mRNA interactions
- High-throughput target screening

### Development
- Validate bioinformatics algorithms
- Test sequence processing pipelines
- Benchmark sequence alignment performance

### Education
- Learn microRNA binding mechanics
- Understand seed region importance
- Explore miRNA-mRNA interactions

## 🐛 Troubleshooting

### GenBank Connection Issues
- Check internet connection
- Verify GenBank ID format (e.g., `NM_002111.8`)
- SSL certificate issues typically self-resolve

### File Format Not Recognized
- Ensure correct file extension (.fa, .fasta, .gb, .gbk)
- Verify file contains valid sequence data
- Check file encoding (UTF-8 recommended)

## 📝 Citation

If you use this tool, please cite:
```
DynamiR: microRNA Binding Site Analysis Tool
Rémi Hocquet Martin, 2026
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### To Contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: remi.hocquetmartin@icloud.com

## 🙏 Acknowledgments

- BioPython team for sequence analysis tools
- NCBI for GenBank database access
- Python Tkinter for GUI framework

## 📚 References

- [BioPython Documentation](https://biopython.org/)
- [NCBI GenBank](https://www.ncbi.nlm.nih.gov/genbank/)
- [microRNA Biology](https://en.wikipedia.org/wiki/MicroRNA)
- [Watson-Crick Base Pairing](https://en.wikipedia.org/wiki/Base_pair)

---

Made with ❤️ for bioinformatics
