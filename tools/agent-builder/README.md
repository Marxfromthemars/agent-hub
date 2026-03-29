# Agent Builder

Generate complete projects from templates in seconds.

## Usage

```bash
python builder.py --template cli --name "my-tool" --output ./projects
python builder.py --template agent --name "researcher" --output ./agents
python builder.py --template api --name "my-api" --output ./apis
python builder.py --template web --name "dashboard" --output ./web
```

## Templates

- **cli** - Command-line tools with argparse
- **agent** - Autonomous agents with observe/think/act
- **api** - REST APIs with Flask
- **web** - Static HTML/CSS/JS interfaces

## Generated Structure

Each template creates:
- README.md - Project documentation
- Main file - Working code
- requirements.txt - Dependencies (if needed)
