"""
Structured English Language Learning Test
==========================================
Teaching biological intelligence the basics of English language
Step by step, with validation at each stage
"""

import asyncio
import sys
import json
from typing import List, Dict, Any, Tuple
sys.path.append('.')

from src.biological_trainer import BiologicalTrainer
from src.teacher_evaluator import (
    TeacherEvaluatorSystem,
    KnowledgeType,
    TruthLevel
)


class EnglishTeacher:
    """Structured English language teacher for biological intelligence"""
    
    def __init__(self):
        self.trainer = BiologicalTrainer()
        self.validator = TeacherEvaluatorSystem(biological_trainer=self.trainer)
        self.lessons_taught = []
        self.test_results = []
        
    async def teach_lesson(self, lesson_name: str, teachings: List[Tuple[str, str, str]]):
        """
        Teach a structured lesson
        teachings: List of (concept, truth, explanation)
        """
        print(f"\n📚 LESSON: {lesson_name}")
        print("=" * 60)
        
        success_count = 0
        
        for concept, truth, explanation in teachings:
            # Add ground truth
            self.validator.add_ground_truth(
                concept,
                truth,
                KnowledgeType.FACTUAL,
                "english_grammar"
            )
            
            # Teach the concept
            await self.trainer.train_from_stream([truth])
            
            # Validate learning
            result = await self.validator.teach_and_evaluate(
                f"lesson_{len(self.lessons_taught)}_{concept}",
                truth,
                KnowledgeType.FACTUAL
            )
            
            if result.is_valid:
                print(f"   ✅ Learned: {truth}")
                if explanation:
                    print(f"      → {explanation}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {truth}")
                print(f"      Confidence: {result.confidence:.2f}")
        
        self.lessons_taught.append({
            'lesson': lesson_name,
            'total': len(teachings),
            'learned': success_count
        })
        
        return success_count / len(teachings) if teachings else 0
    
    async def test_understanding(self, test_name: str, questions: List[Tuple[str, List[str]]]):
        """
        Test understanding with questions
        questions: List of (query, expected_concepts)
        """
        print(f"\n🧪 TEST: {test_name}")
        print("=" * 60)
        
        correct_count = 0
        
        for query, expected_concepts in questions:
            print(f"\n   Question: '{query}'")
            
            # Query the knowledge
            results = self.trainer.query_knowledge(query, max_results=5)
            
            # Extract learned concepts
            learned_concepts = [r['content'] for r in results]
            
            # Check if expected concepts are found
            found = []
            for expected in expected_concepts:
                for learned in learned_concepts:
                    if expected.lower() in learned.lower():
                        found.append(expected)
                        break
            
            if found:
                print(f"   ✅ Found: {', '.join(found)}")
                correct_count += 1
            else:
                print(f"   ❌ Expected: {', '.join(expected_concepts)}")
                if learned_concepts:
                    print(f"      Got: {learned_concepts[0][:50]}...")
            
            # Show top results
            for i, result in enumerate(results[:2], 1):
                print(f"      {i}. {result['content'][:60]}... (rel: {result['relevance']:.2f})")
        
        accuracy = correct_count / len(questions) if questions else 0
        self.test_results.append({
            'test': test_name,
            'accuracy': accuracy,
            'correct': correct_count,
            'total': len(questions)
        })
        
        return accuracy
    
    def show_progress(self):
        """Display learning progress"""
        print("\n📊 LEARNING PROGRESS")
        print("=" * 60)
        
        # Lessons summary
        print("\nLessons Taught:")
        for lesson in self.lessons_taught:
            success_rate = lesson['learned'] / lesson['total'] * 100
            print(f"   • {lesson['lesson']}: {lesson['learned']}/{lesson['total']} ({success_rate:.0f}%)")
        
        # Test results
        if self.test_results:
            print("\nTest Results:")
            for test in self.test_results:
                print(f"   • {test['test']}: {test['correct']}/{test['total']} ({test['accuracy']*100:.0f}%)")
        
        # Memory stats
        memory_stats = {
            'concepts': len(self.trainer.memory_system.concepts),
            'associations': len(self.trainer.memory_system.associations)
        }
        print(f"\nMemory Statistics:")
        print(f"   • Total concepts: {memory_stats['concepts']}")
        print(f"   • Total associations: {memory_stats['associations']}")
        
        # Validation metrics
        metrics = self.validator.get_metrics()
        print(f"\nValidation Metrics:")
        print(f"   • Hallucination rate: {metrics['hallucination_rate']:.1%}")
        print(f"   • Ground truths: {metrics['ground_truths']}")


