"""
Prometheus UI - Shared UI components for Prometheus code analysis tools.

Copyright (c) 2025 Andrew H. Bond <andrew.bond@sjsu.edu>
All rights reserved.

This software is provided for educational and research purposes.
Unauthorized copying, modification, or distribution is prohibited.

Contains:
- CSS styles (bivariate palette, dark theme)
- HTML component generators (quadrant chart, tables, legends)
- GitHub avatar URL resolution
"""

# =============================================================================
# COPYRIGHT
# =============================================================================

COPYRIGHT_NOTICE = "Copyright © 2025 Andrew H. Bond <andrew.bond@sjsu.edu> • All rights reserved"
COPYRIGHT_HTML = '<p style="text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 1rem;">Copyright © 2025 Andrew H. Bond &lt;andrew.bond@sjsu.edu&gt; • All rights reserved</p>'

# =============================================================================
# COLOR PALETTE - Custom bivariate pastel (muted)
# =============================================================================

QUADRANT_COLORS = {
    'BUNKER': '#e8c8a0',       # Stronger tan (underground)
    'FORTRESS': '#a8a8b8',     # Steel blue-grey (fortified)
    'GLASS HOUSE': '#b0c8e8',  # Original pastel blue (fragile)
    'DEATHTRAP': '#e8b0b0',    # Original pastel red (danger)
}

# For quadrant label text (slightly more saturated for readability)
QUADRANT_TEXT_COLORS = {
    'BUNKER': '#c4a484',       # Brown
    'FORTRESS': '#888888',     # Grey
    'GLASS HOUSE': '#88a8c8',  # Blue
    'DEATHTRAP': '#d88888',    # Red
}

# Fallback colors for repo dots (Tableau 10)
FALLBACK_COLORS = [
    '#4e79a7', '#f28e2b', '#e15759', '#76b7b2',
    '#59a14f', '#edc948', '#b07aa1', '#ff9da7',
]


# =============================================================================
# GITHUB AVATAR RESOLUTION
# =============================================================================

KNOWN_REPOS = {
    'flask': 'pallets',
    'django': 'django',
    'fastapi': 'tiangolo',
    'requests': 'psf',
    'numpy': 'numpy',
    'pandas': 'pandas-dev',
    'react': 'facebook',
    'vue': 'vuejs',
    'tensorflow': 'tensorflow',
    'pytorch': 'pytorch',
    'kubernetes': 'kubernetes',
    'docker': 'docker',
    'redis': 'redis',
    'postgres': 'postgres',
    'node': 'nodejs',
    'express': 'expressjs',
    'spring-boot': 'spring-projects',
    'rails': 'rails',
    'laravel': 'laravel',
    'gin': 'gin-gonic',
    'echo': 'labstack',
    'actix': 'actix',
    'rocket': 'rwf2',
    'prometheus': 'anthropics',  # our tool
}


def get_github_avatar_url(repo_name: str) -> str:
    """Get GitHub avatar URL for a repo owner."""
    # Handle owner/repo format
    if '/' in repo_name:
        owner = repo_name.split('/')[0]
        return f"https://github.com/{owner}.png?size=80"
    
    # Handle owner_repo format (from prometheus output)
    if '_' in repo_name:
        parts = repo_name.split('_')
        # Try first part as owner
        owner = parts[0]
        # Also check if second part is a known repo
        if len(parts) > 1 and parts[1].lower() in KNOWN_REPOS:
            owner = KNOWN_REPOS[parts[1].lower()]
        return f"https://github.com/{owner}.png?size=80"
    
    # Check known repos
    repo_lower = repo_name.lower()
    if repo_lower in KNOWN_REPOS:
        owner = KNOWN_REPOS[repo_lower]
        return f"https://github.com/{owner}.png?size=80"
    
    return f"https://github.com/{repo_name}.png?size=80"


# =============================================================================
# CSS STYLES
# =============================================================================

