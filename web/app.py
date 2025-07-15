import sys
import os
import tempfile
import io
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_flow import run_scheduling

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit uploads to 2MB


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        duration = int(request.form.get('duration', 30))
        alice_file = request.files['alice_file']
        bob_file = request.files['bob_file']

        if not alice_file or not bob_file:
            result = "❌ Please upload both Alice and Bob's calendar files."
            return render_template('index.html', result=result)

        # Save uploaded files to a temporary directory
        temp_dir = tempfile.gettempdir()
        alice_path = os.path.join(temp_dir, secure_filename(alice_file.filename))
        bob_path = os.path.join(temp_dir, secure_filename(bob_file.filename))

        alice_file.save(alice_path)
        bob_file.save(bob_path)

        # Run scheduling and capture output
        buffer = io.StringIO()
        sys.stdout = buffer
        run_scheduling(alice_path, bob_path, min_duration=duration)
        sys.stdout = sys.__stdout__
        result = buffer.getvalue()

        # Debug: Confirm PDF exists
        pdf_dir = os.path.join(app.root_path, 'static', 'pdfs')
        alice_pdf = os.path.join(pdf_dir, 'alice_updated.pdf')
        bob_pdf = os.path.join(pdf_dir, 'bob_updated.pdf')
        print(f"✅ PDF Exists Check:\n  - Alice → {os.path.exists(alice_pdf)} | Path: {alice_pdf}\n  - Bob   → {os.path.exists(bob_pdf)} | Path: {bob_pdf}")

    return render_template('index.html', result=result)


# ✅ Route to download generated PDF
@app.route('/download/<filename>')
def download_pdf(filename):
    pdf_dir = os.path.join(app.root_path, 'static', 'pdfs')
    file_path = os.path.join(pdf_dir, filename)
    

    if not os.path.isfile(file_path):
        print(f"❌ PDF Not Found at: {file_path}")
        return f"❌ File {filename} not found at {file_path}", 404

    print(f"📥 Downloading → {file_path}")
    return send_from_directory(pdf_dir, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

