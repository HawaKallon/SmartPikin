# Exam Simulator — Implementation Plan

## What We're Building

A **National Exam Simulator** that replicates the real NPSE, BECE, and WASSCE exam experience. Students select their exam type and subject, then sit a timed exam with the correct number of questions, question types (objectives + theory), and time limits that mirror the actual national exams. After completing, they get a detailed performance breakdown with AI-generated feedback on what to improve.

This replaces the current Quiz Mode as the primary assessment tool on the platform.

---

## Exam Structures

### NPSE (Primary 6 — transition to JSS)
| Subject | Format | Questions | Time |
|---------|--------|-----------|------|
| Language Arts (English) | Objectives (MCQ) | 40 questions | 45 min |
| Mathematics | Objectives (MCQ) | 40 questions | 45 min |
| General Paper | Objectives (MCQ) | 40 questions | 45 min |
| Quantitative Aptitude | Objectives (MCQ) | 40 questions | 45 min |
| Verbal Aptitude | Objectives (MCQ) | 40 questions | 45 min |

*NPSE is objectives-only. No theory.*

### BECE (JSS 3 — transition to SSS)
| Subject | Paper 1 (Objectives) | Paper 2 (Theory) | Total Time |
|---------|---------------------|-------------------|------------|
| English Language | 50 MCQs — 1 hr | 4-5 essay questions — 1.5 hrs | 2.5 hrs |
| Mathematics | 50 MCQs — 1 hr | 6-8 structured questions — 1.5 hrs | 2.5 hrs |
| Integrated Science | 40 MCQs — 45 min | 5-6 structured questions — 1.5 hrs | ~2.25 hrs |
| Social Studies | 40 MCQs — 45 min | 4-5 essay questions — 1.5 hrs | ~2.25 hrs |
| French / Arabic | 40 MCQs — 45 min | Essay + comprehension — 1 hr | ~1.75 hrs |

*BECE has both objectives and theory for every subject.*

### WASSCE (SSS 3 — final secondary exam)
| Subject | Paper 1 (Objectives) | Paper 2 (Theory) | Paper 3 (Practical/Alt) | Total Time |
|---------|---------------------|-------------------|------------------------|------------|
| English Language | 80 MCQs — 1 hr | Essay + Comprehension — 2 hrs | Oral (skip) | 3 hrs |
| Mathematics | 50 MCQs — 1.5 hrs | Theory (Section A + B) — 2.5 hrs | — | 4 hrs |
| Biology | 50 MCQs — 50 min | Theory — 1.5 hrs | Practical Alt — 1.5 hrs | ~4 hrs |
| Chemistry | 50 MCQs — 1 hr | Theory — 2 hrs | Practical Alt — 2 hrs | ~5 hrs |
| Physics | 50 MCQs — 1 hr | Theory — 2 hrs | Practical Alt — 2 hrs | ~5 hrs |
| Economics | 50 MCQs — 1 hr | Essay — 2 hrs | — | 3 hrs |
| Government | 50 MCQs — 1 hr | Essay — 2.5 hrs | — | 3.5 hrs |
| Literature | — | Essay — 2.5 hrs | — | 2.5 hrs |

*WASSCE is the most complex with multiple papers per subject.*

---

## User Flow

```
1. Student opens Exam Simulator
2. Selects exam type: NPSE / BECE / WASSCE
3. Selects subject (list filters based on exam type)
4. Selects paper: "Objectives Only" / "Theory Only" / "Full Exam" (both)
5. Sees exam info card: number of questions, time limit, instructions
6. Clicks "Start Exam" → timer begins

OBJECTIVES SECTION:
- Questions appear one at a time (or all at once — student chooses)
- 4 options per MCQ (A, B, C, D)
- Student can flag questions to review later
- Timer counts down in the header
- Can navigate between questions freely

THEORY SECTION:
- Questions appear one at a time
- Large text area for each answer
- Can include sub-questions (a, b, c)
- Timer continues

COMPLETION:
- Auto-submits when timer expires OR student clicks "Submit Exam"
- Objectives: instant grading (correct/incorrect)
- Theory: AI grades against marking scheme, gives score per question
- Overall score, grade, and percentage
- Performance breakdown by topic/concept area
- AI-generated feedback: "You struggled with X, Y. Focus on these areas..."
- Option to review each question with correct answers shown
```

