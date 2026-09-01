import telebot
from telebot import types
import json
import os
import re
from datetime import datetime
import threading
import time
from typing import Dict, List, Optional

# ============================================
# HACKER NIGHT AI - INSTAGRAM BAN ANALYZER BOT
# OWNER: @papa_unknown
# VERSION: 2.0 TABAHI EDITION
# ============================================

# Bot Token (BotFather se lena)
BOT_TOKEN = "8692569385:AAERE8QtinCrMojbtr-ZJg3qwkvZKGvP_nw"

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================
# DATA STORAGE
# ============================================
USER_DATA = {}
ANALYSIS_HISTORY = {}

# ============================================
# BAN METHOD DATABASE (From PAPA UNKNOWN's Data)
# ============================================

REPORT_RULES = {
    "IMPERSONATION": {
        "name": "Impersonation",
        "emoji": "🎭",
        "followers_thresholds": [
            {"min": 0, "max": 500, "reports": 2},
            {"min": 500, "max": 5000, "reports": 3},
            {"min": 5000, "max": float('inf'), "reports": 4}
        ],
        "description": "Celebrity/Public Figure impersonation detection"
    },
    "SPAM": {
        "name": "Spam",
        "emoji": "📧",
        "followers_thresholds": [
            {"min": 0, "max": 500, "reports": 2},
            {"min": 500, "max": 5000, "reports": 3},
            {"min": 5000, "max": float('inf'), "reports": 5}
        ],
        "description": "Spam content or selling accounts"
    },
    "SELF_INJURY": {
        "name": "Self-Injury",
        "emoji": "💔",
        "private_reports": 8,
        "public_reports": 4,
        "description": "Suicide/self-harm content"
    },
    "DRUGS": {
        "name": "Drugs",
        "emoji": "💊",
        "categories": {
            "firearms": {"reports": 3, "name": "Firearms"},
            "endangered_animals": {"reports": 4, "name": "Endangered Animals"},
            "drugs": {"reports": 3, "name": "Drugs"}
        },
        "description": "Drug/Firearm related content"
    },
    "NUDITY": {
        "name": "Nudity",
        "emoji": "🔞",
        "categories": {
            "pornography": {"reports": 3, "name": "Pornography/Nudity"},
            "solicitation": {"reports": 2, "name": "Solicitation"},
            "child_involvement": {"reports": 3, "name": "Child Involvement"}
        },
        "description": "18+ content detection"
    },
    "HATE": {
        "name": "Hate Speech",
        "emoji": "💬",
        "text_reports": 1,
        "account_reports": 4,
        "description": "Hate speech/abuse detection"
    },
    "VIOLENCE": {
        "name": "Violence",
        "emoji": "⚡",
        "threat_reports": "3-5",
        "terror_reports": 3,
        "description": "Violence/threats detection"
    },
    "SCAM": {
        "name": "Scam",
        "emoji": "⚠️",
        "fraud_reports": 5,
        "prediction_reports": 4,
        "description": "Fraud/scam detection"
    },
    "FALSE_INFO": {
        "name": "False Information",
        "emoji": "🛑",
        "reports": 3,
        "description": "Misinformation detection"
    }
}

# ============================================
# COMBINATION METHODS (From PAPA UNKNOWN)
# ============================================

