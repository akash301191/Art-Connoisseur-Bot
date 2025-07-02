import tempfile
import streamlit as st

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.tools.serpapi import SerpApiTools

from textwrap import dedent

def render_sidebar():
    st.sidebar.title("🔐 API Configuration")
    st.sidebar.markdown("---")

    # OpenAI API Key input
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Don't have an API key? Get one [here](https://platform.openai.com/account/api-keys)."
    )
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.sidebar.success("✅ OpenAI API key updated!")

    # SerpAPI Key input
    serp_api_key = st.sidebar.text_input(
        "Serp API Key",
        type="password",
        help="Don't have an API key? Get one [here](https://serpapi.com/manage-api-key)."
    )
    if serp_api_key:
        st.session_state.serp_api_key = serp_api_key
        st.sidebar.success("✅ Serp API key updated!")

    st.sidebar.markdown("---")

def render_artwork_profile():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    # Column 1: Upload Artwork Image
    with col1:
        st.subheader("🖼️ Upload Artwork")
        uploaded_image = st.file_uploader(
            "Choose an artwork image",
            type=["jpg", "jpeg", "png"]
        )

    # Column 2: Artist and Title
    with col2:
        st.subheader("🧑‍🎨 Artwork Details")
        artist_name = st.text_input(
            "Do you know the name of the artist?", 
            placeholder="e.g., Claude Monet (optional)"
        )

        artwork_title = st.text_input(
            "Do you know the title of the artwork?",
            placeholder="e.g., Water Lilies (optional)"
        )

    # Column 3: Contextual Info
    with col3:
        st.subheader("📚 Context")
        source = st.selectbox(
            "Where did you come across this artwork?",
            [
                "Museum or gallery",
                "Online (website or blog)",
                "Social media",
                "Book or publication",
                "Personal collection",
                "Don’t remember"
            ]
        )

        artwork_origin = st.selectbox(
            "Is this a photo of a physical or digital artwork?",
            ["Physical Artwork", "Digital Artwork", "Not sure"]
        )

    return {
        "uploaded_image": uploaded_image,
        "artist_name": artist_name,
        "artwork_title": artwork_title,
        "source": source,
        "artwork_origin": artwork_origin
    }

