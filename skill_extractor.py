import easyocr
import spacy
import re

class SkillExtractor:
    def __init__(self, gpu=False):
        self.reader = easyocr.Reader(['en'], gpu=gpu)
        self.nlp = spacy.load("en_core_web_sm")
        self.predefined_skills = {
            "Python", "Java", "JavaScript", "HTML", "CSS",
            "React", "SQL", "AWS", "Docker", "Machine Learning"
        }
    
    def extract_text_from_image(self, image_path):
        result = self.reader.readtext(image_path)
        return " ".join([entry[1] for entry in result])
    
    def extract_skills(self, text):
        text = text.lower()
        skills_found = [skill for skill in self.predefined_skills if skill.lower() in text]
        doc = self.nlp(text)
        nouns = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
        return list(set(skills_found + nouns))
    
    def process_resume_image(self, image_path):
        text = self.extract_text_from_image(image_path)
        skills = self.extract_skills(text)
        return skills, text