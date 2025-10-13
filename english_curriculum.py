#!/usr/bin/env python3
"""
📚 ENGLISH LANGUAGE CURRICULUM FOR BIOLOGICAL INTELLIGENCE
Progressive curriculum to teach English from fundamentals to fluency.

This curriculum follows natural language acquisition:
1. Phonetics & Alphabet
2. Basic Words & Vocabulary
3. Grammar Structures
4. Sentence Formation
5. Semantic Understanding
6. Complex Language Use
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
import random


class EnglishCurriculum:
    """
    Structured English curriculum for biological intelligence learning.
    """
    
    def __init__(self):
        self.curriculum_path = Path("./english_curriculum")
        self.curriculum_path.mkdir(exist_ok=True)
        
    def generate_level_1_alphabet(self) -> List[str]:
        """Level 1: The English alphabet and basic phonetics."""
        lessons = []
        
        # Individual letters
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in alphabet:
            lessons.append(f"The letter {letter} (uppercase) and {letter.lower()} (lowercase) is part of the English alphabet.")
        
        # Vowels and consonants
        lessons.append("The vowels in English are: A, E, I, O, U, and sometimes Y.")
        lessons.append("The consonants are all other letters: B, C, D, F, G, H, J, K, L, M, N, P, Q, R, S, T, V, W, X, Z.")
        
        # Basic phonetics
        phonetic_examples = [
            "A sounds like 'ay' in 'day' or 'ah' in 'cat'.",
            "E sounds like 'ee' in 'see' or 'eh' in 'bed'.",
            "I sounds like 'eye' or 'ih' in 'sit'.",
            "O sounds like 'oh' in 'go' or 'aw' in 'hot'.",
            "U sounds like 'you' or 'uh' in 'cup'."
        ]
        lessons.extend(phonetic_examples)
        
        # Letter combinations
        lessons.append("Letters combine to form digraphs like 'th', 'ch', 'sh', 'wh', 'ph'.")
        lessons.append("The combination 'th' makes the sound in 'think' or 'this'.")
        lessons.append("The combination 'ch' makes the sound in 'chair' or 'cheese'.")
        lessons.append("The combination 'sh' makes the sound in 'ship' or 'fish'.")
        
        return lessons
    
    def generate_level_2_basic_words(self) -> List[str]:
        """Level 2: Basic vocabulary and word formation."""
        lessons = []
        
        # Articles
        lessons.append("'A' and 'an' are indefinite articles. 'A' is used before consonant sounds, 'an' before vowel sounds.")
        lessons.append("'The' is the definite article, referring to specific things.")
        
        # Common nouns
        basic_nouns = [
            ("cat", "a small domestic animal with fur"),
            ("dog", "a loyal domestic animal that barks"),
            ("house", "a building where people live"),
            ("tree", "a tall plant with a trunk and branches"),
            ("water", "a clear liquid essential for life"),
            ("sun", "the star that gives Earth light and heat"),
            ("food", "what people and animals eat"),
            ("book", "pages with writing bound together"),
            ("car", "a vehicle with four wheels for transportation"),
            ("person", "a human being")
        ]
        
        for word, definition in basic_nouns:
            lessons.append(f"The word '{word}' is a noun meaning {definition}.")
        
        # Common verbs
        basic_verbs = [
            ("run", "move quickly on feet"),
            ("walk", "move at regular pace on feet"),
            ("eat", "consume food"),
            ("sleep", "rest with eyes closed"),
            ("think", "use the mind to consider"),
            ("see", "perceive with eyes"),
            ("hear", "perceive with ears"),
            ("speak", "produce words with voice"),
            ("write", "form letters or words on surface"),
            ("read", "look at and understand written words")
        ]
        
        for word, definition in basic_verbs:
            lessons.append(f"The word '{word}' is a verb meaning to {definition}.")
        
        # Common adjectives
        basic_adjectives = [
            ("big", "large in size"),
            ("small", "little in size"),
            ("hot", "having high temperature"),
            ("cold", "having low temperature"),
            ("happy", "feeling joy"),
            ("sad", "feeling sorrow"),
            ("fast", "moving quickly"),
            ("slow", "moving without speed"),
            ("good", "positive quality"),
            ("bad", "negative quality")
        ]
        
        for word, definition in basic_adjectives:
            lessons.append(f"The word '{word}' is an adjective meaning {definition}.")
        
        # Pronouns
        lessons.append("Personal pronouns replace nouns: I, you, he, she, it, we, they.")
        lessons.append("'I' refers to the speaker. 'You' refers to the listener.")
        lessons.append("'He' refers to a male. 'She' refers to a female. 'It' refers to things.")
        lessons.append("'We' refers to a group including the speaker. 'They' refers to others.")
        
        return lessons
    
    def generate_level_3_grammar(self) -> List[str]:
        """Level 3: Basic grammar rules and structures."""
        lessons = []
        
        # Sentence structure
        lessons.append("English sentences typically follow Subject-Verb-Object (SVO) order.")
        lessons.append("A complete sentence must have at least a subject and a verb.")
        lessons.append("The subject performs the action. The verb is the action. The object receives the action.")
        
        # Present tense
        lessons.append("Present tense describes actions happening now or regularly.")
        lessons.append("For third person singular (he/she/it), add 's' to the verb: 'He runs.'")
        lessons.append("For I/you/we/they, use the base verb: 'They run.'")
        
        # Past tense
        lessons.append("Past tense describes completed actions.")
        lessons.append("Regular verbs add '-ed': walk → walked, talk → talked.")
        lessons.append("Irregular verbs change form: go → went, see → saw, eat → ate.")
        
        # Future tense
        lessons.append("Future tense uses 'will' + base verb: 'I will go.'")
        lessons.append("'Going to' also expresses future: 'I am going to study.'")
        
        # Plurals
        lessons.append("Add 's' to make most nouns plural: cat → cats, book → books.")
        lessons.append("Nouns ending in s, x, z, ch, sh add 'es': box → boxes, wish → wishes.")
        lessons.append("Some plurals are irregular: child → children, mouse → mice, foot → feet.")
        
        # Questions
        lessons.append("Questions often start with: who, what, where, when, why, how.")
        lessons.append("Yes/no questions use auxiliary verbs: 'Do you like coffee?'")
        lessons.append("Information questions seek specific answers: 'Where do you live?'")
        
        # Negation
        lessons.append("Use 'not' to make sentences negative: 'I do not (don't) understand.'")
        lessons.append("'No' negates nouns: 'I have no money.'")
        
        return lessons
    
    def generate_level_4_sentences(self) -> List[str]:
        """Level 4: Sentence construction and patterns."""
        lessons = []
        
        # Simple sentences
        simple_examples = [
            "The cat sleeps. (Subject + Verb)",
            "Birds fly high. (Subject + Verb + Adverb)",
            "She reads books. (Subject + Verb + Object)",
            "The dog is happy. (Subject + Verb + Adjective)",
            "They are students. (Subject + Verb + Noun)"
        ]
        
        for example in simple_examples:
            lessons.append(f"Simple sentence pattern: {example}")
        
        # Compound sentences
        lessons.append("Compound sentences join two independent clauses with coordinating conjunctions.")
        lessons.append("Coordinating conjunctions: for, and, nor, but, or, yet, so (FANBOYS).")
        compound_examples = [
            "I like coffee, but she prefers tea.",
            "He studied hard, so he passed the exam.",
            "We can go to the park, or we can stay home.",
            "She sings beautifully, and she plays piano."
        ]
        
        for example in compound_examples:
            lessons.append(f"Compound sentence: {example}")
        
        # Complex sentences
        lessons.append("Complex sentences have an independent clause and dependent clause.")
        lessons.append("Subordinating conjunctions: because, although, when, while, if, since, after, before.")
        complex_examples = [
            "I go to school because I want to learn.",
            "Although it rained, we went outside.",
            "When the sun sets, the sky turns orange.",
            "If you study hard, you will succeed."
        ]
        
        for example in complex_examples:
            lessons.append(f"Complex sentence: {example}")
        
        # Common patterns
        patterns = [
            "There is/are pattern: 'There is a book on the table.'",
            "It is pattern: 'It is raining today.'",
            "Question pattern: 'What time is it?'",
            "Imperative pattern: 'Please close the door.'",
            "Exclamatory pattern: 'What a beautiful day!'"
        ]
        lessons.extend(patterns)
        
        return lessons
    
    def generate_level_5_semantics(self) -> List[str]:
        """Level 5: Semantic relationships and meaning."""
        lessons = []
        
        # Synonyms
        lessons.append("Synonyms are words with similar meanings.")
        synonym_pairs = [
            ("happy", "joyful", "glad", "pleased"),
            ("big", "large", "huge", "enormous"),
            ("small", "tiny", "little", "minute"),
            ("fast", "quick", "rapid", "swift"),
            ("smart", "intelligent", "clever", "bright")
        ]
        
        for words in synonym_pairs:
            lessons.append(f"Synonyms: {', '.join(words)} all express similar ideas.")
        
        # Antonyms
        lessons.append("Antonyms are words with opposite meanings.")
        antonym_pairs = [
            ("hot", "cold"),
            ("light", "dark"),
            ("up", "down"),
            ("in", "out"),
            ("love", "hate"),
            ("start", "finish"),
            ("young", "old"),
            ("rich", "poor")
        ]
        
        for word1, word2 in antonym_pairs:
            lessons.append(f"Antonyms: '{word1}' is the opposite of '{word2}'.")
        
        # Homonyms
        lessons.append("Homonyms sound the same but have different meanings.")
        homonym_examples = [
            "to, too, two (direction, also, number)",
            "there, their, they're (location, possession, they are)",
            "right, write (correct, to inscribe)",
            "hear, here (perceive sound, location)",
            "break, brake (damage, stop)"
        ]
        
        for example in homonym_examples:
            lessons.append(f"Homonyms: {example}")
        
        # Collocations
        lessons.append("Collocations are words that naturally go together.")
        collocations = [
            "make a decision (not 'do a decision')",
            "take a photo (not 'make a photo')",
            "heavy rain (not 'strong rain')",
            "strong coffee (not 'powerful coffee')",
            "fast food (not 'quick food')"
        ]
        
        for collocation in collocations:
            lessons.append(f"Natural collocation: {collocation}")
        
        # Idioms
        lessons.append("Idioms are expressions whose meaning isn't literal.")
        idioms = [
            "'Break the ice' means to start a conversation.",
            "'Piece of cake' means something very easy.",
            "'Under the weather' means feeling sick.",
            "'Hit the books' means to study hard.",
            "'Spill the beans' means to reveal a secret."
        ]
        lessons.extend(idioms)
        
        return lessons
    
    def generate_level_6_advanced(self) -> List[str]:
        """Level 6: Advanced language concepts and usage."""
        lessons = []
        
        # Passive voice
        lessons.append("Passive voice emphasizes the action or result rather than the doer.")
        lessons.append("Active: 'The chef cooks the meal.' Passive: 'The meal is cooked by the chef.'")
        lessons.append("Passive formation: be + past participle.")
        
        # Conditional sentences
        lessons.append("Zero conditional (general truths): If water reaches 100°C, it boils.")
        lessons.append("First conditional (real possibility): If it rains, I will stay home.")
        lessons.append("Second conditional (hypothetical): If I were rich, I would travel.")
        lessons.append("Third conditional (past hypothetical): If I had studied, I would have passed.")
        
        # Perfect tenses
        lessons.append("Present perfect connects past to present: 'I have lived here for 5 years.'")
        lessons.append("Past perfect shows earlier past: 'I had eaten before he arrived.'")
        lessons.append("Future perfect shows completion before future point: 'I will have finished by noon.'")
        
        # Reported speech
        lessons.append("Direct speech: He said, 'I am happy.'")
        lessons.append("Reported speech: He said that he was happy.")
        lessons.append("Tense shifts back in reported speech: present → past, will → would.")
        
        # Modal verbs
        lessons.append("Modal verbs express possibility, permission, ability, obligation.")
        modals = [
            "Can/Could: ability or possibility",
            "May/Might: permission or possibility",
            "Must: strong obligation or certainty",
            "Should: advice or recommendation",
            "Would: hypothetical or polite requests"
        ]
        
        for modal in modals:
            lessons.append(f"Modal verb - {modal}")
        
        # Register and style
        lessons.append("Formal register: 'I would be grateful if you could assist me.'")
        lessons.append("Informal register: 'Can you help me out?'")
        lessons.append("Academic style uses passive voice and formal vocabulary.")
        lessons.append("Conversational style uses contractions and phrasal verbs.")
        
        # Discourse markers
        lessons.append("Discourse markers organize ideas: firstly, secondly, however, therefore, moreover.")
        lessons.append("Addition: furthermore, additionally, moreover, besides.")
        lessons.append("Contrast: however, nevertheless, on the other hand, whereas.")
        lessons.append("Cause/Effect: therefore, consequently, as a result, thus.")
        lessons.append("Conclusion: in conclusion, to sum up, overall, finally.")
        
        return lessons
    
    def generate_full_curriculum(self) -> Dict[str, List[str]]:
        """Generate the complete curriculum organized by levels."""
        curriculum = {
            "level_1_alphabet": self.generate_level_1_alphabet(),
            "level_2_words": self.generate_level_2_basic_words(),
            "level_3_grammar": self.generate_level_3_grammar(),
            "level_4_sentences": self.generate_level_4_sentences(),
            "level_5_semantics": self.generate_level_5_semantics(),
            "level_6_advanced": self.generate_level_6_advanced()
        }
        
        return curriculum
    
    def save_curriculum(self):
        """Save the curriculum to JSON files for feeding."""
        curriculum = self.generate_full_curriculum()
        
        # Save each level separately
        for level_name, lessons in curriculum.items():
            filepath = self.curriculum_path / f"{level_name}.json"
            with open(filepath, 'w') as f:
                json.dump({"level": level_name, "lessons": lessons}, f, indent=2)
            print(f"✅ Saved {len(lessons)} lessons to {filepath}")
        
        # Save complete curriculum
        complete_path = self.curriculum_path / "complete_curriculum.json"
        with open(complete_path, 'w') as f:
            json.dump(curriculum, f, indent=2)
        print(f"✅ Saved complete curriculum to {complete_path}")
        
        # Save learning order
        order = [
            "level_1_alphabet",
            "level_2_words",
            "level_3_grammar",
            "level_4_sentences",
            "level_5_semantics",
            "level_6_advanced"
        ]
        order_path = self.curriculum_path / "learning_order.json"
        with open(order_path, 'w') as f:
            json.dump({"order": order, "total_lessons": sum(len(curriculum[l]) for l in order)}, f, indent=2)
        
        total = sum(len(lessons) for lessons in curriculum.values())
        print(f"\n📚 Total curriculum: {total} lessons across 6 levels")
        
        return curriculum
    
    def generate_practice_texts(self) -> List[str]:
        """Generate practice texts for comprehension testing."""
        texts = [
            # Simple texts
            "The sun is bright today. Birds sing in the trees. Children play in the park.",
            "I have a cat. My cat is black and white. She likes to sleep on my bed.",
            "Water is important for life. We need to drink water every day. Plants also need water to grow.",
            
            # Medium complexity
            "Learning a new language takes time and practice. Every day, students study new words and grammar rules. With patience, they improve their skills.",
            "The library is a quiet place where people read books and study. Many students go there to do homework. Librarians help people find information.",
            
            # Complex texts
            "Although technology has transformed how we communicate, face-to-face conversation remains irreplaceable. Digital messages lack the nuance of tone and body language that enrich human interaction.",
            "Scientific research has demonstrated that regular exercise not only improves physical health but also enhances cognitive function and emotional well-being. These benefits accumulate over time.",
            
            # Various topics
            "Cooking involves combining ingredients using different techniques. Heat transforms raw materials into delicious meals. Recipes guide cooks through each step.",
            "Music expresses emotions without words. Different instruments create unique sounds. When combined in harmony, they produce beautiful compositions.",
            "The seasons change throughout the year. Spring brings new growth, summer provides warmth, autumn displays colors, and winter offers rest."
        ]
        
        return texts


def main():
    """Generate and save the English curriculum."""
    curriculum = EnglishCurriculum()
    curriculum.save_curriculum()
    
    # Also generate practice texts
    practice = curriculum.generate_practice_texts()
    practice_path = curriculum.curriculum_path / "practice_texts.json"
    with open(practice_path, 'w') as f:
        json.dump({"practice_texts": practice}, f, indent=2)
    print(f"✅ Saved {len(practice)} practice texts")
    
    print("\n🎓 English curriculum ready for biological intelligence learning!")
    print("\nTo start teaching:")
    print("1. Start the biological service: python biological_service.py")
    print("2. Feed the curriculum: python biological_feeder.py json english_curriculum/level_1_alphabet.json")
    print("3. Observe learning: python biological_observer.py")


if __name__ == "__main__":
    main()