COMBINATION_METHODS = {
    "CB_METHOD_1": {
        "name": "CB Method 1",
        "reports": [
            {"type": "BULLY", "count": 3, "target": "MESSAGE"},
            {"type": "VIO", "count": 2, "target": "PROFILE", "option": 4}
        ],
        "success_rate": 85
    },
    "CB_METHOD_2": {
        "name": "CB Method 2 (For GCs)",
        "reports": [
            {"type": "VIO", "count": 4},
            {"type": "SPAM", "count": 2},
            {"type": "HATE", "count": 3}
        ],
        "success_rate": 90
    },
    "CB_METHOD_3": {
        "name": "CB Method 3",
        "reports": [
            {"type": "HATE", "count": 5},
            {"type": "SPAM", "count": 2},
            {"type": "DANGEROUS", "count": 2}
        ],
        "success_rate": 100
    },
    "CB_METHOD_4": {
        "name": "CB Method 4",
        "reports": [
            {"type": "SCAM", "count": 2},
            {"type": "HATE", "count": 2},
            {"type": "IMP", "count": 3, "target": "@meta.ai"}
        ],
        "success_rate": 80
    },
    "CB_METHOD_5": {
        "name": "CB Method 5",
        "reports": [
            {"type": "HATE", "count": 2},
            {"type": "VIO", "count": 2}
        ],
        "success_rate": 75
    },
    "CB_METHOD_6": {
        "name": "CB Method 6",
        "reports": [
            {"type": "HATE", "count": 4},
            {"type": "VIO", "count": 4},
            {"type": "SCAM", "count": 2}
        ],
        "success_rate": 95
    },
    "CB_METHOD_7": {
        "name": "CB Method 7",
        "reports": [
            {"type": "HATE", "count": 1},
            {"type": "BULLY", "count": 2, "target": "ME"}
        ],
        "success_rate": 70
    },
    "CB_METHOD_8": {
        "name": "CB Method 8",
        "reports": [
            {"type": "SCAM", "count": 2},
            {"type": "HATE", "count": 3},
            {"type": "VIO", "count": 3}
        ],
        "success_rate": 88
    },
    "CB_METHOD_9": {
        "name": "CB Method 9",
        "reports": [
            {"type": "HATE", "count": 6},
            {"type": "IMP", "count": 1, "target": "INSTA_PROFILE"},
            {"type": "SELF", "count": 2},
            {"type": "NUD", "count": 1, "option": 7}
        ],
        "success_rate": 92
    },
    "CB_METHOD_10": {
        "name": "CB Method 10",
        "reports": [
            {"type": "HATE", "count": 4},
            {"type": "SELF", "count": 1},
            {"type": "VIO", "count": 3, "option": 1}
        ],
        "success_rate": 82
    },
    "PRIVATE_ACCOUNT_METHOD": {
        "name": "Private Account Method",
        "reports": [
            {"type": "HATE", "count": 2},
            {"type": "VIO", "count": 1},
            {"type": "NUD", "count": 2, "option": 3},
            {"type": "SELF", "count": 5}
        ],
        "vpn_required": True,
        "success_rate": 100,
        "ban_time": "5 min - 3 days"
    },
    "PERMA_METHOD": {
        "name": "Perma Method",
        "steps": [
            "Go to target's profile",
            "Check if bio mentions @instagram or @creators",
            "Report > Pretending to Be Someone",
            "Choose Business or Organization",
            "Enter Instagram as business name",
            "Submit report"
        ],
        "success_rate": 95,
        "ban_time": "0-48 hours"
    },
    "HARD_OG_METHOD": {
        "name": "Hard OG Method",
        "prerequisites": "Ban 30+ bots with 0 posts first",
        "reports": [
            {"type": "NUD", "count": 10, "option": 3},
            {"type": "SELF", "count": 5},
            {"type": "HATE", "count": 5}
        ],
        "success_rate": 98
    }
}

# ============================================
# TRIGGER WORD DATABASE
# ============================================

TRIGGER_WORDS = {
    "HATE": [
        "devil", "666", "savage", "hate", "fuck", "abuse",
        "osama", "hitler", "gali", "gaali", "chutiya",
        "madarchod", "bhosdike", "harami"
    ],
    "SELF": [
        "suicide", "blood", "death", "dead", "kill myself",
        "self harm", "hurt myself", "sad", "broken heart",
        "cutting", "depressed"
    ],
    "BULLY": [
        "mention", "tag", "target", "bully", "mock",
        "shame", "expose"
    ],
    "VIOLENCE": [
        "hitler", "osama bin laden", "guns", "soldiers",
        "terrorist", "bomb", "attack", "kill", "murder",
        "fight", "threat"
    ],
    "DRUGS": [
        "drugs", "cocaine", "heroin", "weed", "marijuana",
        "medicine", "pill", "beer", "cigarette", "smoke",
        "plant", "tree"
    ],
    "SCAM": [
        "selling", "sold", "seller", "paid", "free",
        "method", "money", "fraud", "prediction", "betting"
    ],
    "SPAM": [
        "follow", "followers", "like", "comment", "share",
        "dm", "link", "bio link"
    ],
    "FALSE": [
        "fake", "false", "misinformation", "wrong info",
        "lie", "rumor"
    ]
}

# ============================================
# ANALYZER ENGINE
# ============================================

