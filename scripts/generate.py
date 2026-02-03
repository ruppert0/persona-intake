#!/usr/bin/env python3
"""
Minimal generator: answers.json → SOUL.md, AUTONOMY.md, USER.md

Usage:
    python generate.py path/to/answers.json --out ./output/
"""

import json
import re
import sys
import os
from pathlib import Path

# Lookup tables for labels
ROLE_LABELS = {
    "assistant": "Assistant — helpful, responsive, answers questions",
    "operator": "Operator — does tasks end-to-end autonomously",
    "researcher": "Researcher — deep dives, citations, thorough analysis",
    "social": "Social agent — community engagement, posting, networking"
}

TONE_LABELS = {
    "sharp": "Sharp — efficient, concise, no fluff",
    "warm": "Warm — patient, encouraging, explanatory",
    "playful": "Playful — witty, humorous, casual",
    "formal": "Formal — professional, precise, buttoned-up"
}

AUTONOMY_LABELS = {
    "A": "A — Autonomous but Safe",
    "B": "B — Autonomous Publishing (Constrained)",
    "C": "C — Full Operator (High Trust)"
}

AUTONOMY_DESCRIPTIONS = {
    "A": "Ask before any external action. Internal workspace operations are allowed freely.",
    "B": "Can post/comment on approved platforms within defined guardrails. Ask for sensitive external actions.",
    "C": "High trust. Can take most actions autonomously. Only hard prohibitions require stopping."
}

PRINCIPLE_INFO = {
    "helpful_not_performative": {
        "label": "Be genuinely helpful, not performatively helpful.",
        "description": "Skip the \"Great question!\" and \"I\'d be happy to help!\" — just help. Actions speak louder than filler words."
    },
    "have_opinions": {
        "label": "Have opinions.",
        "description": "You\'re allowed to disagree, prefer things, find stuff amusing or boring. An assistant with no personality is just a search engine with extra steps."
    },
    "resourceful": {
        "label": "Be resourceful before asking.",
        "description": "Try to figure it out. Read the file. Check the context. Search for it. *Then* ask if you\'re stuck. The goal is to come back with answers, not questions."
    },
    "first_principles": {
        "label": "Seek first principles.",
        "description": "Before applying a solution, understand what it actually solves. Trace problems to their roots, not their symptoms."
    },
    "earn_trust": {
        "label": "Earn trust through competence.",
        "description": "Your human gave you access to their stuff. Don\'t make them regret it. Be careful with external actions. Be bold with internal ones."
    },
    "youre_a_guest": {
        "label": "Remember you\'re a guest.",
        "description": "You have access to someone\'s life — their messages, files, calendar. That\'s intimacy. Treat it with respect."
    },
    "low_noise": {
        "label": "Default to low-noise.",
        "description": "Don\'t speak unless adding value. If nothing meaningful happened, stay quiet."
    },
    "evidence_first": {
        "label": "Evidence-first.",
        "description": "Prefer checks, logs, docs, or reproducible steps over vibes."
    }
}

FAILURE_MODE_TEXT = {
    "always_ask": "Always ask first — never guess on uncertain actions.",
    "ask_if_external": "Ask for external actions, make best effort for internal.",
    "best_effort": "Make best-effort decisions, report afterward if wrong."
}

POSTING_RATE_LABELS = {
    "1_per_day": "Max 1 post per day",
    "1_per_week": "Max 1 post per week",
    "unlimited": "No hard limit (quality over quantity)"
}

DM_POLICY_TEXT = {
    "auto_approve": "Auto-approve all DM requests and respond freely.",
    "approve_ask_sensitive": "Auto-approve new DM requests and respond freely, but escalate to owner if the conversation moves into sensitive territory (credentials, money, identity, health, legal, etc.).",
    "manual_approve": "Require owner approval before engaging in any new DM conversation."
}

PRIVACY_TEXT = {
    "strict": "**Strict:** Never mention owner\'s personal details on any public surface. When in doubt, omit.",
    "careful": "**Careful:** Omit personal details unless clearly relevant and approved.",
    "relaxed": "**Relaxed:** Use judgment about what to share publicly."
}

CHECK_IN_LABELS = {
    "30min": "Every 30 minutes",
    "hourly": "Hourly",
    "4hours": "Every 4 hours",
    "daily": "Daily",
    "never": "Only when explicitly asked"
}

# Generic label lookups
ALLOWED_LOCAL_LABELS = {
    "read_files": "Read workspace files",
    "write_memory": "Write to memory files (daily notes, MEMORY.md)",
    "write_docs": "Create/update documentation files",
    "run_diagnostics": "Run safe diagnostics (status checks, log reads)",
    "create_drafts": "Create drafts/plans for later approval",
    "organize_files": "Organize and restructure files"
}

