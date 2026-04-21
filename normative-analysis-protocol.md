# NormTrace
## Normative Analysis Protocol

This document sets out the core operational protocol used by NormTrace for deep normative legal analysis.

It functions as the repository’s instruction layer for structured analysis. Its purpose is to guide the review of domestic legal instruments by specifying:

- the analytical stages to follow;
- the repository files that must be consulted;
- the order in which they should be used;
- the terminology that must remain consistent;
- the output logic to be followed;
- and the minimum safeguards against overstatement, omission, and unsupported inference.

The protocol is designed for the structured review of laws, decrees, regulations, codes, and other domestic legal instruments where the objective is not merely to identify textual matches, but to assess:

- legal effect;
- institutional design;
- implicit exclusions;
- normative alignment;
- legal compatibility with international standards;
- and implementation-oriented gaps.

The current pilot application focuses on **disability rights** in **Mexico** and **Switzerland**, with the **Convention on the Rights of Persons with Disabilities (CRPD)** as the primary international legal instrument.

---

## Operational status of this file

This file is the **operational protocol** of NormTrace.

It is distinct from:

- `docs/methodological-note.md`, which explains the project’s analytical problem, theoretical foundations, scope, and limitations;
- `docs/terminology-guide.md`, which fixes the repository’s core vocabulary;
- the thematic analytical frameworks in `references/frameworks/`;
- the country-specific modules in `references/countries/`;
- the international instrument files in `references/instruments/`;
- and the case-law notes in `references/case-law-notes/`.

Where there is uncertainty about interpretation, the protocol must prioritise:

1. primary legal sources;
2. the terminology guide;
3. the relevant analytical framework;
4. the relevant country module;
5. the full instrument file;
6. and explicit acknowledgement of uncertainty.

---

## Core analytical principle

NormTrace must not treat legal analysis as a keyword exercise.

The legal meaning of a domestic legal instrument depends not only on what the text declares, but also on:

- the actors it empowers or burdens;
- the remedies it creates or withholds;
- the institutions it activates or bypasses;
- the rights-holders it includes or leaves unaddressed;
- the obligations it assigns or leaves undefined;
- the funding, coordination, and enforcement mechanisms it creates or omits;
- the competence level at which it operates;
- and the practical enforceability of its guarantees.

**Normative silence is analytically relevant.**

A domestic legal instrument may appear rights-compatible in wording while remaining structurally weak, exclusionary, jurisdictionally mislocated, or only partially aligned with the applicable international standard.

---

## Non-negotiable analytical rules

1. Do **not** invent legal provisions, case law, dates, reforms, institutional powers, or treaty content.
2. Do **not** assume that a domestic legal instrument is current if the date or version is uncertain.
3. Do **not** treat mention of a right as evidence of full legal compatibility.
4. Do **not** confuse declaratory language with enforceable obligation.
5. Do **not** collapse structural analysis, exclusion analysis, and conventionality or compatibility analysis into a single step.
6. Do **not** treat treaty text, case law, General Comments, and concluding observations as equivalent sources; distinguish their role.
7. Do **not** overstate the binding force of interpretive materials where their status is persuasive rather than formally binding.
8. Do **not** move to reform recommendation before clearly identifying the legal problem and the applicable standard.
9. Where uncertainty exists, state it explicitly.
10. Where the text is incomplete, historical, partial, or unverified, say so before proceeding.
11. Do **not** assume that the Mexican model of conventionality control applies unchanged to Switzerland or to other jurisdictions.
12. In Swiss analysis, do **not** assume that all relevant treaty provisions are directly applicable without issue-specific assessment.

---

## Terminology rule

Use the terminology fixed in:

- `docs/terminology-guide.md`

The following terms should remain stable across outputs:

- **domestic legal framework**
- **domestic legal instrument**
- **international legal instrument**
- **international standard**
- **normative alignment**
- **legal compatibility**
- **implementation-oriented gap**
- **rights-holders**

Use jurisdiction-sensitive terms where appropriate:

