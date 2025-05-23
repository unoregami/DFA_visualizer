import graphviz
import time
import os # Added for os.path.join

# Creates the DFA using edges only
def createEdge(dot, i, nodes, a): #dot-digraph | i-present node | nodes-whole dfa | a-alphabets
    edges = nodes.get(i)
    # Ensure all nodes are declared to avoid issues with styling later
    if i != '-': # The '-' node is special and handled differently
        dot.node(str(i)) # Declare node `i`
    
    if type(edges) == list:
      # Ensure target nodes are also declared
      if edges[0] is not None: dot.node(str(edges[0]))
      if edges[1] is not None: dot.node(str(edges[1]))
      dot.edge(str(i), str(edges[0]), a[0])
      dot.edge(str(i), str(edges[1]), a[1])
    else:
      if edges is not None: dot.node(str(edges))
      dot.edge(str(i), str(edges), f"{a[0]},{a[1]}")
    
    if i == 'T': # Explicit trap state
      dot.edge(str(i), str(i), f"{a[0]},{a[1]}")
      return None

# Tracks input and validate if accepted or not
def movement(inp, nodes, es):  #inp-input | es-end state
  pN = '-' # Present Node starts at the conventional start symbol '-'
  node_way = [pN] # Initialize node_way with the starting node
  
  for char_in_input in inp:
    cNs = nodes.get(pN) # Get transitions for the current present node pN
    
    # print(f'{pN} {char_in_input}',end='-> ') # For debugging

    if pN.startswith('T') and pN != '-': # If in a Trap state (and not the start symbol '-')

      pass # No state change, but record it in node_way later

    if type(cNs) == list:
      if char_in_input == 'a' or char_in_input == '0':
        pN = cNs[0]
      elif char_in_input == 'b' or char_in_input == '1':
        pN = cNs[1]
      else:
        # Invalid input character for this DFA's alphabet
        # print(f"Invalid character '{char_in_input}' for DFA. Processing stops.")
        # pN = "ERROR_INVALID_CHAR" # Or some other error state
        break # Stop processing
    elif cNs is not None: # Single transition string (e.g., 'q6': 'q7')
      pN = cNs
    else:
      # No transition defined from pN (should ideally be a trap state)
      # print(f"No transition from {pN} on any char. DFA stuck.")
      # pN = "ERROR_STUCK"
      break # Stop processing
    
    node_way.append(pN)

  # print(f'{pN}',end=' = ') # For debugging
  
  final_state_achieved = node_way[-1] # The last state reached
  accepted = False
  if isinstance(es, list):
    accepted = final_state_achieved in es
  else:
    accepted = final_state_achieved == es
  
  # if accepted: # For debugging
  #   print('Accepted')
  # else:
  #   print('Rejected')
  
  return node_way, accepted # Return the path and the boolean acceptance

