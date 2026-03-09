# Biological Concepts

## What are microRNAs?

### Basic Definition

**microRNAs (miRNAs)** are small RNA molecules (~22 nucleotides) that regulate gene expression by binding to messenger RNA (mRNA) and controlling their stability and translation.

```
microRNA: 5'- UGUGAAACGUGCGACACUAA -3'  (22 nt)
         Small, regulatory RNA molecule
```

### Where They Come From

1. **Transcribed** from DNA as long precursors
2. **Processed** by cellular machinery
3. **Loaded** into RISC complex (regulatory protein)
4. **Mature form** is the active ~22 nucleotide molecule
5. **Binds** to target mRNAs

### Their Role in Cells

- 🎯 **Gene regulation**: Control when proteins are made
- 🛑 **Silencing**: Reduce or block protein production
- 🔄 **Fine-tuning**: Adjust gene expression levels
- 🧬 **Development**: Regulate developmental processes
- ⚖️ **Homeostasis**: Maintain cellular balance

---

## What is mRNA?

### Basic Definition

**Messenger RNA (mRNA)** carries genetic instructions from DNA to ribosomes, where proteins are synthesized.

```
DNA → mRNA → Protein
     (transcription)  (translation)
```

### mRNA Structure

```
5' cap ─── 5'UTR ─── CDS ─── 3'UTR ─── poly(A) tail
        (untranslated) (protein coding) (untranslated)
```

### 3'UTR: Where microRNAs Bind

The **3' Untranslated Region (3'UTR)** is the critical zone:
- Located AFTER the protein-coding sequence
- Not translated into protein
- Contains microRNA binding sites
- ~100-1000+ nucleotides typically
- Multiple microRNAs can bind one 3'UTR

**Why here?**
- ✅ Accessible to microRNAs
- ✅ Doesn't interfere with protein production
- ✅ Regulatory region (intended for control)
- ✅ Evolutionarily conserved

---

## How Binding Works

### Step 1: Seed Region Recognition

The **seed region** (nucleotides 2-7 of microRNA) is critical:

```
microRNA:  5'- U GUGAAACGUGCGACACUAA -3'
Position:     1 2345678910...
                 └─seed region─┘
              (positions 2-7)
```

The seed is short (6 nucleotides) but extremely important:
- ✅ Provides specificity
- ✅ Determines target mRNA selection
- ✅ Must be complementary to mRNA
- ✅ Watson-Crick base pairing

### Step 2: Finding the Match

The seed reverse complement searches for matching sequences:

```
microRNA seed:    5'- G U A A C G -3'
Reverse:          3'- G A U U C G -5'
Complement:       3'- C G U A G C -5'

Looking for in mRNA:
3'- C G U A G C -5'   ← This sequence in mRNA
5'- G C A U C G -3'   (displayed 5' to 3')
```

### Step 3: Duplex Formation

When a match is found, base pairing occurs:

```
microRNA:  5'- U GUA ACG UGC GA -3'
           ··· ││||::│││││ ··
mRNA:      3'- A CAU UGC ACG CU -5'

│ = Watson-Crick pair (strong)
: = Wobble pair (G-U, weaker)
· = Mismatch (no pairing)
```

### Step 4: Functional Outcome

Once bound, the microRNA-mRNA complex:
- 🛑 Recruits degradation machinery
- 🔇 Silences translation
- ⚡ Reduces protein levels
- 📉 Effectively "turns off" the gene

---

## Base Pairing Rules

### Watson-Crick Pairs (Strong)

Standard RNA base pairing:

```
Adenine (A) pairs with Uracil (U):     A-U
   ││  
Guanine (G) pairs with Cytosine (C):   G-C
   ││
```

**Characteristics**:
- ✅ Most stable
- ✅ Standard geometry
- ✅ Full score in binding calculations
- ✅ Preferred by RISC complex

**Example**:
```
microRNA: A
mRNA:     U
Result: Watson-Crick pair (score: 1.0)
```

### Wobble Pairs (Weaker)

Special non-standard pairing:

```
Guanine (G) can pair with Uracil (U):  G-U
   :
```

**Characteristics**:
- ⚠️ Less stable than Watson-Crick
- ⚠️ Non-standard geometry
- ⚠️ Partial score in calculations
- ✅ Biologically tolerated
- ✅ Increases binding flexibility

**Example**:
```
microRNA: G
mRNA:     U
Result: Wobble pair (score: 0.5)
```

### No Pairing (Mismatch)

```
Adenine (A) with Cytosine (C):     A-C ✗
```

**Meaning**:
- ❌ Cannot pair
- ❌ Mismatch
- ❌ No contribution to binding strength
- ✅ Allowed in supplementary regions

---

## Seed Region Specificity

### Why Seed Matters Most

The seed determines target selection:

```
Position:        1  2  3  4  5  6  7  8  9 10...
microRNA:        U  G  U  A  A  C  G  U  G  C
                    └──seed (2-7)──┘
                 MUST match exactly!
```

**The seed requirement**:
- ✅ Positions 2-7 MUST be complementary
- ✅ This narrowing is what gives specificity
- ✅ Thousands of mRNAs, but correct seed matches are rare
- ✅ Even one mismatch in seed = no binding

### Alternative Seed Definitions

