#!/usr/bin/env python3
"""
Test script for the enhanced course recommendation system
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examvault.settings')
django.setup()

from recommender.views import fetch_courses_for_skill, rank_courses_by_similarity

def test_course_search():
    """Test the dynamic course search functionality"""
    print("Testing Enhanced Course Recommendation System")
    print("=" * 50)
    
    # Test skills
    test_skills = ["python", "machine learning", "react", "docker"]
    
    for skill in test_skills:
        print(f"\n🔍 Searching for courses on: {skill}")
        print("-" * 30)
        
        try:
            courses = fetch_courses_for_skill(skill, max_results=2)
            
            if courses:
                print(f"Found {len(courses)} courses:")
                for i, course in enumerate(courses, 1):
                    print(f"{i}. {course.get('title', 'N/A')}")
                    print(f"   Platform: {course.get('platform', 'N/A')}")
                    print(f"   URL: {course.get('url', 'N/A')}")
                    if course.get('description'):
                        print(f"   Description: {course.get('description')[:100]}...")
                    print()
            else:
                print("No courses found.")
                
        except Exception as e:
            print(f"Error searching for {skill}: {e}")
    
    # Test ranking functionality
    print("\n🎯 Testing Course Ranking")
    print("-" * 30)
    
    sample_resume = "I am a software developer with experience in Python, Django, and web development. I want to learn machine learning and data science."
    
    try:
        courses = fetch_courses_for_skill("machine learning", max_results=3)
        if courses:
            ranked_courses = rank_courses_by_similarity(sample_resume, courses)
            print("Courses ranked by relevance to resume:")
            for i, course in enumerate(ranked_courses, 1):
                score = course.get('score', 0)
                print(f"{i}. {course.get('title', 'N/A')} (Score: {score:.3f})")
        else:
            print("No courses to rank.")
    except Exception as e:
        print(f"Error in ranking: {e}")

if __name__ == "__main__":
    test_course_search()
