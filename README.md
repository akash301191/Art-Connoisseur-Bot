# Art Connoisseur Bot

**Art Connoisseur Bot** is a smart Streamlit application that analyzes your uploaded artwork to uncover its artistic style, historical context, and visual influences. Powered by [Agno](https://github.com/agno-agi/agno), OpenAI's GPT-4o, and SerpAPI, the bot generates a beautifully structured art brief with style analysis, interpretation, and curated references.


## Folder Structure

```
Art-Connoisseur-Bot/
├── art-connoisseur-bot.py
├── README.md
└── requirements.txt
```

* **art-connoisseur-bot.py**: The main Streamlit application.
* **requirements.txt**: Required Python packages.
* **README.md**: This documentation file.



## Features

* **Artwork Profile Input**
  Upload an artwork image and (optionally) provide the artist's name, title, source, and origin to enrich the analysis.

* **AI-Powered Visual Analysis**
  The **Art Style Analyzer** examines the image to identify its likely art style and visual characteristics, including brushwork, form, and era-specific traits.

* **Web-Based Research**
  The **Art Research Assistant** crafts focused Google searches using SerpAPI to fetch relevant pages, essays, and galleries for further reference.

* **Structured Art Brief**
  The **Art Report Generator** compiles a cohesive Markdown-style report that includes detected style, artist commentary, historical context, visual interpretation, and curated reference links.

* **Clean Markdown Output**
  Your report is generated in easy-to-read Markdown format with section headers, short paragraphs, and embedded links.

* **Download Option**
  Download the final artwork brief as a `.md` file to save, study, or share.

* **Streamlined Streamlit UI**
  Built using Streamlit for a clean, responsive, and user-friendly interface.



## Prerequisites

* Python 3.11 or higher
* An OpenAI API key ([Get one here](https://platform.openai.com/account/api-keys))
* A SerpAPI key ([Get one here](https://serpapi.com/manage-api-key))



## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/akash301191/Art-Connoisseur-Bot.git
   cd Art-Connoisseur-Bot
   ```

2. **(Optional) Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate        # On macOS/Linux
   # or
   venv\Scripts\activate           # On Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```



## Usage

1. **Run the app**:

   ```bash
   streamlit run art-connoisseur-bot.py
   ```

2. **In your browser**:

   * Upload an artwork image and optionally fill in details like artist and title.
   * Add your OpenAI and SerpAPI keys in the sidebar.
   * Click **🎨 Generate Artwork Report**.
   * View your generated art brief and explore the structured insights.

3. **Download Option**
   Use the **📥 Download Artwork Report** button to save your personalized `.md` report.



## Code Overview

* **`render_artwork_profile()`**: Collects artwork image and optional metadata like artist name, title, and context.
* **`render_sidebar()`**: Lets users enter OpenAI and SerpAPI keys, stored in session state.
* **`generate_artwork_report()`**:

  * Uses the **Art Style Analyzer** to interpret the artwork visually.
  * Calls the **Art Research Assistant** to gather relevant web resources.
  * Uses the **Art Report Generator** to compose the final structured brief.
* **`main()`**: Handles app layout, event handling, and display logic.


## Contributions

Contributions are welcome! Feel free to fork the repo, suggest features, report bugs, or open a pull request. Please ensure your changes are clean, tested, and aligned with the project’s purpose.
