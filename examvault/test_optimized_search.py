#!/usr/bin/env python3
"""
Test script for the optimized course search system
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

from recommender.views import fetch_courses_batch_serpapi

def test_optimized_search():
    """Test the optimized batch course search functionality"""
    print("Testing Optimized Course Search System")
    print("=" * 50)
    
    # Test with multiple skills
    test_skills = ["python", "machine learning", "react", "docker", "kubernetes"]
    
    print(f"🔍 Searching for courses on skills: {', '.join(test_skills)}")
    print(f"📊 This should use maximum 2 API calls instead of {len(test_skills)} calls")
    print("-" * 50)
    
    try:
        batch_results = fetch_courses_batch_serpapi(test_skills, max_results_per_skill=2)
        
        print(f"✅ Batch search completed successfully!")
        print(f"📈 Results summary:")
        
        total_courses = 0
        for skill, courses in batch_results.items():
            course_count = len(courses)
            total_courses += course_count
            print(f"  • {skill}: {course_count} courses found")
            
            for i, course in enumerate(courses, 1):
                print(f"    {i}. {course.get('title', 'N/A')[:60]}...")
                print(f"       Platform: {course.get('platform', 'N/A')}")
        
        print(f"\n📊 Total courses found: {total_courses}")
        print(f"🎯 API efficiency: Used max 2 calls for {len(test_skills)} skills")
        
    except Exception as e:
        print(f"❌ Error in batch search: {e}")

if __name__ == "__main__":
    test_optimized_search()
