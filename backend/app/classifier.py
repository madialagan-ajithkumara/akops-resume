"""
Local ML career-category classifier. TF-IDF + Logistic Regression.

No external AI API calls, no tokens, no per-request cost. The model is
tiny (fits in memory in <1 second) and is trained once at process
startup from skills_data.CAREER_SKILLS.

Continuous learning (in-memory only): add_feedback() lets the app fold a
user-confirmed correction ("this resume's skills should have matched X
category") into the training set and retrain immediately, live, while
the process is running. This is genuine online learning -- predictions
really do improve within the server's lifetime -- but nothing is written
to disk, so it resets whenever the process restarts (e.g. Render's free
tier spinning down after ~15 min idle, or a redeploy). That's an
intentional tradeoff: it keeps the zero-storage / zero-cost privacy
promise ("we never store your CV") -- feedback only ever carries the
already-detected skill keywords and the category the user picked, never
resume text or personal info.

If you obtain a real labeled resume CSV (e.g. Kaggle's
"UpdatedResumeDataSet.csv" with columns Category,Resume), call
train_from_csv(path) instead of train_from_taxonomy() to train on real
resume text -- everything else in the app stays the same.
"""
import random
import threading

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .skills_data import CAREER_SKILLS

_RNG = random.Random(42)


def _synthetic_documents(category: str, core: list[str], next_skills: list[str], n_docs: int = 70) -> list[str]:
    """
    Build n_docs synthetic 'resume skill sections' for a category by sampling
    varying subsets of its core (and occasionally adjacent 'next') skills.
    This gives the TF-IDF/LogReg classifier enough varied examples per class
    to learn robust term weights, without needing a scraped dataset.
    """
    docs = []
    pool_core = core[:]
    for _ in range(n_docs):
        k = _RNG.randint(max(3, len(pool_core) // 2), len(pool_core))
        sampled = _RNG.sample(pool_core, k)
        if next_skills and _RNG.random() < 0.4:
            sampled += _RNG.sample(next_skills, min(2, len(next_skills)))
        _RNG.shuffle(sampled)
        # repeat a couple of the most defining (first two core) skills to mimic
        # how real resumes restate their primary stack in summary + skills section
        doc = " ".join(sampled) + " " + " ".join(core[:2])
        docs.append(doc)
    return docs


class CareerClassifier:
    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None
        self.model: LogisticRegression | None = None
        self.classes_: list[str] = []
        self._texts: list[str] = []
        self._labels: list[str] = []
        self._feedback_count = 0
        self._train_lock = threading.Lock()

    def train_from_taxonomy(self):
        texts, labels = [], []
        for category, data in CAREER_SKILLS.items():
            for doc in _synthetic_documents(category, data["core"], data["next"]):
                texts.append(doc)
                labels.append(category)
        with self._train_lock:
            self._texts, self._labels = texts, labels
            self._fit()
        return self

    def train_from_csv(self, path: str, text_col: str = "Resume", label_col: str = "Category"):
        """Optional: train on a real dataset (e.g. Kaggle UpdatedResumeDataSet.csv)."""
        import csv as _csv

        texts, labels = [], []
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = _csv.DictReader(f)
            for row in reader:
                if row.get(text_col) and row.get(label_col):
                    texts.append(row[text_col])
                    labels.append(row[label_col])

        with self._train_lock:
            self._texts, self._labels = texts, labels
            self._fit(max_features=20000, stop_words="english")
        return self

    def _fit(self, **vectorizer_kwargs):
        """Rebuild vectorizer + model from self._texts/_labels. Caller must hold _train_lock."""
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True, **vectorizer_kwargs)
        X = self.vectorizer.fit_transform(self._texts)
        self.model = LogisticRegression(max_iter=2000)
        self.model.fit(X, self._labels)
        self.classes_ = list(self.model.classes_)

    def add_feedback(self, skills_text: str, correct_category: str):
        """
        Fold one user-confirmed (skills -> correct category) example into the
        live training set and retrain immediately. skills_text should be the
        already-detected skill keywords joined by spaces (analyzer.py's
        detected_skills), NOT raw resume text -- keeps this feature aligned
        with the "we never store your CV" promise, and matches the
        distribution the model is trained on (see analyzer.build_career_matches
        for why that distribution match matters).
        """
        if not skills_text or not skills_text.strip():
            raise ValueError("No skills provided.")
        if correct_category not in CAREER_SKILLS:
            raise ValueError(f"Unknown category: {correct_category}")
        with self._train_lock:
            self._texts.append(skills_text.strip())
            self._labels.append(correct_category)
            self._feedback_count += 1
            self._fit()

    def feedback_count(self) -> int:
        return self._feedback_count

    def predict_top_k(self, text: str, k: int = 3) -> list[tuple[str, float]]:
        if not self.model or not self.vectorizer:
            raise RuntimeError("Classifier not trained yet")
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        ranked = sorted(zip(self.classes_, probs), key=lambda x: x[1], reverse=True)
        return ranked[:k]


# Singleton, trained once when the module is imported (fast: <1s, no I/O, no network).
career_classifier = CareerClassifier().train_from_taxonomy()
