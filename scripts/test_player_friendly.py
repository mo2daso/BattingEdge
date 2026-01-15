"""
Test the player-friendly enhancements
Compares old vs new scoring to verify improvements

Place in ROOT directory and run: python test_player_friendly.py
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from shot_rules import ShotRules

# ========================================
# TEST CASES: Realistic Player Metrics
# ========================================

test_cases = [
    {
        'name': "Professional Cover Drive",
        'shot': 'Cover Drive',
        'metrics': {
            'elbow_angle': 155,
            'head_drift': 6,
            'hip_rotation': 38,
            'bat_angle': 12,
            'back_lift': 3
        },
        'expected_range': (85, 95),  # Should score Excellent
        'description': "Near-perfect technique from club player"
    },
    {
        'name': "Good Pull Shot",
        'shot': 'Pull',
        'metrics': {
            'elbow_angle': 110,
            'head_drift': 12,
            'hip_rotation': 72,  # Great rotation!
            'bat_angle': 85,
            'back_lift': 6
        },
        'expected_range': (80, 90),  # Should score Excellent
        'description': "Strong hip rotation compensates for slight head drift"
    },
    {
        'name': "Beginner Cut Shot",
        'shot': 'Cut',
        'metrics': {
            'elbow_angle': 95,
            'head_drift': 16,
            'hip_rotation': 25,
            'bat_angle': 42,
            'back_lift': 11,
            'wrist_above_elbow': False  # Key issue
        },
        'expected_range': (55, 70),  # Learning/Developing
        'description': "Beginner making common mistakes"
    },
    {
        'name': "Solid Defense",
        'shot': 'Defense',
        'metrics': {
            'elbow_angle': 125,
            'head_drift': 4,
            'bat_angle': 8,
            'backlift': 12,
            'head_over_ball': True,
            'front_foot_forward': True
        },
        'expected_range': (85, 95),  # Should score Excellent
        'description': "Textbook defensive technique"
    },
    {
        'name': "Acceptable Sweep",
        'shot': 'Sweep',
        'metrics': {
            'front_knee': 95,
            'head_drift': 8,
            'hip_rotation': 48,
            'bat_angle': 88,
            'head_over_ball': True,
            'weight_forward': True
        },
        'expected_range': (75, 85),  # Good
        'description': "Decent sweep with good fundamentals"
    },
    {
        'name': "Poor Pull (Arm Swing)",
        'shot': 'Pull',
        'metrics': {
            'elbow_angle': 135,  # Too straight
            'head_drift': 18,  # Too much
            'hip_rotation': 35,  # Not enough! (CRITICAL)
            'bat_angle': 65,
            'back_lift': 14
        },
        'expected_range': (50, 65),  # Developing/Learning
        'description': "Classic mistake: arm swing instead of hip rotation"
    }
]

# ========================================
# RUN TESTS
# ========================================

def main():
    print("=" * 80)
    print("PLAYER-FRIENDLY SCORING SYSTEM TEST")
    print("=" * 80)
    print("\nValidating that realistic shots score appropriately...")
    print()
    
    results = []
    total_passed = 0
    total_tests = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{total_tests}: {test['name']}")
        print(f"{'='*80}")
        print(f"Shot Type: {test['shot']}")
        print(f"Description: {test['description']}")
        print(f"\nMetrics Provided:")
        for key, value in test['metrics'].items():
            print(f"  • {key}: {value}")
        
        # Analyze with new system
        analysis = ShotRules.analyze_shot(test['metrics'], test['shot'])
        
        score = analysis['overall_score']
        level = analysis['performance_level']
        expected_min, expected_max = test['expected_range']
        
        print(f"\n📊 RESULTS:")
        print(f"  Score: {score}%")
        print(f"  Level: {level}")
        print(f"  Expected Range: {expected_min}-{expected_max}%")
        
        # Check if score is in expected range
        passed = expected_min <= score <= expected_max
        
        if passed:
            print(f"  Status: ✅ PASS (score within expected range)")
            total_passed += 1
        else:
            if score < expected_min:
                print(f"  Status: ❌ FAIL (score too low by {expected_min - score}%)")
            else:
                print(f"  Status: ❌ FAIL (score too high by {score - expected_max}%)")
        
        # Show summary and feedback
        print(f"\n💬 Coach's Feedback:")
        print(f"  \"{analysis['summary']}\"")
        
        if analysis['strengths']:
            print(f"\n✅ Strengths:")
            for strength in analysis['strengths'][:2]:
                print(f"  • {strength[:70]}...")
        
        if analysis['key_improvements']:
            print(f"\n⚡ Areas to Develop:")
            for improvement in analysis['key_improvements'][:2]:
                print(f"  • {improvement[:70]}...")
        
        # Show detailed checks
        print(f"\n📋 Detailed Breakdown:")
        for check in analysis['checks']:
            status_icon = "✓" if check['score_pct'] >= 80 else "○" if check['score_pct'] >= 60 else "◐"
            print(f"  {status_icon} {check['name']:<20s}: {check['value']:<10s} → {check['status']}")
        
        results.append({
            'test': test['name'],
            'score': score,
            'expected': f"{expected_min}-{expected_max}%",
            'passed': passed,
            'level': level
        })
    
    # ========================================
    # SUMMARY
    # ========================================
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"{'Test Name':<35s} {'Score':>8s} {'Expected':>12s} {'Level':>15s} {'Status':>8s}")
    print("-" * 80)
    
    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        print(f"{r['test']:<35s} {r['score']:>7}% {r['expected']:>12s} {r['level']:>15s} {status:>8s}")
    
    print("-" * 80)
    print(f"Total Passed: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.0f}%)")
    print()
    
    # ========================================
    # VALIDATION CHECKS
    # ========================================
    print(f"{'='*80}")
    print("VALIDATION CHECKS")
    print(f"{'='*80}\n")
    
    # Check 1: Professional shots should score well
    pro_scores = [r['score'] for r in results if 'Professional' in r['test'] or 'Solid' in r['test']]
    if pro_scores:
        avg_pro_score = sum(pro_scores) / len(pro_scores)
        print(f"✓ Professional/Solid shots average: {avg_pro_score:.1f}%")
        if avg_pro_score >= 85:
            print(f"  ✅ GOOD: Pro shots score in Excellent range")
        else:
            print(f"  ⚠️  WARNING: Pro shots should average 85%+")
    
    # Check 2: Beginner shots should still score reasonably
    beginner_scores = [r['score'] for r in results if 'Beginner' in r['test'] or 'Poor' in r['test']]
    if beginner_scores:
        avg_beginner_score = sum(beginner_scores) / len(beginner_scores)
        print(f"\n✓ Beginner/Learning shots average: {avg_beginner_score:.1f}%")
        if 50 <= avg_beginner_score <= 65:
            print(f"  ✅ GOOD: Beginner shots score in Learning/Developing range")
        elif avg_beginner_score < 50:
            print(f"  ⚠️  WARNING: Might be too harsh on beginners")
        else:
            print(f"  ⚠️  WARNING: Might be too lenient on poor technique")
    
    # Check 3: Score distribution
    all_scores = [r['score'] for r in results]
    min_score = min(all_scores)
    max_score = max(all_scores)
    avg_score = sum(all_scores) / len(all_scores)
    
    print(f"\n✓ Overall score distribution:")
    print(f"  Min: {min_score}%")
    print(f"  Max: {max_score}%")
    print(f"  Avg: {avg_score:.1f}%")
    
    if 60 <= avg_score <= 80:
        print(f"  ✅ GOOD: Healthy distribution around 70%")
    else:
        print(f"  ⚠️  WARNING: Distribution might need adjustment")
    
    print(f"\n{'='*80}")
    
    if total_passed == total_tests:
        print("✅ ALL TESTS PASSED!")
        print("\nThe player-friendly scoring system is working as intended:")
        print("  • Professional shots score Excellent")
        print("  • Good shots score Good")
        print("  • Beginner shots score Learning/Developing")
        print("  • Feedback is encouraging and actionable")
    else:
        print(f"⚠️  {total_tests - total_passed} test(s) failed")
        print("\nReview the failed tests above and adjust thresholds if needed.")
    
    print(f"{'='*80}\n")
    
    # ========================================
    # RECOMMENDATIONS
    # ========================================
    print("💡 RECOMMENDATIONS:")
    print()
    
    if total_passed == total_tests:
        print("✅ System is ready for deployment!")
        print("   Test with real videos using test_single_video.py")
    else:
        print("⚠️  Fine-tuning needed:")
        print("   1. Review failed test cases above")
        print("   2. Adjust thresholds in shot_rules.py if necessary")
        print("   3. Re-run this test until all pass")
    
    print()

if __name__ == "__main__":
    main()