#!/usr/bin/env python3
"""
📚 ENHANCED ENGLISH CURRICULUM GENERATOR

This creates a comprehensive, progressive English language curriculum 
designed specifically for biological intelligence learning. The curriculum
includes better content quality, logical progression, and comprehensive
coverage of English language fundamentals.

Features:
- Progressive difficulty levels with clear prerequisites
- Comprehensive vocabulary with semantic relationships
- Grammar concepts with practical examples
- Real-world usage patterns and context
- Assessment checkpoints and validation
- Enhanced content depth and quality
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class SkillLevel(Enum):
    """Skill progression levels for English learning"""
    FOUNDATION = "foundation"      # Basic alphabet, phonics
    ELEMENTARY = "elementary"      # Simple words, basic grammar
    INTERMEDIATE = "intermediate"  # Complex sentences, tenses
    ADVANCED = "advanced"         # Nuanced concepts, advanced grammar
    PROFICIENT = "proficient"     # Sophisticated language use


@dataclass
class LessonContent:
    """Structure for individual lesson content"""
    concept: str
    explanation: str
    examples: List[str]
    related_concepts: List[str]
    difficulty_level: SkillLevel
    prerequisite_concepts: List[str]


@dataclass
class CurriculumLevel:
    """Structure for curriculum level organization"""
    level_name: str
    level_number: int
    skill_level: SkillLevel
    description: str
    lessons: List[LessonContent]
    learning_objectives: List[str]


class EnhancedEnglishCurriculum:
    """Enhanced curriculum generator for comprehensive English learning"""
    
    def __init__(self):
        self.curriculum_levels: List[CurriculumLevel] = []
        self._build_comprehensive_curriculum()
    
    def _build_comprehensive_curriculum(self):
        """Build the complete enhanced curriculum"""
        
        # Level 1: Foundation - Alphabet and Phonics
        level_1 = CurriculumLevel(
            level_name="Foundation Alphabet & Phonics",
            level_number=1,
            skill_level=SkillLevel.FOUNDATION,
            description="Master the English alphabet, letter sounds, and basic phonetic patterns",
            learning_objectives=[
                "Recognize all 26 letters in uppercase and lowercase",
                "Understand vowel and consonant distinctions",
                "Master basic phonetic sounds and combinations",
                "Identify common letter patterns and digraphs"
            ],
            lessons=self._create_foundation_lessons()
        )
        
        # Level 2: Elementary Vocabulary
        level_2 = CurriculumLevel(
            level_name="Elementary Vocabulary & Word Types",
            level_number=2,
            skill_level=SkillLevel.ELEMENTARY,
            description="Build essential vocabulary with proper word classifications",
            learning_objectives=[
                "Learn 200+ essential English words",
                "Understand nouns, verbs, adjectives, and adverbs",
                "Master articles and pronouns",
                "Recognize word relationships and synonyms"
            ],
            lessons=self._create_elementary_vocabulary_lessons()
        )
        
        # Level 3: Intermediate Grammar Structures
        level_3 = CurriculumLevel(
            level_name="Intermediate Grammar & Sentence Structure", 
            level_number=3,
            skill_level=SkillLevel.INTERMEDIATE,
            description="Master sentence construction and fundamental grammar rules",
            learning_objectives=[
                "Construct complete sentences with proper structure",
                "Use present, past, and future tenses correctly",
                "Form questions and negations properly",
                "Understand subject-verb agreement"
            ],
            lessons=self._create_intermediate_grammar_lessons()
        )
        
        # Level 4: Advanced Communication
        level_4 = CurriculumLevel(
            level_name="Advanced Communication & Complex Structures",
            level_number=4, 
            skill_level=SkillLevel.ADVANCED,
            description="Develop sophisticated communication skills and complex grammar",
            learning_objectives=[
                "Use complex sentence structures with conjunctions",
                "Master conditional sentences and modal verbs",
                "Understand passive voice and reported speech",
                "Express relationships between ideas clearly"
            ],
            lessons=self._create_advanced_communication_lessons()
        )
        
        # Level 5: Proficient Usage
        level_5 = CurriculumLevel(
            level_name="Proficient Usage & Nuanced Expression",
            level_number=5,
            skill_level=SkillLevel.PROFICIENT,
            description="Achieve nuanced expression and sophisticated language use",
            learning_objectives=[
                "Use idiomatic expressions appropriately",
                "Understand cultural and contextual nuances",
                "Master advanced punctuation and style",
                "Express abstract concepts and emotions"
            ],
            lessons=self._create_proficient_usage_lessons()
        )
        
        self.curriculum_levels = [level_1, level_2, level_3, level_4, level_5]
    
    def _create_foundation_lessons(self) -> List[LessonContent]:
        """Create comprehensive foundation-level lessons"""
        lessons = []
        
        # Alphabet mastery with enhanced content
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            lessons.append(LessonContent(
                concept=f"Letter {letter}",
                explanation=f"The letter {letter} (uppercase) and {letter.lower()} (lowercase) is the {ord(letter) - ord('A') + 1}th letter of the English alphabet.",
                examples=[
                    f"{letter} as in 'Apple'" if letter == 'A' else f"{letter} as in words starting with {letter}",
                    f"Lowercase {letter.lower()} appears in the middle and end of words",
                    f"The letter {letter} can make different sounds depending on context"
                ],
                related_concepts=["alphabet", "uppercase", "lowercase", "phonics"],
                difficulty_level=SkillLevel.FOUNDATION,
                prerequisite_concepts=[]
            ))
        
        # Enhanced vowel concepts
        lessons.append(LessonContent(
            concept="Vowels",
            explanation="Vowels are the letters A, E, I, O, U, and sometimes Y. They form the core sounds of syllables and are essential for pronunciation.",
            examples=[
                "A: sounds like 'ay' in 'day', 'ah' in 'cat', or 'aw' in 'ball'",
                "E: sounds like 'ee' in 'see', 'eh' in 'bed', or silent in 'make'",
                "I: sounds like 'eye' in 'pie', 'ih' in 'sit', or 'ee' in 'machine'",
                "O: sounds like 'oh' in 'go', 'aw' in 'hot', or 'oo' in 'move'",
                "U: sounds like 'you' in 'use', 'uh' in 'cup', or 'oo' in 'rule'",
                "Y: sounds like 'ee' in 'happy' or 'eye' in 'my'"
            ],
            related_concepts=["consonants", "syllables", "pronunciation", "phonics"],
            difficulty_level=SkillLevel.FOUNDATION,
            prerequisite_concepts=["alphabet"]
        ))
        
        # Consonants with enhanced explanations
        lessons.append(LessonContent(
            concept="Consonants",
            explanation="Consonants are all the letters that are not vowels: B, C, D, F, G, H, J, K, L, M, N, P, Q, R, S, T, V, W, X, Z. They provide structure and clarity to words.",
            examples=[
                "B makes a 'buh' sound as in 'ball' and 'cab'",
                "C can sound like 'k' in 'cat' or 's' in 'city'",
                "G can sound hard as in 'go' or soft as in 'giant'",
                "Consonants often combine with vowels to form syllables"
            ],
            related_concepts=["vowels", "syllables", "phonics", "word_formation"],
            difficulty_level=SkillLevel.FOUNDATION,
            prerequisite_concepts=["vowels"]
        ))
        
        # Digraphs and letter combinations
        digraphs = [
            ("th", "think, this, with", "Can be voiced (this) or unvoiced (think)"),
            ("ch", "chair, cheese, much", "Makes the sound /tʃ/ as in church"),
            ("sh", "ship, fish, wash", "Makes the sound /ʃ/ as in shoe"),
            ("wh", "where, what, which", "Often pronounced as 'w' sound"),
            ("ph", "phone, graph, photo", "Makes the 'f' sound in English")
        ]
        
        for digraph, examples, note in digraphs:
            lessons.append(LessonContent(
                concept=f"Digraph {digraph.upper()}",
                explanation=f"The combination '{digraph}' creates a distinct sound different from the individual letters. {note}",
                examples=examples.split(", "),
                related_concepts=["phonics", "pronunciation", "spelling_patterns"],
                difficulty_level=SkillLevel.FOUNDATION,
                prerequisite_concepts=["consonants", "vowels"]
            ))
        
        return lessons
    
    def _create_elementary_vocabulary_lessons(self) -> List[LessonContent]:
        """Create comprehensive elementary vocabulary lessons"""
        lessons = []
        
        # Enhanced word categories with semantic relationships
        word_categories = {
            "Animals": {
                "words": ["cat", "dog", "bird", "fish", "horse", "cow", "pig", "chicken", "sheep", "goat"],
                "concept": "Animals are living creatures that move, eat, and breathe. They can be domestic (pets/farm) or wild.",
                "relationships": ["domestic_animals", "farm_animals", "pets", "wildlife"]
            },
            "Family": {
                "words": ["mother", "father", "sister", "brother", "grandmother", "grandfather", "aunt", "uncle", "cousin", "family"],
                "concept": "Family members are people related by blood, marriage, or adoption who form a household unit.",
                "relationships": ["relationships", "generations", "household", "kinship"]
            },
            "Colors": {
                "words": ["red", "blue", "green", "yellow", "orange", "purple", "black", "white", "brown", "pink"],
                "concept": "Colors are visual properties of objects that we perceive through light reflection.",
                "relationships": ["visual_properties", "description", "adjectives", "appearance"]
            },
            "Numbers": {
                "words": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
                "concept": "Numbers represent quantities and are essential for counting, measuring, and mathematics.",
                "relationships": ["quantity", "counting", "mathematics", "measurement"]
            },
            "Body_Parts": {
                "words": ["head", "eye", "ear", "nose", "mouth", "hand", "arm", "leg", "foot", "body"],
                "concept": "Body parts are the physical components that make up the human body and enable us to function.",
                "relationships": ["anatomy", "physical_self", "health", "movement"]
            },
            "Actions": {
                "words": ["run", "walk", "jump", "eat", "drink", "sleep", "play", "work", "read", "write"],
                "concept": "Action words (verbs) describe what people, animals, or things do or what happens to them.",
                "relationships": ["verbs", "movement", "activities", "behavior"]
            }
        }
        
        for category, info in word_categories.items():
            for word in info["words"]:
                lessons.append(LessonContent(
                    concept=f"Word: {word}",
                    explanation=f"'{word}' is a {category.lower().replace('_', ' ')} word. {info['concept']}",
                    examples=[
                        f"The word '{word}' belongs to the {category.replace('_', ' ').lower()} category",
                        f"Example sentence: 'I see a {word}'" if category != "Actions" else f"Example sentence: 'I {word} every day'",
                        f"'{word}' relates to: {', '.join(info['relationships'])}"
                    ],
                    related_concepts=info["relationships"] + [category.lower()],
                    difficulty_level=SkillLevel.ELEMENTARY,
                    prerequisite_concepts=["alphabet", "phonics"]
                ))
        
        # Parts of speech with comprehensive explanations
        parts_of_speech = [
            ("Nouns", "Words that name people, places, things, or ideas", ["cat", "house", "love", "teacher"]),
            ("Verbs", "Words that show action or state of being", ["run", "is", "think", "become"]),
            ("Adjectives", "Words that describe or modify nouns", ["big", "red", "happy", "beautiful"]),
            ("Adverbs", "Words that describe verbs, adjectives, or other adverbs", ["quickly", "very", "often", "carefully"]),
            ("Pronouns", "Words that take the place of nouns", ["I", "you", "he", "she", "it", "we", "they"]),
            ("Articles", "Words that introduce nouns", ["a", "an", "the"])
        ]
        
        for pos, explanation, examples in parts_of_speech:
            lessons.append(LessonContent(
                concept=pos,
                explanation=f"{pos} are {explanation.lower()}. They are essential building blocks of sentences.",
                examples=[f"Examples of {pos.lower()}: {', '.join(examples)}", 
                         f"{pos} help us construct meaningful sentences",
                         f"Every sentence needs at least one {pos.lower()[:-1] if pos != 'Articles' else 'article'}"],
                related_concepts=["grammar", "sentence_structure", "parts_of_speech"],
                difficulty_level=SkillLevel.ELEMENTARY,
                prerequisite_concepts=["basic_vocabulary"]
            ))
        
        return lessons
    
    def _create_intermediate_grammar_lessons(self) -> List[LessonContent]:
        """Create comprehensive intermediate grammar lessons"""
        lessons = []
        
        # Sentence structure with detailed explanations
        sentence_concepts = [
            ("Subject-Verb-Object Order", 
             "English sentences typically follow Subject-Verb-Object (SVO) pattern. The subject performs the action, the verb describes the action, and the object receives the action.",
             ["'John (Subject) kicks (Verb) the ball (Object)'", 
              "'She (Subject) reads (Verb) books (Object)'",
              "This pattern helps create clear, understandable sentences"]),
            
            ("Complete Sentences",
             "A complete sentence must have at least a subject and a predicate (verb phrase). This creates a complete thought.",
             ["'Birds fly' - complete with subject and verb",
              "'The dog barks loudly' - subject, verb, and modifier", 
              "Incomplete: 'In the garden' - missing subject and verb"]),
            
            ("Compound Sentences",
             "Compound sentences join two independent clauses with coordinating conjunctions (and, but, or, so, yet, for, nor).",
             ["'I study hard, and I get good grades'",
              "'It was raining, but we went outside'",
              "'You can walk, or you can take the bus'"])
        ]
        
        for concept, explanation, examples in sentence_concepts:
            lessons.append(LessonContent(
                concept=concept,
                explanation=explanation,
                examples=examples,
                related_concepts=["grammar", "sentence_construction", "communication"],
                difficulty_level=SkillLevel.INTERMEDIATE,
                prerequisite_concepts=["nouns", "verbs", "basic_vocabulary"]
            ))
        
        # Comprehensive tense system
        tense_lessons = [
            ("Present Tense", 
             "Present tense describes actions happening now, habitual actions, or general truths.",
             ["'I eat breakfast every morning' (habitual)",
              "'The sun rises in the east' (general truth)",
              "'She is reading now' (present continuous)"]),
            
            ("Past Tense",
             "Past tense describes completed actions or states in the past.",
             ["'I walked to school yesterday' (regular verb + -ed)",
              "'She went home early' (irregular verb form)",
              "'They were happy' (past state of being)"]),
            
            ("Future Tense",
             "Future tense describes actions that will happen later.",
             ["'I will study tonight' (will + base verb)",
              "'She is going to visit her friend' (be going to)",
              "'The train leaves at 3 PM' (present for scheduled future)"])
        ]
        
        for tense, explanation, examples in tense_lessons:
            lessons.append(LessonContent(
                concept=tense,
                explanation=explanation,
                examples=examples,
                related_concepts=["time", "verb_conjugation", "temporal_expression"],
                difficulty_level=SkillLevel.INTERMEDIATE,
                prerequisite_concepts=["verbs", "sentence_structure"]
            ))
        
        return lessons
    
    def _create_advanced_communication_lessons(self) -> List[LessonContent]:
        """Create advanced communication lessons"""
        lessons = []
        
        # Complex sentence structures
        advanced_concepts = [
            ("Complex Sentences",
             "Complex sentences contain an independent clause and one or more dependent clauses, connected by subordinating conjunctions.",
             ["'When I finish work, I will call you' (time clause)",
              "'Because it was raining, we stayed inside' (reason clause)",
              "'The book that you recommended is excellent' (relative clause)"]),
            
            ("Conditional Sentences",
             "Conditional sentences express hypothetical situations and their consequences using 'if' clauses.",
             ["'If it rains, we will stay home' (first conditional - real possibility)",
              "'If I won the lottery, I would travel the world' (second conditional - hypothetical)",
              "'If I had studied harder, I would have passed' (third conditional - past hypothetical)"]),
            
            ("Modal Verbs",
             "Modal verbs express possibility, necessity, ability, permission, and advice.",
             ["'You must wear a seatbelt' (necessity/obligation)",
              "'She can speak three languages' (ability)",
              "'May I help you?' (polite permission/offer)"])
        ]
        
        for concept, explanation, examples in advanced_concepts:
            lessons.append(LessonContent(
                concept=concept,
                explanation=explanation,
                examples=examples,
                related_concepts=["complex_grammar", "nuanced_expression", "formal_language"],
                difficulty_level=SkillLevel.ADVANCED,
                prerequisite_concepts=["sentence_structure", "tenses", "conjunctions"]
            ))
        
        return lessons
    
    def _create_proficient_usage_lessons(self) -> List[LessonContent]:
        """Create proficient usage lessons for sophisticated expression"""
        lessons = []
        
        # Idiomatic and nuanced expression
        proficient_concepts = [
            ("Idiomatic Expressions",
             "Idioms are phrases whose meaning cannot be understood from the individual words. They add natural fluency to communication.",
             ["'Break a leg' means 'good luck' in theater",
              "'It's raining cats and dogs' means 'raining heavily'",
              "'Time flies when you're having fun' means 'enjoyable time passes quickly'"]),
            
            ("Figurative Language",
             "Figurative language uses words beyond their literal meaning to create vivid expressions and deeper understanding.",
             ["'Her voice is music to my ears' (metaphor)",
              "'The wind whispered through the trees' (personification)",
              "'Life is like a journey' (simile)"]),
            
            ("Register and Formality",
             "Register refers to the level of formality in language use, adapting to different social contexts and audiences.",
             ["Formal: 'I would appreciate your assistance'",
              "Informal: 'Can you help me out?'",
              "Academic: 'The data suggests a significant correlation'"])
        ]
        
        for concept, explanation, examples in proficient_concepts:
            lessons.append(LessonContent(
                concept=concept,
                explanation=explanation,
                examples=examples,
                related_concepts=["cultural_context", "advanced_expression", "pragmatics"],
                difficulty_level=SkillLevel.PROFICIENT,
                prerequisite_concepts=["complex_sentences", "vocabulary_range", "cultural_awareness"]
            ))
        
        return lessons
    
    def generate_curriculum_files(self, output_dir: str = "enhanced_english_curriculum"):
        """Generate enhanced curriculum files with comprehensive structure"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate individual level files
        total_lessons = 0
        for level in self.curriculum_levels:
            level_data = {
                "level": f"level_{level.level_number}_{level.level_name.lower().replace(' ', '_').replace('&', 'and')}",
                "level_number": level.level_number,
                "skill_level": level.skill_level.value,
                "description": level.description,
                "learning_objectives": level.learning_objectives,
                "lessons": []
            }
            
            for lesson in level.lessons:
                lesson_text = f"{lesson.explanation} Examples: {' | '.join(lesson.examples)}"
                level_data["lessons"].append(lesson_text)
                total_lessons += 1
            
            filename = f"level_{level.level_number}_{level.level_name.lower().replace(' ', '_').replace('&', 'and')}.json"
            with open(output_path / filename, 'w') as f:
                json.dump(level_data, f, indent=2)
        
        # Generate complete curriculum file
        complete_curriculum = {
            "curriculum_name": "Enhanced English Language Learning",
            "total_levels": len(self.curriculum_levels),
            "total_lessons": total_lessons,
            "skill_progression": [level.skill_level.value for level in self.curriculum_levels],
            "levels": []
        }
        
        for level in self.curriculum_levels:
            complete_curriculum["levels"].append({
                "level_number": level.level_number,
                "level_name": level.level_name,
                "skill_level": level.skill_level.value,
                "lesson_count": len(level.lessons),
                "description": level.description,
                "learning_objectives": level.learning_objectives
            })
        
        with open(output_path / "complete_enhanced_curriculum.json", 'w') as f:
            json.dump(complete_curriculum, f, indent=2)
        
        # Generate learning sequence for optimal training
        learning_sequence = []
        for level in self.curriculum_levels:
            for lesson in level.lessons:
                learning_sequence.append({
                    "level": level.level_number,
                    "skill_level": level.skill_level.value,
                    "concept": lesson.concept,
                    "content": f"{lesson.explanation} Examples: {' | '.join(lesson.examples)}",
                    "prerequisites": lesson.prerequisite_concepts,
                    "related_concepts": lesson.related_concepts,
                    "difficulty": lesson.difficulty_level.value
                })
        
        with open(output_path / "optimal_learning_sequence.json", 'w') as f:
            json.dump({"sequence": learning_sequence}, f, indent=2)
        
        return total_lessons, len(self.curriculum_levels)


if __name__ == "__main__":
    print("📚 ENHANCED ENGLISH CURRICULUM GENERATOR")
    print("=" * 60)
    
    curriculum = EnhancedEnglishCurriculum()
    
    total_lessons, total_levels = curriculum.generate_curriculum_files()
    
    print(f"✅ Generated enhanced English curriculum:")
    print(f"   📖 Levels: {total_levels}")
    print(f"   📝 Total Lessons: {total_lessons}")
    print(f"   🎯 Skill Progression: Foundation → Elementary → Intermediate → Advanced → Proficient")
    print(f"   📁 Output Directory: enhanced_english_curriculum/")
    
    print(f"\n📊 Level Breakdown:")
    for level in curriculum.curriculum_levels:
        print(f"   Level {level.level_number}: {level.level_name} ({len(level.lessons)} lessons)")
    
    print(f"\n🚀 Ready for robust biological intelligence training!")