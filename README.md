# ArXivist

A framework for building Discord bots that provide daily ArXiv updates on relevant topics.
Currently being used for a Radio Astronomy research group server.

## Running the Bot

### Clone the Project

To run the bot, first clone this repository:
```bash
$ git clone https://github.com/AJWestley/ArXiv-Bot.git
```

### Setup Your `.env` File

Inside the `ArXiv-Bot` directiory, you must add your Discord API token to a `.env` file:
```bash
$ cd ArXiv-Bot
$ echo 'DISCORD_TOKEN=YourAPITokenGoesHere' > .env
```

### Execution

The bot can then be run with the following command:
```bash
$ python bot_runner.py 
```

## Customising Your Own ArXivist

Only the `src` directory and its contents are necessary to use your own ArXivist.
The other files in the base directory are merely the configuration for my own bot.

### The ArXivist Class

To make your own ArXivist, you must import the class at the top of the respective file (from inside the base directory).

```python
from src.arxivist import ArXivist
```

The constructor takes five arguments:
- `time` (`tuple[int,int]`): the hour and minute to send the daily updates.
- `channel_json_path` (`str`): the path to the channel config json file.
- `taxonomy_json_path` (`str`): the path to the taxonomy config json file.
- `filter_json_path` (`str`): the path to the filter config json file.
- `timezone` (`str`) **OPTIONAL**: the timezone to operate in. Defaults to 'UTC'.

Once constructed, the bot can be run using the `run()` function.

#### Example:

```python
from src.arxivist import ArXivist

bot = ArXivist(
    (17, 30), 
    'channels.json', 
    'taxonomy.json', 
    'filtering.json', 
    timezone="Europe/Berlin")

bot.run('discord_api_token')
```

#### Time and Timezones

##### The `time` Parameter
The time parameter should be a two-element tuple with the following contents:
1. An integer between 0 and 23 (inclusive), representing the hour of the day in 24-hour format (where 0 is midnight).
2. An integer between 0 and 59 (inclusive), representing the minute of the hour.

##### Selecting a Timezone

The following script checks if particular string is a valid timezone:
```python
import zoneinfo
print('timezone string' in zoneinfo.available_timezones())
```
This should output `True` or `False` respectively.

Alternatively, you can get a list of all the possible timezones as follows:
```python
import zoneinfo
print(zoneinfo.available_timezones())
```
The resulting list contains over 500 items, so I recommend the first option.

## Config Files

There are three config files needed to run your ArXivist.

1. **Taxonomy config**: Specifies which fields and subfields you would like the bot to find on the ArXiv.
2. **Channel config**: Lists the channels that the daily updates will be sent to, as well as the fields that will be included in each channel's updates.
3. **Filtering config**: Specifies keywords of interest, with their respective relevance weight. Used to order the results by relevance.

### Taxonomy Config

The taxonomy config file has the following schema:
```json
{
    "Field 1": ["Subfield 1", "Subfield 2", ...],
    "Field 2": ["Subfield 1", "Subfield 2", ...],
    ...
}
```
Here, each field and subfield is the full text name of the respective field or subfield in the ArXiv taxonomy.

#### Example

Below is an example containing all the supported fields and subfields.
It can be used as a basis for creating your own config file.

