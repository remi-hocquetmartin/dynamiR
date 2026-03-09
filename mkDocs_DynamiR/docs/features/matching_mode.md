# Matching Mode - Direct Analysis

## Overview

**Matching Mode** allows you to analyze a **specific microRNA** against a **target mRNA** to determine if binding can occur and where the binding sites are located.

Perfect for:
- ✅ Validating known microRNA-mRNA interactions
- ✅ Testing hypothesis about specific regulators
- ✅ Getting detailed binding site information
- ✅ Visualizing RNA duplex alignments

---

## How Matching Mode Works

### The Algorithm

```
1. User provides: microRNA + mRNA + Seed Region
   Example: mir-30a + SMAD1 gene + positions 2-7
   
2. Extract seed from microRNA (positions 2-7)
   Example: GCCAUC
   
3. Reverse complement the seed
   microRNA:  5'- G C C A U C -3'
   Complement:3'- C G G U A G -5'
   
4. Search for this sequence throughout mRNA
   
5. For each match found:
   - Display position in mRNA
   - Show full duplex alignment
   - Calculate pairing statistics
```

### Input Requirements

| Component | Format | Example |
|-----------|--------|---------|
| **microRNA** | Sequence (19-23 nt) | UGUGAAACGUGCGACACUAA |
| **mRNA** | Sequence (100+ nt) | AUGAAACGCGAGCGACGAGC... |
| **Seed Region** | Positions (start-end) | 2-7 |

---

## Step-by-Step Analysis

### 1️⃣ Input: microRNA

Choose how to provide the microRNA:

#### Option A: Database ID
```
Select: ⊙ DB ID
Enter: MIMAT0007560
```
**Fetches from**: miRBase database  
**Auto-loads**: Full mature microRNA sequence  
**Example IDs**:
- MIMAT0007560 (mmu-mir-30a)
- MIMAT0000062 (mmu-let-7a)

#### Option B: File
```
Select: ⊙ File
Choose: [Browse] → select_file.fa
```
**Format**: FASTA file  
**Content**: Plain RNA/DNA sequence  
**Example file**:
```
>mir-30a
UGUGAAACGUGCGACACUAA
```

#### Option C: Direct Sequence
```
Select: ⊙ Sequence
Paste: UGUGAAACGUGCGACACUAA
```
**Format**: Plain text sequence  
**Notes**: Whitespace ignored, case-insensitive

---

### 2️⃣ Input: Target mRNA

