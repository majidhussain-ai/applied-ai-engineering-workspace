# Get all built-in names from Python
builtins_dict = __builtins__.__dict__

print("MAIN BUILT-IN PYTHON ERRORS")

# Loop and print only real Exceptions line-by-line
for name, obj in builtins_dict.items():
    if isinstance(obj, type) and issubclass(obj, Exception):
        print(f"-> {name}")
