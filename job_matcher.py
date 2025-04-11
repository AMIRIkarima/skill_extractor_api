import easyocr
import spacy
import re
from typing import List, Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from collections import Counter


class SkillMatcher:
    def __init__(self, mongo_uri: str, db_name: str = "job_offers", gpu: bool = False):
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Check Atlas connection
        except ConnectionFailure:
            raise ConnectionError("❌ Could not connect to MongoDB Atlas. Check your URI and network.")

        self.db = self.client[db_name]
        self.reader = easyocr.Reader(['en'], gpu=gpu)
        self.nlp = spacy.load("en_core_web_sm")

        self.common_words = {
            "experience", "skills", "resume", "education", "work",
            "summary", "years", "email", "phone", "github", "linkedin"
        }

    def extract_text(self, image_path: str) -> str:
        try:
            results = self.reader.readtext(image_path, detail=0)
            return " ".join(results)
        except Exception as e:
            raise ValueError(f"OCR failed: {str(e)}")

    def extract_candidate_skills(self, text: str) -> List[str]:
        text = re.sub(r'[^a-zA-Z0-9\s\-]', '', text.lower())
        doc = self.nlp(text)

        candidates = set()
        for chunk in doc.noun_chunks:
            if 3 <= len(chunk.text) <= 50:
                candidates.add(chunk.text.title())

        for ent in doc.ents:
            if ent.label_ in ["ORG", "TECH"] and 3 <= len(ent.text) <= 50:
                candidates.add(ent.text.title())

        return [s for s in candidates if s.lower() not in self.common_words]

    def get_job_offers(self, collection: str = "offers", limit: int = 10) -> List[Dict]:
        pipeline = [
            {"$project": {
                "title": 1,
                "skills": {"$ifNull": ["$skills", []]},
                "normalized_skills": {
                    "$map": {
                        "input": {"$ifNull": ["$skills", []]},
                        "as": "skill",
                        "in": {"$toLower": "$$skill"}
                    }
                }
            }},
            {"$limit": limit}
        ]
        return list(self.db[collection].aggregate(pipeline))

    def calculate_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        resume_skills_lower = [s.lower() for s in resume_skills]
        job_skills_lower = [s.lower() for s in job_skills]

        matches = set(resume_skills_lower) & set(job_skills_lower)
        match_score = len(matches) / max(len(set(job_skills_lower)), 1)

        skill_counts = Counter(resume_skills_lower + job_skills_lower)
        weighted_score = sum(
            1 / skill_counts[s] for s in matches
        ) / max(len(set(job_skills_lower)), 1)

        return {
            "match_score": round(match_score, 2),
            "weighted_score": round(weighted_score, 2),
            "matches": list(matches),
            "missing_skills": list(set(job_skills_lower) - matches),
            "resume_skills": resume_skills,
            "job_skills": job_skills
        }

    def process_resume(self, image_path: str) -> Dict:
        text = self.extract_text(image_path)
        skills = self.extract_candidate_skills(text)
        offers = self.get_job_offers()

        results = []
        for offer in offers:
            match_result = self.calculate_match(skills, offer.get("normalized_skills", []))
            results.append({
                "job_id": str(offer["_id"]),
                "job_title": offer["title"],
                **match_result
            })

        results.sort(key=lambda x: x["weighted_score"], reverse=True)

        return {
            "resume_skills": skills,
            "matching_results": results,
            "extracted_text": text
        }