def get_base_css() -> str:
    """Base CSS for dark theme."""
    return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: #e2e8f0;
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(30, 41, 59, 0.8);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        h1, h2, h3 {
            color: #f8fafc;
        }
        
        h2 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
    """


def get_quadrant_css() -> str:
    """CSS for the bivariate quadrant chart."""
    return """
        /* Quadrant wrapper and labels */
        .quadrant-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .top-labels {
            display: flex;
            width: 100%;
            max-width: 500px;
            margin-bottom: 0.25rem;
        }
        
        .top-label {
            flex: 1;
            text-align: center;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .top-label.left { color: #d88888; }   /* DEATHTRAP - red */
        .top-label.right { color: #888888; } /* FORTRESS - grey */
        
        .chart-with-sides {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .side-label {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            font-size: 0.65rem;
            color: #64748b;
            padding: 0.5rem 0;
        }
        
        .side-label.left {
            transform: rotate(180deg);
        }
        
        /* Quadrant chart container */
        .quadrant-chart {
            position: relative;
            width: 500px;
            height: 500px;
            border: 2px solid #334155;
            border-radius: 0.25rem;
            overflow: visible;
        }
        
        /* 16x16 Bivariate gradient - dithered, correct corners */
        .bivariate-grid {
            display: grid;
            grid-template-columns: repeat(16, 1fr);
            grid-template-rows: repeat(16, 1fr);
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }

        /*
         * Corners (dithered):
         * - DEATHTRAP (top-left, cell 1): #e8b0b0 pastel red
         * - FORTRESS (top-right, cell 16): #a8a8b8 steel blue-grey
         * - GLASS HOUSE (bottom-left, cell 241): #b0c8e8 pastel blue
         * - BUNKER (bottom-right, cell 256): #e8c8a0 tan
         */

        .cell-1 { background: #e7b0b0; }
        .cell-2 { background: #e8b0b0; }
        .cell-3 { background: #e4b4b4; }
        .cell-4 { background: #e0b9b9; }
        .cell-5 { background: #d9c2c2; }
        .cell-6 { background: #d5c8c8; }
        .cell-7 { background: #d1cece; }
        .cell-8 { background: #d1cdcd; }
        .cell-9 { background: #cfcfcf; }
        .cell-10 { background: #c9c9cb; }
        .cell-11 { background: #c3c3c8; }
        .cell-12 { background: #bebec5; }
        .cell-13 { background: #b3b3be; }
        .cell-14 { background: #adadbb; }
        .cell-15 { background: #aaaab9; }
        .cell-16 { background: #a8a8b8; }
        .cell-17 { background: #e7b0b0; }
        .cell-18 { background: #e6b1b1; }
        .cell-19 { background: #e2b7b7; }
        .cell-20 { background: #e1b8b8; }
        .cell-21 { background: #d9c3c3; }
        .cell-22 { background: #d5c8c8; }
        .cell-23 { background: #d3cbcb; }
        .cell-24 { background: #d1cdcd; }
        .cell-25 { background: #d0d0d0; }
        .cell-26 { background: #cacacc; }
        .cell-27 { background: #c3c3c8; }
        .cell-28 { background: #bbbbc3; }
        .cell-29 { background: #b8b8c1; }
        .cell-30 { background: #afafbc; }
        .cell-31 { background: #ababba; }
        .cell-32 { background: #ababb9; }
        .cell-33 { background: #e3b5b5; }
        .cell-34 { background: #e2b7b7; }
        .cell-35 { background: #e4b5b5; }
        .cell-36 { background: #dfbbbb; }
        .cell-37 { background: #d9c3c3; }
        .cell-38 { background: #d5c8c8; }
        .cell-39 { background: #d1cece; }
        .cell-40 { background: #d0cfcf; }
        .cell-41 { background: #d0d0d0; }
        .cell-42 { background: #c9c9cb; }
        .cell-43 { background: #c3c3c8; }
        .cell-44 { background: #bcbcc4; }
        .cell-45 { background: #b3b3be; }
        .cell-46 { background: #adadbb; }
        .cell-47 { background: #acacba; }
        .cell-48 { background: #adadbb; }
        .cell-49 { background: #dfbbbb; }
        .cell-50 { background: #e0baba; }
        .cell-51 { background: #e0baba; }
        .cell-52 { background: #e0b9b9; }
        .cell-53 { background: #dbc0c0; }
        .cell-54 { background: #d4c9c9; }
        .cell-55 { background: #d1cdcd; }
        .cell-56 { background: #d0d0d0; }
        .cell-57 { background: #cdcdce; }
        .cell-58 { background: #cdcdce; }
        .cell-59 { background: #c3c3c8; }
        .cell-60 { background: #bdbdc4; }
        .cell-61 { background: #b9b9c2; }
        .cell-62 { background: #b6b6c0; }
        .cell-63 { background: #b6b6c0; }
        .cell-64 { background: #b7b7c1; }
        .cell-65 { background: #d9c3c3; }
        .cell-66 { background: #d9c2c2; }
        .cell-67 { background: #dbc0c0; }
        .cell-68 { background: #dcbfbf; }
        .cell-69 { background: #dbc0c0; }
        .cell-70 { background: #d7c6c6; }
        .cell-71 { background: #d3cbcb; }
        .cell-72 { background: #d0d0d0; }
        .cell-73 { background: #d0d0d0; }
        .cell-74 { background: #cacacc; }
        .cell-75 { background: #c6c6ca; }
        .cell-76 { background: #bdbdc4; }
        .cell-77 { background: #c0c0c6; }
        .cell-78 { background: #bdbdc5; }
        .cell-79 { background: #bcbcc4; }
        .cell-80 { background: #bcbcc4; }
        .cell-81 { background: #d6c7c7; }
        .cell-82 { background: #d7c6c6; }
        .cell-83 { background: #d5c8c8; }
        .cell-84 { background: #d4c9c9; }
        .cell-85 { background: #d6c7c7; }
        .cell-86 { background: #d7c6c6; }
        .cell-87 { background: #d0cfcf; }
        .cell-88 { background: #d0cfcf; }
        .cell-89 { background: #cdcdce; }
        .cell-90 { background: #c9c9cb; }
        .cell-91 { background: #c3c3c8; }
        .cell-92 { background: #c6c6ca; }
        .cell-93 { background: #c7c7ca; }
        .cell-94 { background: #c5c5c9; }
        .cell-95 { background: #c3c3c8; }
        .cell-96 { background: #c4c4c9; }
        .cell-97 { background: #d0cfcf; }
        .cell-98 { background: #d2cccc; }
        .cell-99 { background: #d0cece; }
        .cell-100 { background: #d1cece; }
        .cell-101 { background: #d4caca; }
        .cell-102 { background: #d1cdcd; }
        .cell-103 { background: #d1cdcd; }
        .cell-104 { background: #d0cfcf; }
        .cell-105 { background: #cecece; }
        .cell-106 { background: #ccccce; }
        .cell-107 { background: #c9c9cc; }
        .cell-108 { background: #cbcbcd; }
        .cell-109 { background: #cbcbcd; }
        .cell-110 { background: #cececf; }
        .cell-111 { background: #cecece; }
        .cell-112 { background: #cacacc; }
        .cell-113 { background: #d0cfcf; }
        .cell-114 { background: #d1cece; }
        .cell-115 { background: #d0d0d0; }
        .cell-116 { background: #d0d0d0; }
        .cell-117 { background: #d1cece; }
        .cell-118 { background: #d0d0d0; }
        .cell-119 { background: #d0d0d0; }
        .cell-120 { background: #d1cdcd; }
        .cell-121 { background: #d0d0d0; }
        .cell-122 { background: #cfcfcf; }
        .cell-123 { background: #d0d0d0; }
        .cell-124 { background: #cfcfcf; }
        .cell-125 { background: #cccccd; }
        .cell-126 { background: #cececf; }
        .cell-127 { background: #cccccd; }
        .cell-128 { background: #d0d0d0; }
        .cell-129 { background: #d0d0d0; }
        .cell-130 { background: #d0d0d0; }
        .cell-131 { background: #cecfd0; }
        .cell-132 { background: #cdcfd1; }
        .cell-133 { background: #d0d0d0; }
        .cell-134 { background: #d0d0d0; }
        .cell-135 { background: #cdcfd1; }
        .cell-136 { background: #cfcfd0; }
        .cell-137 { background: #d1cfcc; }
        .cell-138 { background: #d0d0d0; }
        .cell-139 { background: #d0d0d0; }
        .cell-140 { background: #d1cfcc; }
        .cell-141 { background: #d0cfcf; }
        .cell-142 { background: #d0cfcf; }
        .cell-143 { background: #d1cfcd; }
        .cell-144 { background: #d0d0d0; }
        .cell-145 { background: #cccfd2; }
        .cell-146 { background: #cbced3; }
        .cell-147 { background: #cccfd2; }
        .cell-148 { background: #cdcfd1; }
        .cell-149 { background: #cbced3; }
        .cell-150 { background: #cbced3; }
        .cell-151 { background: #cfcfd0; }
        .cell-152 { background: #d0d0d0; }
        .cell-153 { background: #d0cfce; }
        .cell-154 { background: #d2cfcb; }
        .cell-155 { background: #d3cec8; }
        .cell-156 { background: #d3cec9; }
        .cell-157 { background: #d3cec9; }
        .cell-158 { background: #d2cfcb; }
        .cell-159 { background: #d3cec9; }
        .cell-160 { background: #d3cec8; }
        .cell-161 { background: #c5cdd7; }
        .cell-162 { background: #c8ced5; }
        .cell-163 { background: #c6cdd7; }
        .cell-164 { background: #c9ced4; }
        .cell-165 { background: #c9ced4; }
        .cell-166 { background: #c5cdd7; }
        .cell-167 { background: #cbced3; }
        .cell-168 { background: #d0d0d0; }
        .cell-169 { background: #d1cfcd; }
        .cell-170 { background: #d3cec8; }
        .cell-171 { background: #d4cec6; }
        .cell-172 { background: #d5cec4; }
        .cell-173 { background: #d6cdc3; }
        .cell-174 { background: #d5cec5; }
        .cell-175 { background: #d5cec5; }
        .cell-176 { background: #d7cdc1; }
        .cell-177 { background: #bfcbdc; }
        .cell-178 { background: #c1ccdb; }
        .cell-179 { background: #c1ccdb; }
        .cell-180 { background: #c1ccda; }
        .cell-181 { background: #c2ccd9; }
        .cell-182 { background: #c8ced5; }
        .cell-183 { background: #cecfd0; }
        .cell-184 { background: #cdcfd1; }
        .cell-185 { background: #d0cfce; }
        .cell-186 { background: #d3cec9; }
        .cell-187 { background: #d4cec6; }
        .cell-188 { background: #dbccb8; }
        .cell-189 { background: #dbccb8; }
        .cell-190 { background: #daccba; }
        .cell-191 { background: #dbccb9; }
        .cell-192 { background: #dbccb8; }
        .cell-193 { background: #bacae0; }
        .cell-194 { background: #bdcbde; }
        .cell-195 { background: #bacadf; }
        .cell-196 { background: #bccbde; }
        .cell-197 { background: #c1ccda; }
        .cell-198 { background: #c5cdd7; }
        .cell-199 { background: #cfcfd0; }
        .cell-200 { background: #d0d0d0; }
        .cell-201 { background: #d0d0d0; }
        .cell-202 { background: #d0cfce; }
        .cell-203 { background: #d4cec6; }
        .cell-204 { background: #dccbb7; }
        .cell-205 { background: #dfcab0; }
        .cell-206 { background: #e0caae; }
        .cell-207 { background: #dfcab0; }
        .cell-208 { background: #e1caad; }
        .cell-209 { background: #b5c9e4; }
        .cell-210 { background: #b7c9e2; }
        .cell-211 { background: #b4c9e4; }
        .cell-212 { background: #bccbde; }
        .cell-213 { background: #c1ccda; }
        .cell-214 { background: #c7cdd6; }
        .cell-215 { background: #cecfd0; }
        .cell-216 { background: #d0d0d0; }
        .cell-217 { background: #d0cfcf; }
        .cell-218 { background: #d1cfcc; }
        .cell-219 { background: #d7cdc1; }
        .cell-220 { background: #dbccb8; }
        .cell-221 { background: #ddcbb4; }
        .cell-222 { background: #e3c9a8; }
        .cell-223 { background: #e3c9a8; }
        .cell-224 { background: #e2c9aa; }
        .cell-225 { background: #b0c8e8; }
        .cell-226 { background: #b1c8e6; }
        .cell-227 { background: #b5c9e3; }
        .cell-228 { background: #bccbde; }
        .cell-229 { background: #bfcbdc; }
        .cell-230 { background: #c9ced4; }
        .cell-231 { background: #caced4; }
        .cell-232 { background: #cecfd1; }
        .cell-233 { background: #d0d0d0; }
        .cell-234 { background: #d1cfcc; }
        .cell-235 { background: #d7cdc1; }
        .cell-236 { background: #dccbb7; }
        .cell-237 { background: #decbb3; }
        .cell-238 { background: #e4c9a6; }
        .cell-239 { background: #e6c8a3; }
        .cell-240 { background: #e6c8a3; }
        .cell-241 { background: #b0c8e8; }
        .cell-242 { background: #b1c8e6; }
        .cell-243 { background: #b5c9e3; }
        .cell-244 { background: #bdcbdd; }
        .cell-245 { background: #c0ccdb; }
        .cell-246 { background: #c8ced5; }
        .cell-247 { background: #cbced3; }
        .cell-248 { background: #cfcfd0; }
        .cell-249 { background: #d0d0d0; }
        .cell-250 { background: #d3cec9; }
        .cell-251 { background: #d6cdc2; }
        .cell-252 { background: #d9ccbc; }
        .cell-253 { background: #e1caad; }
        .cell-254 { background: #e3c9a8; }
        .cell-255 { background: #e5c8a5; }
        .cell-256 { background: #e6c8a3; }
        
        /* Axis lines - bold */
        .axis-line {
            position: absolute;
            background: #475569;
            z-index: 5;
        }
        
        .axis-h {
            left: 0;
            right: 0;
            top: 50%;
            height: 2px;
            transform: translateY(-50%);
        }
        
        .axis-v {
            top: 0;
            bottom: 0;
            left: 50%;
            width: 2px;
            transform: translateX(-50%);
        }
        
        /* Repo dots with avatars */
        .repo-dot {
            position: absolute;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            border: 3px solid rgba(255, 255, 255, 0.9);
            cursor: pointer;
            z-index: 10;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            overflow: hidden;
            background: #334155;
        }
        
        .repo-dot img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .repo-dot:hover {
            transform: translate(-50%, -50%) scale(1.3);
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            z-index: 20;
        }
        
        .dot-label {
            position: absolute;
            top: -22px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.65rem;
            color: #e2e8f0;
            white-space: nowrap;
            background: rgba(15, 23, 42, 0.95);
            padding: 2px 6px;
            border-radius: 3px;
            pointer-events: none;
            font-weight: 500;
        }
        
        /* Bottom labels */
        .bottom-labels {
            display: flex;
            width: 100%;
            max-width: 500px;
            margin-top: 0.25rem;
        }
        
        .bottom-label {
            flex: 1;
            text-align: center;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .bottom-label.left { color: #88a8c8; }  /* GLASS HOUSE - blue */
        .bottom-label.right { color: #c4a484; } /* BUNKER - brown */
        
        .axis-title {
            color: #64748b;
            font-size: 0.65rem;
            text-align: center;
            margin-top: 0.75rem;
        }
        
        /* Legend */
        .legend {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1.25rem;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid #334155;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
        }
        
        .legend-avatar {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.6);
            flex-shrink: 0;
            object-fit: cover;
        }
        
        .legend-dot-fallback {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.6);
            flex-shrink: 0;
        }
        
        .legend-name {
            color: #e2e8f0;
        }
        
        .legend-quadrant {
            font-size: 0.7rem;
            font-weight: 600;
        }
    """


def get_table_css() -> str:
    """CSS for data tables."""
    return """
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 0.75rem;
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #334155;
        }
        
        td {
            padding: 0.75rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            color: #cbd5e1;
        }
        
        tr:hover {
            background: rgba(148, 163, 184, 0.05);
        }
        
        .badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
        }
    """


# =============================================================================
# HTML COMPONENT GENERATORS
# =============================================================================

def generate_bivariate_grid_html() -> str:
    """Generate the 16x16 bivariate gradient grid (256 cells)."""
    cells = []
    for i in range(1, 257):
        cells.append(f'<div class="cell-{i}"></div>')
    return '<div class="bivariate-grid">\n' + ''.join(cells) + '\n</div>'


def generate_repo_dot_html(name: str, x_pct: float, y_pct: float, 
                           avatar_url: str, fallback_color: str,
                           quadrant: str, complexity: float, resilience: float,
                           theater: float = 1.0) -> str:
    """Generate HTML for a single repo dot on the quadrant."""
    short_name = name.split('/')[-1][:10]
    theater_str = f"&#10;Theater: {theater:.2f}" if theater != 1.0 else ""
    return f'''
        <div class="repo-dot" style="left: {x_pct}%; top: {y_pct}%;"
             title="{name}&#10;Quadrant: {quadrant}&#10;Complexity: {complexity:.0f}&#10;Resilience: {resilience:.0f}{theater_str}">
            <img src="{avatar_url}" alt="{name}" 
                 onerror="this.style.display='none'; this.parentElement.style.backgroundColor='{fallback_color}';">
            <span class="dot-label">{short_name}</span>
        </div>
    '''


def generate_legend_item_html(name: str, avatar_url: str, fallback_color: str, quadrant: str) -> str:
    """Generate HTML for a legend item."""
    quadrant_color = QUADRANT_TEXT_COLORS.get(quadrant, '#64748b')
    return f'''
        <div class="legend-item">
            <img class="legend-avatar" src="{avatar_url}" alt="{name}"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
            <span class="legend-dot-fallback" style="background-color: {fallback_color}; display: none;"></span>
            <span class="legend-name">{name}</span>
            <span class="legend-quadrant" style="color: {quadrant_color};">{quadrant}</span>
        </div>
    '''


def generate_quadrant_chart_html(dots_html: str, legend_html: str) -> str:
    """Generate the complete quadrant chart with labels."""
    return f'''
        <div class="quadrant-wrapper">
            <!-- Top labels -->
            <div class="top-labels">
                <div class="top-label left">☠️ DEATHTRAP</div>
                <div class="top-label right">🏯 FORTRESS</div>
            </div>
            
            <div class="chart-with-sides">
                <div class="side-label left">← High Resilience</div>
                
                <div class="quadrant-chart">
                    {generate_bivariate_grid_html()}
                    
                    <div class="axis-line axis-h"></div>
                    <div class="axis-line axis-v"></div>
                    
                    {dots_html}
                </div>
                
                <div class="side-label right">Low Resilience →</div>
            </div>
            
            <!-- Bottom labels -->
            <div class="bottom-labels">
                <div class="bottom-label left">🏠 GLASS HOUSE</div>
                <div class="bottom-label right">🏰 BUNKER</div>
            </div>
            
            <div class="axis-title">
                X: Complexity Score (left=high, right=low) • Y: Resilience Score (top=high, bottom=low)
            </div>
        </div>
        
        <div class="legend">
            {legend_html}
        </div>
    '''


def generate_comparison_table_html(repos: list) -> str:
    """
    Generate a comparison table for multiple repos.
    
    repos: list of dicts with keys: name, health, quadrant, complexity, resilience, theater
    """
    rows = ""
    for i, repo in enumerate(repos, 1):
        health = repo.get('health', 0)
        health_color = '#22c55e' if health >= 70 else '#f59e0b' if health >= 50 else '#ef4444'
        quadrant_color = QUADRANT_TEXT_COLORS.get(repo.get('quadrant', ''), '#64748b')
        
        rows += f'''
        <tr>
            <td>{i}</td>
            <td style="font-weight: 500; color: #e2e8f0;">{repo.get('name', '')}</td>
            <td><span class="badge" style="background: {health_color}">{health:.0f}</span></td>
            <td style="color: {quadrant_color}; font-weight: 600;">{repo.get('quadrant', '')}</td>
            <td>{repo.get('complexity', 0):.0f}</td>
            <td>{repo.get('resilience', 0):.0f}</td>
            <td>{repo.get('theater', 1.0):.2f}</td>
        </tr>
        '''
    
    return f'''
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Repository</th>
                    <th>Health</th>
                    <th>Quadrant</th>
                    <th>Complexity</th>
                    <th>Resilience</th>
                    <th>Theater</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    '''


def calculate_dot_position(complexity_score: float, resilience_score: float) -> tuple:
    """
    Calculate X/Y position for a repo dot.
    
    Returns (x_pct, y_pct) where:
    - x_pct: 0 = left (high complexity), 100 = right (low complexity)
    - y_pct: 0 = top (high resilience), 100 = bottom (low resilience)
    """
    # Complexity score: higher = lower complexity, so use directly for X
    x_pct = complexity_score
    
    # Resilience score: higher = better, but CSS top=0 is top, so invert
    y_pct = 100 - resilience_score
    
    # Handle edge cases
    if resilience_score < 0:
        y_pct = 50
    
    # Clamp with padding
    x_pct = max(8, min(92, x_pct))
    y_pct = max(8, min(92, y_pct))
    
    return x_pct, y_pct
