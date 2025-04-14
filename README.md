
<h1 align="center"> 
🏢 Are Paris and Lyon Still Monocentric Cities?
</h1>
</p>
<p align="center"> 
  <a href="https://github.com/jkengineer42/Urban-Economics">
    <img src="https://img.shields.io/github/contributors/jkengineer42/Urban-Economics.svg?style=for-the-badge" alt="Contributors" /> </a>
  <a href="https://github.com/jkengineer42/Urban-Economics">
    <img alt="Issues" src="https://img.shields.io/github/issues/jkengineer42/Urban-Economics?style=for-the-badge">
    </a>
  <a href="https://github.com/jkengineer42/Urban-Economics">
    <img alt="Forks" src="https://img.shields.io/github/forks/jkengineer42/Urban-Economics.svg?style=for-the-badge"></a>
  <a href="https://github.com/jkengineer42/Urban-Economics">
    <img alt="Stars" src="https://img.shields.io/github/stars/jkengineer42/Urban-Economics.svg?style=for-the-badge"></a>
  <a href="https://raw.githubusercontent.com/jkengineer42/Urban-Economics/master/LICENSE">
    <img src="https://img.shields.io/badge/License-BSD-blue?style=for-the-badge" alt="License" /> </a>
</p>

## 🎯 Project Goal

This project aims to study the evolution of the spatial distribution of jobs in the French metropolitan areas of **Paris** and **Lyon**, between **1968 and 2021**, to determine whether these cities still follow a **monocentric** model or are tending towards **polycentrism**.

The analysis is based on the theoretical framework of the **Alonso (1964) monocentric model**, compared with real-world data and map visualizations.

## 📁 Project Structure

```bash
Urban-Economics/
│
├── do/                  # Python scripts for processing and analysis
│   └── analysis.py
│
├── input/               # Excel files containing INSEE data
│
├── output/              # Results: graphs, maps, text files
│
├── Presentation.pdf     # Theoretical background and project presentation
│
├── requirements.txt     # Required libraries
│
└── LICENSE
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/jkengineer42/Urban-Economics.git
cd Urban-Economics
```

### 2. Install dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

Then install the required libraries:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

Run the main script:

```bash
python do/analysis.py
```

The results are generated in the `output/` directory as graphs (.png) and tables (.txt).

## 📊 Expected Results

- **Maps** of employment evolution in Paris and Lyon (1968, 1999, 2021)
- **Graphs** of employment concentration
- **Linear regression** of employment density as a function of distance to the center
- Comparison between the theoretical monocentric model and empirical observations

## 📘 Economic Theory

The project primarily relies on:

- **Alonso (1964)** – Monocentric model
- Concepts of **transport costs**, **decreasing rents**, and **bid-rent function**
- The model's limitations are discussed (polycentrism, household heterogeneity, temporal dynamics)

## 📖 Presentations

*   [View the presentation in English (PDF)](Presentation_en.pdf)
*   [Consulter la présentation en Français (PDF)](Presentation_fr.pdf)

## 👥 Authors

- Jérémie Konda
- Alexandre Klobb

## 📄 License

This project is licensed under the **BSD 2-Clause License**. See the [LICENSE](LICENSE) file for more information.
