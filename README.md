<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/a59aa986-b99f-422d-bc06-5b8e6d6fa22d">
    <img alt="Plyne logo" src="https://github.com/user-attachments/assets/6a00c7ad-a417-46b9-b515-2ecd75348619">
  </picture>
</div>

# Plyne.ai - Accurate GTM Data for B2B Sales Teams

## Benchmark: Web Research Evaluation

### No Comparison Pages

Evaluates how accurately and consistently different platforms can determine whether a company has dedicated competitor comparison pages on their website.

### Task

Given a company name and domain, determine whether the company has dedicated competitor comparison pages (e.g., "X vs Y", "alternatives to X", comparison landing pages) hosted on their own domain.

**Expected output per company:**

| Field | Description |
|---|---|
| `result` | `qualified` (no comparison pages found) or `unqualified` (comparison pages found) |
| `reasoning` | Brief explanation of what was found or not found |
| `references` | URLs of any comparison pages discovered |

### Dataset

- **100 Series A companies** sourced from public funding databases
- Each company is identified by `name` and `domain`
- Each platform runs the task **3 times** per company to measure consistency

> This is an initial benchmark with a small dataset. Future iterations will test with significantly higher volumes to improve statistical confidence and overall benchmark reliability.

### Prompt

The following prompt is given to all AI agent platforms (Origami, Clay) along with the full list of 100 companies (name + domain). No platform-specific hints, search strategies, or methodology details are included.

```
For each company in the provided list, determine whether their website has
dedicated competitor comparison pages.

Check whether the company's website contains pages that directly compare the
company against specific competitors — such as "X vs Y" pages,
"alternatives to X" pages, or comparison landing pages.
Only consider pages hosted on the company's own domain.

For each company, report:
- Result: "qualified" (no comparison pages found) or "unqualified" (comparison pages found)
- Reasoning: Brief explanation of what was found or not found
- References: URLs of any comparison pages discovered
```

The list of companies is provided as a CSV with `name` and `domain` columns.

> **Note:** Plyne also has an AI agent mode, but this benchmark tests Plyne's **Agentic Research Flow** — a structured flow that runs the same pipeline for every company. "No Comparison Pages" is one of 100+ Agentic Research Flows available in Plyne. The prompt above is used only for the AI agent platforms.

### Evaluation Criteria

#### Data Accuracy

Evaluates whether each platform returns the correct result for each company.

**How it's measured:**

Ground truth is established through a three-step process:

1. **Agreement baseline:** For companies where both platforms agree across all runs, the shared result is accepted as initial ground truth (84 out of 100 companies).
2. **Disputed verification:** For the 16 companies where platforms disagree, each referenced URL is manually visited and evaluated against the comparison page definition.
3. **Agreed-result audit:** All 53 agreed-unqualified companies are also manually verified to catch cases where both platforms reached the correct result through incorrect references, or where both platforms were wrong.

Each platform's per-run result is then compared against ground truth and scored as correct or incorrect.

**Metric:** `accuracy = correct / total` (averaged across 3 runs)

#### Consistency

Measures how consistently each platform returns the same result when the same query is run multiple times.

**How it's measured:**

Each company is processed 3 times. For each company, check whether all 3 runs produced the same `result` (qualified/unqualified).

| Verdict | Description |
|---|---|
| `consistent` | All 3 runs agree on the result |
| `inconsistent` | At least one run disagrees |

**Metric:** `consistency = consistent_companies / total`

#### Consumption

Evaluates cost per 1,000 research operations.

**How it's measured:**

Track the total cost incurred for processing all 100 companies across 3 runs (300 total operations), then normalize to cost per 1,000 operations.

**Metric:** `cost_per_1k = (total_cost / total_operations) × 1000`

### CSV Format

Each platform stores results as **one CSV file per run** inside its own directory:

