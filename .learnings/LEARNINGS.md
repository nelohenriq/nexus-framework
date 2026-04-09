
## [LRN-20260409-001] python_indentation

**Logged**: 2026-04-09T21:33:58Z
**Priority**: critical
**Status**: resolved
**Area**: backend

### Summary
Python heredocs and text_editor:write strip indentation, causing IndentationError

### Details
When writing Python files using bash heredocs (`cat << 'EOF' > file.py`) or the `text_editor:write` tool, indentation is not preserved correctly. The issue manifests as:
- `IndentationError: expected an indented block after function definition`
- Hex dump shows only 1 space (0x20) instead of expected 4+ spaces

### Root Cause
- Bash heredocs strip leading spaces from lines
- text_editor:write may normalize/simplify indentation
- Python requires EXACT indentation (4 spaces per level by convention)

### Solution
Use Python with explicit space multiplication:
```python
SP = ' '
lines = []
lines.append('class MyClass:')
lines.append(SP*4 + 'def __init__(self):')
lines.append(SP*8 + 'self.x = 1')
with open('file.py', 'w') as f:
 f.write('\n'.join(lines))
```

### Metadata
- Source: error
- Related Files: nexus/security/__init__.py, nexus/adapters/multimodal/__init__.py
- Tags: python, indentation, heredoc, text_editor
- Pattern-Key: python.indentation_heredoc
- Recurrence-Count: 5
- First-Seen: 2026-04-09
- Last-Seen: 2026-04-09

---
