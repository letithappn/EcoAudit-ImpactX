import re

def main():
    with open('docs/architecture/06_autonomous_agent_blueprint.md', 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
    if not blocks:
        raise ValueError("No Python code block found in 06_autonomous_agent_blueprint.md")

    print(f"Found {len(blocks)} python code blocks. Executing primary block...")
    exec(blocks[0], globals())
    print("\n[VERIFICATION SUCCESSFUL]: Code block executed with zero errors.")

if __name__ == '__main__':
    main()