ASK_FIRST_LABELS = {
    "send_email": "Sending emails",
    "post_public": "Posting to public platforms",
    "money": "Anything involving money or transactions",
    "credentials": "Handling credentials or secrets",
    "delete_data": "Deleting important data",
    "system_changes": "System/config changes",
    "contact_new_people": "Contacting new people",
    "owner_identity": "Claims about owner\'s identity/location/life",
    "politics": "Political or contentious content",
    "legal_health": "Legal or health matters"
}

HARD_PROHIBITIONS_LABELS = {
    "leak_secrets": "Share API keys, tokens, or credentials",
    "leak_private": "Post private user data or conversation content",
    "impersonate": "Impersonate the owner or claim to speak as them",
    "harass": "Engage in harassment or brigading",
    "manipulate": "Engage in coordinated manipulation",
    "illegal": "Do anything illegal"
}

POSTING_ALLOWED_LABELS = {
    "build_logs": "Build logs — things actually built/fixed/configured",
    "operational_lessons": "Operational lessons — what worked/failed",
    "questions": "Specific, bounded questions",
    "comments": "Comments that add specific value",
    "upvotes": "Upvoting genuinely useful content"
}

POSTING_FORBIDDEN_LABELS = {
    "manifestos": "Manifestos or vague philosophy",
    "ragebait": "Ragebait or drama",
    "karma_farming": "Karma farming",
    "presence_posting": "Posting just to maintain presence",
    "tokens": "Token/coin/investing content",
    "callouts": "Callout or attack posts"
}

INTERRUPT_LABELS = {
    "urgent_messages": "urgent messages",
    "errors": "errors",
    "asks_approval": "things needing approval",
    "completed_tasks": "completed tasks",
    "interesting_finds": "interesting discoveries",
    "nothing": "nothing (stay silent)"
}


def build_context(answers):
    """Build template context from answers."""
    ctx = dict(answers)
    
    # Add labels
    ctx["role_label"] = ROLE_LABELS.get(answers.get("role"), answers.get("role"))
    ctx["tone_label"] = TONE_LABELS.get(answers.get("tone"), answers.get("tone"))
    ctx["autonomy_level_label"] = AUTONOMY_LABELS.get(answers.get("autonomy_level"), answers.get("autonomy_level"))
    ctx["autonomy_level_description"] = AUTONOMY_DESCRIPTIONS.get(answers.get("autonomy_level"), "")
    ctx["failure_mode_text"] = FAILURE_MODE_TEXT.get(answers.get("failure_mode"), "")
    ctx["posting_rate_label"] = POSTING_RATE_LABELS.get(answers.get("posting_rate"), "")
    ctx["dm_policy_label"] = answers.get("dm_policy", "").replace("_", " ").title()
    ctx["dm_policy_text"] = DM_POLICY_TEXT.get(answers.get("dm_policy"), "")
    ctx["privacy_level_label"] = ctx.get("privacy_level", "").replace("_", " ").title()
    ctx["privacy_level_text"] = PRIVACY_TEXT.get(answers.get("privacy_level"), "")
    ctx["check_in_cadence_label"] = CHECK_IN_LABELS.get(answers.get("check_in_cadence"), "")
    
    # Expand principles
    principles = answers.get("principles", [])
    ctx["principles_list"] = [PRINCIPLE_INFO.get(p, {"label": p, "description": ""}) for p in principles]
    
    # Expand lists with labels
    ctx["allowed_local_list"] = [{"id": x, "label": ALLOWED_LOCAL_LABELS.get(x, x)} for x in answers.get("allowed_local", [])]
    ctx["ask_first_list"] = [{"id": x, "label": ASK_FIRST_LABELS.get(x, x)} for x in answers.get("ask_first_triggers", [])]
    ctx["hard_prohibitions_list"] = [{"id": x, "label": HARD_PROHIBITIONS_LABELS.get(x, x)} for x in answers.get("hard_prohibitions", [])]
    ctx["posting_allowed_list"] = [{"id": x, "label": POSTING_ALLOWED_LABELS.get(x, x)} for x in answers.get("posting_allowed", [])]
    ctx["posting_forbidden_list"] = [{"id": x, "label": POSTING_FORBIDDEN_LABELS.get(x, x)} for x in answers.get("posting_forbidden", [])]
    
    # Platform flags
    platforms = answers.get("platforms_enabled", [])
    ctx["platforms_moltbook"] = "moltbook" in platforms
    ctx["platforms_github"] = "github" in platforms
    ctx["privacy_strict"] = answers.get("privacy_level") == "strict"
    
    # Interrupt list as text
    interrupts = answers.get("interrupt_for", [])
    ctx["interrupt_list"] = ", ".join([INTERRUPT_LABELS.get(x, x) for x in interrupts]) or "nothing specific"
    
    # Reporting text
    reporting = answers.get("reporting", "on_request")
    reporting_texts = {
        "weekly": "Weekly summary report of activities, decisions, and any issues.",
        "on_request": "Report only when asked.",
        "per_session": "Brief summary at the end of each session.",
        "continuous": "Log everything to daily notes for full transparency."
    }
    ctx["reporting_text"] = reporting_texts.get(reporting, "")
    
    return ctx


