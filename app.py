from flask import Flask, render_template, request, jsonify
from dfa_visualizer import run_dfa # Your existing DFA logic module
import os

app = Flask(__name__)

# It's good practice to set up logging, especially for errors.
# import logging
# if not app.debug:
#     # Configure your production logging here
#     pass


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', result=None)

@app.route('/user_manual', methods=['GET'])
def user_manual():
    return render_template('user_manual.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    data = request.get_json()
    user_input = data.get('input', '').lower()
    regex_id = str(data.get('regex_id', '1')) # Ensure regex_id is a string if run_dfa expects it

    # --- IMPORTANT: File Cleanup and Generation Order ---

    # 1. Define path to the static directory
    #    app.static_folder is usually 'static'. app.root_path is the app's root dir.
    static_dir_path = os.path.join(app.root_path, app.static_folder)

    # 2. Clean up step SVG files from the *previous* run *before* generating new ones.
    try:
        for fname in os.listdir(static_dir_path):
            if fname.startswith('dfa_step') and fname.endswith('.svg'): # Corrected to .svg
                try:
                    os.remove(os.path.join(static_dir_path, fname))
                except OSError as e:
                    app.logger.error(f"Error removing old step file {os.path.join(static_dir_path, fname)}: {e}")
                    # Depending on your error handling strategy, you might want to inform the user.
                    # For now, we'll log and attempt to continue.
    except FileNotFoundError:
        app.logger.error(f"Static directory not found at {static_dir_path}. Check Flask configuration.")
        return jsonify({'error': 'Server configuration error related to static files path.'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during file cleanup: {e}")
        return jsonify({'error': 'Server error during file cleanup.'}), 500

    # 3. Generate new DFA step files for the current input.
    #    ASSUMPTIONS for run_dfa(regex_id, user_input):
    #    a) It saves new SVG files named 'dfa_step0.svg', 'dfa_step1.svg', ..., 'dfa_stepL.svg'
    #       (where L is len(user_input)) into the 'static' directory (i.e., static_dir_path).
    #    b) It returns num_steps = L (the length of the user_input).
    #       This means L+1 SVG files are created (indices 0 to L).
    #    c) It handles user_input="" correctly (e.g., generates 'dfa_step0.svg', returns num_steps=0).
    try:
        node_way, es, result, num_steps = run_dfa(regex_id, user_input)
    except Exception as e:
        app.logger.error(f"Error executing run_dfa for input '{user_input}' and regex_id '{regex_id}': {e}")
        return jsonify({'error': 'Failed to process DFA visualization.', 'details': str(e)}), 500

    # Sanity check: num_steps should usually be len(user_input) based on common conventions.
    # If your run_dfa uses a different meaning for num_steps, ensure JS is aligned.
    if not isinstance(num_steps, int) or num_steps < 0:
        app.logger.error(f"run_dfa returned invalid num_steps: {num_steps}")
        return jsonify({'error': 'Invalid step count from DFA processing.'}), 500
    # If num_steps is strictly expected to be len(user_input):
    # if num_steps != len(user_input):
    #     app.logger.warning(f"Mismatch: num_steps ({num_steps}) vs len(user_input) ({len(user_input)}). JS might behave unexpectedly.")


    return jsonify({'result': result, 'num_steps': num_steps})

if __name__ == '__main__':
    # Consider adding host='0.0.0.0' if you need to access it from other devices on your network
    app.run(debug=True)