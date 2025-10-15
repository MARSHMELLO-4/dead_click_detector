from flask import Flask, request, jsonify, render_template
from tester import ClickableElementTester  # If using locally
import traceback
import logging
import os

# Vercel-safe logging (console only)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "✅ Flask app is running on Vercel!"})

@app.route('/test_url', methods=['POST'])
def run_test():
    data = request.get_json(silent=True) or {}
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required.'}), 400

    # Detect if running on Vercel (no Selenium allowed)
    if os.environ.get("VERCEL"):
        logger.info("Running in Vercel environment — skipping Selenium test.")
        return jsonify({
            "status": "ok",
            "message": f"Received URL: {url} (Selenium test skipped on Vercel)"
        }), 200

    tester = ClickableElementTester(headless=True, timeout=15, max_workers=3)
    try:
        logger.info(f"🚀 Starting test for URL: {url}")
        results = tester.run_comprehensive_test_concurrent(url)
        logger.info(f"✅ Test finished for URL: {url}")
        return jsonify(results)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            tester.close()
            logger.info("🧹 Closed browser session.")
        except Exception as e:
            logger.warning(f"Error closing tester: {e}")

if __name__ == "__main__":
    app.run(debug=True)