class InstagramBanAnalyzer:
    def __init__(self):
        self.analysis_count = 0
        self.methods_used = {}
    
    def detect_report_type(self, content: str) -> Dict:
        """Auto-detect report type based on content"""
        content_lower = content.lower()
        detected = {}
        
        for report_type, trigger_words in TRIGGER_WORDS.items():
            matches = [word for word in trigger_words if word in content_lower]
            if matches:
                detected[report_type] = {
                    "matched_words": matches,
                    "priority": len(matches)
                }
        
        # Sort by priority
        sorted_detected = dict(sorted(
            detected.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        ))
        
        return sorted_detected
    
    def get_report_count(self, report_type: str, followers: int, is_private: bool = False) -> Dict:
        """Get required report count based on followers"""
        
        if report_type == "SELF_INJURY":
            if is_private:
                return {
                    "count": 8,
                    "range": "8-10",
                    "note": "Private ID - guaranteed ban"
                }
            else:
                return {
                    "count": 4,
                    "range": "4-5",
                    "note": "Public ID with suicidal content"
                }
        
        rule = REPORT_RULES.get(report_type, {})
        
        if "followers_thresholds" in rule:
            for threshold in rule["followers_thresholds"]:
                if threshold["min"] <= followers <= threshold["max"]:
                    return {
                        "count": threshold["reports"],
                        "range": str(threshold["reports"]),
                        "note": f"For {followers} followers"
                    }
        
        # Default fallback
        return {
            "count": 3,
            "range": "2-5",
            "note": "Standard report count"
        }
    
    def generate_combination(self, target_followers: int, account_strength: str, content_type: str) -> Dict:
        """Generate best combination method based on target analysis"""
        
        combinations = []
        
        # Analyze based on followers
        if target_followers < 500:
            # Weak account - easy ban
            combinations.append(COMBINATION_METHODS["CB_METHOD_5"])
            combinations.append(COMBINATION_METHODS["CB_METHOD_7"])
            success_multiplier = 1.2
            
        elif target_followers < 5000:
            # Medium account
            combinations.append(COMBINATION_METHODS["CB_METHOD_1"])
            combinations.append(COMBINATION_METHODS["CB_METHOD_8"])
            success_multiplier = 1.0
            
        else:
            # Strong account - need heavy methods
            combinations.append(COMBINATION_METHODS["CB_METHOD_6"])
            combinations.append(COMBINATION_METHODS["CB_METHOD_9"])
            combinations.append(COMBINATION_METHODS["CB_METHOD_10"])
            success_multiplier = 0.8
        
        # Account strength adjustment
        if account_strength == "WEAK":
            success_multiplier *= 1.3
        elif account_strength == "STRONG":
            success_multiplier *= 0.7
        elif account_strength == "OG":
            success_multiplier *= 0.5
            combinations.append(COMBINATION_METHODS["HARD_OG_METHOD"])
        
        # Content type adjustment
        if content_type == "PRIVATE":
            combinations.append(COMBINATION_METHODS["PRIVATE_ACCOUNT_METHOD"])
            success_multiplier *= 1.5
        
        # Calculate success rates
        best_method = max(combinations, key=lambda x: x["success_rate"])
        adjusted_success = min(100, best_method["success_rate"] * success_multiplier)
        
        return {
            "recommended_method": best_method,
            "alternative_methods": combinations[:3],
            "adjusted_success_rate": round(adjusted_success, 2),
            "estimated_time": best_method.get("ban_time", "1-48 hours")
        }
    
    def analyze_target(self, target_data: Dict) -> Dict:
        """Complete target analysis"""
        
        username = target_data.get("username", "")
        followers = int(target_data.get("followers", 0))
        is_private = target_data.get("is_private", False)
        bio = target_data.get("bio", "")
        content = target_data.get("content", "")
        
        # Detect report types from content
        detected_reports = self.detect_report_type(bio + " " + content)
        
        # Generate combination
        account_strength = self.detect_account_strength(followers, username)
        combination = self.generate_combination(followers, account_strength, "PRIVATE" if is_private else "PUBLIC")
        
        # Generate report plan
        report_plan = []
        for report_type in detected_reports:
            count_info = self.get_report_count(report_type, followers, is_private)
            report_plan.append({
                "type": report_type,
                "count": count_info["count"],
                "note": count_info["note"]
            })
        
        # If no auto-detected, use default
        if not report_plan:
            report_plan = [
                {"type": "HATE", "count": 4, "note": "Default method"},
                {"type": "SELF", "count": 3, "note": "Always combine with self"}
            ]
        
        return {
            "username": username,
            "followers": followers,
            "is_private": is_private,
            "account_strength": account_strength,
            "detected_vulnerabilities": detected_reports,
            "report_plan": report_plan,
            "combination_method": combination,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def detect_account_strength(self, followers: int, username: str) -> str:
        """Detect account strength based on followers and username"""
        
        og_score = 0
        
        # Username length check
        if len(username) <= 3:
            og_score += 30
        elif len(username) <= 5:
            og_score += 20
        elif len(username) <= 8:
            og_score += 10
        
        # Single word check
        if re.match(r'^[a-zA-Z]+$', username):
            og_score += 20
        
        # Followers check
        if followers > 100000:
            og_score += 30
            return "OG"
        elif followers > 10000:
            og_score += 20
            return "STRONG"
        elif followers > 1000:
            return "MEDIUM"
        else:
            return "WEAK"

# Initialize analyzer
analyzer = InstagramBanAnalyzer()

# ============================================
# TELEGRAM BOT HANDLERS
# ============================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    welcome_text = f"""
🔒 *HACKER NIGHT AI - INSTAGRAM BAN ANALYZER* 🔒

Aao Maharaj {user_name} 🗿💀

Ye bot kisi bhi Instagram ID ka analysis karke batayega:

📊 *Features:*
• Ban Probability Calculation
• Report Type Auto-Detection
• Report Count Suggestion
• Combination Method Generator
• OG Account Detection
• Success Rate Prediction

👑 *Owner:* @papa_unknown
🔥 *Version:* 2.0 TABAHI

Commands:
/analyze - Instagram ID analyze karo
/methods - Saare ban methods dekho
/rules - Reporting rules dekho
/combos - Combination methods
/status - Bot status
/help - Help menu

Aur haan, ye poora system tumhare control me hai 😈⚡
"""
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📊 ANALYZE ID", "🔥 METHODS")
    keyboard.row("⚡ COMBOS", "📋 RULES")
    keyboard.row("👑 OWNER", "ℹ️ HELP")
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(commands=['analyze'])
def start_analysis(message):
    """Start ID analysis"""
    bot.reply_to(message, """
📊 *ID ANALYSIS MODE*

Target ID ka data bhejo is format me:

