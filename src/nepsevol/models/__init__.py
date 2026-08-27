"""Volatility models fitted in this project.

Two ideas drive the choice of models, and neither is GARCH:

1. **Future squared returns are a noisy but UNBIASED proxy for volatility.** So a
   forecast horse-race, scored with a proxy-robust loss, ranks estimators without
   ever observing true volatility. This is the answer to the project's central
   obstacle (charter Q1).

2. **A latent-state model identifies estimator bias from data.** If log-variance is
   an unobserved AR(1) and each estimator is a biased, noisy measurement of it, then
   the measurement intercepts ARE the biases -- estimated, not assumed from simulation.
"""
