# Background: Robust Statistical Analysis on Streaming Data with Near-Duplicates

## Main article
**Zhang, Qin. (2025).** *Robust Statistical Analysis on Streaming Data with Near-Duplicates in General Metric Spaces.*
Proc. ACM Manag. Data 3, 2 (PODS), Article 111.
`articles/robust-streaming-near-duplicates-zhang2025.pdf`

---

## Topic overview

The paper asks: can we run standard streaming statistics (distinct element count, random sampling) on a noisy dataset where many items are "the same" up to small noise — without first cleaning the data?

The core difficulty is that previous work only handled near-duplicates in **low-dimensional Euclidean space** (O(1) dimensions). This paper generalises to **arbitrary metric spaces**, motivated by high-dimensional data (text, images, quantum states) where the Euclidean embedding would be intractably large.

### Key concepts to understand the paper

- **Data stream model**: elements arrive one by one; you can only use sublinear memory; no full pass back over the data.
- **F₀ (distinct elements)**: count how many distinct items are in the stream.
- **Robust F₀ / α-valid partition**: group items within distance α together; count groups, not raw items.
- **ℓ₀-sampling**: output a uniformly random distinct element from the stream.
- **Robust ℓ₀-sampling**: output a uniformly random group representative.
- **F₀-ambiguity (τ)**: fraction of items that are "borderline" — they could belong to multiple groups; controls the hardness of the problem.
- **Well-shaped dataset**: groups are far enough apart that the valid partition is unique and easy to define.
- **General metric space**: distance function d(·,·) with no algebraic structure assumed; can't hash near-duplicates together cheaply.

### Why general metric spaces are harder
In Euclidean space you can use grid-snapping or locality-sensitive hashing to approximately map near-duplicates to the same bucket. In a general metric space there is no such trick, so the algorithms need a fundamentally different approach (sketching over the metric structure).

---

## Relevant literature — what each source contributes

Papers are grouped by the **sub-topic** they cover. The `articles/` folder is where you add the PDFs.

---

### 1. Foundations of streaming / F₀ estimation

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `alon-matias-szegedy1999.pdf` | Alon, Matias, Szegedy. *The space complexity of approximating the frequency moments.* JCSS 58(1), 1999. | Founding paper of the streaming model and F₀/Fp estimation. Defines the space complexity framework used throughout the field. |
| NOT `bar-yossef2002.pdf` | Bar-Yossef, Jayram, Kumar, Sivakumar, Trevisan. *Counting distinct elements in a data stream.* RANDOM 2002. | First near-optimal F₀ streaming algorithm; introduces the "sketching by hashing" paradigm. |
| `kane-nelson-woodruff2010.pdf` | Kane, Nelson, Woodruff. *An optimal algorithm for the distinct elements problem.* PODS 2010. | Optimal-space algorithm for F₀; the clean theoretical benchmark that later robust variants are compared to. |
| `flajolet-martin1985.pdf` | Flajolet, Martin. *Probabilistic counting algorithms for database applications.* JCSS 31(2), 1985. | Original probabilistic distinct-count algorithm; historical anchor for the topic. |
| `hyperloglog2008.pdf` | Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* DMTCS 2008. | Practical F₀ algorithm used in production systems; bridges theory to practice. |

---

### 2. ℓ₀-sampling and Lp-sampling in streams

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `jowhari-saglam-tardos2011.pdf` | Jowhari, Saglam, Tardos. *Tight bounds for Lp samplers, finding duplicates in streams, and related problems.* PODS 2011. | Tight space bounds for ℓ₀-sampling; directly cited as the baseline the robust variant must match. |
| `cormode-muthukrishnan-rozenbaum2005.pdf` | Cormode, Muthukrishnan, Rozenbaum. *Summarizing and mining inverse distributions on data streams via dynamic inverse sampling.* VLDB 2005. | Streaming sampling techniques; background for the sampling side of the paper. |
| `frahling-indyk-sohler2008.pdf` | Frahling, Indyk, Sohler. *Sampling in dynamic data streams and applications.* IJCGA 18(1/2), 2008. | Geometric sampling in streams; covers sampling in metric spaces, which is closer to the setting of the main article. |

---

### 3. Robust / noisy streaming — direct predecessors

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `chen-zhang2016.pdf` | Di Chen, Qin Zhang. *Streaming algorithms for robust distinct elements.* SIGMOD 2016. | **Direct predecessor.** Same problem (robust F₀) but restricted to O(1)-dimensional Euclidean space. The main article generalises this. |
| `chen-zhang2018.pdf` | Jiecao Chen, Qin Zhang. *Distinct sampling on streaming data with near-duplicates.* PODS 2018. | **Direct predecessor.** Robust ℓ₀-sampling in Euclidean space. The other direct precursor to the main article. |

---

### 4. Approximate nearest neighbours and LSH (metric-space tools)

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `indyk-motwani1998.pdf` | Indyk, Motwani. *Approximate nearest neighbors: towards removing the curse of dimensionality.* STOC 1998. | Introduces LSH; foundational for understanding why near-duplicate detection in low-dim Euclidean space is tractable and why general metric spaces are harder. |

---

### 5. Duplicate detection and data cleaning (applied context)

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `elmagarmid-ipeirotis-verykios2007.pdf` | Elmagarmid, Ipeirotis, Verykios. *Duplicate record detection: a survey.* IEEE TKDE 19(1), 2007. | Survey of practical duplicate detection; motivates why streaming dedup is needed (full offline cleaning is too expensive). |
| `koudas-sarawagi-srivastava2006.pdf` | Koudas, Sarawagi, Srivastava. *Record linkage: similarity measures and algorithms.* SIGMOD 2006. | Similarity measures used in practice; connects the abstract metric distance model to real-world data. |
| `dong-naumann2009.pdf` | Dong, Naumann. *Data fusion: resolving data conflicts for integration.* VLDB 2009. | Data quality and conflict resolution angle; background motivation for why near-duplicates matter in analytics pipelines. |

---

### 6. Communication complexity lower bounds (proof technique)

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `yao1979.pdf` | Yao. *Probabilistic computations: toward a unified measure of complexity.* FOCS 1979. | Yao's minimax principle; the standard tool for proving streaming lower bounds via communication complexity reductions. |
| `bar-yossef-jayram-kerenidis2004.pdf` | Bar-Yossef, Jayram, Kerenidis. *Exponential separation of quantum and classical one-way communication complexity.* STOC 2004. | Communication complexity lower bound used by the paper to show the hardness gap between general metric and Euclidean cases. |

---

### 7. Graph sketching (supporting techniques)

| File (add to articles/) | Citation | What it contributes |
|---|---|---|
| `ahn-guha-mcgregor2012-pods.pdf` | Ahn, Guha, McGregor. *Graph sketches: sparsification, spanners, and subgraphs.* PODS 2012. | Graph-based streaming sketches; the paper uses a graph construction (Steiner tree on metric) internally. |

---

## Reading order for a deep dive

1. **Alon–Matias–Szegedy 1999** — understand the streaming model and what F₀ means.
2. **Kane–Nelson–Woodruff 2010** — optimal clean F₀; the baseline to beat.
3. **Jowhari–Saglam–Tardos 2011** — optimal ℓ₀-sampling baseline.
4. **Chen–Zhang 2016** and **Chen–Zhang 2018** — the direct predecessors; read these before the main article.
5. **Indyk–Motwani 1998** — LSH; explains why Euclidean space is special.
6. **Main article (Zhang 2025)** — now you have the full context.
7. **Yao 1979 + Bar-Yossef 2004** — needed to follow the lower-bound proofs.

---

## Possible directions for your own experiment / extension

- **Empirical blow-up study**: implement the Chen–Zhang 2016 Euclidean algorithm and the new metric-space algorithm on synthetic datasets of varying dimension; measure space vs accuracy tradeoff.
- **Real-data near-duplicate test**: apply the F₀-estimation algorithm on a real noisy dataset (e.g. deduplicating log lines or address strings using edit distance as the metric).
- **F₀-ambiguity sensitivity**: vary τ (the ambiguity parameter) on synthetic data and measure how quickly accuracy degrades — validate the theoretical bound experimentally.
- **Comparison of metric structures**: run the algorithm on several metric spaces (edit distance, Earth Mover Distance, tree metric) and compare empirical performance to theoretical predictions.
