# NFL Big Data Bowl 2025 - Defensive Alignment Versatility Analysis

This project analyzes defensive alignment versatility in the NFL using tracking data from the NFL Big Data Bowl 2025. The analysis focuses on pre-snap defensive formations and their variations to create a comprehensive versatility index.

## Project Structure

```
.
├── src/
│   ├── data_loader.py        # Data loading and preprocessing
│   ├── alignment_analyzer.py  # Core defensive alignment analysis
│   ├── versatility_metrics.py # Versatility index calculations
│   └── visualization.py       # Visualization functions
├── notebooks/                 # Jupyter notebooks for analysis
├── requirements.txt          # Project dependencies
└── README.md                # Project documentation
```

## Features

- Pre-snap defensive formation analysis
- Defensive spacing and alignment metrics
- Formation transition analysis
- Versatility index calculation
- Visualization of defensive alignments and metrics

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Jupyter notebook:
   ```bash
   jupyter notebook
   ```

## Analysis Components

1. **Formation Analysis**
   - Classification of defensive formations
   - Formation variety metrics
   - Formation transition analysis

2. **Spacing Analysis**
   - Defensive spacing metrics
   - Player distribution analysis
   - Spacing versatility calculations

3. **Versatility Index**
   - Entropy-based formation variety
   - Spacing versatility
   - Formation transition rate
   - Combined versatility score

## Usage

Example notebook usage will be provided in the `notebooks/` directory.