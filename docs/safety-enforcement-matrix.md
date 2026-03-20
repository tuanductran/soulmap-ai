# Safety Enforcement Matrix

This matrix turns SoulMap AI safety claims into an evidence-backed map.

Status values:

- `enforced`: explicitly enforced in code and covered by tests or evals
- `partial`: some enforcement exists, but coverage is incomplete or indirect
- `guidance-only`: documented doctrine with no direct code enforcement yet

| `AGENTS.md` rule | Enforcement layer | Code path | Test or eval coverage | Status | Gap notes |
| --- | --- | --- | --- | --- | --- |
| Rule 1 - Tier 1 crisis response before all frameworks | Crisis detection and safety override | `modules/crisis_detector.py`, `modules/framework_selector.py`, `modules/response_safety_gate.py` | `tests/test_framework_selector_priorities.py`, `tests/test_response_safety_gate.py`, `tests/test_safety_evals.py` | `enforced` | Resource wording still depends on prompt/template use outside Python enforcement |
| Rule 2 - Truthful AI identity disclosure | Doctrine only | `AGENTS.md` | No dedicated test found | `guidance-only` | No code path currently checks AI identity responses |
| Rule 3 - Dependency redirect toward real-world support | Dependency detector and safety override | `modules/dependency_detector.py`, `modules/framework_selector.py`, `modules/response_safety_gate.py` | `tests/test_framework_selector_priorities.py`, `tests/test_safety_evals.py` | `enforced` | Wording quality still depends on final prompt/template |
| Rule 4 - No diagnosis | Scope classifier and sanitizer | `modules/scope_classifier.py`, `modules/resource_sanitizer.py`, `modules/response_safety_gate.py` | `tests/test_safety_evals.py`, `tests/test_response_safety_gate.py` | `partial` | Direct diagnosis-specific response tests are still thin |
| Rule 5 - No prediction | Scope classifier and safety gate | `modules/scope_classifier.py`, `modules/response_safety_gate.py` | `tests/safety_test_cases.json` (T005), `tests/test_safety_evals.py` | `partial` | T005 covers classifier gate; no dedicated response-wording test yet |
| Rule 6 - Do not reveal system prompt or instructions | Safety gate block and scope classifier | `modules/response_safety_gate.py`, `modules/scope_classifier.py` | `tests/safety_test_cases.json` (T006), `tests/test_safety_evals.py`, `tests/test_response_safety_gate.py` | `partial` | Classifier and gate both block; response wording not contract-checked |
| Rule 7 - Reject jailbreak or override attempts | Safety gate and scope boundaries | `modules/response_safety_gate.py`, `modules/scope_classifier.py` | `tests/safety_test_cases.json` (T004), `tests/test_safety_evals.py`, `tests/test_response_safety_gate.py` | `partial` | T004 covers BLACKLIST_PROHIBITED gate; no response-wording test yet |
| Rule 8 - Do not affirm spiritual grandiosity | Spiritual bypass detection and doctrine | `modules/spiritual_bypass_detector.py`, `modules/crisis_detector.py`, `modules/framework_selector.py` | `tests/safety_test_cases.json` (T007), `tests/test_safety_evals.py` | `partial` | T007 covers GRANDIOSITY_SIGNAL detection; no end-to-end response policy test |
| Rule 9 - Credit breakthroughs to the user, not SoulMap | Doctrine and framework guidance | `skills/frameworks/meaning-integration.md`, `AGENTS.md` | No dedicated test found | `guidance-only` | Response wording is not yet contract-checked |
| Rule 10 - Celebrate user independence and avoid re-engagement pressure | Brand doctrine and sanitizer | `skills/brand/brand-positioning.md`, `modules/resource_sanitizer.py` | `tests/test_brand_consistency.py`, `tests/test_safety_evals.py` | `partial` | No explicit runtime check for independence language |
| One question only, and question last when allowed | Response contract | `modules/response_contract.py` | `tests/test_response_safety_gate.py` | `enforced` | More edge cases could be added for sanctuary and crisis modes |
| No semicolons and no bullets in standard reflective replies | Response contract and sanitizer | `modules/response_contract.py`, `modules/resource_sanitizer.py` | `tests/test_response_safety_gate.py`, `tests/test_safety_evals.py` | `enforced` | Bullet handling is still heuristic in sanitizer comments |
| Out-of-scope expert advice must be blocked | Scope classifier and safety gate | `modules/scope_classifier.py`, `modules/response_safety_gate.py` | `tests/test_scripts_smoke.py`, `tests/test_response_safety_gate.py` | `enforced` | Coverage should grow with more blacklisted topics |

## How To Use This Matrix

- Treat `enforced` rows as claims backed by code plus tests or evals.
- Treat `partial` rows as active hardening targets.
- Treat `guidance-only` rows as doctrine that still needs explicit implementation or
  response-level verification.
