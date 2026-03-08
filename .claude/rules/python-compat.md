# Python Compatibility

- Project targets Python 3.13. Be aware of breaking changes:
  - `@classmethod @property` chaining is broken — use `@classmethod` with explicit `()` calls instead.
  - `greenlet` must be >= 3.1.1 (3.0.x fails to compile on 3.13).
- Always iterate defensively over query results that may return None on empty DB (use `or []` guards).