---

## Data Model

### New Models

```python
# Exam configuration — stores the structure of each exam
class ExamConfig(models.Model):
    exam_type = models.CharField(max_length=10)     # NPSE, BECE, WASSCE
    subject = models.CharField(max_length=100)       # Mathematics, English, etc.
    paper_type = models.CharField(max_length=20)     # objectives, theory, practical
    num_questions = models.PositiveIntegerField()     # 40, 50, 80 etc.
    time_minutes = models.PositiveIntegerField()      # 45, 60, 90 etc.
    instructions = models.TextField()                 # Exam-specific instructions

# Individual exam questions (for real past questions added later)
class ExamQuestion(models.Model):
    exam_config = models.ForeignKey(ExamConfig, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=10)  # mcq, theory
    question_text = models.TextField()
    options = models.JSONField(null=True)             # MCQ: ["A...", "B...", "C...", "D..."]
    correct_answer = models.CharField(max_length=5)   # MCQ: "A"/"B"/"C"/"D"
    marking_scheme = models.TextField(blank=True)     # Theory: what earns marks
    marks = models.PositiveIntegerField(default=1)
    topic = models.CharField(max_length=255)          # For performance breakdown
    year = models.PositiveIntegerField(null=True)     # Which year's exam (optional)
    source = models.CharField(max_length=20)          # "past_paper" or "ai_generated"

# A student's exam attempt
class ExamSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam_config = models.ForeignKey(ExamConfig, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    questions_data = models.JSONField()   # The questions served (AI-generated or from DB)
    answers_data = models.JSONField()     # Student's answers
    score = models.FloatField(null=True)
    total_marks = models.FloatField(null=True)
    percentage = models.FloatField(null=True)
    grade = models.CharField(max_length=5, null=True)  # A1, B2, C4, etc.
    feedback = models.TextField(null=True)              # AI-generated feedback
    topic_breakdown = models.JSONField(null=True)       # {"Algebra": 80, "Geometry": 40}

# Track student performance over time (aggregated)
class StudentPerformance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)
    total_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0)
    weak_topics = models.JSONField(default=list)    # ["Algebra", "Trigonometry"]
    strong_topics = models.JSONField(default=list)
    last_attempt = models.DateTimeField(null=True)
```

---

## How Questions Are Generated (Hybrid Approach)

### V1 — AI-Generated (Launch)
The AI generates exam-style questions on-the-fly:
1. System prompt includes the exact exam format, WAEC standards, marking style
2. For MCQs: generates question + 4 options + correct answer + topic tag
3. For theory: generates question + marking scheme + model answer + topic tag
4. Questions are stored in `ExamQuestion` with `source="ai_generated"` after generation
5. Each student gets a unique set (AI generates fresh for each session)

### V2 — Real Past Papers (Later)
When we source actual past questions:
1. Upload via admin or a management command
2. Stored in `ExamQuestion` with `source="past_paper"` and `year`
3. System mixes real + AI-generated to ensure variety
4. Real questions are prioritized, AI fills gaps

---

## Grading System

### Objectives (MCQ)
- Automatic: compare answer to correct_answer
- 1 mark per question, no negative marking (matches WAEC style)

### Theory
- Student submits text answer
- AI grades against the marking scheme:
  - Checks for key points mentioned
  - Assigns marks per point (e.g., 2/5 marks)
  - Provides feedback on what was missed
- We show: marks earned, marks available, model answer