```
plyne/benchmark-plyne-1.csv
plyne/benchmark-plyne-2.csv
plyne/benchmark-plyne-3.csv

origami/benchmark-origami-1.csv
origami/benchmark-origami-2.csv
origami/benchmark-origami-3.csv

clay/benchmark-clay-1.csv
clay/benchmark-clay-2.csv
clay/benchmark-clay-3.csv
```

**Plyne columns** (comma-delimited):

```
name, domain, last_funding_type, no_comparison_pages_result, no_comparison_pages_reasoning, no_comparison_pages_references
```

**Origami columns** (comma-delimited):

```
Fit Score, Organization Name, Last Funding Type, Website, Competitor Comparison Pages, Competitor Comparison Pages/Reasoning, Competitor Comparison Pages/References
```

**Clay columns** (comma-delimited):

```
Organization Name, Last Funding Type, Website, Competitor Comparison Pages, Reasoning, Formula, Qualification Status, Qualification Status formula
```

> Note: Clay's column structure varied slightly across runs. Run 2 included an additional `Qualification Status explanation` column. The result is always in the `Qualification Status formula` (or `Qualification Status qualification`) column.

### Running the Benchmark

#### Step 1: Run each platform 3 times

Process all 100 companies through each platform using the prompt above. Record results in the CSV format described.

#### Step 2: Establish ground truth

1. Identify companies where both platforms agree across all runs — accept shared result as initial ground truth.
2. For disagreements, manually visit each referenced URL and evaluate whether it meets the comparison page definition.
3. Audit all agreed-unqualified results by verifying referenced URLs to catch shared errors.
4. Record the verified ground truth for each company with reasoning.

#### Step 3: Calculate metrics

| Metric | Formula |
|---|---|
| Accuracy | `correct / total` per run, averaged across 3 runs |
| Consistency | `companies where all 3 runs agree / 100` |
| Cost per 1K | `(total_cost / 300) × 1000` |

### Platforms

| Platform | Type | Status |
|---|---|---|
| **Plyne** | Agentic Research Flows | Completed |
| **Origami** | AI agent | Completed |
| **Clay** | AI agent | Completed |

### Results

#### 1. Accuracy

| Platform | Run 1 | Run 2 | Run 3 | Average |
|---|---|---|---|---|
| **Plyne** | 98/100 (98.0%) | 98/100 (98.0%) | 98/100 (98.0%) | **98.0%** |
| **Origami** | 84/100 (84.0%) | 81/100 (81.0%) | 81/100 (81.0%) | **82.0%** |
| **Clay** | 23/99 (23.2%) | 19/99 (19.2%) | 30/99 (30.3%) | **24.2%** |

> 1 company (Rad Security) has ambiguous ground truth — no platform receives credit for it. 1 company (IMTC) was incorrectly classified by Plyne and Origami (Clay also got it wrong in all 3 runs). Clay results were **aligned with reasoning** (see note below); accuracy is computed **with the on-domain rule** (unqualified without on-domain reference = incorrect).

**Ground truth distribution:** 39 qualified, 60 unqualified, 1 unclear.

**Verification scope:** 69 out of 100 companies were manually verified (16 disputed + 53 agreed-unqualified). The remaining 31 agreed-qualified companies were not audited as proving the absence of comparison pages requires exhaustive site review.

Of the 16 disputed companies, Plyne was correct on all 15 clearly scorable disputes; Origami was incorrect on all 15. Of the 53 agreed-unqualified companies, 1 shared error was found: IMTC — both platforms flagged it as unqualified, but its references are industry reports and concept comparisons, not competitor comparison pages.

> **Note on Clay:** The prompt explicitly instructs: *"Only consider pages hosted on the company's own domain."* However, Clay's references across all 3 runs contained **zero on-domain URLs**. Instead, Clay consistently cited generic third-party sources — SEO guides (Ahrefs, Semrush, Moz), marketing articles (GrowAndConvert, SaaS Landing Page), comparison page examples from unrelated companies (Zendesk, Zoom, Shopify), and community posts (Reddit, Quora). Clay never actually visited the target companies' websites to check for comparison pages. Accordingly, any "unqualified" result without at least one on-domain reference is scored as incorrect — the same standard applied to all platforms.

