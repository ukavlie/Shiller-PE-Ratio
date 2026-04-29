# Shiller CAPE & Market Regimes

An empirical analysis of Robert Shiller's Cyclically Adjusted Price-to-Earnings
ratio (CAPE) as a predictor of long-run equity returns and market stress regimes.
Data spans January 1871 to present, fetched directly from Shiller's dataset via API.

## Motivation

This project grew out of a personal interest in understanding how macroeconomic
valuation signals translate into measurable market outcomes. CAPE is one of the
most studied long-run return predictors in empirical finance, and combining it
with unsupervised regime detection felt like a natural extension — moving from
"what does valuation predict on average?" to "does valuation tell us something
about the *type* of market environment we are heading into?"

## Structure

The analysis is organised into seven sections:

1. **Data import & validation** — fetches Shiller's Excel dataset via HTTP,
   handles multi-row headers, fractional date encoding, and validates uniqueness
   and monotonicity of the date index.

2. **Exploratory data analysis** — visualises CAPE over time with annotated
   historical peaks (1929, dot-com, 2021), scatter plots of CAPE against forward
   10-year equity and bond returns, and distribution analysis motivating the
   log-transformation of CAPE.

3. **Regression modelling** — OLS regression of log(CAPE) on forward 10-year
   equity returns, with Newey-West (HAC) standard errors using `maxlags=120` to
   correct for the autocorrelation induced by overlapping 10-year windows. A
   non-parametric CAPE quintile analysis provides an intuitive complement to the
   regression.

4. **Interaction with inflation** — tests whether the CAPE–return relationship
   varies across inflation regimes using a CAPE × inflation interaction model
   with HAC standard errors, visualised as a median return heatmap across
   CAPE quintiles and inflation terciles.

5. **Hidden Markov Model** — fits a two-state Gaussian HMM on monthly log
   returns, bond returns, and realised volatility to identify latent market
   regimes (*calm* and *stress*) without supervision. Includes transition matrix
   analysis, implied regime durations, and a three-panel time series
   visualisation of regimes over the full 150-year sample.

6. **CAPE as a predictor of stress** — merges the HMM regime labels with the
   CAPE series and tests the relationship via logistic regression and distributional
   comparison. Finds a spurious negative contemporaneous relationship driven by
   the mechanical co-movement of falling prices, falling CAPE, and rising stress.

7. **Lagged CAPE as a leading indicator** — addresses the contemporaneous bias
   by lagging CAPE across horizons of 1, 6, 12, 24, and 36 months. Finds that
   the predictive relationship inverts at 24 months and becomes strongly positive
   and statistically significant at 24–36 months (p < 0.05), with AUC consistently
   above 0.50 across all horizons. This is consistent with the broader empirical
   finance literature: CAPE is a medium-term vulnerability indicator, not a
   short-term timing tool.

## Key Findings

- Log(CAPE) explains a meaningful share of the variation in forward 10-year
  equity returns. The relationship is robust to HAC correction.
- High inflation dampens returns at all CAPE levels; the interaction effect is
  most pronounced in expensive markets.
- The HMM cleanly identifies two persistent regimes. Stress regimes are
  characterised by roughly double the volatility and near-zero or negative
  returns, and align with known historical crises.
- Contemporaneous CAPE is negatively associated with stress — a mechanical
  artefact of prices falling during crises.
- Lagged CAPE turns positive and significant at 24–36 month horizons,
  suggesting elevated valuations increase market vulnerability on a 2–3 year
  horizon even if short-term timing is uninformative.

## Methods & Tools

- **Python**: pandas, numpy, statsmodels, seaborn, matplotlib, hmmlearn, scikit-learn
- **Econometrics**: OLS, Newey-West HAC, logistic regression, interaction models
- **Machine learning**: Gaussian Hidden Markov Model (Baum-Welch / Viterbi)
- **Data**: Robert Shiller's *Irrational Exuberance* dataset (1871–present)