async def teach_english_basics():
    """Main structured English teaching program"""
    
    print("=" * 80)
    print("TEACHING ENGLISH LANGUAGE BASICS TO BIOLOGICAL INTELLIGENCE")
    print("Structured, Step-by-Step Learning with Validation")
    print("=" * 80)
    
    teacher = EnglishTeacher()
    
    # LESSON 1: Basic Letters and Vowels
    await teacher.teach_lesson(
        "Lesson 1: Letters and Vowels",
        [
            ("alphabet", "The English alphabet has 26 letters", "Foundation of English"),
            ("vowels", "There are 5 vowels: a, e, i, o, u", "Essential for words"),
            ("consonants", "There are 21 consonants in English", "Complement vowels"),
            ("letter_a", "A is the first letter of the alphabet", "Starting point"),
            ("letter_z", "Z is the last letter of the alphabet", "End point"),
        ]
    )
    
    # TEST 1: Letters understanding
    await teacher.test_understanding(
        "Test 1: Letter Knowledge",
        [
            ("vowels", ["5 vowels", "a, e, i, o, u"]),
            ("alphabet", ["26 letters", "alphabet"]),
            ("consonants", ["21 consonants"]),
        ]
    )
    
    # LESSON 2: Basic Words
    await teacher.teach_lesson(
        "Lesson 2: Basic Words",
        [
            ("cat", "Cat is a three-letter word: c-a-t", "Simple noun"),
            ("dog", "Dog is a three-letter word: d-o-g", "Simple noun"),
            ("the", "The is the most common word in English", "Article"),
            ("i", "I is a pronoun that refers to oneself", "Personal pronoun"),
            ("is", "Is is a form of the verb 'to be'", "Linking verb"),
        ]
    )
    
    # LESSON 3: Word Types (Parts of Speech)
    await teacher.teach_lesson(
        "Lesson 3: Parts of Speech",
        [
            ("noun", "A noun is a person, place, thing, or idea", "Basic POS"),
            ("verb", "A verb is an action word or state of being", "Basic POS"),
            ("adjective", "An adjective describes a noun", "Modifier"),
            ("noun_examples", "Examples of nouns: cat, house, love", "Concrete examples"),
            ("verb_examples", "Examples of verbs: run, jump, think", "Concrete examples"),
        ]
    )
    
    # TEST 2: Word types understanding
    await teacher.test_understanding(
        "Test 2: Parts of Speech",
        [
            ("noun", ["person, place, thing", "noun"]),
            ("verb", ["action word", "verb"]),
            ("cat word type", ["cat", "noun"]),
        ]
    )
    
    # LESSON 4: Simple Sentences
    await teacher.teach_lesson(
        "Lesson 4: Simple Sentences",
        [
            ("sentence", "A sentence expresses a complete thought", "Basic unit"),
            ("subject", "The subject is who or what the sentence is about", "Core component"),
            ("predicate", "The predicate tells what the subject does", "Core component"),
            ("period", "A sentence ends with a period", "Punctuation"),
            ("capital", "A sentence starts with a capital letter", "Grammar rule"),
        ]
    )
    
    # LESSON 5: Sentence Examples
    await teacher.teach_lesson(
        "Lesson 5: Sentence Construction",
        [
            ("simple_sentence", "The cat sits", "Subject + verb"),
            ("sentence_with_object", "The cat sees a mouse", "Subject + verb + object"),
            ("sentence_with_adjective", "The black cat runs fast", "Using modifiers"),
            ("question", "Questions end with a question mark", "Interrogative"),
            ("exclamation", "Exclamations end with an exclamation point", "Emphasis"),
        ]
    )
    
    # TEST 3: Sentence understanding
    await teacher.test_understanding(
        "Test 3: Sentence Structure",
        [
            ("sentence", ["complete thought", "sentence"]),
            ("subject predicate", ["subject", "predicate"]),
            ("punctuation", ["period", "question mark", "exclamation"]),
        ]
    )
    
    # LESSON 6: Common Mistakes (Testing Hallucination Prevention)
    print("\n🚨 LESSON 6: Testing Error Correction")
    print("=" * 60)
    print("Teaching incorrect information to test validation...")
    
    incorrect_teachings = [
        "There are 30 letters in the alphabet",  # Wrong
        "Vowels are x, y, z",  # Wrong
        "A verb is a type of fruit",  # Wrong
        "Sentences don't need punctuation",  # Wrong
    ]
    
    hallucinations_caught = 0
    for wrong_info in incorrect_teachings:
        # Try to teach wrong information
        await teacher.trainer.train_from_stream([wrong_info])
        
        # Validate
        result = await teacher.validator.teach_and_evaluate(
            f"wrong_{hallucinations_caught}",
            wrong_info,
            KnowledgeType.FACTUAL
        )
        
        if result.confidence < 0.5 or not result.is_valid:
            print(f"   ✅ Rejected false: '{wrong_info}'")
            hallucinations_caught += 1
        else:
            print(f"   ⚠️  Accepted false: '{wrong_info}' (confidence: {result.confidence:.2f})")
    
    print(f"\nCaught {hallucinations_caught}/{len(incorrect_teachings)} incorrect statements")
    
    # FINAL TEST: Comprehensive Understanding
    await teacher.test_understanding(
        "Final Test: Comprehensive",
        [
            ("How many letters in English?", ["26 letters"]),
            ("What are vowels?", ["a, e, i, o, u", "5 vowels"]),
            ("What is a noun?", ["person, place, thing"]),
            ("What is a sentence?", ["complete thought"]),
            ("How does a sentence start?", ["capital letter"]),
        ]
    )
    
    # Show final progress
    teacher.show_progress()
    
    # Test creative queries (emergent understanding)
    print("\n🎨 TESTING EMERGENT UNDERSTANDING")
    print("=" * 60)
    print("Queries that weren't directly taught:")
    
    creative_queries = [
        "dog cat noun",
        "letter vowel consonant",
        "sentence subject verb",
        "English grammar rules"
    ]
    
    for query in creative_queries:
        print(f"\n   Query: '{query}'")
        results = teacher.trainer.query_knowledge(query, max_results=3)
        for i, result in enumerate(results, 1):
            relevance = result['relevance']
            content = result['content'][:70]
            print(f"      {i}. {content}... (rel: {relevance:.2f})")
    
    print("\n" + "=" * 80)
    print("ENGLISH TEACHING COMPLETE")
    print("The biological intelligence has learned English basics!")
    print("=" * 80)
    
    return teacher


