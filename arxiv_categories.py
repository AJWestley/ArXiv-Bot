categories = {
    'Astrophysics': {
        'Solar and Stellar Physics': 'astro-ph.SR',
        'Earth and Planetary Physics': 'astro-ph.EP',
        'High Energy Phenomena': 'astro-ph.HE',
        'Galactic Astrophysics': 'astro-ph.GA',
        'Cosmology and Nongalactic Astrophysics': 'astro-ph.CO',
        'Instrumentation and Methods': 'astro-ph.IM',
    },
    'Computer Science': {
        'Machine Learning': 'cs.LG',
        'Computer Vision and Pattern Recognition': 'cs.CV',
        'Neural and Evolutionary Computing': 'cs.NE',
        'Distributed, Parallel and Cluster Computing': 'cs.CD',
        'Mathematical Software': 'cs.MS'
    }
}

cat_map = {
    'Astrophysics': 'astro-ph',
    'Computer Science': 'cs'
}

emoji_map = {
    'Astrophysics': '🌠',
    'Computer Science': '💻',
    'Astrophysics Solar and Stellar Physics': '☀️',
    'Astrophysics Earth and Planetary Physics': '🪐',
    'Astrophysics High Energy Phenomena': '💥',
    'Astrophysics Galactic Astrophysics': '🌌',
    'Astrophysics Cosmology and Nongalactic Astrophysics': '☄️',
    'Astrophysics Instrumentation and Methods': '🛰️',
    'Computer Science Machine Learning': '🧠',
    'Computer Science Computer Vision and Pattern Recognition': '👁️',
    'Computer Science Neural and Evolutionary Computing': '🧬',
    'Computer Science Distributed, Parallel and Cluster Computing': '⚡',
    'Computer Science Mathematical Software': '📐'
}

code_map = {
    code: (field, subfield)
    for field, subfields in categories.items()
    for subfield, code in subfields.items()
}