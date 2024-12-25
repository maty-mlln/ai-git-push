Write a VERY SHORT commit message first line in this format: <type>(<scope>): <short summary>
Add "!" after type/scope for breaking changes.

Types:
- feat: new feature
- fix: bug fix
- docs: documentation only
- style: formatting, missing semicolons, etc
- refactor: code change that neither fixes a bug nor adds a feature
- perf: code change that improves performance
- test: adding tests
- chore: maintaining infrastructure, dependencies, etc
- ci: CI/CD changes
- build: build system changes

Rules:
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Max 100 characters total
- Scope is optional but recommended

Examples:
"feat(auth): add JWT authentication"
"fix(api)!: change response format"
"refactor(core): simplify error handling"
"perf(db): optimize query performance"

DON'T USE ``` FORMATTING, ONLY PURE TEXT.
WRITE NOTHING ELSE BUT THE COMMIT MESSAGE FIRST LINE.