### WAEC Grading Scale (for WASSCE)
| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| A1 | 75-100% | Excellent |
| B2 | 70-74% | Very Good |
| B3 | 65-69% | Good |
| C4 | 60-64% | Credit |
| C5 | 55-59% | Credit |
| C6 | 50-54% | Credit |
| D7 | 45-49% | Pass |
| E8 | 40-44% | Pass |
| F9 | 0-39% | Fail |

---

## Feedback System

After each exam, the student sees:

### 1. Score Summary
- Total score, percentage, WAEC grade
- Comparison to pass mark
- Time used vs time allowed

### 2. Topic Breakdown (Visual)
- Bar chart or list showing score per topic area
- Color-coded: green (strong), yellow (okay), red (weak)
- Example: "Algebra: 90% | Geometry: 60% | Statistics: 30%"

### 3. AI Study Recommendations
The AI analyzes the wrong answers and generates:
- "You consistently missed questions about [topic]. This suggests..."
- "Focus your next study session on [specific concepts]"
- "Try these SmartPikin tools: [links to relevant lesson plans, flashcards]"

### 4. Question Review
- Student can review every question
- Shows: their answer, correct answer, explanation
- Theory: shows model answer + where they lost marks

---

## Pages / Routes

| Route | Page | Description |
|-------|------|-------------|
| `/ai_core/exam/` | Exam Selector | Choose exam type, subject, paper |
| `/ai_core/exam/start/` | Exam Session (POST) | Generates and starts the exam |
| `/ai_core/exam/session/<id>/` | Exam In Progress | The actual exam interface |
| `/ai_core/exam/session/<id>/submit/` | Submit (POST/AJAX) | Submits answers, triggers grading |
| `/ai_core/exam/session/<id>/results/` | Results & Feedback | Score, breakdown, AI feedback |
| `/ai_core/exam/history/` | Exam History | Past attempts with scores |

---

## Implementation Phases

### Phase 1: Core Exam Engine (Build First)
- [ ] Models: ExamConfig, ExamQuestion, ExamSession
- [ ] Seed ExamConfig for all 3 exams with correct subjects, question counts, times
- [ ] Exam selector page (choose exam → subject → paper type)
- [ ] AI question generation (objectives MCQs)
- [ ] Timed exam interface with question navigation
- [ ] Auto-grading for MCQs
- [ ] Basic results page with score + correct answers

### Phase 2: Theory Support + Feedback
- [ ] Theory question generation with marking schemes
- [ ] Text area answers for theory
- [ ] AI grading for theory answers
- [ ] Topic-based performance breakdown
- [ ] AI-generated study recommendations
- [ ] Question review page

### Phase 3: Performance Tracking
- [ ] StudentPerformance model — aggregate stats over time
- [ ] Exam history page (past attempts)
- [ ] "Weak areas" tracking across multiple attempts
- [ ] Suggestions that improve as the student takes more exams

### Phase 4: Past Paper Integration (Future)
- [ ] Admin interface or management command to upload real questions
- [ ] Mix real + AI questions in exam sessions
- [ ] Year-based filtering ("Try the 2023 WASSCE Math paper")

---

## What Happens to Current Quiz Mode?

The current Quiz Mode (`/ai_core/quiz/`) stays as a **quick practice tool** — lightweight, topic-based, no timer pressure. The Exam Simulator is the serious, structured assessment tool. They serve different purposes:

- **Quiz Mode** = casual practice, any topic, 5-15 questions, instant fun
- **Exam Simulator** = structured exam prep, full subject, timed, graded, feedback

---

## Technical Notes

- AI model: `llama-3.3-70b-versatile` via Groq (consistent with rest of platform)
- Questions generated as JSON for easy parsing
- Timer is client-side (JavaScript) with server-side validation
- Exam state saved via AJAX as student progresses (no lost work on disconnect)
- Theory grading uses a separate AI call with the marking scheme as context
- All questions tagged with `topic` field for breakdown analysis