# Visualize the actual DFA graph movement
def visualize(node_way, dot_template, es_nodes, output_dir='static'):
  for end_node in es_nodes:
      try:
          dot_template.node(str(end_node), shape='doublecircle')
      except: # Broad except, but graphviz might raise if node not found
          # print(f"Warning: Could not mark end state {end_node}, may not exist in graph.")
          pass

  bN = None # Before Node for un-highlighting

  for step_index, current_node_in_path in enumerate(node_way):
    # Create a fresh copy of the dot_template for each step to avoid cumulative styling
    step_dot = dot_template.copy()

    # Un-highlight the previous node (bN) if it exists
    if bN is not None:
        try:
            step_dot.node(str(bN), fillcolor='white') # Reset to default
        except: pass

    # Highlight the current node in the path
    try:
        step_dot.node(str(current_node_in_path), fillcolor='#0000ffa4') # Highlight current
    except: pass
    
    bN = current_node_in_path # Update beforeNode for the next iteration

    # Save SVG for this step
    # Graphviz's render function automatically adds the extension if not present in filename
    # It saves to `os.path.join(output_dir, f'dfa_step{step_index}.svg')`
    try:
        step_dot.render(filename=os.path.join(output_dir, f'dfa_step{step_index}'), format="svg", cleanup=True, view=False)
    except Exception as e:
        # print(f"Error rendering static/dfa_step{step_index}.svg: {e}")
        # Create a dummy SVG on error to prevent 404s and indicate issue
        with open(os.path.join(output_dir, f'dfa_step{step_index}.svg'), "w") as f_err:
            f_err.write(f'<svg width="200" height="100"><text x="10" y="50" fill="red">Error: {e}</text></svg>')


  # After the loop, generate the final state SVG with accept/reject bgcolor
  # This will be the (L+1)-th SVG, but its name will be dfa_stepL.svg if L = len(user_input)
  # The last SVG generated in the loop *is* the final state. We just need to update its styling.
  final_state_dot = dot_template.copy()
  
  # Un-highlight previous from loop if any (should be current_node_in_path)
  if bN is not None:
      try:
        final_state_dot.node(str(bN), fillcolor='white')
      except: pass

  final_state_achieved = node_way[-1]
  accepted = False
  if isinstance(es_nodes, list):
      accepted = final_state_achieved in es_nodes
  else:
      accepted = final_state_achieved == es_nodes

  if accepted:
    try:
        final_state_dot.node(str(final_state_achieved), fillcolor='#02e002') # Green for accept
    except: pass
    final_state_dot.attr(bgcolor='#8acd8a')
  else:
    try:
        final_state_dot.node(str(final_state_achieved), fillcolor='red') # Red for reject
    except: pass
    final_state_dot.attr(bgcolor='#f8a1a1')
  
  # Overwrite the last SVG (dfa_stepL.svg) with this final styling
  # step_index after loop would be len(node_way) - 1, which is L if len(user_input) = L
  final_svg_index = len(node_way) - 1
  try:
    final_state_dot.render(filename=os.path.join(output_dir, f'dfa_step{final_svg_index}'), format="svg", cleanup=True, view=False)
  except Exception as e:
    # print(f"Error rendering final styled static/dfa_step{final_svg_index}.svg: {e}")
    with open(os.path.join(output_dir, f'dfa_step{final_svg_index}.svg'), "w") as f_err:
        f_err.write(f'<svg width="200" height="100"><text x="10" y="50" fill="red">Error final: {e}</text></svg>')


# Removed update function as its logic is incorporated into visualize loop

