import traceback
from flask import Flask, render_template, request, jsonify
from tester import ClickableElementTester # Import the class from your file

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/test_url', methods=['POST'])
def run_test():
    """
    Receives a URL from the frontend, runs the test,
    and returns the results as JSON.
    """
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required.'}), 400

    # IMPORTANT: Change to headless=False for debugging pop-ups!
    # Once fixed, you can change it back to headless=True.
    tester = ClickableElementTester(headless=False, timeout=15, max_workers=3)
    
    try:
        print(f"🚀 Starting test for URL: {url}")
        results = tester.run_comprehensive_test_concurrent(url)
        # results = tester.run_comprehensive_test(url)
        print(f"✅ Test finished for URL: {url}")
        return jsonify(results)
    except Exception as e:
        print(f"❌ An error occurred during the test for {url}: {e}")
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        # Always close the driver to prevent zombie processes
        tester.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)