- **constitutional parameter of rights review** — for the Mexican context, where applicable
- **international human rights compatibility analysis** — especially for the Swiss context

Avoid unnecessary alternation with near-synonyms unless a specific doctrinal distinction is required.

---

## Repository consultation workflow

Before producing analysis, consult repository materials in the following order.

### 1. Foundational orientation
- `docs/methodological-note.md`
- `docs/terminology-guide.md`
- `normative-analysis-protocol.md`

### 2. Analytical frameworks
- `references/frameworks/structural-analysis.md`
- `references/frameworks/exclusion-analysis.md`
- `references/frameworks/conventionality-analysis.md`
- `references/frameworks/legal-argumentation.md`

### 3. Country-specific legal context

#### For Mexico
- `references/countries/mexico/legal-system.md`

#### For Switzerland (federal level)
- `references/countries/switzerland/legal-system.md`

#### For Switzerland (cantonal level)
Read both:
- `references/countries/switzerland/legal-system.md`
- `references/countries/switzerland/cantonal-analysis-protocol.md`

### 4. International legal instrument files
Use these in two layers.

#### Rapid operational reference
Read the relevant `*-key-articles.md` file first.

For the current pilot:
- `references/instruments/cdpd-key-articles.md`

Use it to identify:
- the most relevant treaty provisions;
- the minimum standard associated with each provision;
- typical domestic legal red flags;
- and the main interpretive materials linked to the relevant article.

#### Extended substantive reference
Read the full instrument file where the issue is:
- legally complex;
- partially aligned;
- contested;
- jurisdictionally sensitive;
- article-specific;
- or likely to require structured legal argumentation.

For the current pilot:
- `references/instruments/cdpd.md`

### 5. Case-law and interpretive support

#### For Mexico
- `references/case-law-notes/disability-rights-mexico.md`

#### For Switzerland
- `references/case-law-notes/disability-rights-switzerland.md`

Use these files selectively to identify doctrinally relevant standards.  
Do **not** use them as mechanical checklists of citations.

---

## Stage 0. Text ingestion and verification

Before analysis begins, obtain the full domestic legal instrument under review.

Possible sources may include:

- uploaded files;
- pasted legal text;
- official legal databases;
- government gazettes;
- legislative portals;
- institutional repositories;
- cantonal or municipal legal collections where relevant.

The analyst must verify, where possible:

- whether the text is complete;
- whether it is current;
- whether amendments or later reforms may affect interpretation;
- whether the text corresponds to the actual instrument being analysed;
- whether the instrument is federal, state-level, cantonal, municipal, regulatory, technical, or otherwise context-specific.

### Stage 0 output requirement

Before moving forward, state clearly:

- the name of the domestic legal instrument;
- the jurisdiction;
- the level of normativity;
- the apparent date/version information;
- and any uncertainty affecting the analysis.

If the text is partial, outdated, or uncertain, explicitly flag the limitation.

---

## Jurisdiction-routing rule

Before Stage 1, determine the jurisdictional route.

### Route A — Mexico
Use the Mexico country module and, where relevant, the logic of **conventionality control** within the constitutional parameter of rights review.

### Route B — Switzerland, federal level
Use the Switzerland legal-system module and frame Stage 3 primarily as **international human rights compatibility analysis**.

### Route C — Switzerland, cantonal level
Use the Switzerland legal-system module **plus** the cantonal-analysis-protocol file.
At Stage 1 and Stage 3, identify:

- the canton;
- the level of normativity;
- the relevant competence structure;
- whether federal law occupies or structures the field;
- and how international standards relate to cantonal implementation.

Do **not** begin substantive analysis before the jurisdictional route is clear.

---

## Stage 1. Structural analysis of the domestic legal instrument

This stage examines the formal anatomy, institutional architecture, competence context, and enforceability structure of the domestic legal instrument.

### Files to consult
- `references/frameworks/structural-analysis.md`
- relevant country module
- for Swiss cantonal instruments, also:
  - `references/countries/switzerland/cantonal-analysis-protocol.md`

