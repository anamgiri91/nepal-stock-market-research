"""NEPSE trading calendar.

NEPSE trades Sunday-Thursday. Friday sessions are rare specials (24 in 16 years);
Saturday never. Two consequences that every downstream module depends on:

1. The annualization factor is not 252.
2. The weekend gap is Thursday close -> Sunday open, so the overnight return that
   Yang-Zhang requires is not the standard Monday-Friday construction.

This package also owns the structural closures: the 2015 earthquake (31 days),
COVID-19 (~98 days across two 2020 gaps), and annual Dashain/Tihar closures.
"""
