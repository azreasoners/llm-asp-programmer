prompt_formatter = '''You are tasked with writing the answer set produced by running Clingo into a human-readable form.

Here is the problem description:
<PROB_DESC>

Clingo output:
<ANSWER_SET>
<DOMAIN_SPECIFIC_INSTRUCTIONS>
<INSTRUCTION>'''



# <DOMAIN_SPECIFIC_INSTRUCTIONS>



prompt_formatter_old = '''You are tasked with writing the answer set produced by running Clingo into a human-readable form.

Here is the problem description:
<PROB_DESC>
<DOMAIN_SPECIFIC_INSTRUCTIONS>
Clingo output:
<ANSWER_SET>

Your conversion should be encapsulated completely in 3 backticks, without any extraneous text. It should be in natural language, and precise. If the Clingo output is unsatisfiable, or the program produces an error, the write "UNSAT" or "ERROR" encapsulated in 3 backticks.'''



prompt_evaluator = '''You are tasked with checking whether a proposed answer is correct, by comparing to the ground truth. The form of the answer may differ, but the meaning should match. The proposed answer is produced from an answer set, so it may have extra information, only judge if it can be interpreted as matching the ground truth or not.

Original problem description:
<PROB_DESC>

Ground truth:
<GROUND_TRUTH>

Proposed answer:
<PROPOSED_ANSWER>

Respond ONLY with a single word either "CORRECT" or "WRONG".'''