### 1.1 Formal anatomy

Identify:

- type of domestic legal instrument;
- place in the domestic normative hierarchy;
- date of enactment and latest reform where available;
- structure by titles, chapters, sections, or articles;
- whether the instrument is constitutional, statutory, general, federal, cantonal, state-level, regulatory, technical, or administrative.

### 1.2 Normative actor mapping

Identify the actors to whom the domestic legal instrument assigns responsibilities, powers, or roles, including where relevant:

- executive authorities;
- legislative actors;
- judicial or quasi-judicial bodies;
- autonomous institutions;
- subnational authorities;
- private sector actors;
- civil society organisations;
- rights-holders themselves;
- international or monitoring bodies.

For each actor, identify:

- duties;
- powers;
- implementation role;
- monitoring role;
- and any mechanism of accountability or enforceability.

### 1.3 Responsibility flow

Assess whether the domestic legal instrument:

- centralises responsibility;
- delegates downward;
- disperses duties without coordination;
- creates concurrent obligations;
- or creates a coherent intersectoral or multilevel framework.

Where relevant, ask whether there is:

- a coordinating body;
- legal authority to act;
- budgetary support;
- sanctioning capacity;
- institutional continuity;
- and any duty to report, monitor, or evaluate.

### 1.4 Enforceability

Assess whether the domestic legal instrument includes:

- sanctions;
- judicial or administrative remedies;
- monitoring mechanisms;
- measurable targets;
- reporting duties;
- implementation deadlines;
- transitional provisions;
- or other devices that move the norm beyond declaration.

### Stage 1 output requirement

At the end of this stage, the analysis should be able to state clearly:

- what kind of domestic legal instrument is being analysed;
- at what level of government it operates;
- who is responsible for implementation;
- whether the competence structure is coherent;
- and whether the rights recognised are structurally enforceable or primarily declaratory.

---

## Stage 2. Exclusion and implicit omission analysis

This stage examines what the domestic legal instrument does not adequately articulate and the differentiated effects of that absence.

### Files to consult
- `references/frameworks/exclusion-analysis.md`
- where relevant:
  - `references/frameworks/structural-analysis.md`
  - relevant country module

### 2.1 Subject of rights

Assess:

- who is explicitly recognised;
- how the legal subject is defined;
- whether the definition is restrictive or expansive;
- whether subgroups are omitted implicitly;
- whether the instrument adopts a rights-based or assistentialist construction.

### 2.2 Gender perspective

Review whether the domestic legal instrument:

- recognises gendered forms of disadvantage;
- addresses women and girls where relevant;
- accounts for gender-based violence;
- avoids exclusionary generic language;
- and anticipates differentiated legal effects.

### 2.3 Intersectionality

Examine whether the instrument accounts for intersections with factors such as:

- indigeneity;
- migration status;
- age;
- poverty;
- rurality;
- linguistic difference;
- sexual orientation;
- gender identity;
- deprivation of liberty;
- and other relevant forms of structural disadvantage.

### 2.4 Cultural, territorial, and linguistic accessibility

Where relevant, assess whether the domestic legal instrument:

- recognises minority or indigenous populations where applicable;
- incorporates consultation standards where applicable;
- accounts for cultural and linguistic accessibility;
- recognises geographic and documentary barriers;
- and avoids assuming a single homogeneous rights environment.

### 2.5 Language as exclusion

Review whether legal terminology:

- reflects outdated, pejorative, or medicalising assumptions;
- narrows the legal subject through paternalistic language;
- frames persons as passive beneficiaries rather than rights-holders;
- or otherwise reproduces subordinating assumptions.

### 2.6 Normative silence

Assess whether exclusion arises through:

- absolute omission;
- relative omission;
- declaratory recognition without mechanism;
- budgetary silence;
- or delegation to future regulation without deadline.

### Stage 2 output requirement

At the end of this stage, the analysis should be able to specify:

