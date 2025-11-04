# LLM-ASP-Programmer

# Introduction
LLM coupled with ASP for complex reasoning.

## Repository Structure
Below is an overview of the directory structure and the purpose of each folder and file:
```
llm-asp-programmer/
├── envs/                      # Contains files for running domains.
├── resources/                 # Contains resource text files to be placed in the prompt.
├── datasets/                  # Folder which contains any data to be loaded.
├── keys.py                    # OpenAI API keys (should be filled in).
├── run_instance.py            # Main file which runs the LLM-ASP-Programmer pipeline.
├── run_datasets.py            # Main file which runs the LLM-ASP-Programmer pipeline with automatic evaluation on a dataset.
├── prompts.py                 # Prompts used in the pipeline.
├── prompts_post_output.py     # Prompts for formatting and automatic evaluation.
├── README.md                  # Description of the repository and instructions for usage.
├── utils.py                   # Useful functions used in the pipeline.
├── load_datasets.py           # File which stores the functions to load datasets.
├── generate_zebra.py          # File which generates size nxn Zebra puzzles.
```

## Setup

1. Python version 3.9+ is required. Install dependencies:
```bash
conda install -c potassco clingo \
&& pip install openai \
&& python -m pip install --user --upgrade clingo \
&& pip install -q -U google-genai \
&& pip install --upgrade google-cloud-aiplatform \
&& pip install datasets
```

2. Place your OpenAI and Google API keys in `keys.py` file in the following format:
```python
API_KEY = "your_openai_api_key"
API_KEY_GEM = "your_google_api_key"
API_KEY_DEEPSEEK = "your_deepseek_api_key"
```

To use RAG, in `keys.py` the relevant variables need to be set.

For OpenAI (o4-mini, etc.):
```python
vs_id = "your vector store ID"
```
For Google (Gemini models):
```
PROJECT_ID = "your project ID"
CORPUS_NAME = "your corpus name"
```

# Running LLM-ASP-Programmer

## Running a problem
Execute the run_instance script with the desired task name:
```bash
python main_updates.py --task <TASK NAME>
```
<TASK_NAME> should be the name of a folder in `envs`, which contains a `problem.txt`, specifying the problem description.

### Additional Parameters
- **`--o <OUTPUT FOLDER NAME>`**: Output folder name (default: same as the task name).
- **`--model <LLM MODEL>`**: LLM model to use (default: `"o4-mini"`. Options: `"gpt-4o"`, `"o1-preview"`, `"o4-mini"`, `"gemini-2.5-pro"`, `"gemini-2.5-flash"`, `"deepseek-reasoner"`, `"deepseek-chat"`).
- **`--max_updates <MAX LLM REVISIONS>`**: Maximum number of revisions from the LLM (default: 10).
- **`--resource <resource filename>`**: Resource file in `resources` directory (default: none).
- **`--RAG <name for RAG run>`**: A name to distinguish between RAG runs (default: none).
- **`--timeout <maximum length for Clingo>`**: The maximum allowed time (seconds) for a Clingo call (default: 80).

### Example:
To run on a big bench extra hard instance of "shuffled objects" task with default parameters, use:
```bash
python run_instance.py --task river
```

To run on a big bench extra hard instance of "shuffled objects", with `gpt-4o` as the underlying LLM, with at most 6 updates, use:
```bash
python run_instance.py --task river --model gpt-4o --max_updates 6
```
---

### Outputs
The intermediate outputs and final results are stored in the `outputs_<model>` folder.

---

### Adding a problem

To add a new problem, create a folder in the `envs` directory with the name of the task. In this new folder place the problem description in a single file named `problem.txt`.

### Running the New Problem
If the folder is named, for example, `blocksworld`, run the following command:
```bash
python run_instance.py --task blocksworld
```


## Running a dataset
Execute the run_datasets script with the desired dataset:
```bash
python run_datasets.py  --model <MODEL NAME> --dataset <DATASET NAME>
```

### Additional Parameters
- **`--model <LLM model>`**: LLM model to use (default: `"o4-mini"`. Options: `"gpt-4o"`, `"o1-preview"`, `"o4-mini"`, `"gemini-2.5-pro"`, `"gemini-2.5-flash"`, `"deepseek-reasoner"`, `"deepseek-chat"`).
- **`--dataset <dataset name>`**: Name of the dataset to run (default: None. Options: (see below))).
- **`--max_updates <max LLM revisions>`**: Maximum number of revisions from the LLM (default: 10).
- **`--resource <resource filename>`**: Resource file in `"resources"` directory (default: none).
- **`--limit <limit>`**: Maximum number of instances to run (default: 10e6).
- **`--RAG <name for RAG run>`**: A name to distinguish between RAG runs (default: none).
- **`--timeout <maximum length for Clingo>`**: The maximum allowed time (seconds) for a Clingo call (default: 80).


Current datasets supported (replace "<datasets name>" with any of the following):
`"zlb-xl"` (ZebraLogic XL)
`"zebra-generated-100"` (Zebra Logic XXL)
`"sakana-100"` (SudokuBench)
`"pb-mystery"` (Mystery Blocksworld)

(From NPHardEval)
`"edp_p-20"`
`"gcp_d-20"`
`"gcp_hard-20"`
`"ksp-20"`
`"tsp_hard-20"`
`"bsp_p-20"`
`"spp_p-20"`
`"tsp_d-20"`
`"msp_hard-20"`

### Example:
To run on 10 instances of the ZebraLogicBench dataset, task:
```bash
python run_datasets.py --model gemini-2.5-pro-preview-03-25 --resource v4.txt --max_updates 10 --dataset zebra --limit 10
```

---

### Outputs
The intermediate outputs and final results are stored in the `outputs_<model>/<dataset>` folder.

---

### Adding a dataset

To add a new dataset, you must add a key which is the dataset's name (e.g., "blocksworld"), and a value which is a function to the loaders_dict dictionary in the `load_datasets.py` file, which returns a dictionary in the following format:

```
{   'problem-id-1': {
                        'problem': <problem description> (string),
                        'solution': <solution> (string)
                    },
    ...,
    'problem-id-n': {
                        'problem': <problem description> (string),
                        'solution': <solution> (string)
                        }
}
```
(you can follow the examples in `load_datasets.py`)

### Running the new dataset
Using the name of the dataset you defined, for example, `blocksworld`, run the following command:
```bash
python run_datasets.py --model gemini-2.5-pro-preview-03-25 --resource v4.txt --max_updates 10 --dataset blocksworld
```
