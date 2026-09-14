# Password Generator

A customizable and secure Python Random Password Generator featuring password strength evaluation (entropy calculation), batch generation, and custom character set rules.

## Features
- **Custom Length & Rules**: Choose length, uppercase/lowercase letters, digits, and special characters.
- **Ambiguous Character Filtering**: Optionally exclude easy-to-confuse characters (`l`, `1`, `I`, `o`, `0`, `O`).
- **Strength Evaluator**: Calculates bits of entropy and evaluates password strength.
- **Batch Generation**: Generate multiple passwords at once.
- **CLI Interface & Reusable Module**: Run directly in terminal or import functions into your own Python projects.

## Usage

### Run CLI Tool
```bash
python password_generator.py
```

### Import as Module
```python
import password_generator

# Generate a 16-character secure password
pwd = password_generator.generate_password(length=16)
print("Password:", pwd)

# Check password strength
entropy, rating = password_generator.evaluate_strength(pwd)
print(f"Rating: {rating} ({entropy} bits)")
```
