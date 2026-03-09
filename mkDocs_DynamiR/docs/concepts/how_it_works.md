# How It Works

## System Overview

DynamiR provides a system for analyzing how microRNAs interact with mRNA sequences. This page explains the overall workflow and how the two analysis modes work together.

```
┌─────────────────────────────────────────────────────────┐
│                     DynamiR                             │
│                                                         │
│  Input: microRNA + mRNA → Analysis → Results          │
│                                                         │
│  Two Analysis Modes:                                    │
│  1. Matching Mode: Direct analysis                     │
│  2. Dynamite Mode: Database scanning                   │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Workflow

### Step 1: Launch Application

User runs `projet.py` which starts the graphical interface:

```
projet.py
   ↓
gui_frontend.py (Main Window)
   ├─ Input Panel (left)
   ├─ Output Panel (right)
   └─ Mode Selection (top)
```

### Step 2: Provide Input

User specifies sequences in three possible ways:

```
Input Option 1: Database ID
  Example: "let-7a-1" or GenBank "NM_004317"
  Source: NCBI/GenBank lookup
  Result: Automatic sequence fetch

Input Option 2: File Upload
  Example: FASTA file or GenBank file
  Source: User's local files
  Result: Parse sequences from file

Input Option 3: Direct Sequence
  Example: Paste FASTA-formatted text
  Source: Direct user input
  Result: Use provided sequence as-is
```

### Step 3: Select Analysis Mode

User chooses what to analyze:

#### Mode A: Matching
```
Purpose: Direct Analysis
Input:   microRNA + mRNA (user provides both)
Process: Compare seed region to find binding sites
Output:  List of all matches with scores
Time:    Fast (seconds)
```

#### Mode B: Dynamite
```
Purpose: Database Scanning
Input:   mRNA only (database provides microRNAs)
Process: Scan all ~48,860 microRNAs in database
Output:  Ranked list of which microRNAs bind
Time:    Slow (minutes)
```

### Step 4: Configure Search

User optionally adjusts seed region:

```
Default: Positions 2-7 (6 nucleotides)
Options: 2-6 (relaxed), 2-8 (strict), custom

Example microRNA:
5'- U GUAACGUGCGACACUAA -3'
   Position numbers:
   1 2345678910111213...
     └seed region─┘
```

### Step 5: Run Analysis

User clicks "Run Analysis" button:

```
Matching Mode:
  Input validation ✓
  Seed region extracted ✓
  Reverse complement created ✓
  Search mRNA for matches ✓
  Score all matches ✓
  Display results ✓

Dynamite Mode:
  Input validation ✓
  Database loaded ✓
  Progress window opened ✓
  For each microRNA (48,860):
    - Extract seed region
    - Search target mRNA
    - Score any matches
    - Store results
  Display ranked results ✓
```

### Step 6: View Results

Results appear in output panel:

#### Matching Mode Results
```
Alignment display:
microRNA: 5'- GUAACGUGCGACACUAA -3'
         ├──│││::││││││ ││ ├──
mRNA:    3'- CUUGCACGCUGUGAUU -5'

Statistics:
- Watson-Crick pairs: 14
- Wobble pairs: 2
- Total score: 15.0
- Binding strength: High
- Position in mRNA: 123-140
```

#### Dynamite Mode Results
```
Ranked Results Table:
Rank │ microRNA │ Position │ Score │ W-C │ Wobble
──────┼──────────┼──────────┼───────┼─────┼────────
  1  │ mir-30a  │ 456-473  │ 18.0  │ 16  │  2
  2  │ mir-29b  │ 234-251  │ 17.5  │ 17  │  1
  3  │ let-7a   │ 189-206  │ 16.0  │ 14  │  4