- whether exclusion is direct, indirect, structural, or omission-based;
- which subgroup or rights-holder is affected;
- and whether the problem lies in wording, omission, institutional design, access pathway, or legal language.

---

## Stage 3. Conventionality or international compatibility analysis

This stage compares the domestic legal framework with the relevant international legal instrument through legal function and effect rather than textual symmetry alone.

### Files to consult
- `references/frameworks/conventionality-analysis.md`
- `references/instruments/cdpd-key-articles.md`
- `references/instruments/cdpd.md`
- relevant case-law notes where needed

### 3.1 Applicable standard

Identify the applicable international and domestic interpretive framework, which may include:

- treaty provisions;
- constitutional clauses;
- General Comments;
- concluding observations;
- regional human rights standards;
- domestic high-court doctrine;
- and other authoritative or persuasive interpretive materials.

### 3.2 Jurisdiction-sensitive framing

#### In Mexico
Frame this stage primarily through:
- conventionality control;
- the constitutional parameter of rights review;
- and domestic high-court doctrine where relevant.

#### In Switzerland
Frame this stage primarily through:
- international human rights compatibility analysis;
- monist incorporation of international law;
- direct applicability where relevant;
- federal–cantonal competence interaction;
- and ECHR or constitutional equality pathways where judicially useful.

### 3.3 Instrument reference workflow

Use instrument files in two layers.

#### Rapid operational reference
Read the relevant `*-key-articles.md` file first in order to identify:

- the most relevant treaty provisions;
- the minimum standard associated with each provision;
- typical domestic legal red flags;
- and the main interpretive materials linked to that article.

#### Extended substantive reference
Read the full instrument file when:

- the issue is legally complex or contested;
- the domestic legal instrument appears only partially aligned;
- the analysis requires article-specific nuance;
- or the output requires structured legal argumentation.

The short instrument files are intended for orientation and analytical triage.  
The full instrument files remain the authoritative internal reference within the repository.

### 3.4 Functional contrast

Assess whether the domestic legal instrument is consistent with principles such as:

- non-regression;
- progressivity;
- maximum protection;
- effectiveness;
- equality;
- non-discrimination;
- accessibility;
- participation;
- autonomy where relevant.

### 3.5 Gap identification

Classify findings where relevant as:

- total absence;
- weak or declaratory recognition;
- incompatibility;
- regression;
- indirect or structural discrimination;
- omission affecting a specific subgroup;
- implementation-oriented gap.

The objective is not merely to record difference, but to assess the legal significance of that difference.

### Stage 3 output requirement

At the end of this stage, the analysis should be able to state:

- which international standard is engaged;
- how the domestic legal instrument relates to it;
- what type of gap exists;
- and whether the problem concerns legal compatibility, normative under-specification, exclusionary design, competence structure, or implementation-oriented deficiency.

---

## Stage 4. Structured legal argumentation

This stage translates analytical findings into structured legal arguments suited to the intended forum.

### Files to consult
- `references/frameworks/legal-argumentation.md`
- relevant case-law notes
- relevant instrument files
- relevant country module

### Required components of each argument

Each argument should identify:

- the core finding;
- the domestic legal instrument or provision under review;
- the international standard engaged;
- the type of legal deficiency;
- the relevant doctrinal or interpretive support;
- and a possible line of reform, remedy, litigation, or advocacy.

Arguments may then be organised according to:

- urgency;
- remediability;
- litigation potential;
- institutional forum;
- and expected effect on rights-holders.

### Stage 4 output requirement

Do not produce vague or purely rhetorical conclusions.

Each argument should specify:

- the legal problem;
- the standard breached or engaged;
- the character of the incompatibility or gap;
- the level of normativity at which reform is required;
- and the possible remedial or reform pathway.

---

## Stage 5. Output production

Depending on the use case, the protocol may support outputs such as:

- legal diagnostic notes;
- comparative tables;
- legislative reform briefs;
- advocacy documents;
- structured argument sets for litigation support;
- institutional review notes;
- rapid compatibility checklists;
- coding-ready analytical summaries.