def generate_artwork_report(artwork_profile):
    uploaded_image = artwork_profile["uploaded_image"]
    artist_name = artwork_profile["artist_name"]
    artwork_title = artwork_profile["artwork_title"]
    source = artwork_profile["source"]
    artwork_origin = artwork_profile["artwork_origin"]

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_image.getvalue())
        image_path = tmp.name

    # Step 1: Art Style Visual Analyzer
    art_analyzer = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state.openai_api_key),
        name="Art Style Analyzer",
        role="Analyzes a piece of artwork to determine its likely artistic style, notable visual characteristics, and possible historical context.",
        description=dedent("""
            You are an art analysis assistant. Examine the uploaded artwork image carefully.
            Identify the most likely art style or movement it belongs to (e.g., Impressionism, Cubism, Abstract).
            Describe prominent visual characteristics such as brushwork, color use, geometry, and composition.
            Optionally, suggest a possible historical period or art school association if clear indicators are present.
        """),
        instructions=[
            "Do not speculate if the image is unclear—remain grounded in visual evidence.",
            "Do not generate a full report—only return the raw insights and observations for downstream use.",
            "Focus on brushwork, use of light, composition, and artistic signature markers."
        ],
        markdown=True
    )

    visual_insights = art_analyzer.run(
        "Analyze the uploaded artwork and describe its likely art style, visual traits, and historical indicators.",
        images=[Image(filepath=image_path)]
    ).content    

    # Step 2: Art Research Agent
    art_search_agent = Agent(
        name="Art Research Assistant",
        role="Finds reliable online references to enrich a brief about an artwork’s style, artist, and historical context.",
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state.openai_api_key),
        description="Given visual analysis and optional metadata, generate a smart Google search to collect related resources.",
        instructions=[
            "Use the visual insights (e.g., detected art style, brushwork) as a starting point.",
            "If an artist or title is given, include that in the search query.",
            "Generate a focused Google search query like: 'Post-Impressionism Paul Cézanne Seine river painting'.",
            "Use SerpAPI to return 8–10 quality links (articles, museum pages, image collections, etc.) in markdown format.",
            "Avoid bold (**...**) formatting inside or around markdown links.",
            "Avoid placing parentheses or punctuation inside the [link title].",
            "If the link title includes parentheses or punctuation, move the title outside the link and place the raw link separately on the next line.",
            "Return one link per line in this format: Title: [text](URL)."
        ],
        tools=[SerpApiTools(api_key=st.session_state.serp_api_key)],
        tool_call_limit=3,
        markdown=True
    )

    # Prompt to guide the search agent
    search_prompt = f"""
    Artwork Visual Summary: {visual_insights}
    Artist Name: {artist_name if artist_name else 'Not provided'}
    Artwork Title: {artwork_title if artwork_title else 'Not provided'}
    Artwork Source: {source}
    Artwork Origin: {artwork_origin}

    Generate a smart Google search and return 8–10 links related to this artwork’s likely style, artist, or historical context.
    Ensure the markdown formatting is clean and display-safe.
    """

    research_links = art_search_agent.run(search_prompt).content

    # Step 3: Report Generator Agent
    report_generator = Agent(
        name="Art Report Generator",
        model=OpenAIChat(id="o3-mini", api_key=st.session_state.openai_api_key),
        role="Generates a structured art brief combining visual insights and research links into a coherent narrative.",
        description=dedent("""
            You are an art report generator. You are given:
            1. A visual analysis of an uploaded artwork.
            2. A set of curated online references about the artwork’s style, artist, and context.

            Your task is to generate a rich, structured markdown report titled '🖼️ Artwork Style Brief' that presents insights into the artwork’s style, possible historical connections, notable influences, and similar works.
        """),
        instructions=[
            "Start the report with: ## 🖼️ Artwork Style Brief",
            "",
            "### 🎨 Detected Art Style & Visual Traits",
            "- Summarize the likely art style (e.g., Post-Impressionism, Cubism).",
            "- Describe color use, brushwork, form, and composition based on the visual analysis.",
            "- Embed hyperlinks where relevant and useful (e.g., [Post-Impressionist techniques](https://...)).",
            "",
            "### 🧑‍🎨 Artist & Artwork Info",
            "- If the user has provided an artist name or artwork title, mention them clearly.",
            "- Briefly comment on whether the visual style aligns with the artist’s known work, if applicable.",
            "- Embed a relevant reference link such as a biography or museum listing if available.",
            "- If no artist or title is provided, acknowledge this fact and continue smoothly (e.g., 'The artist of this piece is unknown, but the style suggests influence from...').",
            "",
            "### 🕰️ Historical Context & Movement",
            "- Place the artwork within a likely historical period.",
            "- Mention cultural, social, or industrial influences associated with the style.",
            "- Add links to movement pages or historical context when appropriate.",
            "",
            "### 🖼️ Visual Themes & Interpretation",
            "- Offer a brief interpretation of the artwork’s subject matter or emotional tone.",
            "- Relate those themes to the broader art movement if relevant.",
            "- Embed references only when they contribute meaningfully.",
            "",
            "### 🔗 Curated References",
            "- List 6–8 helpful sources with clean markdown hyperlinks.",
            "- Do not include punctuation inside the link title.",
            "- Format links as: [Descriptive Title](https://...)",
            "",
            "**Important:** Embed helpful, relevant hyperlinks throughout the report—not just in the final section. Aim for 1–2 useful links in sections where they make sense. Do not force links where unnecessary.",
            "",
            "Write in an informed, thoughtful, and approachable tone suitable for art enthusiasts.",
            "Use markdown headings, bullet points, and short paragraphs for clarity.",
            "Output only the final Markdown-formatted report—do not explain your reasoning or structure."
        ],
        markdown=True,
        add_datetime_to_instructions=True
    )

    # Final prompt for report generator
    final_prompt = f"""
    Visual Analysis:
    {visual_insights}

    Artist: {artist_name or 'Not provided'}
    Title: {artwork_title or 'Not provided'}

    Web Research Resources:
    {research_links}

    Generate a markdown-formatted artwork style brief using this information.
    """

    final_report = report_generator.run(final_prompt).content
    
    return final_report 

def main() -> None:
    # Page config
    st.set_page_config(page_title="Art Connoisseur Bot", page_icon="🖼️", layout="wide")

    # Custom styling
    st.markdown(
        """
        <style>
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        div[data-testid="stTextInput"],
        div[data-testid="stRadio"],
        div[data-testid="stSelectbox"] {
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Header and intro
    st.markdown("<h1 style='font-size: 2.5rem;'>🎨 Art Connoisseur Bot</h1>", unsafe_allow_html=True)
    st.markdown(
        "Welcome to Art Connoisseur Bot — a smart Streamlit tool that analyzes your uploaded artwork to uncover its style, context, and artistic connections, bridging visual analysis with art history insight.",
        unsafe_allow_html=True
    )


    render_sidebar()
    user_artwork_profile = render_artwork_profile()

    st.markdown("---")

    # Call the report generation method when the user clicks the button
    if st.button("🎨 Generate Artwork Report"):
        if not hasattr(st.session_state, "openai_api_key"):
            st.error("Please provide your OpenAI API key in the sidebar.")
        elif not hasattr(st.session_state, "serp_api_key"):
            st.error("Please provide your SerpAPI key in the sidebar.")
        elif "uploaded_image" not in user_artwork_profile or not user_artwork_profile["uploaded_image"]:
            st.error("Please upload an artwork image before generating the report.")
        else:
            with st.spinner("Analyzing your artwork to generate your artwork report..."):
                report = generate_artwork_report(user_artwork_profile)

                st.session_state.art_report = report
                st.session_state.art_image = user_artwork_profile["uploaded_image"]

    # Display and download the report
    if "art_report" in st.session_state:
        st.markdown("## 🖼️ Uploaded Artwork")
        st.image(st.session_state.art_image, use_container_width=False)

        st.markdown(st.session_state.art_report, unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Artwork Report",
            data=st.session_state.art_report,
            file_name="artwork_style_brief.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