Researchers sometimes use:
- **2-7**: Standard (6 nt) - most common
- **2-8**: Extended (7 nt) - more stringent
- **1-8**: Strictest (8 nt) - highest specificity
- **2-6**: Relaxed (5 nt) - more permissive

This tool uses **2-7 by default** but allows configuration.

---

## Supplementary Pairing

### Beyond the Seed

After the seed matches, additional nucleotides may pair:

```
microRNA:  5'- U GGUAACGUGCGACAC UAA -3'
Position:     1  2345678910111213141516171819...
Seed (2-7):     └─required─┘
Extra pairing:       └────optional─────┘

Outside seed (1, 8-22):
- Not required for binding
- But strengthen the interaction
- Show in results as "Other Pairs"
```

### Impact of Supplementary Pairs

| Situation | Result |
|-----------|--------|
| Seed only, no extra | Weak binding, may not be functional |
| Seed + some extra | Moderate binding, likely functional |
| Seed + extra pairing | Strong binding, likely functional |

### Scoring System

```
Total Score = (WC pairs × 1.0) + (Wobble pairs × 0.5)

Example 1 (strong):
  Watson-Crick: 16 pairs × 1.0 = 16.0
  Wobble: 2 pairs × 0.5 = 1.0
  Total: 17.0 (strong)

Example 2 (weak):
  Watson-Crick: 6 pairs × 1.0 = 6.0
  Wobble: 0 pairs × 0.5 = 0
  Total: 6.0 (weak)
```

---

## 3'UTR Importance

### Why Only 3'UTR?

microRNAs bind specifically to 3'UTR because:

```
5' cap ─── 5'UTR ─── CDS ─── 3'UTR ─── poly(A)
                   (protein code)
         Blocked:          ✅ Accessible:
         - In translation   - Post-transcriptional
         - Ribosome there    - Exposed to RISC
         - Not accessible   - Regulatory purpose
```

### Accessibility

- **Coding sequence**: Ribosome blocking access (physically)
- **3'UTR**: Free to interact with regulatory proteins
- **Ribosome**: Only reads 5'UTR through CDS
- **RISC complex**: Finds microRNAs in 3'UTR

### Regulatory Effect

microRNA binding to 3'UTR causes:
1. **mRNA destabilization**: Triggers degradation
2. **Translation block**: Prevents protein synthesis
3. **Overall effect**: Reduced protein levels

---

## Biological Reality

### How Many microRNAs Target One Gene?

Typical mRNA is targeted by **5-20 different microRNAs**:

```
mRNA 3'UTR:
┌─ microRNA A site ─┬─ microRNA B site ─┬─ microRNA C site ┬─...
│ CCGAUGC           │ GCAUU              │ ACGUAG            │
└──────────────────┴───────────────────┴────────────────────┴─...
```

**Result**:
- Multiple regulatory pathways
- Combinatorial control
- Gene expression fine-tuning
- Multiple regulatory pathways

### One microRNA Targets Multiple Genes

A single microRNA targets **200-300 different mRNAs**:

```
mir-30a ┬─→ mRNA 1 → Protein 1 ↓
        ├─→ mRNA 2 → Protein 2 ↓
        ├─→ mRNA 3 → Protein 3 ↓
        └─→ ... 200+ targets
```

**Result**:
- Coordinated gene silencing
- Pathway-level effects
- Disease involvement when dysregulated
- Central in gene regulatory networks

### Examples of Biological Importance

| microRNA | Targets | Function |
|----------|---------|----------|
| let-7 | Oncogenes | Tumor suppression |
| mir-122 | Viral RNA | Antiviral defense |
| mir-29 | Collagen | ECM regulation |
| mir-200 | E-cadherin | Epithelial-mesenchymal transition |

---

## When This Tool Is Used

### In Research

1. **Validation**: Confirm predicted interactions
2. **Discovery**: Find new targets for genes of interest
3. **Network analysis**: Map regulatory pathways
4. **Drug development**: Identify therapeutic targets

### In Diagnosis

1. **Biomarkers**: Dysregulated microRNAs indicate disease
2. **Classification**: microRNA signatures classify cancer subtypes
3. **Prognosis**: microRNA levels predict outcomes

### In Development

1. **Gene regulation**: microRNAs control developmental timing
2. **Differentiation**: Control cell fate decisions
3. **Homeostasis**: Maintain cellular stability

---

## Assumptions & Limitations

### This Tool Assumes

✅ Watson-Crick pairing follows standard rules  
✅ Wobble G-U pairs are possible  
✅ Seed region (2-7) is most critical  
✅ Accessibility is sufficient in 3'UTR  
✅ RNA sequences are correctly provided  

### What This Tool Does NOT Include

❌ mRNA secondary structure (can block access)  
❌ Protein binding sites (compete with microRNAs)  
❌ Cellular localization effects  
❌ Tissue-specific expression patterns  
❌ Thermodynamic free energy calculations  
❌ Evolutionary conservation  

### Real-World Complexity

Actual microRNA function depends on:
- 📍 mRNA secondary structure
- 🔬 Protein-RNA interactions
- 🧬 Sequence context effects
- ⏰ Cellular conditions
- 🔄 Competition with other molecules

**Bottom Line**: This tool identifies *potential* binding sites. Experimental validation is recommended for important findings.

