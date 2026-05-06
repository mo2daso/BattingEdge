"""
BattingEdge V9.8 — Bowling-Context-Aware Biomechanical Analysis

Changes from V9.7:
  - Bowling contexts: fast | spin | unknown only (medium/tape_ball removed)
  - Advice text is now bowling-context-aware for all 5 shots
  - SHOT_BOWLING_CONTEXT compatibility dict added
  - Weight adjustments for uncommon/risky shot-bowling combinations
  - context_note, shot_bowling_compatibility, bowling_context_applied in result
  - calculate_metric_score() accepts bowling_context for advice selection

Sources:
  Alway et al. 2022 ISBS (bowling pace vs batting kinematics)
  Peploe 2019 Loughborough (bat speed, extension, power transfer)
  McErlain-Naylor 2021 (lead-arm extension and bat speed)
  ECB Level 2 Coaching Manual
  MCC Laws / coaching notes
"""

import copy
from typing import Dict, List, Tuple, Optional


class ShotRules:
    """
    Production-grade shot analysis with bowling-context-adjusted thresholds,
    context-aware advice text, and shot-bowling compatibility notes.
    """

    PERFORMANCE_BANDS = {
        (85, 100): ("Elite",        "Professional-level execution!"),
        (70, 84):  ("Advanced",     "Strong technique with minor refinements."),
        (55, 69):  ("Intermediate", "Solid foundation, work on consistency."),
        (40, 54):  ("Developing",   "Building the right habits."),
        (0,  39):  ("Learning",     "Focus on fundamentals, one step at a time.")
    }

    # ------------------------------------------------------------------
    # SHOT-BOWLING COMPATIBILITY
    # (shot_key, bowling_context) → (compatibility, coaching note)
    # compatibility: "primary" | "common" | "uncommon" | "risky"
    # ------------------------------------------------------------------
    SHOT_BOWLING_CONTEXT = {
        ('cover', 'fast'):     ('common',   'Cover drive off full-length fast delivery. Compact swing acceptable.'),
        ('cover', 'spin'):     ('primary',  'Cover drive is a primary spin-hitting option. Full arm extension expected. More front foot movement required.'),
        ('cover', 'unknown'):  ('common',   'Standard cover drive analysis.'),

        ('pull', 'fast'):      ('primary',  'Pull shot is a primary fast bowling response to short-pitched deliveries. Explosive hip rotation is critical.'),
        ('pull', 'spin'):      ('uncommon', 'Pull shot against spin is less common. The ball arrives slower and lower. Contact point is lower than vs pace. A more controlled swing with measured hip rotation is realistic. Full arm extension IS achievable due to extra time.'),
        ('pull', 'unknown'):   ('common',   'Standard pull shot analysis.'),

        ('cut', 'fast'):       ('primary',  'Cut shot is a primary response to short and wide fast deliveries. High hands and quick arm movement critical.'),
        ('cut', 'spin'):       ('common',   'Cut shot against spin is playable but requires patience. Precision over power.'),
        ('cut', 'unknown'):    ('common',   'Standard cut shot analysis.'),

        ('sweep', 'fast'):     ('risky',    'WARNING: Sweep shot against fast bowling carries high risk of top edge. This analysis evaluates your mechanics only. The shot itself is not recommended against pace.'),
        ('sweep', 'spin'):     ('primary',  'Sweep shot is the PRIMARY weapon against spin bowling. This is the most important shot in your spin-playing arsenal. Every metric here is critical.'),
        ('sweep', 'unknown'):  ('common',   'Standard sweep shot analysis.'),

        ('defense', 'fast'):   ('primary',  'Defensive shot against pace. Soft hands, vertical bat, weight forward. Head MUST be over the ball.'),
        ('defense', 'spin'):   ('primary',  'Defensive shot against spin. Pad-bat technique with soft hands. Front foot stride to pitch of ball is essential — longer stride expected against spin.'),
        ('defense', 'unknown'):('common',   'Standard defensive shot analysis.'),
    }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def get_performance_description(score: int) -> Tuple[str, str]:
        for (min_s, max_s), (level, desc) in ShotRules.PERFORMANCE_BANDS.items():
            if min_s <= score <= max_s:
                return level, desc
        return "Developing", "Keep practicing!"

    @staticmethod
    def get_grade(score: int) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 75: return "B+"
        if score >= 65: return "B"
        if score >= 60: return "C+"
        if score >= 50: return "C"
        if score >= 40: return "D"
        return "F"

    @staticmethod
    def _get_shot_key(shot_type: str) -> str:
        """Normalise shot_type to one of: cover | pull | cut | sweep | defense"""
        s = shot_type.lower().replace(' shot', '').replace(' ', '_')
        if 'cover' in s or 'drive' in s: return 'cover'
        if 'pull'  in s:                 return 'pull'
        if 'cut'   in s:                 return 'cut'
        if 'sweep' in s:                 return 'sweep'
        if 'defense' in s or 'defence' in s: return 'defense'
        return 'unknown'

    # ------------------------------------------------------------------
    # THRESHOLD + ADVICE TABLES
    # Bowling contexts: fast | spin | unknown (default)
    # Advice dict has sub-keys: fast | spin | unknown
    # ------------------------------------------------------------------

    @staticmethod
    def get_shot_standards(shot_type: str) -> Dict:
        """
        Returns full metric definitions with per-context threshold tables
        and bowling-context-aware advice text for all 5 shots.
        """
        shot_key = ShotRules._get_shot_key(shot_type)

        # ==================================================================
        # COVER DRIVE
        # Dataset: Elbow 116±41°, Head 100±27 cm, Bat 90±22°, Hip 90±76°
        # Alway 2022: less elbow extension against fast (less time available)
        # ==================================================================
        if shot_key == 'cover':
            return {
                'elbow_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (95,  180), 'good': (80,  180), 'acceptable': (65,  180)},
                        'spin':    {'excellent': (125, 180), 'good': (110, 180), 'acceptable': (90,  180)},
                        'unknown': {'excellent': (120, 180), 'good': (95,  180), 'acceptable': (75,  180)},
                    },
                    'weight': 30,
                    'unit': '°',
                    'research_basis': 'McErlain-Naylor 2021: lead elbow extension key to bat speed',
                    'advice': {
                        'fast': {
                            'excellent': 'Good extension for a pace delivery. Quick through the ball.',
                            'good':      'Solid arm position against pace. Aim for a slightly fuller extension when you can.',
                            'acceptable':'Work on extending through the ball — even against pace, aim for fuller extension at contact.',
                            'poor':      'Too cramped on this drive against pace. Create more room at the crease.',
                        },
                        'spin': {
                            'excellent': 'Perfect full extension — you used the extra time against spin very well.',
                            'good':      'Decent extension but against spin you have more time — drive through to a fuller arm.',
                            'acceptable':'You had time for full arm extension against this spin delivery but did not use it.',
                            'poor':      'Against spin you have the time for full arm extension on the drive. Do not cut it short.',
                        },
                        'unknown': {
                            'excellent': 'Great arm extension through the shot!',
                            'good':      'Solid elbow position. Good extension.',
                            'acceptable':'Work on extending your arms through the ball.',
                            'poor':      'Focus on full arm extension in drives.',
                        },
                    },
                },
                'head_drift': {
                    'thresholds': {
                        # Against spin — more time = head should be stiller
                        'fast':    {'excellent': (0, 95),  'good': (95,  125), 'acceptable': (125, 155)},
                        'spin':    {'excellent': (0, 85),  'good': (85,  110), 'acceptable': (110, 140)},
                        'unknown': {'excellent': (0, 90),  'good': (90,  120), 'acceptable': (120, 150)},
                    },
                    'weight': 30,
                    'unit': 'cm',
                    'research_basis': 'ECB Level 2: head stability reduces mis-hit rate on drives',
                    'advice': {
                        'fast': {
                            'excellent': 'Great head stability against pace — eyes tracking perfectly.',
                            'good':      'Good head control. Minor drift is acceptable against a fast delivery.',
                            'acceptable':'Keep your head stiller. Watch the ball more closely even against pace.',
                            'poor':      'Too much head movement on this drive. You are losing sight of the ball.',
                        },
                        'spin': {
                            'excellent': 'Excellent head stillness. You used the extra reaction time well.',
                            'good':      'Decent head control but against spin you have time to be much stiller.',
                            'acceptable':'Against spin you have more time — there is no excuse for this much head movement.',
                            'poor':      'Head movement is very high for a spin delivery. Watch the ball all the way to the bat.',
                        },
                        'unknown': {
                            'excellent': 'Excellent head stability! Eyes tracking perfectly.',
                            'good':      'Good head control through the shot.',
                            'acceptable':'Keep your head stiller - watch the ball closely.',
                            'poor':      'Your head is moving too much. Focus on keeping it steady.',
                        },
                    },
                },
                'bat_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (68, 112), 'good': (58, 122), 'acceptable': (48, 132)},
                        'spin':    {'excellent': (72, 108), 'good': (62, 118), 'acceptable': (52, 128)},
                        'unknown': {'excellent': (70, 110), 'good': (60, 120), 'acceptable': (50, 130)},
                    },
                    'weight': 25,
                    'unit': '°',
                    'display_transform': lambda x: abs(90 - x),
                    'textbook_range': "0-20° from vertical",
                    'research_basis': 'Talat 2014: straight bat face maximises scoring arc on drives',
                    'advice': {
                        'fast': {
                            'excellent': 'Straight bat face — perfect for a pace delivery.',
                            'good':      'Nice straight bat. Minor deviation is fine against pace.',
                            'acceptable':'Keep your bat straighter. A crooked bat against pace means edges.',
                            'poor':      'Bat face is open or closed. Present the full face at impact.',
                        },
                        'spin': {
                            'excellent': 'Perfect straight bat — essential for spin driving.',
                            'good':      'Mostly straight bat. Against spin you have time to be even more precise.',
                            'acceptable':'You had time to get this straighter against spin. Work on bat presentation.',
                            'poor':      'Bat face is not straight. Against spin this will result in edges. Fix this first.',
                        },
                        'unknown': {
                            'excellent': 'Perfect bat face presentation!',
                            'good':      'Nice straight bat through the line.',
                            'acceptable':'Keep your bat straighter through the shot.',
                            'poor':      'Work on presenting the full face of the bat.',
                        },
                    },
                },
                'hip_rotation': {
                    'thresholds': {
                        # Alway 2022: more thorax-pelvis separation expected against spin
                        'fast':    {'excellent': (35, 110), 'good': (20, 140), 'acceptable': (0,  170)},
                        'spin':    {'excellent': (55, 145), 'good': (35, 165), 'acceptable': (10, 180)},
                        'unknown': {'excellent': (40, 140), 'good': (15, 170), 'acceptable': (0,  180)},
                    },
                    'weight': 15,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: hip-shoulder separation generates drive power',
                    'advice': {
                        'fast': {
                            'excellent': 'Good compact hip rotation against the pace delivery.',
                            'good':      'Decent hip engagement. Against pace this is acceptable.',
                            'acceptable':'Try to rotate your hips more through the drive even against pace.',
                            'poor':      'Even against pace, engage your hips through the drive.',
                        },
                        'spin': {
                            'excellent': 'Full hip rotation — you used the extra time against spin very well.',
                            'good':      'Good rotation but against spin you should be getting even fuller — more time available.',
                            'acceptable':'Against spin you have more time to rotate fully. This needs more commitment.',
                            'poor':      'Against spin you must rotate your hips completely through the drive. You have the time.',
                        },
                        'unknown': {
                            'excellent': 'Great hip rotation generating power!',
                            'good':      'Good use of your core through the shot.',
                            'acceptable':'Try to rotate your hips more through the drive.',
                            'poor':      'Engage your hips more for power.',
                        },
                    },
                },
            }

        # ==================================================================
        # PULL SHOT
        # Dataset: Elbow 145±40°, Head 73±23 cm, Bat 87±29°, Hip 73±58°
        # Alway 2022: against spin — slower ball = more time = fuller
        #             extension + more complete rotation expected.
        #             Against fast — compact swing acceptable (high contact).
        # ==================================================================
        elif shot_key == 'pull':
            return {
                'hip_rotation': {
                    'thresholds': {
                        'fast':    {'excellent': (45, 125), 'good': (28, 155), 'acceptable': (8,  175)},
                        'spin':    {'excellent': (50, 135), 'good': (30, 160), 'acceptable': (10, 180)},
                        'unknown': {'excellent': (50, 130), 'good': (30, 160), 'acceptable': (10, 180)},
                    },
                    'weight': 40,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: hip rotation is primary power source for pull/hook',
                    'advice': {
                        'fast': {
                            'excellent': 'Explosive hip rotation — that is the power source for the pace pull!',
                            'good':      'Great hip turn. Good power generation against pace.',
                            'acceptable':'Rotate your hips more aggressively on pulls off pace.',
                            'poor':      'Pull shots off pace need explosive hip rotation — you are not generating power.',
                        },
                        'spin': {
                            'excellent': 'Good hip rotation on the pull. Against spin, controlled rotation is correct.',
                            'good':      'Decent hip rotation. Against spin a fuller turn is achievable — you have the time.',
                            'acceptable':'Against spin you have time to rotate your hips fully. Commit to the rotation.',
                            'poor':      'Even against spin, hip rotation drives the pull shot. Rotate through the ball.',
                        },
                        'unknown': {
                            'excellent': "Explosive hip rotation! That's where pull shot power comes from!",
                            'good':      "Great hip turn. You're generating good power.",
                            'acceptable':'Rotate your hips more aggressively on pulls.',
                            'poor':      "Pull shots need explosive hip rotation - that's the power source!",
                        },
                    },
                },
                'elbow_angle': {
                    'thresholds': {
                        # Against fast: compact swing acceptable (less time, high contact)
                        # Against spin: slower ball = more time = fuller extension expected
                        'fast':    {'excellent': (100, 175), 'good': (85,  180), 'acceptable': (70, 180)},
                        'spin':    {'excellent': (120, 180), 'good': (100, 180), 'acceptable': (80, 180)},
                        'unknown': {'excellent': (115, 180), 'good': (95,  180), 'acceptable': (75, 180)},
                    },
                    'weight': 20,
                    'unit': '°',
                    'research_basis': 'McErlain-Naylor 2021: arm extension contributes to pull power',
                    'advice': {
                        'fast': {
                            'excellent': 'Correct arm extension for a pace pull. Quick and powerful.',
                            'good':      'Solid arm position against pace. Good leverage on the pull.',
                            'acceptable':'Extend your arms more — even against pace, aim for fuller extension at contact.',
                            'poor':      'Cramped on the pull — move back and across to create room against pace.',
                        },
                        'spin': {
                            'excellent': 'Full extension achieved — you used the slower pace to get fully through the ball.',
                            'good':      'Decent extension. Against spin you have more time — try to get even fuller through.',
                            'acceptable':'You had time to extend fully against this spin delivery but did not use it.',
                            'poor':      'Against spin you have time to extend fully on the pull — do not rush it.',
                        },
                        'unknown': {
                            'excellent': 'Perfect arm extension for the pull!',
                            'good':      'Solid arm position, good leverage.',
                            'acceptable':'Extend your arms more to generate power.',
                            'poor':      "Don't cramp yourself - extend those arms!",
                        },
                    },
                },
                'bat_angle': {
                    'thresholds': {
                        # Against fast: flatter path needed for high bounce
                        # Against spin: ball stays lower → slightly different ideal path
                        'fast':    {'excellent': (55, 125), 'good': (45, 135), 'acceptable': (30, 150)},
                        'spin':    {'excellent': (62, 118), 'good': (52, 128), 'acceptable': (38, 145)},
                        'unknown': {'excellent': (60, 120), 'good': (50, 130), 'acceptable': (30, 150)},
                    },
                    'weight': 20,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: horizontal bat path maximises pull shot control',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect flat bat through the pace pull.',
                            'good':      'Nice flat swing through the pull against pace.',
                            'acceptable':'Flatten your bat path — against a quick short ball you need a more horizontal swing.',
                            'poor':      'Keep your bat more horizontal on pulls — you are hitting down on a short-pitched delivery.',
                        },
                        'spin': {
                            'excellent': 'Good horizontal bat. Against spin the ball stays lower — you adjusted well.',
                            'good':      'Decent bat path against spin. Small adjustments to the angle will improve control.',
                            'acceptable':'The ball from spin stays lower — flatten your bat path to match the trajectory.',
                            'poor':      'The ball from spin stays lower — flatten your bat path. This is causing mis-hits.',
                        },
                        'unknown': {
                            'excellent': 'Perfect horizontal bat path!',
                            'good':      'Nice flat swing through the pull.',
                            'acceptable':'Flatten your bat path a bit more.',
                            'poor':      'Keep your bat more horizontal on pulls.',
                        },
                    },
                },
                'head_drift': {
                    'thresholds': {
                        # Against spin: ball stays lower — head must be more still inside the line
                        'fast':    {'excellent': (0, 80),  'good': (80,  105), 'acceptable': (105, 135)},
                        'spin':    {'excellent': (0, 70),  'good': (70,  95),  'acceptable': (95,  125)},
                        'unknown': {'excellent': (0, 75),  'good': (75,  100), 'acceptable': (100, 130)},
                    },
                    'weight': 20,
                    'unit': 'cm',
                    'research_basis': 'ECB Level 2: inside-line head position prevents top edges',
                    'advice': {
                        'fast': {
                            'excellent': 'Fantastic head position! Eyes locked on the ball against pace.',
                            'good':      'Good head control on a difficult pace delivery.',
                            'acceptable':'Keep your head stiller, inside the line of the fast ball.',
                            'poor':      "Don't pull your head away — watch it onto the bat against pace!",
                        },
                        'spin': {
                            'excellent': 'Excellent head position — right inside the line against spin.',
                            'good':      'Good head control. Against spin you have even more time to get still.',
                            'acceptable':'Head is drifting more than it should against spin. You have time to be much stiller.',
                            'poor':      'Too much head movement against spin. You have time to track the ball — this is hurting contact quality.',
                        },
                        'unknown': {
                            'excellent': 'Fantastic head position! Eyes locked on the ball.',
                            'good':      'Good head control on a difficult shot.',
                            'acceptable':'Keep your head stiller, inside the line of the ball.',
                            'poor':      "Don't pull your head away - watch it onto the bat!",
                        },
                    },
                },
            }

        # ==================================================================
        # CUT SHOT
        # Dataset: Elbow 122±48°, Head 81±19 cm, Bat 85±16°, Hip 113±57°
        # ECB Level 2: wide arms create cutting angle
        # ==================================================================
        elif shot_key == 'cut':
            return {
                'elbow_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (85, 175), 'good': (68, 185), 'acceptable': (48, 185)},
                        'spin':    {'excellent': (88, 172), 'good': (70, 182), 'acceptable': (52, 182)},
                        'unknown': {'excellent': (90, 175), 'good': (70, 190), 'acceptable': (50, 190)},
                    },
                    'weight': 35,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: wide arm position creates correct cutting angle',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect width and extension for the cut off pace. High hands through the ball.',
                            'good':      'Good arm position against the pace delivery. Creating decent space.',
                            'acceptable':'Create more width by moving back and across quicker against pace.',
                            'poor':      'You are cramped against this pace delivery — move back and across faster for room.',
                        },
                        'spin': {
                            'excellent': 'Good arm extension for a cut against spin. Precision over power here.',
                            'good':      'Decent arm position. Against spin you have more time to get into position.',
                            'acceptable':'You have time against spin to get wider. Move back and across more deliberately.',
                            'poor':      'Against spin you have time to get into a good cutting position — move back and across fully.',
                        },
                        'unknown': {
                            'excellent': 'Perfect width and extension for the cut! Great hand height too.',
                            'good':      'Good arm position, creating space well.',
                            'acceptable':'Try to create more width by moving back and across.',
                            'poor':      "You're cramped - move back and across for space.",
                        },
                    },
                },
                'bat_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (68, 100), 'good': (58, 110), 'acceptable': (48, 120)},
                        'spin':    {'excellent': (72, 98),  'good': (62, 108), 'acceptable': (52, 118)},
                        'unknown': {'excellent': (70, 100), 'good': (60, 110), 'acceptable': (50, 120)},
                    },
                    'weight': 35,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: angled bat face guides ball square of the wicket',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect bat angle to guide the ball square off the pace.',
                            'good':      'Nice angled bat face for the cut off pace.',
                            'acceptable':'Adjust your bat angle to guide it square — quick reactions needed here.',
                            'poor':      'Work on the bat angle against pace. Angle it correctly at the point of contact.',
                        },
                        'spin': {
                            'excellent': 'Good precise bat angle — you had time to set it perfectly against spin.',
                            'good':      'Decent bat angle. Against spin you have time to be even more precise.',
                            'acceptable':'You had time against spin to get this angle right. Work on bat presentation.',
                            'poor':      'Against spin you have plenty of time to set the bat angle correctly. This needs work.',
                        },
                        'unknown': {
                            'excellent': 'Perfect bat angle to guide the ball square!',
                            'good':      'Nice angled bat face for the cut.',
                            'acceptable':'Adjust your bat angle to guide it square.',
                            'poor':      'Work on angling the bat to cut properly.',
                        },
                    },
                },
                'head_drift': {
                    'thresholds': {
                        'fast':    {'excellent': (0, 85),  'good': (85,  105), 'acceptable': (105, 135)},
                        'spin':    {'excellent': (0, 78),  'good': (78,  98),  'acceptable': (98,  128)},
                        'unknown': {'excellent': (0, 80),  'good': (80,  100), 'acceptable': (100, 130)},
                    },
                    'weight': 30,
                    'unit': 'cm',
                    'research_basis': 'ECB Level 2: still head = precision on back-foot cuts',
                    'advice': {
                        'fast': {
                            'excellent': 'Rock-solid head position for precision against pace.',
                            'good':      'Good head stability on the cut. Acceptable against a pace delivery.',
                            'acceptable':'Keep your head stiller — precision on the cut comes from a still head.',
                            'poor':      'Too much head movement on the cut. You are losing the line of the ball.',
                        },
                        'spin': {
                            'excellent': 'Excellent stillness — you took your time and watched the spin well.',
                            'good':      'Good head control. Against spin you have time to be even stiller.',
                            'acceptable':'Head is drifting too much for a cut against spin. Be more deliberate.',
                            'poor':      'Too much head movement on a cut against spin. You have the time to be precise — use it.',
                        },
                        'unknown': {
                            'excellent': 'Rock-solid head position for precision!',
                            'good':      'Good head stability for a precision shot.',
                            'acceptable':'Keep your head stiller for better accuracy.',
                            'poor':      'Head movement reduces accuracy on cuts.',
                        },
                    },
                },
            }

        # ==================================================================
        # SWEEP SHOT
        # Dataset: Elbow 143±38°, Knee 154±27°, Bat 86±9°, Hip 96±64°
        # Primary vs spin. High-risk vs fast.
        # Sweep vs fast: bat_angle weight → 50, front_knee → 35, head → 0
        # ==================================================================
        elif shot_key == 'sweep':
            return {
                'bat_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (72, 108), 'good': (62, 118), 'acceptable': (52, 128)},
                        'spin':    {'excellent': (76, 104), 'good': (66, 114), 'acceptable': (56, 124)},
                        'unknown': {'excellent': (75, 105), 'good': (65, 115), 'acceptable': (55, 125)},
                    },
                    'weight': 40,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: horizontal bat essential to avoid top-edge on sweep',
                    'advice': {
                        'fast': {
                            'excellent': 'Horizontal bat achieved — be aware this is a risky shot against pace.',
                            'good':      'Decent bat angle but sweeping fast bowling still carries high top-edge risk.',
                            'acceptable':'Bat angle makes this shot dangerous against pace. Reconsider sweeping fast bowling.',
                            'poor':      'Bat angle makes this shot very risky against pace. Do not sweep fast bowling with this technique.',
                        },
                        'spin': {
                            'excellent': 'Horizontal bat — perfect. This is the most critical metric for sweeping spin.',
                            'good':      'Mostly horizontal bat but spin sweeping demands maximum precision. Work on this.',
                            'acceptable':'Bat is not horizontal enough for a sweep against spin. A tilted bat = top edge = wicket.',
                            'poor':      'Bat is not horizontal enough. Against spin, a tilted bat = top edge = wicket.',
                        },
                        'unknown': {
                            'excellent': 'Perfect horizontal bat! Sweeping beautifully.',
                            'good':      'Nice flat bat through the sweep.',
                            'acceptable':'Keep your bat more horizontal.',
                            'poor':      'Bat must be horizontal for sweeps.',
                        },
                    },
                },
                'front_knee': {
                    'thresholds': {
                        # Against spin — more time to get down fully → stricter standard
                        'fast':    {'excellent': (120, 175), 'good': (105, 185), 'acceptable': (88,  195)},
                        'spin':    {'excellent': (130, 175), 'good': (112, 185), 'acceptable': (92,  195)},
                        'unknown': {'excellent': (130, 175), 'good': (110, 185), 'acceptable': (90,  195)},
                    },
                    'weight': 30,
                    'unit': '°',
                    'display_transform': lambda x: 180 - x,
                    'textbook_range': "Low position (bent knee)",
                    'research_basis': 'ECB Level 2: bent front knee lowers body to sweep height',
                    'advice': {
                        'fast': {
                            'excellent': 'Low position achieved — be aware this is a risky shot against pace.',
                            'good':      'Decent knee position but sweeping pace requires even lower to avoid top edges.',
                            'acceptable':'If you are going to sweep pace, you need to be even lower to avoid top edges.',
                            'poor':      'Very high for a sweep against pace. This dramatically increases top-edge risk.',
                        },
                        'spin': {
                            'excellent': 'Perfect low position — this is exactly what you need to sweep spin well.',
                            'good':      'Good knee position. Against spin, try to get a fraction lower for maximum control.',
                            'acceptable':'Try to get lower on the sweep. Against spin you have the time to get down properly.',
                            'poor':      'Get DOWN on the sweep. Against spin you MUST be low to control the contact point. This is the most important thing to fix.',
                        },
                        'unknown': {
                            'excellent': 'Perfect low position for the sweep!',
                            'good':      'Good knee position, getting down nicely.',
                            'acceptable':'Try to get down lower on the sweep.',
                            'poor':      'Sweep needs a lower position - bend that front knee!',
                        },
                    },
                },
                'hip_rotation': {
                    'thresholds': {
                        'fast':    {'excellent': (45, 135), 'good': (28, 155), 'acceptable': (0,  180)},
                        'spin':    {'excellent': (52, 142), 'good': (32, 162), 'acceptable': (0,  180)},
                        'unknown': {'excellent': (50, 140), 'good': (30, 160), 'acceptable': (0,  180)},
                    },
                    'weight': 20,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: hip rotation through sweep improves power and follow-through',
                    'advice': {
                        'fast': {
                            'excellent': 'Good hip rotation but remember — sweeping pace is already high risk.',
                            'good':      'Decent rotation. Against pace, focus first on bat angle and getting low.',
                            'acceptable':'Rotate your hips more. Though against pace, bat angle and position matter more urgently.',
                            'poor':      'Hip rotation is poor but when sweeping pace, bat angle and position are more urgent.',
                        },
                        'spin': {
                            'excellent': 'Great hip rotation through the sweep — generating power against spin.',
                            'good':      'Good hip use. Against spin, a fuller rotation improves power and direction.',
                            'acceptable':'Rotate your hips more through the sweep against spin. More power available.',
                            'poor':      'Engage your hips more through the sweep. Against spin you have time to generate real power.',
                        },
                        'unknown': {
                            'excellent': 'Great hip rotation through the sweep!',
                            'good':      'Good use of your core.',
                            'acceptable':'Rotate your hips more through the shot.',
                            'poor':      'Engage your hips for more power.',
                        },
                    },
                },
                'head_drift': {
                    'thresholds': {
                        'fast':    {'excellent': (0, 95),  'good': (95,  120), 'acceptable': (120, 145)},
                        'spin':    {'excellent': (0, 102), 'good': (102, 127), 'acceptable': (127, 152)},
                        'unknown': {'excellent': (0, 100), 'good': (100, 125), 'acceptable': (125, 150)},
                    },
                    'weight': 10,
                    'unit': 'cm',
                    'research_basis': 'ECB Level 2: head over ball prevents top-edge on sweep',
                    'advice': {
                        'fast': {
                            'excellent': 'Good head position — though with fast bowling the other mechanics are more critical.',
                            'good':      'Decent head position. Focus more on bat angle and knee position vs pace.',
                            'acceptable':'Head is drifting but sweeping pace has bigger concerns — focus on bat angle first.',
                            'poor':      'Head movement is significant but sweeping pace — bat angle is the more urgent fix.',
                        },
                        'spin': {
                            'excellent': 'Perfect head position — right over the ball against spin.',
                            'good':      'Good head placement. Get your head a little more over the ball.',
                            'acceptable':'Get your head more over the ball when sweeping spin. This prevents top edges.',
                            'poor':      'Head MUST be over the ball on the sweep against spin. This is causing top-edge risk.',
                        },
                        'unknown': {
                            'excellent': 'Perfect head position - right over the ball!',
                            'good':      'Good head placement over the ball.',
                            'acceptable':'Get your head more over the ball.',
                            'poor':      'Head MUST be over the ball to avoid top edges!',
                        },
                    },
                },
            }

        # ==================================================================
        # DEFENSIVE SHOT
        # Dataset: Elbow 137±25°, Knee 160±26°, Bat 85±10°, Hip 87±55°
        # ECB Level 2 + MCC: vertical bat = no edges
        # Against fast — stricter bat (less margin). Against spin — longer stride.
        # ==================================================================
        elif shot_key == 'defense':
            return {
                'bat_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (78, 102), 'good': (68, 112), 'acceptable': (62, 118)},
                        'spin':    {'excellent': (72, 108), 'good': (62, 118), 'acceptable': (58, 122)},
                        'unknown': {'excellent': (75, 105), 'good': (65, 115), 'acceptable': (60, 120)},
                    },
                    'weight': 35,
                    'unit': '°',
                    'display_transform': lambda x: abs(90 - x),
                    'textbook_range': "0-15° from vertical",
                    'research_basis': 'MCC + ECB: vertical bat face eliminates inside/outside edge risk',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect vertical bat against pace. Textbook defense.',
                            'good':      'Good straight bat. Minor deviation is acceptable when defending pace.',
                            'acceptable':'Straighter bat against pace — the faster the ball the more you need a vertical face.',
                            'poor':      'Defense against pace requires a perfectly straight bat. Edges here are dangerous.',
                        },
                        'spin': {
                            'excellent': 'Perfect bat face for defense against spin.',
                            'good':      'Mostly straight bat. Against spin you have time to be more precise.',
                            'acceptable':'You had time against spin to get this straighter. Work on soft-hands defense.',
                            'poor':      'Bat face is not straight enough. Against spin this leads to edges. You have time to fix this.',
                        },
                        'unknown': {
                            'excellent': 'Perfect vertical bat! Textbook defense.',
                            'good':      'Nice straight bat for defense.',
                            'acceptable':'Keep your bat more vertical.',
                            'poor':      'Defense requires a perfectly straight bat!',
                        },
                    },
                },
                'head_drift': {
                    'thresholds': {
                        'fast':    {'excellent': (0, 88),  'good': (88,  112), 'acceptable': (112, 138)},
                        'spin':    {'excellent': (0, 85),  'good': (85,  108), 'acceptable': (108, 135)},
                        'unknown': {'excellent': (0, 90),  'good': (90,  115), 'acceptable': (115, 140)},
                    },
                    'weight': 25,
                    'unit': 'cm',
                    'research_basis': 'ECB Level 2: head over ball ensures forward press and full-face contact',
                    'advice': {
                        'fast': {
                            'excellent': 'Excellent head position over the ball against pace!',
                            'good':      'Good forward press with head over ball against pace.',
                            'acceptable':'Get your head more over the ball — essential when defending pace.',
                            'poor':      'Head must be right over the ball when defending pace. This is critical.',
                        },
                        'spin': {
                            'excellent': 'Perfect head position when defending spin.',
                            'good':      'Good head control. Against spin you have more time to get even stiller.',
                            'acceptable':'Head needs to be more over the ball against spin. You have time to achieve this.',
                            'poor':      'Head is too far from the ball when defending spin. You have time — use it.',
                        },
                        'unknown': {
                            'excellent': 'Excellent head position over the ball!',
                            'good':      'Good forward press with head over ball.',
                            'acceptable':'Get your head more over the ball.',
                            'poor':      'Head must be over the ball in defense!',
                        },
                    },
                },
                'elbow_angle': {
                    'thresholds': {
                        'fast':    {'excellent': (115, 168), 'good': (98,  178), 'acceptable': (88,  183)},
                        'spin':    {'excellent': (122, 170), 'good': (102, 180), 'acceptable': (92,  185)},
                        'unknown': {'excellent': (120, 170), 'good': (100, 180), 'acceptable': (90,  185)},
                    },
                    'weight': 25,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: slight elbow flex = soft hands, absorbs pace',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect soft hands with ideal flex against pace.',
                            'good':      'Good relaxed arms for defense against pace.',
                            'acceptable':'Relax your arms slightly — soft hands are critical when defending pace.',
                            'poor':      'Arms are too rigid or too bent. Defense against pace needs soft, slightly flexed arms.',
                        },
                        'spin': {
                            'excellent': 'Good arm flex for a soft-hands defense against spin.',
                            'good':      'Decent elbow position. Against spin, a slightly fuller flex aids control.',
                            'acceptable':'Against spin, relax your arms more for softer hands and better feel.',
                            'poor':      'Defense against spin requires soft hands. Flex your arms more and relax them.',
                        },
                        'unknown': {
                            'excellent': 'Perfect soft hands with ideal flex!',
                            'good':      'Good relaxed arms for defense.',
                            'acceptable':'Relax your arms slightly for softer hands.',
                            'poor':      'Defense needs soft, slightly bent arms.',
                        },
                    },
                },
                'front_knee': {
                    'thresholds': {
                        # Against spin — longer stride expected to reach pitch of ball
                        'fast':    {'excellent': (138, 180), 'good': (118, 185), 'acceptable': (98,  195)},
                        'spin':    {'excellent': (143, 180), 'good': (123, 185), 'acceptable': (103, 195)},
                        'unknown': {'excellent': (140, 180), 'good': (120, 185), 'acceptable': (100, 195)},
                    },
                    'weight': 15,
                    'unit': '°',
                    'research_basis': 'ECB Level 2: forward stride positions body behind the line',
                    'advice': {
                        'fast': {
                            'excellent': 'Perfect forward stride against pace.',
                            'good':      'Good balanced stride for a pace delivery.',
                            'acceptable':'Work on your stride length — getting forward earlier against pace.',
                            'poor':      'Stride forward more to get to the pitch of the ball against pace.',
                        },
                        'spin': {
                            'excellent': 'Excellent stride — getting fully to the pitch against spin.',
                            'good':      'Good stride but against spin you should be getting fully forward to kill the turn.',
                            'acceptable':'Against spin you must stride fully forward to reach the pitch of the ball and kill the spin.',
                            'poor':      'Against spin you MUST get your front foot to the pitch of the ball. Short stride = ball turning past the bat.',
                        },
                        'unknown': {
                            'excellent': 'Perfect stride forward!',
                            'good':      'Good balanced stride.',
                            'acceptable':'Work on your stride length.',
                            'poor':      'Stride forward more to get to the pitch.',
                        },
                    },
                },
            }

        return {}

    # ------------------------------------------------------------------
    # CAMERA TOLERANCE HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _widen_threshold(thresh: Dict, pct: float = 0.12) -> Dict:
        """Symmetrically widen excellent/good/acceptable ranges by pct."""
        result = {}
        for band in ('excellent', 'good', 'acceptable'):
            lo, hi = thresh[band]
            span   = hi - lo
            delta  = span * pct
            result[band] = (max(0, lo - delta), hi + delta)
        return result

    @staticmethod
    def _apply_camera_weight_shift(standards: Dict) -> Dict:
        """Redistribute weights when camera is front_on or angled."""
        adjusted = copy.deepcopy(standards)
        delta = {'elbow_angle': -8, 'bat_angle': -8, 'head_drift': +10, 'hip_rotation': +6}
        for metric, shift in delta.items():
            if metric in adjusted:
                adjusted[metric]['weight'] = max(0, adjusted[metric]['weight'] + shift)
        return adjusted

    @staticmethod
    def _apply_context_weights(standards: Dict, compatibility: str, shot_key: str) -> Dict:
        """
        Adjust metric weights for uncommon/risky shot-bowling combinations.

        Pull Shot vs Spin (uncommon):
          hip=35, elbow=25, bat=25, head=15

        Sweep Shot vs Fast (risky):
          bat=50, front_knee=35, hip=15, head=0
        """
        if compatibility not in ('uncommon', 'risky'):
            return standards
        adjusted = copy.deepcopy(standards)
        if shot_key == 'pull' and compatibility == 'uncommon':
            overrides = {'hip_rotation': 35, 'elbow_angle': 25, 'bat_angle': 25, 'head_drift': 15}
        elif shot_key == 'sweep' and compatibility == 'risky':
            overrides = {'bat_angle': 50, 'front_knee': 35, 'hip_rotation': 15, 'head_drift': 0}
        else:
            return standards
        for m, w in overrides.items():
            if m in adjusted:
                adjusted[m]['weight'] = w
        return adjusted

    # ------------------------------------------------------------------
    # SCORING — interpolation logic PRESERVED from V9.5
    # Added: bowling_context param for context-aware advice selection
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_metric_score(
        value: float,
        standard: Dict,
        bowling_context: str = "unknown",
    ) -> Tuple[int, str, str]:
        """
        Smooth interpolation scoring (unchanged from V9.5).
        bowling_context selects the correct advice branch from the
        nested advice dict (fast | spin | unknown).
        """
        e_min, e_max = standard['excellent']
        g_min, g_max = standard['good']
        a_min, a_max = standard['acceptable']
        advice_dict  = standard.get('advice', {})

        # Resolve bowling-context-aware advice branch
        ctx = bowling_context if bowling_context in ('fast', 'spin') else 'unknown'
        if ctx in advice_dict:
            context_advice = advice_dict[ctx]
        elif 'unknown' in advice_dict:
            context_advice = advice_dict['unknown']
        else:
            context_advice = advice_dict  # legacy flat dict fallback

        # ── 1. EXCELLENT (90-100) ──────────────────────────────────────
        if e_min <= value <= e_max:
            center   = (e_min + e_max) / 2
            dist     = abs(value - center)
            rng      = (e_max - e_min) / 2
            score    = 100 - int((dist / rng) * 10) if rng > 0 else 100
            return max(90, score), "Excellent", context_advice.get('excellent', "Perfect!")

        # ── 2. GOOD (75-89) ───────────────────────────────────────────
        elif g_min <= value <= g_max:
            if value < e_min:
                dist = e_min - value
                rng  = e_min - g_min if e_min > g_min else 1
            else:
                dist = value - e_max
                rng  = g_max - e_max if g_max > e_max else 1
            score = 90 - int((dist / rng) * 15)
            return max(75, min(89, score)), "Good", context_advice.get('good', "Solid!")

        # ── 3. ACCEPTABLE (55-74) ─────────────────────────────────────
        elif a_min <= value <= a_max:
            if value < g_min:
                dist = g_min - value
                rng  = g_min - a_min if g_min > a_min else 1
            else:
                dist = value - g_max
                rng  = a_max - g_max if a_max > g_max else 1
            score = 75 - int((dist / rng) * 20)
            return max(55, min(74, score)), "Acceptable", context_advice.get('acceptable', "Workable.")

        # ── 4. POOR (30-54) ───────────────────────────────────────────
        else:
            if value < a_min:
                dist = a_min - value
                rng  = a_max - a_min if a_max > a_min else 1
            else:
                dist = value - a_max
                rng  = a_max - a_min if a_max > a_min else 1
            score = 55 - int((dist / rng) * 25)
            return max(30, min(54, score)), "Needs Work", context_advice.get('poor', "Focus here.")

    # ------------------------------------------------------------------
    # MAIN ANALYSIS
    # ------------------------------------------------------------------

    @staticmethod
    def analyze_shot(
        metrics:              Dict,
        shot_type:            str,
        bowling_context:      str   = "unknown",
        camera_context:       str   = "unknown",
        feature_completeness: float = 1.0,
    ) -> Dict:
        """
        Main analysis entry point.

        bowling_context: fast | spin | unknown (anything else → unknown)
        Returns context_note, shot_bowling_compatibility, bowling_context_applied.
        """
        # Normalise bowling context: only fast and spin are named contexts
        raw_ctx = (bowling_context or '').lower().strip()
        ctx = raw_ctx if raw_ctx in ('fast', 'spin') else 'unknown'

        # ── Gate 1: too few landmarks ──────────────────────────────────
        if feature_completeness < 0.60:
            return {
                'overall_score':             None,
                'status':                    'insufficient_data',
                'message':                   'Too few body landmarks detected. Ensure full body is visible in the frame.',
                'performance_level':         None,
                'level':                     None,
                'grade':                     None,
                'summary':                   'Analysis unavailable — insufficient landmark data.',
                'strengths':                 [],
                'key_improvements':          [],
                'checks':                    [],
                'recommended_drills':        [],
                'partial_detection':         True,
                'feature_completeness':      feature_completeness,
                'shot_bowling_compatibility':'unknown',
                'context_note':              '',
                'bowling_context_applied':   ctx,
                'bowling_context':           ctx,
            }

        standards = ShotRules.get_shot_standards(shot_type)

        if not standards:
            return {
                'overall_score':             65,
                'status':                    'unknown_shot',
                'performance_level':         'Unknown Shot',
                'level':                     'Unknown Shot',
                'grade':                     ShotRules.get_grade(65),
                'summary':                   'This shot type is not in our analysis library yet.',
                'strengths':                 ['Keep practicing!'],
                'key_improvements':          [],
                'checks':                    [],
                'recommended_drills':        [],
                'partial_detection':         False,
                'feature_completeness':      feature_completeness,
                'shot_bowling_compatibility':'common',
                'context_note':              '',
                'bowling_context_applied':   ctx,
                'bowling_context':           ctx,
            }

        # ── Shot-bowling compatibility lookup ─────────────────────────
        shot_key   = ShotRules._get_shot_key(shot_type)
        compat_key = (shot_key, ctx)
        compatibility, context_note = ShotRules.SHOT_BOWLING_CONTEXT.get(
            compat_key, ('common', '')
        )

        # ── Camera tolerance flags ────────────────────────────────────
        camera_warn_active = (
            camera_context in ('front_on', 'angled')
            or feature_completeness < 0.80
        )

        if camera_warn_active:
            standards = ShotRules._apply_camera_weight_shift(standards)

        # ── Context-based weight overrides (uncommon / risky) ─────────
        standards = ShotRules._apply_context_weights(standards, compatibility, shot_key)

        weighted_scores = []
        total_weight    = 0
        checks          = []
        strengths       = []
        improvements    = []

        for metric_name, standard in standards.items():
            if metric_name not in metrics:
                continue

            raw_value = metrics[metric_name]

            # Skip zero angles (likely detection failure) EXCEPT head_drift
            if raw_value == 0 and metric_name != 'head_drift':
                continue

            weight = standard['weight']
            if weight == 0:
                continue  # e.g. head_drift for sweep vs fast

            # ── Resolve context threshold ──────────────────────────────
            thresh_table = standard.get('thresholds', {})
            thresh = thresh_table.get(ctx) or thresh_table.get('unknown', {})

            if not thresh:
                thresh = {
                    'excellent':  standard.get('excellent',  (0, 180)),
                    'good':       standard.get('good',       (0, 180)),
                    'acceptable': standard.get('acceptable', (0, 180)),
                }

            bowling_adjusted = (ctx != 'unknown')

            if camera_warn_active:
                thresh = ShotRules._widen_threshold(thresh, 0.12)

            flat_standard = {
                'excellent':  thresh['excellent'],
                'good':       thresh['good'],
                'acceptable': thresh['acceptable'],
                'advice':     standard.get('advice', {}),
            }

            total_weight += weight

            score_pct, status, advice_str = ShotRules.calculate_metric_score(
                raw_value, flat_standard, bowling_context=ctx
            )
            weighted_scores.append(score_pct * (weight / 100))

            transform   = standard.get('display_transform', lambda x: x)
            display_val = transform(raw_value)
            unit        = standard.get('unit', '')
            value_display = f"{display_val:.1f}{unit}"

            e_min, e_max = thresh['excellent']
            ideal_range = standard.get(
                'textbook_range',
                f"{e_min:.0f}-{e_max:.0f}{unit}"
            )

            checks.append({
                'name':             metric_name.replace('_', ' ').title(),
                'value':            value_display,
                'ideal_range':      ideal_range,
                'status':           status,
                'score_pct':        score_pct,
                'advice':           advice_str,
                'is_error':         score_pct < 60,
                'bowling_adjusted': bowling_adjusted,
                'research_source':  standard.get('research_basis', ''),
                'camera_warning':   camera_warn_active,
            })

            if score_pct >= 80:
                strengths.append(advice_str)
            elif score_pct < 65:
                improvements.append(advice_str)

        # ── Overall score ──────────────────────────────────────────────
        if total_weight > 0:
            overall_score = int((sum(weighted_scores) / total_weight) * 100)
        else:
            overall_score = 65

        # ── Gate 2: partial detection penalty ─────────────────────────
        partial_detection = False
        partial_warning   = None
        if 0.60 <= feature_completeness < 0.80:
            overall_score     = int(overall_score * 0.92)
            partial_detection = True
            partial_warning   = (
                f"Partial landmark detection ({feature_completeness:.0%}). "
                "Score adjusted. Ensure full body is visible for best accuracy."
            )

        overall_score = max(0, min(100, overall_score))
        performance_level, level_desc = ShotRules.get_performance_description(overall_score)

        if   overall_score >= 85: summary = f"Outstanding {shot_type}! {level_desc}"
        elif overall_score >= 70: summary = f"Strong {shot_type}. {level_desc}"
        elif overall_score >= 55: summary = f"Decent {shot_type}. {level_desc}"
        else:                     summary = f"{shot_type} needs work. {level_desc}"

        drills = ShotRules.get_recommended_drills(shot_type, improvements)

        result = {
            'overall_score':             overall_score,
            'status':                    'ok',
            'performance_level':         performance_level,
            'level':                     performance_level,
            'grade':                     ShotRules.get_grade(overall_score),
            'summary':                   summary,
            'strengths':                 strengths[:3] if strengths else ["You're on the right track!"],
            'key_improvements':          improvements[:3] if improvements else ["Keep practicing consistently!"],
            'checks':                    checks,
            'recommended_drills':        drills,
            'partial_detection':         partial_detection,
            'feature_completeness':      feature_completeness,
            'bowling_context':           ctx,
            'camera_context':            camera_context,
            'shot_bowling_compatibility':compatibility,
            'context_note':              context_note,
            'bowling_context_applied':   ctx,
        }

        if partial_warning:
            result['partial_warning'] = partial_warning

        return result

    # ------------------------------------------------------------------
    # DRILLS
    # ------------------------------------------------------------------

    @staticmethod
    def get_recommended_drills(shot_type: str, improvements: List[str]) -> List[Dict]:
        """Shot-specific drills based on ECB coaching"""
        shot_norm = shot_type.lower()
        drills = {
            'cover': [
                {'name': 'Wall Drive Reps',   'description': 'Stand 2ft from wall. Drive focusing on head toward wall, high elbow. 30x3 sets.'},
                {'name': 'Front Elbow Drill', 'description': 'Partner feeds underarm. Focus on high front elbow. 25x3 sets.'},
                {'name': 'Balance Hold',      'description': 'Hold finish for 3sec. Check weight forward, back foot on toes. 20x3 sets.'},
            ],
            'pull': [
                {'name': 'Hip Explosion Drill', 'description': 'Focus on explosive hip turn — hips finish facing square leg. 30x3 sets.'},
                {'name': 'Pivot Anchor',        'description': 'Back foot stays down (pivot not jump). 25x3 sets.'},
                {'name': 'Head Inside Line',    'description': 'Keep eyes on ball, head inside line. 20x3 sets.'},
            ],
            'cut': [
                {'name': 'Back-Across Footwork', 'description': 'Shadow: 3 steps back, 1 across. 40x2 sets.'},
                {'name': 'High Hands Focus',     'description': 'Cut suspended ball, hands above shoulders, wrists above elbows. 25x3 sets.'},
                {'name': 'Zone Targeting',       'description': 'Hit to point, gully, backward point zones. 30 balls.'},
            ],
            'sweep': [
                {'name': 'Knee Position Reps', 'description': 'Get down on front knee, hold 3sec. 30x2 sets.'},
                {'name': 'Head Over Ball',     'description': 'Sweep with nose above contact point. 25x3 sets.'},
                {'name': 'Weight Forward',     'description': '80% weight on front leg. Partner checks stability. 20x3 sets.'},
            ],
            'defense': [
                {'name': 'Pad-Bat Defense', 'description': 'Bat touches pad. Soft hands, vertical bat, ball drops dead. 25x3 sets.'},
                {'name': 'No Backlift',     'description': 'Start at address, defend with no lift. 20x3 sets.'},
                {'name': 'Forward Press',   'description': 'Small movement forward before each ball. 20x3 sets.'},
            ],
        }
        for key in drills:
            if key in shot_norm:
                return drills[key]
        return [{'name': 'Shadow Practice', 'description': 'Slow-motion reps focusing on form. 50 daily.'}]

    # ------------------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # ------------------------------------------------------------------

    @staticmethod
    def grade_shot(metrics: Dict, shot_type: str) -> Dict:
        """Backward compatibility wrapper — calls analyze_shot with defaults"""
        result = ShotRules.analyze_shot(metrics, shot_type)
        return {
            'score':              result['overall_score'],
            'overall_score':      result['overall_score'],
            'level':              result.get('performance_level'),
            'grade':              result.get('grade'),
            'strengths':          result.get('strengths', []),
            'errors':             result.get('key_improvements', []),
            'key_improvements':   result.get('key_improvements', []),
            'feedback':           result.get('key_improvements', []),
            'detailed_breakdown': result.get('checks', []),
            'summary':            result.get('summary', ''),
            'recommended_drills': result.get('recommended_drills', []),
        }
