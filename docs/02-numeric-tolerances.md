# 02 · Machine-Checkable Numeric Tolerances

When the correct answer is a number, "the model got it right" must mean "the number is inside a stated tolerance band", not "it looks close". Single expected values fail for three boring reasons: intermediate rounding, legitimate method variance, and unit confusion. Tolerance specs fix all three.

## Band types

| Type | Meaning | Use when | Example |
|---|---|---|---|
| `absolute` | ± fixed amount | Small numbers, counts | `{"type":"absolute","value":50}` on an expected 1,250 |
| `relative` | ± fraction of expected | Large or scale-dependent numbers | `{"type":"relative","value":0.02}` = within 2% |
| `points` | percentage-point difference | Comparing percentages/rates | expected 12.4%, answer 13.1% → 0.7 **pp** |
| `interval` | explicit `[low, high]` | Method variance known in advance | `{"type":"interval","low":118,"high":126}` |
| `set` | exact set match | Labels, tickers, line items | `{"type":"set","values":["A","C"]}` |

## The `pp` ≠ `%` trap

If the correct answer is "unemployment rose **by 2 percentage points**" (from 4% to 6%), an answer saying "rose by **50%**" is arithmetically true and completely wrong. Same family of trap: "2x increase" vs "increased to 2x". When a task involves rates, write the unit into the hard constraint and the tolerance spec separately.

## Layered strictness

Not every number in a chain deserves the same band:

```text
Intermediate value (e.g., subtotal)   → relative 5%
Derived ratio (e.g., margin)          → relative 2%
Final decision number (e.g., bid)     → points 0.5 pp or absolute, tightest
Unit / sign / currency                → hard constraint, exact
```

Rationale: intermediate rounding compounds; final answers should not. A model that rounds a subtotal to 1,200.4 vs 1,200.0 is fine; a model that lands 3 pp away from the final margin is not.

## Spec format

One JSON object per checked quantity, kept in the judge namespace (see [03 · Contamination Control](03-contamination-control.md)):

```json
{
  "id": "Q2-final-margin",
  "expected": 12.4,
  "spec": {"type": "points", "value": 0.5},
  "unit": "percentage points",
  "on_fail": "cap_total_at",
  "cap": 40
}
```

`tools/tolerance_check.py` implements exactly this format:

```bash
# 12.8 is 0.4 pp off  -> PASS (within 0.5 pp)
python tools/tolerance_check.py \
  --expected 12.4 --spec '{"type":"points","value":0.5}' --answer 12.8

# 13.0 is 0.6 pp off  -> FAIL (outside 0.5 pp)
python tools/tolerance_check.py \
  --expected 12.4 --spec '{"type":"points","value":0.5}' --answer 13.0
```

Run every band against one passing and one failing borderline answer before shipping. If you cannot construct a failing case for a band, the band is too loose to be meaningful.

## Sanity checks

1. **Unit test the spec, not just the code**: feed the spec one answer 0.4 pp off (should pass) and one 0.6 pp off (should fail).
2. **Method variance audit**: if two defensible methods give 12.1 and 12.9, an expected of 12.4 with ±0.5 pp fails a correct answer. Either widen to an `interval` band or pin the method in the prompt.
3. **Sign and magnitude**: `{"type":"absolute","value":5}` passes on both −1250 and +1250. If sign matters, make it a hard constraint.
