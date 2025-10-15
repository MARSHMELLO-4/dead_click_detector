import traceback
import logging
from flask import Flask, render_template, request, jsonify
from tester import ClickableElementTester  # Import your testing class

# Initialize Flask app
app = Flask(__name__)

# Setup logging for better debugging in production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()          # Log to console (for Render/Vercel)
    ]
)

@app.route('/')
def index():
    """Render the main frontend HTML page."""
    return render_template('index.html')

@app.route('/test_url', methods=['POST'])
def run_test():
    """
    Receives a URL from the frontend, runs the ClickableElementTester,
    and returns the test results as JSON.
    """
    data = request.get_json(silent=True) or {}

    url = data.get('url')
    if not url:
        logging.warning("Missing URL in request.")
        return jsonify({'error': 'URL is required.'}), 400

    # Initialize tester with safe defaults
    tester = ClickableElementTester(
        headless=True,       # Keep headless=True for production
        timeout=15,
        max_workers=3
    )

    try:
        logging.info(f"🚀 Starting test for URL: {url}")
        results = tester.run_comprehensive_test_concurrent(url)
        logging.info(f"✅ Test finished successfully for URL: {url}")
        return jsonify(results), 200

    except Exception as e:
        logging.error(f"❌ Error during test for {url}: {e}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

    finally:
        # Ensure browser/driver is closed even on failure
        try:
            tester.close()
            logging.info("🧹 Browser driver closed successfully.")
        except Exception as close_err:
            logging.warning(f"⚠️ Error closing driver: {close_err}")

# ✅ Make app callable for Vercel or Gunicorn
# Render/Vercel looks for a variable named `app`
if __name__ == "__main__":
    # For local testing / Render
    app.run(debug=True, host="0.0.0.0", port=5000)
