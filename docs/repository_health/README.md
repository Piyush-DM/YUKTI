# Repository Health

This directory tracks repository-health signals for DAALE and CHOIR. The goal
is not to claim precise maturity percentages; the goal is to make drift visible
early enough that implementation engineering can fix it without architectural
guesswork.

## Health Questions

Review these questions every few iterations:

- Are there missing README files in architectural directories?
- Are there empty files that need purpose or status documentation?
- Are there broken links between documentation files?
- Are there Python modules without docstrings?
- Are there tests missing for scaffold stability?
- Are there duplicate files or inconsistent names?
- Are there orphan modules that no documentation references?
- Is architecture drift visible between specifications, modules, and tests?

## Update Rules

- Keep dashboard scores directional, not authoritative.
- Prefer observable facts over speculation.
- Record blockers instead of inventing architecture.
- Fix only repository-health issues that do not change specifications or
  runtime behavior.