...
```

### Step 7: Export or Analyze Further

User can:
- 📊 View alignment details
- 💾 Download results (CSV, text, FASTA)
- 🔄 Run new analysis
- 🔗 Export for further study

---

## Matching Mode Deep Dive

### Purpose
Direct comparison of one specific microRNA with one specific mRNA. Use when you want to know: "Does THIS microRNA bind to THIS mRNA?"

### Workflow

```
User Input:
├─ microRNA ID (or sequence)
├─ mRNA ID (or sequence)
└─ Seed region (optional, default 2-7)

Process:
├─ Fetch/parse sequences ✓
├─ Extract microRNA seed ✓
├─ Create reverse complement ✓
├─ Search mRNA for matches ✓
├─ Score all binding sites ✓
└─ Rank by strength ✓

Output:
├─ Primary result (top match shown)
├─ Alignment visualization
├─ Binding statistics
└─ Download option
```

### Key Algorithm

1. **Extract seed**: nucleotides 2-7 of microRNA
2. **Reverse complement**: Convert to DNA search format
3. **Scan mRNA**: Look for matching sequences in 3'UTR
4. **Score matches**: Calculate Watson-Crick + Wobble pairs
5. **Rank results**: Sort by binding strength

### Data Flow

```
microRNA: let-7a
     ↓
Extract seed (2-7):
"GUAACG"
     ↓
Reverse complement:
"CUUGC"
     ↓
Search in mRNA sequence:
"...ACGCUUGCGCA..."  ← Found!
     ↓
Extract context:
"...ACGCUUGCGCAUUU..."
     ↓
Align with full microRNA:
let-7a:    5'- GGAGGUAGUAGGUUGGUUGUU -3'
mRNA:      3'- UUCC   GAUCA    ACAACA -5'
     ↓
Score: 14 W-C, 2 Wobble = 15.0
     ↓
Display result
```

### Example Use Cases

| Question | Input | Output |
|----------|-------|--------|
| "Does mir-122 target HCV?" | HCV mRNA + mir-122 | Position + strength |
| "Where on 3'UTR?" | 3'UTR + microRNA | Exact position in sequence |
| "How strong is binding?" | Both sequences | Score + alignment |
| "Multiple sites?" | mRNA + microRNA | All positions ranked |

---

## Dynamite Mode Deep Dive

### Purpose
Database screening of an mRNA target against all ~48,860 microRNAs. Use when you want to know: "Which microRNAs in the database can bind to THIS mRNA?"

### Workflow

```
User Input:
├─ mRNA sequence (or ID)
└─ Seed region (optional)

Process:
├─ Load database (~48,860 microRNAs) ✓
├─ Parse mRNA sequence ✓
├─ For each microRNA (serial scan):
│  ├─ Extract seed region
│  ├─ Search in target mRNA
│  ├─ Score any matches
│  └─ Record results
└─ Sort by binding strength ✓

Output:
├─ Progress window (real-time)
├─ Result table (all matches)
├─ Export option
└─ Ranking by score
```

### Why "Dynamite"?

The name reflects the tool's purpose: screen an mRNA "target" against the entire database arsenal of microRNAs. Like scanning a target with dynamite, it finds everything that can "hit" the target.

### Key Algorithm

1. **Load database**: Read all ~48,860 microRNA sequences
2. **For each microRNA**:
   - Extract seed region (2-7)
   - Search target mRNA for matches
   - Score any matches found
   - Store in results
3. **Rank**: Sort by highest score first

### Processing Flow

```
Target mRNA: "ACGUACGUACGUACGU..."

Database search (48,860 microRNAs):

mir-1:     Seed "GUUAA" → Not found
mir-2:     Seed "UCGAU" → Not found
mir-3:     Seed "ACGUA" → Found! Score: 12.0
...
mir-1500:  Seed "GAUCA" → Found! Score: 8.0

