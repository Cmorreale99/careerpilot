---
source_file: "2nd brain/career artifacts/raw drive/NeuroCog_LMS_Business_Model_Canvas.docx"
source_sha256: cda4d5621b949b8020d5fb7e77c13242a4a1a2a9ceafd42299c3534652e259e8
converter: mammoth 1.12.0
---

__The Business Model Canvas__

__Designed for: NeuroCog LMS__

Designed by: Cam Morreale / team draft

Date: May 2026

Version: Draft 1

*Based on repository materials for a cognitive\-aware learning recommendation engine that plugs into existing LMS platforms\.*

__Key Partners__

• LMS platforms and standards ecosystem: Moodle, Canvas, Open edX, Blackboard, Sakai, LTI 1\.3\.

• Google Cloud stack: Gemini API for structured analysis and Google Cloud Vision API for handwriting OCR\.

• Schools, workforce programs, career\-transition organizations, and instructional designers as deployment partners\.

• Research and validation partners for cognitive profiling, bias correction, learning outcomes, and model calibration\.

• Human coaches, counselors, or instructors in later phases; not included in the current MVP scope\.

__Key Activities__

• Run a multi\-modal Discovery intake flow: survey, video notes, handwriting upload, audio chat, optional micro\-assessments\.

• Infer cognitive, motivational, linguistic, and asset profiles from triangulated learner signals\.

• Generate 3 explainable path recommendations: Strength\-Leveraging, Growth\-Stretching, Interest\-Aligned\.

• Maintain integrations: LTI 1\.3 tool, Moodle plugin pathway, and headless FastAPI option\.

• Validate scoring weights, profile confidence, bias correction, and recommendation quality using learner outcomes\.

__Value Propositions__

• Converts a generic LMS experience into a personalized learning\-path engine based on how each learner thinks and engages\.

• Profiles 5 cognitive domains: Attention/Working Memory, Executive Functions, Memory, Visuospatial Abilities, Language\.

• Adds motivation and career alignment through CUTRICE and Ikigai, making the system useful for career\-transitioning adults\.

• Uses an asset\-based model: surfaces strengths, skills, experiences, languages, and non\-traditional knowledge instead of only deficits\.

• Integrates with existing LMS platforms rather than forcing institutions to replace their current LMS\.

• Provides explainable recommendations with confidence scores and plain\-language rationale\.

__Customer Relationships__

• Self\-service learner onboarding through the Discovery flow, with immediate profile and path output\.

• Institutional onboarding for LMS administrators, instructors, and workforce\-program operators\.

• Explainability\-first relationship: learners and staff need to understand why a path was recommended\.

• Potential high\-touch pilot model for early institutional customers to validate outcomes and tune scoring assumptions\.

• Later human coach layer can deepen accountability and support, but it is explicitly outside MVP scope\.

__Customer Segments__

• Primary: adult learners and career transitioners who need personalized learning pathways, not one\-size\-fits\-all content\.

• Institutions: colleges, bootcamps, workforce\-development programs, continuing education, and reskilling organizations\.

• LMS administrators and instructors who need better placement, pathing, advising, and learner\-support insight\.

• Moodle\-first organizations are a plausible early beachhead because the repo explicitly names Moodle plugin deployment\.

• Secondary: counselors, coaches, and program managers who need an explainable learner profile to guide support\.

__Key Resources__

• Frontend: Vite \+ React discovery flow, dashboard, radar charts, recommendation cards, premium dark UI\.

• Backend: Python FastAPI services for intake, OCR, cognitive scoring, linguistic analysis, profile building, and path recommendation\.

• AI/data assets: Gemini prompts, Vision OCR pipeline, cognitive\-domain scoring logic, CUTRICE/Ikigai framework, asset inventory schema\.

• Databases: Postgres V1 ERD schema for production direction; SQLite for MVP recommendation engine\.

• Research base: 25\+ synthesized papers across neurocognition, linguistics, asset mapping, motivation, and informal learning\.

__Channels__

• Embedded LTI 1\.3 app inside LMS environments such as Moodle, Canvas, Blackboard, Sakai, or Open edX\.

• Moodle\-native plugin for Moodle\-first deployments and deeper access to Moodle web\-service capabilities\.

• Headless API for custom learning portals, workforce programs, or experimental frontend experiences\.

• Direct pilots with schools, bootcamps, career\-transition programs, workforce nonprofits, and learning\-engineering teams\.

• Developer credibility through GitHub repo, technical architecture, demo, research documentation, and founder/institutional outreach\.

__Cost Structure__

• AI inference costs: Gemini analysis, structured scoring, audio/text processing, and recommendation generation\.

• Cloud OCR and storage: Google Cloud Vision API, file uploads, handwriting images, transcripts, and profile records\.

• Engineering: frontend, FastAPI backend, database schema, integrations, DevOps, security, and testing\.

• Research/validation: outcome studies, bias audits, calibration datasets, scoring\-weight refinement, psychometric review\.

• Go\-to\-market: pilots, implementation support, LMS integration support, documentation, and institutional sales cycle\.

__Revenue Streams__

• B2B SaaS subscription to institutions, priced by active learner, cohort, department, or LMS deployment\. 

• Implementation/setup fee for LTI integration, Moodle plugin configuration, data mapping, and admin training\.

• Pilot package for workforce programs or schools: fixed fee covering Discovery deployment plus outcome reporting\.

• API usage pricing for headless deployments, potentially metered by profiles generated or recommendation calls\.

• Future services: coach/instructor dashboards, validation reports, curriculum alignment, and custom recommendation frameworks\.

• Unvalidated in repo: pricing, buyer willingness to pay, conversion funnel, and procurement path still need market testing\.

Our top competitior Betterup offers human \+ AI hybrid 1:1 coaching for career transitioners, LMS\.AI is strengths based, has neurocognitive profiling, and RL\-based path adaptation\. BetterUP charges upwards of $300 per year per user \(25 a month at the low end\)\. Thus, I am thinking $20/month/user is a good baseline after the pilot stage 

Universities spend an average of $3k to $4\.5k a year on student services and academic counseling \(our $240/yr per student is thus very high ROI and puts us in a great spot to sell to universities directly post pilot\)

*Source basis: GitHub repository t\-siddharth/myLMS, including README\.md, \_workspace/implementation\_plan\.md, \_workspace/research\_analysis\.md, and \_workspace/response\_to\_comments\.md\. Revenue and pricing entries are marked as unvalidated where not specified in the repo\.*