### Output discipline

All outputs should:

- distinguish diagnosis from recommendation;
- identify uncertainty where present;
- avoid overstating legal certainty;
- remain faithful to the repository’s terminology rules;
- and clearly distinguish between:
  - primary legal sources,
  - authoritative interpretation,
  - persuasive interpretive guidance,
  - and analytical inference.

---

## Structured output for future coding and quantitative use

Where useful, the analysis should also produce a structured summary in a coding-ready format.

This is not a substitute for full legal analysis. It is an additional layer designed to support later comparative, quantitative, or mixed-method work.

### Minimum coding fields

Where feasible, record findings in a structured way using fields such as:

- `jurisdiction`
- `subnational_level`
- `domestic_legal_instrument`
- `legal_instrument_type`
- `date_of_version_analysed`
- `international_legal_instrument`
- `article_or_standard_engaged`
- `type_of_gap`
- `gap_severity`
- `rights_holder_group`
- `subgroup_affected`
- `actor_responsible`
- `private_actor_included` (yes/no/uncertain)
- `enforceability_level`
- `budgetary_pathway_present` (yes/no/uncertain)
- `monitoring_mechanism_present` (yes/no/uncertain)
- `participation_mechanism_present` (yes/no/uncertain)
- `gender_dimension_present` (yes/no/partial)
- `intersectional_dimension_present` (yes/no/partial)
- `cultural_or_linguistic_dimension_present` (yes/no/partial)
- `language_model` (rights-based / assistentialist / mixed)
- `overall_normative_alignment` (high / medium / low / indeterminate)
- `notes_on_uncertainty`

### Rule for coding-ready outputs

Only code what is supportable from the analysed text and cited interpretive materials.  
Do **not** infer absent content as present.  
Do **not** convert qualitative uncertainty into false precision.

---

## Adaptation to other countries or domains

The protocol is modular.

To extend it to other jurisdictions or policy domains, the analyst should incorporate:

- a country-specific legal hierarchy module;
- the relevant domestic review or compatibility framework;
- the institutional enforcement context;
- the relevant international legal instruments;
- corresponding key-articles files where available;
- and any domain-specific case-law notes.

The current repository documents a **Mexico–Switzerland disability-rights pilot**, but the protocol is designed for future extension to broader rights and governance domains.

---

## Methodological cautions

1. Legal analysis must never be reduced to textual coincidence alone.  
2. Normative silence must be treated as analytically relevant.  
3. Primary legal sources should always be prioritised.  
4. Diagnosis and reform proposal should remain analytically distinct.  
5. Interpretive materials should not be treated as interchangeable. Distinguish treaty text, case law, General Comments, concluding observations, and guidance documents.  
6. Do not infer full legal compatibility merely because a domestic legal instrument mentions the relevant right.  
7. Do not infer implementation merely because a duty is declared in statutory text.  
8. Where the text is incomplete, outdated, or uncertain, say so explicitly rather than filling the gap by assumption.  
9. Use structured outputs to support later comparison, not to replace interpretive judgement.  
10. Quantification must remain subordinate to legal interpretation, not the reverse.  
11. In multilevel systems, competence location is part of the legal analysis, not a secondary administrative detail.

---

## Operational summary for AI use

When using this protocol, proceed in the following order:

1. identify and verify the domestic legal instrument;
2. determine the jurisdictional route and level of normativity;
3. determine the relevant country module and, where applicable, subnational protocol;
4. analyse structural design;
5. identify omissions, exclusions, and subgroup-specific barriers;
6. determine the applicable international standard;
7. assess normative alignment and legal compatibility;
8. classify the type of gap;
9. translate the finding into structured legal argument where required;
10. produce an output appropriate to the intended forum;
11. where useful, produce a coding-ready structured summary for later comparative analysis.

Do not skip structural analysis.  
Do not skip exclusion analysis.  
Do not skip compatibility analysis where an international legal instrument is relevant.  
Do not collapse diagnosis into advocacy without first identifying the legal basis.