Results:
┌─ mir-3 (score 12.0)
├─ mir-234 (score 11.5)
├─ mir-789 (score 11.0)
└─ ... sorted descending
```

### Performance Characteristics

| Factor | Details |
|--------|---------|
| Database Size | ~48,860 microRNAs |
| Analysis Target | Single mRNA (3'UTR) |
| Processing Time | 2-10 minutes (depends on mRNA length) |
| Memory Usage | ~50MB (database + results) |
| Result Size | 5-50 matches typically |

### Example Use Cases

| Question | Input | Output |
|----------|-------|--------|
| "What regulates this mRNA?" | mRNA sequence | All regulatory microRNAs ranked |
| "Which microRNAs are involved?" | Gene 3'UTR | Predicted microRNA network |
| "Strongest regulators?" | 3'UTR | Top microRNAs by binding strength |
| "Pathway regulators?" | Pathway gene mRNA | All pathway microRNA regulators |

---

## Comparing the Two Modes

### Side-by-Side Comparison

| Aspect | Matching Mode | Dynamite Mode |
|--------|--------------|-------------|
| **Purpose** | Verify specific interaction | Find all interactions |
| **User Provides** | microRNA + mRNA | mRNA only |
| **Database** | Not used | All 48,860 microRNAs |
| **Processing** | Single comparison | 48,860 comparisons |
| **Time** | Seconds | Minutes |
| **Output** | One top result | Ranked list |
| **Question** | "Does X bind Y?" | "What binds Y?" |
| **Use Case** | Hypothesis testing | Discovery |

### When to Use Each

#### Use Matching Mode When...
- ✅ You have a specific hypothesis
- ✅ Testing one microRNA-mRNA pair
- ✅ Want detailed alignment view
- ✅ Need fast feedback
- ✅ Validating known interactions
- ✅ Teaching/learning mode

#### Use Dynamite Mode When...
- ✅ Discovering new regulators
- ✅ Understanding gene regulation
- ✅ Finding pathway microRNAs
- ✅ Screening multiple candidates
- ✅ Network analysis
- ✅ All regulatory information needed

### Typical Workflow

```
Step 1: Use Dynamite
  "Find all microRNAs targeting this gene"
  → Ranked list of candidates

Step 2: Use Matching
  "Verify top candidate with full details"
  → Detailed alignment and scores

Step 3: Interpret
  "Understand the biology"
  → Read alignment, check conservation, validate
```

---

## Data Sources

### microRNA Database

- **Source**: EMBL microRNA sequences (miRNA.dat)
- **Content**: ~1,500 human microRNA sequences
- **Format**: EMBL flat file format
- **Sequences**: Mature microRNA sequences
- **Coverage**: Human miRNA set
- **Updated**: Periodically from official sources

### External Data Sources

The tool can also access:

1. **NCBI GenBank**
   - Purpose: Fetch sequences by ID
   - Examples: "NM_004317" (mRNA), "let-7a-1" (microRNA)
   - Connection: HTTPS via Biopython

2. **User Files**
   - Format: FASTA or GenBank
   - Purpose: Local sequence analysis
   - No internet required

### GenBank File Handling

When user uploads GenBank files (.gb or .gbk):

```
GenBank file example:
LOCUS NM_004317     1234 bp
...
FEATURES
  source          1..1234
  CDS             1..900
  3'UTR           901..1234

Processing:
1. Detect .gb/.gbk extension
2. Load as GenBank format
3. Extract 3'UTR region (positions 901..1234)
4. Use 3'UTR for analysis
```

---

## Result Interpretation

### Understanding Scores

All binding sites scored by base-pair quality:

```
Score = (Watson-Crick pairs × 1.0) + (Wobble pairs × 0.5)

Example:
  16 Watson-Crick pairs × 1.0 = 16.0
  +  2 Wobble pairs × 0.5 = 1.0
  ─────────────────────────────
  Total Score = 17.0
```

### Binding Strength Classification

| Score | Strength | Interpretation |
|-------|----------|-----------------|
| 14-22 | Very Strong | Highly likely functional |
| 12-14 | Strong | Probably functional |
| 10-12 | Moderate | Might be functional |
| 8-10 | Weak | Uncertain functionality |
| 6-8 | Very Weak | Questionable |
| <6 | Minimal | Seed-only matches |

### Seed-Only Matches

Some matches have only seed region pairing:

```
microRNA: 5'- U GUAACGUGCGACACUAA -3'
             └seed─┘
