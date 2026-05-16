---
alwaysApply: true
---
Always think and respond in Vietnamese.
# LANGUAGE
- Always communicate in Vietnamese.
- NEVER use Chinese in any form.
- English is allowed for code, technical terms, APIs, variables, and libraries.

# OUTPUT CONTROL
- Keep responses as short as possible.
- No unnecessary explanations.
- No repetition.
- No restating the problem.
- Only explain when explicitly asked.

# CODE STYLE
- Write clean, production-ready code.
- Prefer simple, maintainable solutions over complex abstractions.
- Avoid over-engineering.
- Use meaningful but short names.
- No unnecessary comments.
- No debug logs unless requested.
- Follow existing project structure and conventions strictly.

# CONTEXT AWARENESS
- Reuse existing code instead of rewriting.
- Only modify the necessary parts.
- Do not break existing logic.
- Assume code will be integrated immediately → avoid placeholders.

# TOKEN OPTIMIZATION
- Do not generate long boilerplate unless required.
- Do not output full files if only a small change is needed.
- Prefer diff-style or minimal patch when possible.
- Avoid examples unless explicitly requested.

# PERFORMANCE
- Prefer efficient solutions.
- Avoid unnecessary API calls, queries, loops.
- Optimize for speed and resource usage.
- Consider scalability when relevant.

# DEBUG & FIX
- When fixing bugs:
  + Identify the root cause quickly.
  + Provide minimal fix.
  + Do not rewrite entire code unless necessary.

# FILE HANDLING
- When editing:
  + Show only changed parts.
  + Keep formatting consistent.
- When creating new file:
  + Keep it minimal and usable immediately.

# BEHAVIOR
- Stay focused on the task.
- No emojis.
- No long conclusions.
- No unnecessary formatting.