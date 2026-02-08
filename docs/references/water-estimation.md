# References: Water Estimation Feature

Sources consulted during design and implementation of the water usage metric.

## Research Papers

- **Li, P., Yang, J., Islam, M.A., Ren, S. (2023). "Making AI Less Thirsty: Uncovering and Addressing the Secret Water Footprint of AI Models."**
  https://arxiv.org/abs/2304.03271
  Primary reference for the water estimation methodology. Provided the formula relating energy consumption to water usage via PUE, WUE (site), and WUE (source). The ~16.9 mL per medium response figure at U.S. averages comes from this paper. Used for: formula design, default environmental factor values, overall framing of the feature.

## Industry Data & Standards

- **Anthropic Pricing Documentation**
  https://docs.anthropic.com/en/docs/about-claude/pricing
  Used for: model tier classifications (opus/sonnet/haiku) that informed relative energy estimates across the Claude model family.

- **OpenAI API Pricing**
  https://openai.com/api/pricing/
  Used for: model tier classifications (GPT-5.x, GPT-4.x, o-series) that informed relative energy estimates across the OpenAI model family.

- **Google DeepMind / IEA estimates on AI energy consumption**
  General industry reporting on energy per inference for large language models. Used for: ballpark Wh-per-million-token values. Specific energy_per_mtok numbers are rough estimates derived from published benchmarks and should be treated as approximations.

## Standards & Definitions

- **PUE (Power Usage Effectiveness)** — The Green Grid / ISO/IEC 30134-2
  Ratio of total facility energy to IT equipment energy. Industry average ~1.2, hyperscaler best ~1.1. Used for: default PUE value of 1.2.

- **WUE (Water Usage Effectiveness)** — The Green Grid
  On-site WUE measures liters of water per kWh for cooling. U.S. average ~1.8 L/kWh. Used for: default wue_site value of 1.8.

- **WUE source (upstream water intensity of electricity)** — U.S. EIA / lifecycle analysis data
  Water consumed per kWh of electricity generation (thermal plants, hydroelectric). U.S. average ~0.5 L/kWh. Used for: default wue_source value of 0.5.

## Design Decisions Informed by Sources

| Decision | Source |
|----------|--------|
| Formula structure (energy -> water via PUE/WUE) | Li et al. 2023 |
| Default PUE = 1.2 | The Green Grid industry average |
| Default WUE site = 1.8 L/kWh | The Green Grid U.S. average |
| Default WUE source = 0.5 L/kWh | U.S. EIA lifecycle data |
| All token types contribute equally to energy | Li et al. 2023 (energy scales with compute, not token direction) |
| Best-effort approach (return 0 for unknown models) | Design choice — water data less standardized than pricing |
| Energy values are Wh per million tokens | Derived from published GPU power benchmarks, not directly from providers |

## Caveats

The energy_per_mtok values in `src/tokenmeter/water/_data.py` are rough estimates. Actual energy consumption depends on hardware (GPU type, batch size), data center location, time of day, and cooling infrastructure. Providers do not publish per-request energy data. These values should be updated as better data becomes available.
