# PPPD Research Rip — Cached Content Index

A clean, local copy of content ripped from
<https://balanceanddizziness.org> (Balance & Dizziness Canada) about
**Persistent Postural-Perceptual Dizziness (PPPD)** and related
dizziness/balance topics, organized by theme.

Source of truth:
<https://balanceanddizziness.org/disorders/vestibular-disorders/pppd/>

## Structure

- `raw/` — original HTML pages downloaded with curl (41 pages).
- `clean/` — extracted article content converted to Markdown
  (headers, nav, sidebar, footer, sharing widgets, and duplicated
  desktop/mobile navigation removed).
- `extract.py` — the extractor: isolates `<main id="genesis-content">`
  / `<article>`, strips site boilerplate, converts to Markdown.
- `raw/urls.txt` — the fetch list (38 of the 41 pages; the 3 newest were
  fetched directly).
- Summary documents (in `summaries/`):
  - `causes.md`
  - `treatments.md`
  - `personal-experiences.md`

## Clean page inventory

### PPPD core pages

| File | What it is |
|---|---|
| `pppd.md` | Main PPPD page: key points, what PPPD is, causes, symptoms, diagnosis, treatment |
| `balance-system.md` | How the balance system works — vestibular, visual, proprioceptive inputs |
| `visually-induced-dizziness.md` | Visual vertigo / visual dependency — closely linked to PPPD |
| `multifactorial-causes.md` | Multiple overlapping causes of dizziness/imbalance |
| `what-medications-can-contribute-to-dizziness-or-lack-of-balance.md` | Medications that cause dizziness/imbalance |
| `persistent-postural-perceptual-dizziness-article.md` | 2019 announcement article |
| `new-pppd-animation.md` | PPPD animation launch announcement |

### Treatment pages

| File | What it is |
|---|---|
| `what-is-the-treatment-for-pppd.md` | Overview of PPPD treatment approach |
| `vestibular-rehabilitation.md` | Vestibular rehab main page (incl. FAQ) |
| `cawthorne-cooksey-habituation-exercises.md` | Graduated home habituation exercises for dizziness/imbalance |
| `gaining-balance-video.md` | "Gaining Balance" 35-minute home exercise video (downloadable MP4) |
| `medication.md` | Medication for dizziness |
| `cognitive-behavioural-therapy.md` | CBT for dizziness/anxiety |
| `cam-treatments.md` | Complementary & alternative medicine |
| `relaxation-techniques.md` | Relaxation techniques |
| `future-treatments.md` | Emerging treatments (implants, gene therapy, etc.) |
| `relaxation-techniques-reduce-anxiety-caused-by-vestibular-disorders.md` | Relaxation post |
| `good-sleep-habits-can-help-you-cope-with-anxiety.md` | Sleep habits post |

### Personal stories & support

| File | What it is |
|---|---|
| `personal-stories.md` | Index of all personal stories |
| `how-i-cope-with-chronic-dizziness-karens-story.md` | Karen — Ménière's + MAV |
| `chronic-dizziness-and-imbalance-respond-to-physiotherapy.md` | Sara — post-labyrinthitis recovery |
| `face-your-fears-and-risk-getting-better.md` | Shirley — pool therapy after ear surgery |
| `give-physiotherapy-a-try-it-can-make-all-the-difference.md` | Albert — balance exercises at 91 |
| `how-earplugs-and-vestibular-exercises-gave-me-back-my-life.md` | Nickola — Ménière's coping tools |
| `vertigo-changed-this-womans-life-for-the-better.md` | Nancy — vertigo as a life reset |
| `how-a-bc-balance-and-dizziness-meeting-changed-my-life.md` | Wendy — window seat tip |
| `when-dizziness-strikes-an-understanding-employer-can-make-all-the-difference.md` | Andrew — vestibular neuritis, employer accommodation |
| `how-i-cope-with-my-balance-issues-while-walking-two-dogs.md` | Andrea — walking dogs safely |
| `living-with-canvas-syndrome-jays-story.md` | Jay — CANVAS syndrome |
| `living-with-mal-de-debarquement-syndrome-mdds.md` | Brandy — MdDS |
| `living-life-with-episodic-ataxia-type-2-ea-2.md` | David — EA-2 |
| `the-confusing-concussion.md` | Muriel — fall and concussion |
| `fear-came-to-stay-a-poem.md` | Poem — PTSD after car crash |
| `cathy-whites-vestibular-journey-poems-and-paintings.md` | Cathy — poems/paintings, head trauma journey |
| `an-experiment-of-one-n1.md` | Andrea — self-experimentation, keto diet |
| `no-diagnosis-is-all-too-common-for-balance-and-dizziness-sufferers.md` | Diane — undiagnosed symptoms |
| `going-for-a-medical-procedure-ask-for-what-you-need-to-make-you-comfortable.md` | Andrea — MRI accommodations |
| `how-volunteering-helped-one-woman-cope-with-a-debilitating-vestibular-disorder.md` | Joanne — Ménière's support group |
| `never-stop-looking-for-improvement-a-possible-new-treatment-for-balance-issues-a.md` | Jacquie — PoNS device trial |
| `but-you-dont-look-sick.md` | Invisible disability — advice for family/friends |
| `how-im-coping-during-covid-19-lockdown.md` | Andrea — coping during lockdown |

## How the extraction works

1. `raw/urls.txt` lists the pages (extract.py also picks up any `.html`
   in `raw/` that isn't in the list).
2. Raw HTML is saved under `raw/` with curl.
3. `extract.py` parses each file, keeps only the article content,
   removes the repeated site chrome, converts to Markdown in `clean/`.
4. Re-run anytime with: `python3 extract.py`
5. Then verify the whole corpus with `python3 ../check.py` — it catches
   broken links, missing clean/raw pairs, and inventory drift.
