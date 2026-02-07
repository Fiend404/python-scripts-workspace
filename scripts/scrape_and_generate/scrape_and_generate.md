Script: scrape_and_generate.py
Location: scripts/scrape_and_generate/scrape_and_generate.py
Test: scripts/scrape_and_generate/test_scrape_and_generate.py

What it does:
1. Uses pydoll (async CDP browser) to navigate to --website_url and extract full page HTML
2. Saves raw HTML to --html_filepath
3. Sends the HTML + --context description to Gemini 2.0 Flash via google-genai
4. Gemini returns a BS4 parsing script tailored to extract the specified data
5. Strips markdown fences and saves the generated script to --output_python_script_filepath

Usage:
  export GOOGLE_API_KEY=your_key_here
  uv run python scripts/scrape_and_generate/scrape_and_generate.py \
      --website_url https://example.com \
      --context "all product names and prices" \
      --html_filepath output.html \
      --output_python_script_filepath parser.py

CLI Arguments:
  --website_url                    Target webpage URL to scrape
  --context                        Describe what data to extract
  --html_filepath                  File path to save raw HTML
  --output_python_script_filepath  File path to save generated Python script

Dependencies:
  pydoll-python    Async headless browser (CDP)
  google-genai     Gemini API client
  beautifulsoup4   HTML parsing (used in generated scripts)

Validation:
  Tests: 4/4 passed
  Analysis: 9/9 checks passed
  Ruff: clean

Requirements:
  GOOGLE_API_KEY environment variable must be set