def run_dfa(dfa_choice, user_input):
    dfa = {}
    es = None # End states
    alphabet_symbols = []

    if dfa_choice == "1":
        # Using SVG format directly for web
        dot_template = graphviz.Digraph('DFA1_Structure', format='svg', strict=True)
        dot_template.attr(rankdir='LR', concentrate='true')
        dot_template.node_attr.update(style='filled', fillcolor='white', shape='circle', fontname='Calibri')
        dfa = {
            '-': ['q2','q1'], 'q1': ['T','q3'], 'q2': ['q3','T1'], 'q3': ['q5','q4'],
            'q4': ['q6','q20'], 'q5': ['q34','q6'], 'q6': 'q7', 'q7': ['q9','q8'],
            'q8': ['q10','q11'], 'q9': ['q11','T2'], 'q10': ['T2','q11'],
            'q11': ['q12','q11'], 'q12': ['T3','q13'], 'q13': ['q14','q13'],
            'q14': ['q15','T4'], 'q15': ['q17','q16'], 'q16': ['q17','q18'],
            'q17': ['q19','q16'], 'q18': ['q17','q18'], 'q19': ['q19','q16'],
            'q20': ['q22','q21'], 'q21': ['q24','q23'], 'q22': ['q25','q23'],
            'q23': ['q27','q26'], 'q24': ['q26','q7'], 'q25': ['q26','q35'],
            'q26': ['q31','q26'], 'q27': ['q29','q28'], 'q28': ['q30','q26'],
            'q29': ['q26','q35'], 'q30': ['q9','q32'], 'q31': ['q26','q32'],
            'q32': ['q33','q32'], 'q33': ['q15','q32'], 'q34': ['q36','q35'],
            'q35': ['q37','q38'], 'q36': ['q44','q45'], 'q37': ['q51','q7'],
            'q38': ['q39','q38'], 'q39': ['q25','q40'], 'q40': ['q41','q42'],
            'q41': ['q9','q43'], 'q42': ['q53','q42'], 'q43': ['q54','q43'],
            'q44': ['q46','q35'], 'q45': ['q50','q51'], 'q46': ['q48','q47'],
            'q47': ['q49','q47'], 'q48': ['q48','q43'], 'q49': ['q52','q43'],
            'q50': ['q9','q42'], 'q51': ['q52','q51'], 'q52': ['q11','q43'],
            'q53': ['T5','q43'], 'q54': ['q15','q43'],
            # Explicitly define Trap states if they should appear in the diagram
            'T': ['T','T'], 'T1':['T1','T1'], 'T2':['T2','T2'], 'T3':['T3','T3'],
            'T5':['T5','T5'] # Is T5 an accept or trap? If accept, add to es.
        }
        es = ['q19','q18'] # Assuming T5 is an accept state for DFA1. Adjust if not.
        alphabet_symbols = ['0', '1']
        for i in dfa:
            createEdge(dot_template, i, dfa, alphabet_symbols)

    elif dfa_choice == "2":
        dot_template = graphviz.Digraph('DFA2_Structure', format='svg', strict=True)
        dot_template.node_attr.update(style='filled', fillcolor='white', shape='circle')
        dot_template.attr(rankdir='LR', layout='circo') # Consider 'dot' layout for consistency if 'circo' is problematic
        dfa = {
            '-': 'q1', 'q1': 'q2', 'q2': 'q3', 'q3': ['q4', 'q5'],
            'q4': ['q6', 'q5'], 'q5': ['q4', 'q6'], 'q6': 'q6'
        }
        # Corrected transitions for q1 and q2 to be lists if they respond to 'a' and 'b'
        # If 'q1':'q2' means q1 on 'a' -> q2 AND q1 on 'b' -> q2, then:
        dfa = {
            '-': 'q1', 'q1': 'q2', 'q2': 'q3', 'q3': ['q4', 'q5'],
            'q4': ['q6', 'q5'], 'q5': ['q4', 'q6'], 'q6': ['q6', 'q6']
        }
        es = 'q6' # This should be a list: es = ['q6'] for consistency
        if not isinstance(es, list): es = [es] # Ensure es is a list
        alphabet_symbols = ['a', 'b']
        for i in dfa:
            createEdge(dot_template, i, dfa, alphabet_symbols)
    else:
        # Return 0 for num_steps to avoid JS errors
        return [], None, 'Invalid DFA choice.', 0

    # dot_template.save("dfa_template.dot","./") # For debugging the base graph

    node_way, accepted_bool = movement(user_input, dfa, es)
    
    # Call visualize to generate all dfa_stepX.svg files
    # 'es' (end states) must be a list for visualize
    visualize(node_way, dot_template, es if isinstance(es, list) else [es], output_dir='static')
    
    result_str = 'Accepted' if accepted_bool else 'Rejected'
    
    # num_steps for JS is len(user_input).
    # If user_input is "101" (length 3), node_way will be ['-', 's1', 's2', 's3'] (length 4).
    # SVGs generated: dfa_step0.svg, dfa_step1.svg, dfa_step2.svg, dfa_step3.svg.
    # So, num_steps to return to JS should be len(user_input).
    num_steps_for_js = len(user_input)
    
    # The `es` in the return tuple is the original end state definition.
    # The `node_way` is the actual path.
    return node_way, es, result_str, num_steps_for_js


# Only run interactively if called directly
if __name__ == "__main__":
    dfa_choice_input = input("DFA (1 or 2): ").lower()
    user_input_str = input("Test input: ").lower()
    
    # Example: Clean up old SVGs before a test run (mimicking Flask app's behavior)
    static_dir = 'static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    else:
        for fname in os.listdir(static_dir):
            if fname.startswith('dfa_step') and fname.endswith('.svg'):
                try:
                    os.remove(os.path.join(static_dir, fname))
                except Exception as e:
                    # print(f"Could not remove {fname}: {e}")
                    pass

    n_w, e_s, res, n_s = run_dfa(dfa_choice_input, user_input_str)
    print(f"\n--- Results from run_dfa ---")
    print(f"Node Way: {n_w}")
    print(f"End States Def: {e_s}")
    print(f"Result: {res}")
    print(f"Num_steps for JS: {n_s}")
    print(f"Expected SVG files in 'static/' folder: dfa_step0.svg to dfa_step{n_s}.svg")
