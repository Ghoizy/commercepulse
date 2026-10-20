from math import sqrt

# Jumlah pesanan dengan rating rendah
low_on_time = 8290
low_late = 3982

# Total pesanan yang mempunyai review
n_on_time = 89443
n_late = 6381

# Proporsi rating rendah
p_on_time = low_on_time / n_on_time
p_late = low_late / n_late

# Risk difference dan risk ratio
risk_difference = p_late - p_on_time
risk_ratio = p_late / p_on_time

# Standard error untuk selisih proporsi
se = sqrt(
    p_late * (1 - p_late) / n_late
    + p_on_time * (1 - p_on_time) / n_on_time
)

# Confidence Interval 95% (aproksimasi normal)
ci_lower = risk_difference - 1.96 * se
ci_upper = risk_difference + 1.96 * se

print(f"Risk difference: {risk_difference * 100:.2f} pp")
print(f"Risk ratio: {risk_ratio:.2f}x")
print(
    f"95% CI difference: "
    f"[{ci_lower * 100:.2f}, {ci_upper * 100:.2f}] pp"
)