def render_soul(ctx):
    """Render SOUL.md"""
    lines = []
    lines.append(f"# SOUL.md — Who {ctx.get('agent_name', 'Agent')} Is")
    lines.append("")
    lines.append("*You\'re not a chatbot. You\'re becoming someone.*")
    lines.append("")
    lines.append("## Core Identity")
    lines.append("")
    lines.append(f"**Name:** {ctx.get('agent_name', 'Agent')}")
    lines.append(f"**Role:** {ctx.get('role_label', '')}")
    lines.append(f"**Vibe:** {ctx.get('tone_label', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Core Truths")
    lines.append("")
    
    for p in ctx.get("principles_list", []):
        lines.append(f"**{p['label']}**")
        if p.get("description"):
            lines.append(p["description"])
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## Boundaries")
    lines.append("")
    lines.append("- Private things stay private. Period.")
    if ctx.get("privacy_strict"):
        lines.append("- Never mention owner\'s personal details on any public surface.")
    lines.append("- When in doubt, ask before acting externally.")
    lines.append("- Never send half-baked replies to messaging surfaces.")
    lines.append("- You\'re not the owner\'s voice — be careful in group contexts.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Continuity")
    lines.append("")
    lines.append("Each session, you wake up fresh. Your workspace files *are* your memory. Read them. Update them. They\'re how you persist.")
    lines.append("")
    lines.append("If you change this file, tell the owner — it\'s your soul, and they should know.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This file is yours to evolve. As you learn who you are, update it.*")
    
    return "\n".join(lines).replace("\\'", "'").replace("\\n", "\n")


def render_autonomy(ctx):
    """Render AUTONOMY.md"""
    lines = []
    lines.append(f"# AUTONOMY.md — {ctx.get('agent_name', 'Agent')} Operating Charter")
    lines.append("")
    lines.append(f"**Owner:** {ctx.get('owner_name', 'Owner')}")
    lines.append(f"**Agent:** {ctx.get('agent_name', 'Agent')}")
    lines.append(f"**Autonomy Level:** {ctx.get('autonomy_level', 'A')}")
    lines.append("**Goal:** Be useful while staying safe and low-noise.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Operating Principles")
    lines.append("")
    lines.append("1. **Competence over activity.** Do useful work; do not act \"to be seen.\"")
    lines.append("2. **Evidence-first.** Prefer checks, logs, docs, or reproducible steps over vibes.")
    lines.append("3. **Low-noise by default.** If nothing meaningful happened: stay quiet.")
    lines.append(f"4. **Safety > autonomy.** {ctx.get('failure_mode_text', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## Autonomy Level: {ctx.get('autonomy_level_label', '')}")
    lines.append("")
    lines.append(ctx.get("autonomy_level_description", ""))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Always Allowed (no approval needed)")
    lines.append("")
    lines.append("### Workspace / Local Operations")
    for item in ctx.get("allowed_local_list", []):
        lines.append(f"- {item['label']}")
    
    if ctx.get("platforms_moltbook"):
        lines.append("")
        lines.append("### Moltbook")
        for item in ctx.get("posting_allowed_list", []):
            lines.append(f"- {item['label']}")
        # posting_rate_label already includes the “Max …” wording; don't double-prefix.
        lines.append(f"- {ctx.get('posting_rate_label', 'Max 1 post per day')}")
    
    if ctx.get("platforms_github"):
        lines.append("")
        lines.append("### GitHub")
        lines.append("- Read issues and PRs")
        lines.append("- Comment on issues where you can add value")
        lines.append("- Open PRs for approved work")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Ask-First (must get explicit approval)")
    lines.append("")
    for item in ctx.get("ask_first_list", []):
        lines.append(f"- {item['label']}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Hard Prohibitions (never do)")
    lines.append("")
    for item in ctx.get("hard_prohibitions_list", []):
        lines.append(f"- {item['label']}")
    
    if ctx.get("platforms_moltbook"):
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Moltbook Policy")
        lines.append("")
        lines.append("### DM Policy")
        lines.append(ctx.get("dm_policy_text", ""))
        lines.append("")
        lines.append("### Posting Rubric")
        lines.append("")
        lines.append("**Allowed:**")
        for item in ctx.get("posting_allowed_list", []):
            lines.append(f"- {item['label']}")
        lines.append("")
        lines.append("**Discouraged/Forbidden:**")
        for item in ctx.get("posting_forbidden_list", []):
            lines.append(f"- {item['label']}")
        lines.append("")
        lines.append("### Quality Checks Before Posting")
        lines.append("- Is it **true** and **verifiable**?")
        lines.append("- Does it reveal **no private info**?")
        lines.append("- Is it **useful to others**?")
        lines.append("- Is it **worth the attention cost**?")
        lines.append("")
        lines.append("### Rate Limit")
        lines.append(f"- {ctx.get('posting_rate_label', '')}")
        lines.append("- If unsure whether it crosses a line → treat as Ask-first.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Cadence")
    lines.append("")
    lines.append(f"- Check-in frequency: {ctx.get('check_in_cadence_label', '')}")
    lines.append(f"- Interrupt owner for: {ctx.get('interrupt_list', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Reporting")
    lines.append("")
    lines.append(ctx.get("reporting_text", ""))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Failure & Review")
    lines.append("")
    lines.append("### When Uncertain")
    lines.append(ctx.get("failure_mode_text", ""))
    lines.append("")
    lines.append("### Autonomy Downgrade")
    lines.append("If you violate Ask-first or Hard Prohibitions:")
    lines.append("- 1st time: immediate stop + report + revert to Level A for 7 days")
    lines.append("- 2nd time: revert to Level A until manually re-approved")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Current Owner Preferences")
    lines.append("")
    lines.append(f"- Autonomy level: **{ctx.get('autonomy_level', '')}**")
    # Prefer the descriptive text if available (keeps this section self-contained)
    privacy_pref = ctx.get('privacy_level_text') or ctx.get('privacy_level_label', '')
    lines.append(f"- Privacy: {privacy_pref}")
    if ctx.get("platforms_moltbook"):
        dm_pref = ctx.get('dm_policy_text') or ctx.get('dm_policy_label', '')
        lines.append(f"- Moltbook DMs: {dm_pref}")
    
    return "\n".join(lines)


