"""Build a working manuscript directly from the full-chain experiment records."""
import argparse
import json
from pathlib import Path
from statistics import mean
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

parser=argparse.ArgumentParser()
parser.add_argument("--runs",type=Path,required=True)
parser.add_argument("--out",type=Path,required=True)
args=parser.parse_args()
paths=sorted(args.runs.glob("*/metrics.json"))
records=[json.loads(p.read_text()) for p in paths]
expected={(a,s) for a in ("text","atomic","bits") for s in (3,11,29)}
if {(r["arm"],r["seed"]) for r in records} != expected or len(records)!=9:
    raise ValueError("expected all nine protocol runs")
if len({json.dumps(r["source_hashes"],sort_keys=True) for r in records})!=1:
    raise ValueError("mixed training sources")
if any(r["steps"]!=1200 for r in records):
    raise ValueError("unexpected training protocol")
args.out.mkdir(parents=True,exist_ok=False)

title="From Contextual Senses to PanSigna: An Auditable Native-Encoding Pilot"
status="Working draft - controlled synthetic corpus; author and submission metadata pending"
abstract=("We implement and test an auditable transformation from raw controlled-English statements through contextual sense annotation, typed ontology assignment, a versioned notion catalog and a null-skipping bit index to PanSigna-encoded training data. Nine small causal transformers are trained from scratch across text, atomic-notion and bit-stream representations. All three text and all three atomic-notion runs generate correct answers on all 144 held-out prompts per run. Bit-stream models generate catalog-resolvable answers on 87.5-95.8% of prompts, but only 45.8-48.6% are semantically correct. Training-only probes recover some recipient information; the tested ridge-derived interventions show no improvement in recipient swaps over unpatched generation. These results establish a reproducible engineering path through the proposed stages, but do not establish a causal interpretability advantage, broad natural-language coverage, efficient transport, or editable model weights.")
sections=[
("1. Motivation and research question",[
"PanSigna proposes stable notion identities as a shared semantic surface for communication and computation. The present question is narrower: can a complete corpus-to-encoding pipeline train a model that emits readable notion encodings, and do its hidden representations offer selective causal handles on those notions? We distinguish three observations: catalog-resolvable output, correct semantic output, and causal control of internal representations. None entails the next.",
"The distinction between lexical expressions and ontology references has established precedents such as OntoLex-Lemon [1]. Our experimental catalog is a small local inventory, not an implementation or replacement of the full OntoLex model. Causal abstraction [2] motivates testing a proposed neural-to-symbolic mapping with interventions. Circuit tracing [3] likewise validates proposed mechanisms through effects in the original model. We borrow those methodological principles without claiming to reproduce either system."]),
("2. Corpus and transform contracts",[
"The source contains 384 assistant-authored English statements: two word-order forms for each of 192 combinations of eight named entities, three predicates and eight recipients. Three additional inputs intentionally fall outside the supported grammar. This is a controlled synthetic corpus, not a sample of unrestricted writing. The same author designed the grammar and oracle; no independent human annotation study has been performed.",
"Stage 1 preserves raw UTF-8 text, source identifiers and content hashes. Stage 2 assigns contextual senses with exact character spans: for example, passes authority maps to delegation while passes a parcel maps to giving. The deterministic annotator receives only raw text; gold frames reside in a separate file and are used for scoring. Stage 3 assigns a typed actor-action-recipient frame. All 384 supported records match the generator oracle, and all three unsupported records are quarantined. This agreement tests the declared grammar, not word-sense disambiguation quality in general.",
"Stage 4 builds a catalog separating named entities, predicates, roles and a query operator. Definitions carry an experimental namespace and version. Stage 5 assigns unique variable-length bit strings, beginning and ending with 1 and excluding eight consecutive zero bits at every offset. Stage 6 serializes role/value sequences using eight zeros between notion identifiers. All 384 encodings roundtrip to their accepted frames. This is semantic normalization within the fragment; original wording, word order and all grammatical distinctions are not recoverable from the encoding alone.",
"Each stage emits a separate artifact. The training loader verifies file hashes, catalog identity and decoding consistency. Eight repository skills describe ingestion, annotation, assignment, catalog maintenance, indexing, transcoding, evaluation and reporting. These are agent operating instructions; the experiment itself uses deterministic reference transforms, not an independently validated agent swarm."]),
("3. Experimental design",[
"We compare raw text, atomic PanSigna notion tokens, and literal bit tokens. Native arms receive both prompts and answers through the transformed catalog. BOS, ANSWER, EOS and padding are explicit transport-envelope controls outside the notion stream. Each statement produces three field-value questions. Actor-recipient combinations and all their action/template variants are held out together: 864 training, 144 development and 144 test records.",
"All models have two transformer layers, width 48, four attention heads and 54,669 parameters, with a shared finite experimental vocabulary. No pretrained model or concept-supervision objective is used. Training uses full next-token cross entropy, AdamW with learning rate 0.003, batch size 64, 1,200 steps and seeds 3, 11 and 29 on CPU. Arms share sampled example indices per seed. This matches example exposure, not compute; bit sequences are longer. Dependency versions and source hashes are recorded with each run.",
"Evaluation uses unconstrained greedy generation with a 16-token cap. Outputs must terminate and resolve to exactly one catalog item to count as legible. Matching the requested field value is a separate correctness test. No repair, constrained decoder or natural-language fallback is substituted for native generations. The task is field recall and can be solved by copying; it does not require multi-hop reasoning, quantification, negation or variable binding."]),
("4. Vector mapping and intervention",[
"At each layer, we collect the hidden state at the final prompt readout. A training-only ridge decoder (regularization 0.01) predicts recipient identity across all three question types. Its column space, with rank at most seven, defines a candidate recipient subspace. A separate intercept-bearing ridge probe measures held-out recoverability. The mapping family is a simple baseline, not distributed alignment search or interchange intervention training.",
"For a base prompt, a donor shares the queried field but differs in actor, action and recipient. With orthonormal basis Q, the patched state is b + ((d - b)Q)Q-transpose. During generation, that patch is reapplied at the fixed original prompt readout position, not at each newly generated token. We select the layer on development data using the mean of recipient-swap accuracy and actor/action correctness, then freeze it. Random same-rank, shuffled-label and unpatched controls are evaluated on test data.",
"The intervention leaves other context positions intact, allowing later attention to retrieve the original information. In bit generation, a final-layer patch need not control subsequent bits. A null result therefore constrains this mapping and intervention family, not all possible semantic representations. The earlier v0.1 pilot separately verified a full-final-state positive control; that is an implementation check, not evidence of selective control in these native runs."]),
("5. Results",[
"All nine runs terminate on every held-out prompt. Text and atomic-notion runs achieve 144/144 semantically correct responses each. The bit runs achieve 70/144, 66/144 and 70/144 correct responses for seeds 3, 11 and 29, respectively. Catalog-resolvable bit responses number 138, 126 and 126. Thus syntactic/catalog legibility is substantially higher than semantic correctness.",
"Recipient probe accuracies vary with seed and representation. They do not demonstrate a consistent atomic PanSigna advantage. For every run, learned-patch recipient-swap counts equal the corresponding unpatched counts. Nonzero bit-arm donor matches already occur without intervention and must not be interpreted as causal effects. Random and shuffled-label controls provide the same caution. Actor/action preservation is high in the already-perfect categorical arms and lower in the less competent bit models.",
"Each run sees 76,800 sampled records. Atomic runs process 844,800 nonpadding training input tokens; text runs process approximately 909,000; bit runs process approximately 7.53 million. These counts include different serialization units and do not imply directly comparable perplexities or throughput. No significance test or confidence interval is reported from three seeds and correlated synthetic templates."]),
("6. Limitations and next tests",[
"The corpus, ontology and annotation rules are deliberately small and co-designed. The annotation audit lacks independent adjudication, and neither the language coverage nor the inventory resembles a full public ontology. Equivalent paraphrases are normalized, so lexical fidelity must be distinguished from preservation of the declared event frame. Registry hashes are reproducibility checks, not a complete authenticated governance system.",
"The bit objective contains many framing zeros and uses longer contexts. Equal example exposure does not settle whether bit coding is beneficial under equal compute, larger models or different optimization. The query answers involve a single notion and are much simpler than free-form dialogue or executable service plans. Probes are limited to recipient identity and a fixed linear family. Weight editing, persistent learning, compression optimality, security, general AGI and mechanistic completeness are not tested.",
"A next study should freeze a new protocol, compare intervention-optimized alignment with ridge, measure context-path bypass, add compositional answers and use independently annotated natural-language data. It should separate sense annotation, ontology structure, categorical IDs and literal bit serialization through appropriate controls. Larger budgets and fresh held-out data should follow a power analysis rather than a search for a favorable test result."]),
("7. Conclusion",[
"The full reference pipeline can produce native notion training data and legible generated answers in a controlled setting. Atomic notions match the text baseline here; literal bits produce many readable but wrong answers. The tested vector mappings provide no selective causal advantage over unpatched generation. This supplies executable infrastructure and concrete failure cases for a stronger experiment, rather than confirmation of the broader PanSigna hypothesis."]),
("Contributions and publication status",[
"Ryan's PanSigna conception and requested encoding invariants motivated the work. Astra, the Codex AI assistant, designed and implemented this controlled experiment, generated its synthetic corpus, ran the tests, analyzed the recorded outputs and drafted this document. Human verification of the full manuscript and final author metadata remains pending. AI involvement is disclosed as a contribution; no claim of approved AI coauthorship, institutional affiliation, peer review, endorsement or arXiv acceptance is made.",
"This document is a working manuscript, not a submitted preprint. Submission remains deferred while the author metadata, applicable platform requirements and submission route are resolved. Scientific suitability and final author responsibility must be established before submission."]),
("References",[
"[1] Cimiano, McCrae and Buitelaar, eds. Lexicon Model for Ontologies: Community Report. W3C Ontology-Lexica Community Group, 2016. https://www.w3.org/2016/05/ontolex/ . Community report, not a W3C Recommendation.",
"[2] Geiger, Lu, Icard and Potts. Causal Abstractions of Neural Networks. NeurIPS, 2021. https://arxiv.org/abs/2106.02997 .",
"[3] Ameisen et al. Circuit Tracing: Revealing Computational Graphs in Language Models. Transformer Circuits, 2025. https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html .",
"[4] PanSigna executable research repository. https://github.com/Smithright/PanSigna/tree/research/causal-legibility-pilot . Per-run source hashes, corpus receipts and checkpoints are included in the shared project archive."])]