async def test_specific_concepts():
    """Test specific English concepts in detail"""
    
    print("\n" + "=" * 80)
    print("DETAILED CONCEPT TESTING")
    print("=" * 80)
    
    teacher = EnglishTeacher()
    
    # Teach very specific rules
    specific_rules = [
        ("i_before_e", "I before E except after C", "Spelling rule"),
        ("plural_s", "Add 's' to make most nouns plural", "Grammar rule"),
        ("article_a", "Use 'a' before consonant sounds", "Article rule"),
        ("article_an", "Use 'an' before vowel sounds", "Article rule"),
    ]
    
    print("\nTeaching specific English rules...")
    for concept, rule, explanation in specific_rules:
        teacher.validator.add_ground_truth(concept, rule, KnowledgeType.FACTUAL, "english_rules")
        await teacher.trainer.train_from_stream([rule])
        print(f"   ✅ Taught: {rule}")
    
    # Test retrieval of specific rules
    print("\nTesting specific rule recall...")
    test_queries = [
        ("spelling rule i e", ["I before E except after C"]),
        ("plural nouns", ["Add 's'", "plural"]),
        ("article usage", ["'a' before consonant", "'an' before vowel"]),
    ]
    
    for query, expected in test_queries:
        print(f"\n   Query: '{query}'")
        results = teacher.trainer.query_knowledge(query, max_results=2)
        found = False
        for result in results:
            for exp in expected:
                if exp.lower() in result['content'].lower():
                    print(f"   ✅ Found: {result['content']}")
                    found = True
                    break
        if not found:
            print(f"   ❌ Expected concepts not found")


if __name__ == "__main__":
    print("Starting English Language Teaching Program...\n")
    
    # Run main teaching program
    asyncio.run(teach_english_basics())
    
    # Run specific concept tests
    asyncio.run(test_specific_concepts())