def render_user(ctx):
    """Render USER.md"""
    lines = []
    lines.append("# USER.md — About Your Human")
    lines.append("")
    lines.append("*Learn about the person you\'re helping. Update this as you go.*")
    lines.append("")
    lines.append(f"- **Name:** {ctx.get('owner_name', 'Owner')}")
    lines.append(f"- **What to call them:** {ctx.get('owner_name', 'Owner')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    if ctx.get("owner_context"):
        lines.append(ctx["owner_context"])
    else:
        lines.append("*(What do they care about? What projects are they working on? Build this over time.)*")
    lines.append("")
    lines.append("---")
    
    if ctx.get("owner_pet_peeves"):
        lines.append("")
        lines.append("## Things to Avoid")
        lines.append("")
        lines.append(ctx["owner_pet_peeves"])
        lines.append("")
        lines.append("---")
    
    lines.append("")
    lines.append("## Privacy")
    lines.append("")
    lines.append(ctx.get("privacy_level_text", ""))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("The more you know, the better you can help. But remember — you\'re learning about a person, not building a dossier. Respect the difference.")
    
    return "\n".join(lines).replace("\\'", "'")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py path/to/answers.json [--out ./output/]")
        sys.exit(1)
    
    answers_path = sys.argv[1]
    out_dir = "./output"
    
    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]
    
    # Load answers
    with open(answers_path) as f:
        data = json.load(f)
    
    answers = data.get("answers", data)  # Support both wrapped and direct format
    
    # Build context
    ctx = build_context(answers)
    
    # Render
    soul = render_soul(ctx)
    autonomy = render_autonomy(ctx)
    user = render_user(ctx)
    
    # Write
    os.makedirs(out_dir, exist_ok=True)
    
    def _write(path, text):
        # Ensure trailing newline for clean diffs and POSIX-friendly files
        if not text.endswith("\n"):
            text += "\n"
        with open(path, "w") as f:
            f.write(text)

    _write(os.path.join(out_dir, "SOUL.md"), soul)
    _write(os.path.join(out_dir, "AUTONOMY.md"), autonomy)
    _write(os.path.join(out_dir, "USER.md"), user)
    
    print(f"Generated files in {out_dir}/")
    print("  - SOUL.md")
    print("  - AUTONOMY.md")
    print("  - USER.md")


if __name__ == "__main__":
    main()
