"""
BattingEdge V9.6 - Production-Ready Biomechanical Analysis
Fixed: Removed binary metric dependencies, widened professional tolerances
Kept: Smooth scoring interpolation, sophisticated percentile approach
"""

import numpy as np
from typing import Dict, List, Tuple

class ShotRules:
    """
    Production-grade shot analysis with robust scoring
    - No binary metric dependencies (wrist_above_elbow, etc.)
    - Widened tolerances for professional variation
    - Smooth interpolation scoring preserved
    - Graceful handling of missing metrics
    """
    
    PERFORMANCE_BANDS = {
        (85, 100): ("Elite", "Professional-level execution!"),
        (70, 84): ("Advanced", "Strong technique with minor refinements."),
        (55, 69): ("Intermediate", "Solid foundation, work on consistency."),
        (40, 54): ("Developing", "Building the right habits."),
        (0, 39): ("Learning", "Focus on fundamentals, one step at a time.")
    }
    
    @staticmethod
    def get_performance_description(score: int) -> Tuple[str, str]:
        """Convert score to description"""
        for (min_s, max_s), (level, desc) in ShotRules.PERFORMANCE_BANDS.items():
            if min_s <= score <= max_s:
                return level, desc
        return "Developing", "Keep practicing!"

    @staticmethod
    def get_grade(score: int) -> str:
        """Map numeric score to letter grade (A+/A/B+/B/C+/C/D/F)"""
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 75: return "B+"
        if score >= 65: return "B"
        if score >= 60: return "C+"
        if score >= 50: return "C"
        if score >= 40: return "D"
        return "F"
    
    @staticmethod
    def get_shot_standards(shot_type: str) -> Dict:
        """
        Returns CALIBRATED standards with WIDENED professional tolerances
        
        Changes from V9.5:
        - Removed all binary metrics (wrist_position, head_position)
        - Widened 'Excellent' ranges by ~20% for camera angle variation
        - Redistributed weights to reliable angle measurements
        - Added fallback for missing metrics
        """
        shot_normalized = shot_type.lower().replace(' shot', '').replace(' ', '_')
        
        # ==========================================
        # COVER DRIVE
        # Dataset: Elbow 116±41°, Head 100±27cm, Bat 90±22°, Hip 90±76°
        # ==========================================
        if 'cover' in shot_normalized or 'drive' in shot_normalized:
            return {
                'elbow_angle': {
                    'excellent': (120, 180),    # Widened from 135 (mean+0.5σ)
                    'good': (90, 155),          
                    'acceptable': (70, 185),    # Very permissive upper
                    'weight': 30,               # Increased from 20
                    'unit': '°',
                    'advice': {
                        'excellent': "Great arm extension through the shot!",
                        'good': "Solid elbow position. Good extension.",
                        'acceptable': "Work on extending your arms through the ball.",
                        'poor': "Focus on full arm extension in drives."
                    }
                },
                'head_drift': {
                    'excellent': (0, 90),       # Widened from 85cm
                    'good': (90, 120),          
                    'acceptable': (120, 150),   
                    'weight': 30,               # Increased from 25
                    'unit': 'cm',
                    'advice': {
                        'excellent': "Excellent head stability! Eyes tracking perfectly.",
                        'good': "Good head control through the shot.",
                        'acceptable': "Keep your head stiller - watch the ball closely.",
                        'poor': "Your head is moving too much. Focus on keeping it steady."
                    }
                },
                'bat_angle': {
                    'excellent': (70, 110),     # Widened from 78-102
                    'good': (60, 120),          
                    'acceptable': (50, 130),    
                    'weight': 25,               # Kept same
                    'unit': '°',
                    'display_transform': lambda x: abs(90 - x),
                    'textbook_range': "0-20° from vertical",
                    'advice': {
                        'excellent': "Perfect bat face presentation!",
                        'good': "Nice straight bat through the line.",
                        'acceptable': "Keep your bat straighter through the shot.",
                        'poor': "Work on presenting the full face of the bat."
                    }
                },
                'hip_rotation': {
                    'excellent': (40, 140),     # Widened due to high variance
                    'good': (15, 170),          
                    'acceptable': (0, 180),     
                    'weight': 15,               
                    'unit': '°',
                    'advice': {
                        'excellent': "Great hip rotation generating power!",
                        'good': "Good use of your core through the shot.",
                        'acceptable': "Try to rotate your hips more through the drive.",
                        'poor': "Engage your hips more for power."
                    }
                }
            }
        
        # ==========================================
        # PULL SHOT
        # Dataset: Elbow 145±40°, Head 73±23cm, Bat 87±29°, Hip 73±58°
        # ==========================================
        elif 'pull' in shot_normalized:
            return {
                'elbow_angle': {
                    'excellent': (115, 180),    # Widened from 125
                    'good': (95, 180),         
                    'acceptable': (75, 180),    
                    'weight': 20,               
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect arm extension for the pull!",
                        'good': "Solid arm position, good leverage.",
                        'acceptable': "Extend your arms more to generate power.",
                        'poor': "Don't cramp yourself - extend those arms!"
                    }
                },
                'hip_rotation': {
                    'excellent': (50, 130),     # CRITICAL for pulls
                    'good': (30, 160),          
                    'acceptable': (10, 180),    
                    'weight': 40,               # HIGHEST weight - this is THE pull shot metric
                    'unit': '°',
                    'advice': {
                        'excellent': "Explosive hip rotation! That's where pull shot power comes from!",
                        'good': "Great hip turn. You're generating good power.",
                        'acceptable': "Rotate your hips more aggressively on pulls.",
                        'poor': "Pull shots need explosive hip rotation - that's the power source!"
                    }
                },
                'bat_angle': {
                    'excellent': (60, 120),     # Widened from 72-102 (more horizontal tolerance)
                    'good': (50, 130),          
                    'acceptable': (30, 150),    
                    'weight': 20,
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect horizontal bat path!",
                        'good': "Nice flat swing through the pull.",
                        'acceptable': "Flatten your bat path a bit more.",
                        'poor': "Keep your bat more horizontal on pulls."
                    }
                },
                'head_drift': {
                    'excellent': (0, 75),       
                    'good': (75, 100),          
                    'acceptable': (100, 130),   
                    'weight': 20,
                    'unit': 'cm',
                    'advice': {
                        'excellent': "Fantastic head position! Eyes locked on the ball.",
                        'good': "Good head control on a difficult shot.",
                        'acceptable': "Keep your head stiller, inside the line of the ball.",
                        'poor': "Don't pull your head away - watch it onto the bat!"
                    }
                }
            }
        
        # ==========================================
        # CUT SHOT
        # Dataset: Elbow 122±48°, Head 81±19cm, Bat 85±16°, Hip 113±57°
        # FIXED: Removed wrist_position dependency
        # ==========================================
        elif 'cut' in shot_normalized:
            return {
                'elbow_angle': {
                    'excellent': (90, 175),     # Widened from 98-166
                    'good': (70, 190),          
                    'acceptable': (50, 190),    
                    'weight': 35,               # Redistributed from removed wrist_position
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect width and extension for the cut! Great hand height too.",
                        'good': "Good arm position, creating space well.",
                        'acceptable': "Try to create more width by moving back and across.",
                        'poor': "You're cramped - move back and across for space."
                    }
                },
                'bat_angle': {
                    'excellent': (70, 100),     # Widened from 77-93
                    'good': (60, 110),          
                    'acceptable': (50, 120),    
                    'weight': 35,               # Increased importance
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect bat angle to guide the ball square!",
                        'good': "Nice angled bat face for the cut.",
                        'acceptable': "Adjust your bat angle to guide it square.",
                        'poor': "Work on angling the bat to cut properly."
                    }
                },
                'head_drift': {
                    'excellent': (0, 80),       # Slightly widened
                    'good': (80, 100),          
                    'acceptable': (100, 130),   
                    'weight': 30,               
                    'unit': 'cm',
                    'advice': {
                        'excellent': "Rock-solid head position for precision!",
                        'good': "Good head stability for a precision shot.",
                        'acceptable': "Keep your head stiller for better accuracy.",
                        'poor': "Head movement reduces accuracy on cuts."
                    }
                }
            }
        
        # ==========================================
        # SWEEP SHOT
        # Dataset: Elbow 143±38°, Knee 154±27°, Bat 86±9°, Hip 96±64°
        # FIXED: Removed head_position binary dependency
        # ==========================================
        elif 'sweep' in shot_normalized:
            return {
                'front_knee': {
                    'excellent': (130, 175),    # Widened from 140-168
                    'good': (110, 185),         
                    'acceptable': (90, 195),    
                    'weight': 30,               # Adjusted
                    'unit': '°',
                    'display_transform': lambda x: 180 - x,
                    'textbook_range': "Low position (bent knee)",
                    'advice': {
                        'excellent': "Perfect low position for the sweep!",
                        'good': "Good knee position, getting down nicely.",
                        'acceptable': "Try to get down lower on the sweep.",
                        'poor': "Sweep needs a lower position - bend that front knee!"
                    }
                },
                'bat_angle': {
                    'excellent': (75, 105),     # Widened from 81-91 (tight tolerance relaxed)
                    'good': (65, 115),          
                    'acceptable': (55, 125),    
                    'weight': 40,               # Increased - most critical for sweep
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect horizontal bat! Sweeping beautifully.",
                        'good': "Nice flat bat through the sweep.",
                        'acceptable': "Keep your bat more horizontal.",
                        'poor': "Bat must be horizontal for sweeps."
                    }
                },
                'hip_rotation': {
                    'excellent': (50, 140),     # Widened
                    'good': (30, 160),          
                    'acceptable': (0, 180),     
                    'weight': 20,               
                    'unit': '°',
                    'advice': {
                        'excellent': "Great hip rotation through the sweep!",
                        'good': "Good use of your core.",
                        'acceptable': "Rotate your hips more through the shot.",
                        'poor': "Engage your hips for more power."
                    }
                },
                'head_drift': {
                    'excellent': (0, 100),      # NEW: Replaces head_position binary
                    'good': (100, 125),         
                    'acceptable': (125, 150),   
                    'weight': 10,               # Lower weight (head_position was 25)
                    'unit': 'cm',
                    'advice': {
                        'excellent': "Perfect head position - right over the ball!",
                        'good': "Good head placement over the ball.",
                        'acceptable': "Get your head more over the ball.",
                        'poor': "Head MUST be over the ball to avoid top edges!"
                    }
                }
            }
        
        # ==========================================
        # DEFENSE
        # Dataset: Elbow 137±25°, Knee 160±26°, Bat 85±10°, Hip 87±55°
        # ==========================================
        elif 'defense' in shot_normalized or 'defence' in shot_normalized:
            return {
                'elbow_angle': {
                    'excellent': (120, 170),    # Slightly widened
                    'good': (100, 180),         
                    'acceptable': (90, 185),    
                    'weight': 25,
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect soft hands with ideal flex!",
                        'good': "Good relaxed arms for defense.",
                        'acceptable': "Relax your arms slightly for softer hands.",
                        'poor': "Defense needs soft, slightly bent arms."
                    }
                },
                'bat_angle': {
                    'excellent': (75, 105),     # Widened from 80-90 (tight tolerance)
                    'good': (65, 115),          
                    'acceptable': (60, 120),    
                    'weight': 35,               
                    'unit': '°',
                    'display_transform': lambda x: abs(90 - x),
                    'textbook_range': "0-15° from vertical",
                    'advice': {
                        'excellent': "Perfect vertical bat! Textbook defense.",
                        'good': "Nice straight bat for defense.",
                        'acceptable': "Keep your bat more vertical.",
                        'poor': "Defense requires a perfectly straight bat!"
                    }
                },
                'head_drift': {
                    'excellent': (0, 90),       # Widened from 0-83
                    'good': (90, 115),          
                    'acceptable': (115, 140),   
                    'weight': 25,
                    'unit': 'cm',
                    'advice': {
                        'excellent': "Excellent head position over the ball!",
                        'good': "Good forward press with head over ball.",
                        'acceptable': "Get your head more over the ball.",
                        'poor': "Head must be over the ball in defense!"
                    }
                },
                'front_knee': {
                    'excellent': (140, 180),    # Widened
                    'good': (120, 185),         
                    'acceptable': (100, 195),   
                    'weight': 15,
                    'unit': '°',
                    'advice': {
                        'excellent': "Perfect stride forward!",
                        'good': "Good balanced stride.",
                        'acceptable': "Work on your stride length.",
                        'poor': "Stride forward more to get to the pitch."
                    }
                }
            }
        
        return {}
    
    @staticmethod
    def calculate_metric_score(value: float, standard: Dict) -> Tuple[int, str, str]:
        """
        Calculate score with smooth interpolation (PRESERVED from V9.5)
        This sophisticated scoring prevents harsh score cliffs
        """
        e_min, e_max = standard['excellent']
        g_min, g_max = standard['good']
        a_min, a_max = standard['acceptable']
        advice = standard.get('advice', {})
        
        # 1. EXCELLENT (90-100)
        if e_min <= value <= e_max:
            center = (e_min + e_max) / 2
            distance_from_center = abs(value - center)
            range_size = (e_max - e_min) / 2
            score = 100 - int((distance_from_center / range_size) * 10)
            return max(90, score), "Excellent", advice.get('excellent', "Perfect!")
        
        # 2. GOOD (75-89)
        elif g_min <= value <= g_max:
            if value < e_min:
                distance = e_min - value
                range_size = e_min - g_min if e_min > g_min else 1
                score = 90 - int((distance / range_size) * 15)
            else:
                distance = value - e_max
                range_size = g_max - e_max if g_max > e_max else 1
                score = 90 - int((distance / range_size) * 15)
            return max(75, min(89, score)), "Good", advice.get('good', "Solid!")
        
        # 3. ACCEPTABLE (55-74)
        elif a_min <= value <= a_max:
            if value < g_min:
                distance = g_min - value
                range_size = g_min - a_min if g_min > a_min else 1
                score = 75 - int((distance / range_size) * 20)
            else:
                distance = value - g_max
                range_size = a_max - g_max if a_max > g_max else 1
                score = 75 - int((distance / range_size) * 20)
            return max(55, min(74, score)), "Acceptable", advice.get('acceptable', "Workable.")
        
        # 4. POOR (30-54)
        else:
            if value < a_min:
                distance = a_min - value
                range_size = a_max - a_min if a_max > a_min else 1
                score = 55 - int((distance / range_size) * 25)
            else:
                distance = value - a_max
                range_size = a_max - a_min if a_max > a_min else 1
                score = 55 - int((distance / range_size) * 25)
            return max(30, min(54, score)), "Needs Work", advice.get('poor', "Focus here.")
    
    @staticmethod
    def analyze_shot(metrics: Dict, shot_type: str) -> Dict:
        """
        Main analysis function with graceful handling of missing metrics
        """
        standards = ShotRules.get_shot_standards(shot_type)
        
        if not standards:
            return {
                'overall_score': 65,
                'performance_level': "Unknown Shot",
                'summary': "This shot type is not in our analysis library yet.",
                'strengths': ["Keep practicing!"],
                'key_improvements': [],
                'checks': [],
                'recommended_drills': []
            }
        
        weighted_scores = []
        total_weight = 0
        checks = []
        strengths = []
        improvements = []
        
        for metric_name, standard in standards.items():
            # Graceful handling: skip if metric doesn't exist
            if metric_name not in metrics:
                continue
            
            raw_value = metrics.get(metric_name, 0)
            
            # Skip zero angles (likely detection failure) EXCEPT head_drift
            if raw_value == 0 and metric_name != 'head_drift':
                continue
            
            weight = standard['weight']
            total_weight += weight
            
            # Calculate score with smooth interpolation
            score_pct, status, advice = ShotRules.calculate_metric_score(raw_value, standard)
            weighted_scores.append(score_pct * (weight / 100))
            
            # Display transformation (if any)
            transform = standard.get('display_transform', lambda x: x)
            display_val = transform(raw_value)
            
            unit = standard.get('unit', '')
            value_display = f"{display_val:.1f}{unit}"
            
            ideal_range = standard.get('textbook_range', 
                                      f"{standard['excellent'][0]}-{standard['excellent'][1]}{unit}")
            
            checks.append({
                'name': metric_name.replace('_', ' ').title(),
                'value': value_display,
                'ideal_range': ideal_range,
                'status': status,
                'score_pct': score_pct,
                'advice': advice,
                'is_error': score_pct < 60
            })
            
            # Categorize
            if score_pct >= 80:
                strengths.append(advice)
            elif score_pct < 65:
                improvements.append(advice)
        
        # Normalize score if we evaluated fewer metrics than expected
        if total_weight > 0:
            # Calculate as percentage of evaluated weight
            overall_score = int((sum(weighted_scores) / total_weight) * 100)
        else:
            overall_score = 65  # Fallback
        
        performance_level, level_desc = ShotRules.get_performance_description(overall_score)
        
        # Generate summary
        if overall_score >= 85:
            summary = f"Outstanding {shot_type}! {level_desc}"
        elif overall_score >= 70:
            summary = f"Strong {shot_type}. {level_desc}"
        elif overall_score >= 55:
            summary = f"Decent {shot_type}. {level_desc}"
        else:
            summary = f"{shot_type} needs work. {level_desc}"
        
        # Get drills
        drills = ShotRules.get_recommended_drills(shot_type, improvements)
        
        return {
            'overall_score': overall_score,
            'performance_level': performance_level,
            'level': performance_level,
            'grade': ShotRules.get_grade(overall_score),
            'summary': summary,
            'strengths': strengths[:3] if strengths else ["You're on the right track!"],
            'key_improvements': improvements[:3] if improvements else ["Keep practicing consistently!"],
            'checks': checks,
            'recommended_drills': drills
        }
    
    @staticmethod
    def get_recommended_drills(shot_type: str, improvements: List[str]) -> List[Dict]:
        """Shot-specific drills based on ECB coaching"""
        shot_norm = shot_type.lower()
        
        drills = {
            'cover': [
                {'name': 'Wall Drive Reps', 'description': 'Stand 2ft from wall. Drive focusing on head toward wall, high elbow. 30x3 sets.'},
                {'name': 'Front Elbow Drill', 'description': 'Partner feeds underarm. Focus on high front elbow. 25x3 sets.'},
                {'name': 'Balance Hold', 'description': 'Hold finish for 3sec. Check weight forward, back foot on toes. 20x3 sets.'}
            ],
            'pull': [
                {'name': 'Hip Explosion Drill', 'description': 'Focus on explosive hip turn - hips finish facing square leg. 30x3 sets.'},
                {'name': 'Pivot Anchor', 'description': 'Back foot stays down (pivot not jump). 25x3 sets.'},
                {'name': 'Head Inside Line', 'description': 'Keep eyes on ball, head inside line. 20x3 sets.'}
            ],
            'cut': [
                {'name': 'Back-Across Footwork', 'description': 'Shadow: 3 steps back, 1 across. 40x2 sets.'},
                {'name': 'High Hands Focus', 'description': 'Cut suspended ball, hands above shoulders, wrists above elbows. 25x3 sets.'},
                {'name': 'Zone Targeting', 'description': 'Hit to point, gully, backward point zones. 30 balls.'}
            ],
            'sweep': [
                {'name': 'Knee Position Reps', 'description': 'Get down on front knee, hold 3sec. 30x2 sets.'},
                {'name': 'Head Over Ball', 'description': 'Sweep with nose above contact point. 25x3 sets.'},
                {'name': 'Weight Forward', 'description': '80% weight on front leg. Partner checks stability. 20x3 sets.'}
            ],
            'defense': [
                {'name': 'Pad-Bat Defense', 'description': 'Bat touches pad. Soft hands, vertical bat, ball drops dead. 25x3 sets.'},
                {'name': 'No Backlift', 'description': 'Start at address, defend with no lift. 20x3 sets.'},
                {'name': 'Forward Press', 'description': 'Small movement forward before each ball. 20x3 sets.'}
            ]
        }
        
        for key in drills:
            if key in shot_norm:
                return drills[key]
        
        return [{'name': 'Shadow Practice', 'description': 'Slow-motion reps focusing on form. 50 daily.'}]
    
    @staticmethod
    def grade_shot(metrics: Dict, shot_type: str) -> Dict:
        """Backward compatibility wrapper"""
        result = ShotRules.analyze_shot(metrics, shot_type)
        return {
            'score': result['overall_score'],
            'overall_score': result['overall_score'],
            'level': result['performance_level'],
            'grade': result['grade'],
            'strengths': result['strengths'],
            'errors': result['key_improvements'],
            'key_improvements': result['key_improvements'],
            'feedback': result['key_improvements'],
            'detailed_breakdown': result['checks'],
            'summary': result['summary'],
            'recommended_drills': result['recommended_drills']
        }