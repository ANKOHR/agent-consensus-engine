# Lessons for KOML

Exact voting is useful for structured answers but cannot certify factual correctness or agent independence. A strict majority must still be reported as incorrect when it conflicts with an explicit truth label.

The tested assumption is that planted voting cases can be aggregated deterministically and traced exactly. The synthetic test suite validates that assumption; it does not validate demand, productivity savings, or real-world accuracy. Deliberately changing one fixture truth label changes the audit from 120 to 119 correct decisions and introduces one incorrect decision.

Operating rule: keep expectations independent of implementation, mutate ground truth in a test, and ship unresolved cases explicitly instead of forcing a winner. Measure real-use error against human labels before expanding this tool.