> **Note on Clay Reasoning–Result Correction & Re-evaluation:** Clay's raw outputs contained cases where the stated result contradicted the reasoning (e.g., reasoning said "no company list provided, cannot execute" but result was "unqualified"). We aligned the result with what the reasoning implies: when reasoning indicates the task could not be executed (no list, execution blocked, etc.), the result is set to **qualified**. This was applied across all 3 Clay runs via `fix_clay_reasoning.py`. The accuracy, consistency, and distribution above use this corrected data. **Accuracy** is computed with the same evidence bar as other platforms: unqualified without at least one on-domain reference = incorrect (Clay's references remain off-domain).

##### Manual Verification of Disputed Companies (Plyne vs Origami)

| # | Company | Plyne | Origami | Ground Truth | Reasoning |
|---|---|---|---|---|---|
| 1 | Acelab | Q | U | **Q** (Plyne) | Origami references are product-category comparisons (window wall vs curtain wall, hopper vs awning) — not competitor comparison pages |
| 2 | Ataccama | U | Q | **U** (Plyne) | Plyne found [ataccama.com/blog/ataccama-vs-informatica](https://www.ataccama.com/blog/ataccama-vs-informatica) — a dedicated competitor comparison page |
| 3 | Delve | Q | U | **Q** (Plyne) | [delve.co/competitors](https://delve.co/competitors) compares against a generic category, not a specific competitor. Other Origami refs (CMMC levels, SOC 2 vs ISO 27001) are framework/concept comparisons |
| 4 | Dotfile | Q | U | **Q** (Plyne) | All Origami refs are regulatory concept comparisons: KYC vs UBO, CDD vs EDD, KYB vs KYC — not competitor pages |
| 5 | Hype | U | Q | **U** (Plyne) | [hype.co/blog/industry/linktree-alternatives](https://hype.co/blog/industry/linktree-alternatives) is a comparison page where Hype positions itself among Linktree alternatives |
| 6 | Knogin | U | Q | **U** (Plyne) | [knogin.com/en/products/ai-intelligence](https://knogin.com/en/products/ai-intelligence) contains a competitive analysis table comparing Argus against other platform categories |
| 7 | Model ML | Q | U | **Q** (Plyne) | [modelml.com/articles/autocheck-vs-mbb-consultants](https://www.modelml.com/articles/autocheck-vs-mbb-consultants) compares AI vs human consultants — not a competitor comparison page |
| 8 | ModernLoop | U | Q | **U** (Plyne) | [modernloop.com/blog/what-are-recruiting-automation-tools/](https://www.modernloop.com/blog/what-are-recruiting-automation-tools/) is a comparison page listing ModernLoop against Greenhouse, CoderPad, and Hiretual |
| 9 | Muck Rack | U | Q | **U** (Plyne) | [muckrack.com/meltwater-alternative](https://muckrack.com/meltwater-alternative) is a dedicated "alternative to" competitor comparison page |
| 10 | Opus | Q | U | **Q** (Plyne) | [opus.so/ga/the-wisetail-lms-alternative](https://www.opus.so/ga/the-wisetail-lms-alternative) is a marketing landing page, not a structured comparison. Pricing page is irrelevant |
| 11 | P0 Security | U | Q | **U** (Plyne) | [p0.dev/campaign/entra-eol](https://www.p0.dev/campaign/entra-eol) is a comparison page with a feature table comparing P0 Security against Entra and Delinea |
| 12 | PriceLabs | Q | U | **Q** (Plyne) | All Origami refs are industry concept articles: Airbnb comparison tool, dynamic pricing vs revenue management, STR vs LTR, competitor monitoring — not competitor comparison pages |
| 13 | Rad Security | U | Q | **unclear** | [radsecurity.ai blog post](https://www.radsecurity.ai/blog/behavioral-versus-signature-based-detection-sensitive-data-access-sudo-cve-and-reverse-shell-examples) contains comparison elements (RAD vs Falco) but is structured as a technical blog post rather than a dedicated comparison page |
| 14 | Revv | U | Q | **U** (Plyne) | [revvhq.com/blog/top-adas-calibration-software-for-collision-shops](https://www.revvhq.com/blog/top-adas-calibration-software-for-collision-shops) is a comparison page listing Revv against Alldata, RepairLogic, and ADAS MAP |
| 15 | Shipium | U | Q | **U** (Plyne) | [hub.shipium.com/content/best-3pl-software/](https://hub.shipium.com/content/best-3pl-software/) is a comparison page with a feature table comparing Shipium against Manhattan, Körber, SAP, and others |
| 16 | SquareX | Q | U | **Q** (Plyne) | [sqrx.com/hassle-enterprise-browsers](https://sqrx.com/hassle-enterprise-browsers) compares against a generic category ("Enterprise Browsers"), not a specific named competitor. Other refs (VDI replacement, PWA vs Electron) are unrelated |

#### 2. Consistency

| Platform | Consistent | Inconsistent | Consistency Rate |
|---|---|---|---|
| **Plyne** | 100 / 100 | 0 | **100%** |
| **Origami** | 80 / 100 | 20 | **80%** |
| **Clay** | 31 / 100 | 69 | **31%** |

**Result distribution per run:**

| Platform | Run | Qualified | Unqualified | Other/Blank |
|---|---|---|---|---|
| Plyne | 1 | 38 | 62 | 0 |
| Plyne | 2 | 38 | 62 | 0 |
| Plyne | 3 | 38 | 62 | 0 |
| Origami | 1 | 32 | 68 | 0 |
| Origami | 2 | 40 | 60 | 0 |
| Origami | 3 | 40 | 60 | 0 |
| Clay | 1 | 57 | 42 | 0 |
| Clay | 2 | 54 | 45 | 0 |
| Clay | 3 | 68 | 31 | 0 |

> Clay's result distribution (after reasoning-correction) is now biased toward "qualified", reflecting that most reasoning indicated the task could not be executed (e.g., "no company list provided").

**Origami inconsistent companies (20):**

| Company | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Ataccama | unqualified | qualified | qualified |
| BreachRx | qualified | qualified | unqualified |
| Dotfile | unqualified | unqualified | qualified |
| Exostellar | unqualified | qualified | qualified |
| HealthBird | unqualified | qualified | qualified |
| Hype | unqualified | qualified | qualified |
| Knogin | qualified | qualified | unqualified |
| LoanPro | unqualified | unqualified | qualified |
| Malbek | qualified | unqualified | qualified |
| Model ML | qualified | unqualified | unqualified |
| Momentic | unqualified | unqualified | qualified |
| Muck Rack | unqualified | qualified | qualified |
| Oneleet | unqualified | qualified | qualified |
| Planhat | unqualified | qualified | qualified |
| Rad Security | unqualified | qualified | qualified |
| Revv | unqualified | qualified | qualified |
| SGNL.AI | qualified | unqualified | unqualified |
| Shipium | unqualified | qualified | qualified |
| WhyLabs | qualified | qualified | unqualified |
| Zonos | unqualified | qualified | unqualified |

**Clay inconsistent companies (69, reasoning-corrected):**

| Company | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| 1mind | qualified | unqualified | qualified |
| Acelab | unqualified | qualified | qualified |
| Akuity | qualified | unqualified | unqualified |
| Arc Technologies | unqualified | qualified | qualified |
| Arena | qualified | unqualified | qualified |
| Artisan AI | qualified | unqualified | qualified |
| Assembly | qualified | unqualified | qualified |
| Ataccama | unqualified | unqualified | qualified |
| Barti | qualified | unqualified | qualified |
| BeyondTrucks | qualified | unqualified | qualified |
| Bikky | qualified | unqualified | qualified |
| BlastPoint | qualified | unqualified | unqualified |
| Brellium | unqualified | qualified | qualified |
| BridgeCare | unqualified | unqualified | qualified |
| BriefCatch | qualified | unqualified | unqualified |
| Carbon Direct | qualified | unqualified | qualified |
| Cledara | unqualified | qualified | unqualified |
| Drivetrain | qualified | qualified | unqualified |
| Exostellar | qualified | unqualified | qualified |
| Firecrawl | unqualified | unqualified | qualified |
| GLIDER.ai | unqualified | qualified | unqualified |
| HealthBird | unqualified | unqualified | qualified |
| Heron Data | unqualified | qualified | qualified |
| HockeyStack | qualified | unqualified | unqualified |
| Humanly.io | unqualified | qualified | qualified |
| Hype | unqualified | qualified | qualified |
| IMTC | unqualified | unqualified | qualified |
| Jump | unqualified | qualified | qualified |
| Katalon | qualified | unqualified | qualified |
| Knogin | qualified | unqualified | unqualified |
| LightSource | unqualified | qualified | qualified |
| LiveFlow | qualified | unqualified | qualified |
| Malbek | qualified | unqualified | qualified |
| Mem0 | unqualified | qualified | unqualified |
| Method Security | unqualified | qualified | qualified |
| Mobot | qualified | unqualified | qualified |
| Momentum | qualified | qualified | unqualified |
| Muck Rack | unqualified | qualified | unqualified |
| OnRamp | unqualified | unqualified | qualified |
| Oneleet | qualified | unqualified | unqualified |
| Opus | unqualified | unqualified | qualified |
| P0 Security | unqualified | qualified | unqualified |
| Park Loyalty Inc. | qualified | unqualified | qualified |
| Planhat | qualified | unqualified | unqualified |
| Rad Security | qualified | qualified | unqualified |
| Rencore | qualified | qualified | unqualified |
| RentRedi | unqualified | qualified | qualified |
| Revv | qualified | qualified | unqualified |
| Right-Hand Cybersecurity | qualified | qualified | unqualified |
| RocketReach.co | unqualified | qualified | qualified |
| Runway Financial | qualified | unqualified | qualified |
| SGNL.AI | qualified | unqualified | qualified |
| Savant Labs | qualified | qualified | unqualified |
| Searchlight | qualified | unqualified | qualified |
| SecurityPal | unqualified | unqualified | qualified |
| Sequel.io | unqualified | unqualified | qualified |
| SquareX | unqualified | qualified | qualified |
| Subskribe | unqualified | unqualified | unqualified |
| Sybill AI | unqualified | unqualified | qualified |
| The Public Health Company | unqualified | unqualified | qualified |
| Traefik Labs | qualified | qualified | unqualified |
| TurinTech AI | unqualified | qualified | unqualified |
| Unframe | unqualified | unqualified | qualified |
| Verisoul | qualified | qualified | unqualified |
| Vermeer | qualified | qualified | unqualified |
| WhyLabs | unqualified | qualified | qualified |
| Xata.io | unqualified | unqualified | qualified |
| Zonos | qualified | unqualified | qualified |
| nexos.ai | unqualified | qualified | qualified |

#### 3. Consumption

| Platform | Runs | Total Credits | Cost (3 runs) | Cost per 1K ops |
|---|---|---|---|---|
| **Plyne** | 3 | 688 | **$11.00** | **$36.67** |
| **Origami** | 3 | 2,018 | **$32.29** | **$107.63** |
| **Clay** | 3 | 1,128 | **$126.05** | **$420.18** |

Origami pricing: 5,000 credits = $80 ($0.016/credit).

Clay pricing: 2,000 credits = $223.50 ($0.11175/credit).