```json
{
    "Computer Science": [
        "Artificial Intelligence", "Hardware Architecture", "Computational Complexity", 
        "Computational Engineering, Finance and Science", "Computational Geometry", "Computation and Language",
        "Cryprography and Security", "Computer Vision and Pattern Recognition", "Computers and Society",
        "Databases", "Distributed, Parallel and Cluster Computing", "Digital Libraries",
        "Discrete Mathematics", "Data Structures and Algorithms", "Emerging Technologies",
        "Formal Languages and Automata Theory", "General Literature", "Graphics",
        "Computer Science and Game Theory", "Human-Computer Interaction", "Information Retrieval",
        "Information Theory", "Machine Learning", "Logic in Computer Science", "Multiagent Systems",
        "Multimedia", "Mathematical Software", "Numerical Analysis", "Neural and Evolutionary Computing",
        "Networking and Internet Architecture", "Other Computer Science", "Operating Systems",
        "Performance", "Programming Languages", "Robotics", "Symbolic Computation", "Sound",
        "Software Engineering", "Social and Information Networks", "Systems and Control"
    ],
    "Economics": [
        "Econometrics", "General Economics", "Theoretical Economics"
    ],
    "Electrical Engineering and Systems Science": [
        "Audio and Speech Processing", "Image and Video Processing", "Signal Processing"
    ],
    "Mathematics": [
        "Algebraic Topology", "Category Theory", "Classical Analysis and ODEs", "Combinatorics",
        "Commutative Algebra", "Complex Variables", "Differential Geometry", "Dynamical Systems",
        "Functional Analysis", "General Mathematics", "General Topology", "Group Theory",
        "Geometric Topology", "History and Overview", "Information Theory", "K-Theory and Homology",
        "Logic", "Metric Geometry", "Mathematical Physics", "Numerical Analysis", "Number Theory",
        "Operator Algebras", "Optimization and Control", "Probability", "Quantum Algebra",
        "Rings and Algebras", "Representation Theory", "Symplectic Geometry", "Spectral Theory",
        "Statistics Theory"
    ]
    "Astrophysics": [
        "Cosmology and Nongalactic Astrophysics", "Earth and Planetary Astrophysics",
        "Astrophysics of Galaxies", "High Energy Astrophysical Phenomena",
        "Instrumentation and Methods for Astrophysics", "Solar and Stellar Astrophysics"
    ],
    "Condensed Matter" : [
        "Disordered Systems and Neural Networks", "Mesoscale and Nanoscale Physics",
        "Materials Science", "Other Condensed Matter", "Quantum Gases", "Soft Condensed Matter", 
        "Statistical Mechanics", "Strongly Correlated Electrons", "Superconductivity"
    ],
    "Nonlinear Sciences": [
        "Adaptation and Self-Organizing Systems", "Chaotic Dynamics", "Cellular Automata and Lattice Gases",
        "Pattern Formation and Solitons", "Exactly Solvable and Integrable Systems",
    ],
    "Physics": [
        "General Relativity and Quantum Cosmology", "High Energy Physics - Experiment",
        "High Energy Physics - Lattice", "High Energy Physics - Phenomenology",
        "High Energy Physics - Theory", "Mathematical Physics", "Nuclear Experiment",
        "Nuclear Theory", "Quantum Physics", "Accelerator Physics", "Applied Physics",
        "Atmospheric and Oceanic Physics", "Atomic Physics", "Biological Physics",
        "Chemical Physics", "Classical Physics", "Computational Physics",
        "Data Analysis, Statistics and Probability", "Fluid Dynamics", "General Physics",
        "Geophysics", "History and Philosophy of Physics", "Instrumentation and Detectors",
        "Medical Physics", "Optics", "Physics Education", "Physics and Society",
        "Plasma Physics", "Popular Physics", "Space Physics"
    ],
    "Quantitative Biology": [
        "Biomolecules", "Cell Behavior", "Genomics", "Molecular Networks",
        "Neurons and Cognition", "Other Quantitative Biology", "Populations and Evolution",
        "Quantitative Methods", "Subcellular Processes", "Tissues and Organs"
    ],
    "Quantitative Finance": [
        "Computational Finance", "Economics", "General Finance", "Mathematical Finance",
        "Portfolio Management", "Pricing of Securities", "Risk Management",
        "Statistical Finance", "Trading and Market Microstructure"
    ],
    "Statistics": [
        "Applications", "Computation", "Machine Learning",
        "Methodology", "Other Statistics", "Statistics Theory"
    ]
}
```


### Channel Config

The channel config file has the following schema:
```json
{
    "Channel 1": ["Field 1", "Field 2", ...],
    "Channel 2": ["Field 1", "Field 2", ...],
    ...
}
```

#### Example

Below is an example config for a bot which does the following:
1. Sends economics and quantitative finance updates to a channel called "money-money-money".
2. Sends engineering and computer science updates to a channel called "mr-robot".
3. Sends quantitative biology updates to a channel called "powerhouse-of-the-cell".

```json
{
    "money-money-money": ["Economics", "Quantitative Finance"],
    "mr-robot": ["Electrical Engineering and Systems Science", "Computer Science"],
    "powerhouse-of-the-cell": ["Quantitative Finance"]
}
```


### Filtering Config

The filtering config file has the following schema:
```json
{
    "threshold": <integer>,
    "scores": {
        "keyword or phrase 1": <integer>,
        "keyword or phrase 2": <integer>,
        "keyword or phrase 3": <integer>,
        ...
    }
}
```

If you do not want relevance filtering, use the following file:
```json
{
    "threshold": 0,
    "scores": {}
}
```

#### Example

The `filtering.json` file can be used as a reference.
It contains keywords and phrases for radio astronomy and its most useful machine learning methods.