table=[["Arm","Seed","Legible","Correct","Probe","Swap: base / patch"]]
for r in records:
    b=r["test"]["none"]; p=r["test"]["learned"]
    table.append([r["arm"],str(r["seed"]),f"{b['catalog_legible']}/144",f"{b['semantic_correct']}/144",f"{r['recipient_probe_accuracy']:.3f}",f"{b['recipient_swap_successes']}/48 / {p['recipient_swap_successes']}/48"])

md=["# "+title,"",status,"","## Abstract","",abstract,""]
for heading,paragraphs in sections:
    md += ["## "+heading,""]
    for text in paragraphs: md += [text,""]
    if heading=="5. Results":
        md += ["| "+" | ".join(table[0])+" |","| "+" | ".join(["---"]*len(table[0]))+" |"]
        md += ["| "+" | ".join(row)+" |" for row in table[1:]]
        md += [""]
(args.out/"manuscript.md").write_text("\n".join(md))

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="ArticleTitle",fontName="Times-Bold",fontSize=19,leading=22,alignment=TA_CENTER,spaceAfter=12))
styles.add(ParagraphStyle(name="ArticleBody",fontName="Times-Roman",fontSize=10.5,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name="ArticleHeading",fontName="Times-Bold",fontSize=13,leading=16,spaceBefore=12,spaceAfter=7,keepWithNext=True))
styles.add(ParagraphStyle(name="ArticleMeta",fontName="Times-Italic",fontSize=9,leading=12,alignment=TA_CENTER,spaceAfter=12))
story=[Paragraph(escape(title),styles["ArticleTitle"]),Paragraph(escape(status),styles["ArticleMeta"]),Paragraph("10 September 2026",styles["ArticleMeta"]),Paragraph("Abstract",styles["ArticleHeading"]),Paragraph(escape(abstract),styles["ArticleBody"])]
for heading,paragraphs in sections:
    story.append(Paragraph(escape(heading),styles["ArticleHeading"]))
    for text in paragraphs: story.append(Paragraph(escape(text),styles["ArticleBody"]))
    if heading=="5. Results":
        t=Table(table,colWidths=[48,34,62,62,48,142],repeatRows=1,hAlign="CENTER")
        t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8edf2")),("LINEBELOW",(0,0),(-1,0),.7,colors.black),("LINEBELOW",(0,-1),(-1,-1),.5,colors.grey),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story += [t,Spacer(1,10)]

def footer(canvas,doc):
    canvas.saveState(); canvas.setFont("Times-Roman",9)
    canvas.drawString(58,32,"PanSigna - working draft; not submitted")
    canvas.drawRightString(554,32,str(doc.page)); canvas.restoreState()
pdf=args.out/"pansigna-native-encoding-draft.pdf"
SimpleDocTemplate(str(pdf),pagesize=(612,792),rightMargin=58,leftMargin=58,topMargin=50,bottomMargin=48,title=title,author="PanSigna research project; metadata pending").build(story,onFirstPage=footer,onLaterPages=footer)
(args.out/"evidence.json").write_text(json.dumps({"runs":[str(p) for p in paths],"table":table,"source_hashes":records[0]["source_hashes"],"status":status},indent=2)+"\n")
print(pdf)