Choose how to provide the mRNA (important: only 3'UTR is analyzed):

#### Option A: GenBank ID
```
Select: ⊙ GenBank ID
Enter: NM_008539
```
**Fetches from**: NCBI Entrez  
**Auto-extracts**: 3'UTR region (after stop codon)  
**Example IDs**:
- NM_008539 (mouse SMAD1)
- NM_002111.8 (human TP53)

⚠️ **Note on Position Numbering**: When DynamiR extracts the 3'UTR from GenBank, nucleotide position 1 starts at the beginning of the 3'UTR region (right after the CDS stop codon). This is the binding region of interest.

#### Option B: GenBank File
```
Select: ⊙ File
Choose: [Browse] → gene.gb
```
**Format**: GenBank file (.gb, .gbk) or FASTA file (.fa, .fasta)  
**Auto-extracts**: 3'UTR from CDS annotation (GenBank only)  
**Benefits**: No internet needed, local analysis

⚠️ **Note on Position Numbering**: When using GenBank files, nucleotide position 1 is set at the start of the 3'UTR region (right after the CDS stop codon). Results report positions relative to this 3'UTR start point.

#### Option C: FASTA File
```
Select: ⊙ File
Choose: [Browse] → sequence.fa
```
**Format**: FASTA file (.fa, .fasta)  
**Note**: Uses entire sequence (you must provide only 3'UTR)

#### Option D: Direct Sequence
```
Select: ⊙ Sequence
Paste: AUGAAACGCGAGCGACGAGC...
```
**Format**: Plain text  
**Important**: Paste only the 3'UTR region

---

### 3️⃣ Input: Seed Region

Specify which positions of the microRNA must match:

```
Seed: 2-7
```

#### Understanding Seed Positions
```
microRNA sequence (5' to 3'):
Position: 1  2  3  4  5  6  7  8  9  10...
Base:     U  G  U  A  A  C  G  U  G  C

Seed region 2-7: G U A A C G (highlighted)
              ↑  ↑  ↑  ↑  ↑  ↑
              These 6 positions MUST match
```

#### Common Seed Regions
- **2-7**: Most common, 6 nucleotides
- **2-8**: More stringent, 7 nucleotides
- **1-8**: Strictest, 8 nucleotides
- **2-6**: More permissive, 5 nucleotides

#### Why Seed Matters
The seed region is most critical for:
- ✅ Binding specificity
- ✅ Thermodynamic stability
- ✅ Regulatory effectiveness

---

### 4️⃣ Run Analysis

Click the **[ Parse ]** button

**What happens**:
1. Validates all inputs
2. Extracts seed region from microRNA
3. Creates reverse complement
4. Searches entire mRNA
5. For each match: calculates full alignment
6. Displays results

**Timing**: Usually < 1 second

---

## Understanding Results

### Result Display

```
==================================================
Number of binding sites found: 2
==================================================

mRNA binding position: 450
microRNA region:   1- 22
mRNA region:    440-460

3' (22)  CGAGACGUCGAGUGCGACGAU  5' (microRNA): MIMAT0007560
             ||||:||:|||||||||
5' (450) GCUCUGCAGCUCACGCUGCUA  3' (mRNA): NM_008539

Seed region: 2-7 (marked with *)

ALIGNMENT STATISTICS:
  Total base pairs: 18
  Watson-Crick pairs: 16 (strong)
  Wobble pairs: 2 (weak)
  Supplementary pairs outside seed: 10
  Binding strength: 78%
```

### Interpreting Each Line

| Element | Meaning |
|---------|---------|
| **mRNA binding position** | Where in mRNA the binding starts (1-indexed) |
| **microRNA region** | Which nucleotides of microRNA are shown |
| **mRNA region** | Which nucleotides of mRNA are shown |
| **`\|` symbol** | Watson-Crick pair (strong: A-U or C-G) |
| **`:` symbol** | Wobble pair (weaker: G-U) |
| **` ` (space)** | Mismatch (no pairing) |
| **`*` marker** | Seed region (positions 2-7) |

### Statistics Explained

**Watson-Crick Pairs**
- Strongest, most stable bonds
- A pairs with U
- C pairs with G
- Score: 1.0 point each

**Wobble Pairs**
- Weaker but biologically valid
- G pairs with U (non-standard)
- Score: 0.5 point each

**Binding Strength**
```
Formula: (WC_pairs × 1.0 + Wobble_pairs × 0.5) / microRNA_length
Example: (16 + 2×0.5) / 22 = 17/22 = 77%
```

Higher percentage = stronger binding

---

## Interpreting Multiple Binding Sites

If multiple sites are found:

```
Number of binding sites found: 3

[First site alignment]
...

[Second site alignment]
...

[Third site alignment]
...
```

**Meaning**:
- microRNA can bind to multiple locations
- Each location is independent
- Can indicate multiple regulatory pathways
- Some sites may be stronger than others

---

## What Results Mean

### ✅ Positive Result (Sites Found)
```
Number of binding sites found: 2
```
**Interpretation**:
- microRNA likely DOES regulate this mRNA
- Binding can occur at specified location(s)
- The seed region matches perfectly
- Additional pairing provides stability

**Next Steps**:
- Validate experimentally (if needed)
- Study the identified sites
- Check if they're in regulatory regions
- Download results for record-keeping

### ❌ Negative Result (No Sites Found)
```
No binding sites found with these parameters
```
**Possible Meanings**:
- microRNA doesn't bind this mRNA with your seed settings
- Try a different seed region (2-8, 2-6)
- Verify your sequences are correct
- Check that mRNA is the 3'UTR region


---

## Exporting Results

Click the **💾** button to save results

**What gets saved**:
- All binding site information
- Complete alignments
- Statistics and calculations
- Input sequence information

**Format**: Plain text file (.txt)  
**Default name**: `matching_results.txt`

**Use cases**:
- Archive your analysis
- Share with colleagues
- Include in publications
- Integrate with other tools

---

## Tips & Tricks

### 🎯 Get Better Results
1. **Use GenBank IDs** when possible - ensures 3'UTR extraction
2. **Verify input sequences** - typos cause false negatives
3. **Try different seed regions** - sometimes 2-8 works better
4. **Check multiple microRNAs** - helps find primary regulator

### ⏱️ Speed Up Analysis
- Direct sequence input is fastest (no database lookup)
- Files are faster than IDs (no internet needed)
- Short sequences analyze faster than long ones

**Internet Requirements**:

- ⚡ **microRNA Database ID**: No internet needed (database is pre-downloaded locally)
- 🌐 **mRNA GenBank ID**: Requires internet to fetch from NCBI
- 📁 **Files**: No internet needed (local analysis)
- ✏️ **Direct Sequence**: No internet needed

### 🔍 Deeper Exploration
- Run same microRNA against different mRNAs
- Test multiple seed regions
- Use Dynamite mode to find other targets
- Compare results between different annotations

---

## Common Questions

**Q: Why is my seed 2-7 but I see 8 pairing nucleotides?**  
A: The seed (2-7) MUST match, but often additional nucleotides (position 1 and 8+) also pair. These strengthen the binding but aren't required.

**Q: Can I use the full mRNA sequence instead of 3'UTR?**  
A: Yes, but results may include unrealistic binding sites in coding regions. 3'UTR is where real microRNA binding occurs.

**Q: What if I get thousands of binding sites?**  
A: This can happen with short seeds or very long mRNAs. Try a longer seed region (2-8 instead of 2-7) or more stringent criteria.

