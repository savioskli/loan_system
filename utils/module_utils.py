from models.module import Module
from sqlalchemy import func

def generate_module_code(name, parent_id=None):
    """
    Generate a unique module code based on the module name and parent.
    For parent modules: Use first 2-3 letters + '00'
    For child modules: Use parent's prefix + next available number
    """
    if parent_id is None:
        # This is a parent module
        # Take first 3 letters of the name, convert to uppercase
        prefix = ''.join(word[0] for word in name.split()[:3]).upper()
        if len(prefix) < 2:
            prefix = name[:3].upper()
        
        # Ensure prefix is at least 2 characters
        prefix = prefix[:3].ljust(2, 'X')
        
        # Add '00' suffix for parent modules
        code = f"{prefix}00"
        
        # Check if code exists, if so, increment the prefix
        counter = 1
        temp_code = code
        while Module.query.filter_by(code=temp_code).first():
            temp_code = f"{prefix}{counter:02d}"
            counter += 1
        
        return temp_code
    else:
        # This is a child module
        parent = Module.query.get(parent_id)
        if not parent:
            raise ValueError("Parent module not found")
        
        # Get parent's prefix (everything except last 2 digits)
        prefix = parent.code[:-2]
        
        # Find the highest number used for this prefix
        highest_child = (Module.query
                        .filter(Module.code.like(f"{prefix}%"))
                        .filter(Module.code != parent.code)
                        .order_by(func.length(Module.code).desc(), Module.code.desc())
                        .first())
        
        if highest_child:
            # Extract the number from the highest child's code and increment it
            try:
                last_num = int(highest_child.code[-2:])
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
            
        # Format new code with incremented number
        return f"{prefix}{new_num:02d}"
