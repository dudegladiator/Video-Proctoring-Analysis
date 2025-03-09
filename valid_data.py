import json
import os
import glob
import re

def fix_json_content(content):
    # Remove any leading/trailing whitespace and invalid characters
    content = content.strip()
    content = content.replace('\ufeff', '')  # Remove BOM if present
    
    # Fix activityLog quotes
    if content.startswith('activityLog'):
        content = '"activityLog"' + content[len('activityLog'):]
    elif content.startswith('"activityLog'):
        pass  # Already has quotes
    else:
        print("Warning: Content doesn't start with 'activityLog'")
    
    # Count opening and closing square brackets
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    
    # Add missing square brackets if needed
    if open_brackets > close_brackets:
        content = content + ']' * (open_brackets - close_brackets)
    
    # Remove comma after closing square bracket if present
    content = re.sub(r'\],\s*$', ']', content)
    content = re.sub(r'\],\s*}$', ']}', content)
    
    # Add opening brace if missing
    if not content.startswith('{'):
        content = '{' + content
    
    # Add closing brace if missing
    if not content.endswith('}'):
        content = content + '}'
    
    return content

def fix_json_files(directory_path):
    # Get all json files in the directory
    json_files = glob.glob(os.path.join(directory_path, "candidate*.json"))
    
    for file_path in json_files:
        try:
            # Create backup
            backup_path = file_path + '.backup'
            with open(file_path, 'r', encoding='utf-8') as source:
                with open(backup_path, 'w', encoding='utf-8') as target:
                    target.write(source.read())
            
            # Read the content of the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Fix the JSON content
            fixed_content = fix_json_content(content)
            
            try:
                # Validate the JSON
                json_data = json.loads(fixed_content)
                
                # Write the corrected JSON back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(json_data, file, indent=4)
                
                print(f"Successfully fixed {file_path}")
                
                # Remove backup if successful
                os.remove(backup_path)
                
            except json.JSONDecodeError as e:
                print(f"Error in file {file_path}: {str(e)}")
                print("\nOriginal content (first 200 chars):")
                print(content[:200])
                print("\nFixed content attempt (first 200 chars):")
                print(fixed_content[:200])
                
                # Restore from backup
                os.replace(backup_path, file_path)
                print(f"Restored original content from backup for {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            if os.path.exists(backup_path):
                os.replace(backup_path, file_path)
                print(f"Restored original content from backup for {file_path}")

# Usage
directory_path = "data"  # Replace with your directory path
fix_json_files(directory_path)