mRNA:     3'- A CUUGCACGU...    -5'
             └seed─┘

Result: 6 W-C (seed) + 0 others = score 6.0
Meaning: Seed binds but little supplementary pairing
Strength: Weak but biologically possible
```

---

## Technical Details

### Input Validation

The tool validates all inputs:

```
Sequence checks:
✓ Only valid nucleotides (ACGTU)
✓ Minimum length (8 nt minimum)
✓ Format correct (FASTA if file)
✓ ID found in database (if using ID)

Error handling:
✗ Invalid characters → Error message
✗ Sequence too short → Error message
✗ ID not found → Suggest alternatives
✗ File format wrong → Error message
```

### Processing Steps

1. **Preprocessing**
   - Load sequences
   - Validate format
   - Extract regions (seed, 3'UTR)

2. **Seed Extraction**
   - Get nucleotides 2-7
   - Create reverse complement
   - Prepare for scanning

3. **Scanning**
   - Slide seed across mRNA
   - Check for matches
   - Record positions

4. **Scoring**
   - Calculate Watson-Crick pairs
   - Calculate Wobble pairs
   - Sum total score

5. **Ranking**
   - Sort by score descending
   - Assign positions
   - Prepare visualization

6. **Output**
   - Format results
   - Create alignments
   - Enable export

---

## Limitations

### What This Tool Does

✅ Finds potential binding sites by sequence complementarity  
✅ Scores binding site quality  
✅ Visualizes alignments  
✅ Exports results  

### What This Tool Does NOT Do

❌ Evaluate mRNA secondary structure  
❌ Consider protein-RNA interactions  
❌ Account for cellular localization  
❌ Predict actual gene silencing efficiency  
❌ Include thermodynamic calculations  
❌ Assess evolutionary conservation  

### Real Biology Is More Complex

```
Predicted binding site  ≠  Actual functional interaction

Factors beyond this tool:
├─ mRNA forms hairpins blocking access
├─ RNA-binding proteins compete
├─ Subcellular localization differs
├─ Seed region mutations in disease
└─ Regulatory proteins enhance/block binding
```

### Recommendations

1. **Always validate** computationally predicted sites
2. **Check conservation** using alignment tools
3. **Consider structure** using RNA prediction tools
4. **Perform experiments** for important findings
5. **Review literature** for known interactions

---

## Architecture Summary

```
┌───────────────────────────────────────────────────┐
│         User Interface Layer (Tkinter)             │
│  ├─ Main Window (gui_frontend.py)                 │
│  ├─ Matching Tab (matching_tab.py)                │
│  ├─ Dynamite Tab (dynamite_tab.py)                │
│  ├─ Widgets (widgets.py)                          │
│  └─ Loading Popup (loading_popup.py)              │
├───────────────────────────────────────────────────┤
│         Analysis Engine Layer (Backend)            │
│  ├─ Sequence Analysis (stub_backend.py)           │
│  ├─ Seed Extraction                               │
│  ├─ Binding Site Detection                        │
│  └─ Results Scoring                               │
├───────────────────────────────────────────────────┤
│         Utility Layer                              │
│  ├─ File Readers (file_readers.py)                │
│  │  ├─ FASTA parsing                              │
│  │  ├─ GenBank parsing                            │
│  │  └─ 3'UTR extraction                           │
│  ├─ Parsers (parsers.py)                          │
│  │  └─ Seed range parsing                         │
│  └─ Data Access                                   │
├───────────────────────────────────────────────────┤
│         Data Layer                                 │
│  ├─ microRNA Database (~48,860 sequences)          │
│  ├─ User Files (FASTA, GenBank)                   │
│  └─ External APIs (NCBI GenBank)                  │
└───────────────────────────────────────────────────┘
```

---
