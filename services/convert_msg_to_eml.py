#!/usr/bin/env python3
"""
Robust Zimbra .msg to .eml Converter
This script converts Zimbra .msg files to .eml format with special handling for binary data.
It specifically filters emails related to ckiburu@agrifinance.org.
"""

import os
import sys
import re
import email
import argparse
import chardet
import base64
import shutil
from pathlib import Path
from email import policy
from email.parser import BytesParser, Parser
from email.message import EmailMessage

# Default source and output directories
DEFAULT_SOURCE_DIR = "/Users/user/Documents/Zimbra/004/msg/5/"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Documents/Zimbra/kiburu/0")
# Define the target email address
TARGET_EMAIL = "ckkiburu@agrifinance.org"

def detect_encoding(file_path):
    """
    Detect the encoding of a file using chardet
    """
    # Read a sample of the file to detect encoding
    with open(file_path, 'rb') as f:
        # Read first 10KB for detection
        raw_data = f.read(10240)
        result = chardet.detect(raw_data)
        return result['encoding']

def is_binary_data(data, threshold=0.30):
    """
    Check if data appears to be binary by counting non-printable characters
    """
    # Count non-printable ASCII characters
    non_printable = sum(1 for byte in data if byte < 32 and byte not in (9, 10, 13))  # Tab, LF, CR are allowed
    
    # If more than threshold% of characters are non-printable, likely binary
    return (non_printable / len(data)) > threshold if data else False

def try_extract_email_parts(file_path):
    """
    Try to extract email parts from a file that doesn't parse correctly
    """
    # Create a new email message
    new_msg = EmailMessage()
    
    # Read the entire file
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Check if it's binary data
    if is_binary_data(data):
        print(f"File appears to be binary data, using alternative parsing method")
        
        # Try to find common email headers
        # First convert to text with lenient encoding
        try:
            text_data = data.decode('utf-8', errors='replace')
        except:
            text_data = data.decode('latin-1', errors='replace')
        
        # Look for common headers
        from_match = re.search(r'From:(.+?)(?:\r?\n(?![ \t])|\Z)', text_data, re.DOTALL)
        to_match = re.search(r'To:(.+?)(?:\r?\n(?![ \t])|\Z)', text_data, re.DOTALL)
        cc_match = re.search(r'Cc:(.+?)(?:\r?\n(?![ \t])|\Z)', text_data, re.DOTALL)
        subject_match = re.search(r'Subject:(.+?)(?:\r?\n(?![ \t])|\Z)', text_data, re.DOTALL)
        date_match = re.search(r'Date:(.+?)(?:\r?\n(?![ \t])|\Z)', text_data, re.DOTALL)
        
        # Set headers if found
        if from_match:
            new_msg['From'] = from_match.group(1).strip()
        if to_match:
            new_msg['To'] = to_match.group(1).strip()
        if cc_match:
            new_msg['Cc'] = cc_match.group(1).strip()
        if subject_match:
            new_msg['Subject'] = subject_match.group(1).strip()
        if date_match:
            new_msg['Date'] = date_match.group(1).strip()
        
        # Add a default content type
        new_msg['Content-Type'] = 'text/plain; charset="utf-8"'
        
        # Try to find the body
        # Look for common body separators
        body_separators = [
            '\r\n\r\n', '\n\n', 
            'Content-Type: text/plain', 
            'Content-Type: text/html'
        ]
        
        body_text = ""
        for separator in body_separators:
            parts = text_data.split(separator, 1)
            if len(parts) > 1:
                body_text = parts[1]
                break
        
        # If no body found, use the entire content as body
        if not body_text:
            body_text = text_data
        
        # Set the body
        new_msg.set_content(body_text)
        
        return new_msg
    
    return None

def convert_msg_to_eml(msg_file, output_file):
    """
    Convert a .msg file to .eml format with improved handling for different formats
    Returns the parsed email message if successful, None otherwise
    """
    try:
        # Try binary parsing first
        try:
            with open(msg_file, 'rb') as f:
                parser = BytesParser(policy=policy.default)
                msg = parser.parse(f)
                
                # Test if the parsed message has valid structure
                if 'From' not in msg and 'To' not in msg and 'Subject' not in msg:
                    raise ValueError("Parsed message lacks basic email headers")
                
                # Write as .eml
                with open(output_file, 'wb') as out_file:
                    out_file.write(msg.as_bytes())
                print(f"Standard parsing successful for {msg_file}")
                return msg
        except Exception as binary_error:
            print(f"Standard parsing failed: {binary_error}")
            
            # Try to detect encoding
            encoding = detect_encoding(msg_file)
            print(f"Detected encoding: {encoding or 'unknown'}")
            
            # If encoding detection fails, use UTF-8 as a fallback
            if not encoding:
                encoding = 'utf-8'
            
            # Try text-based parsing
            try:
                with open(msg_file, 'r', encoding=encoding, errors='replace') as f:
                    parser = Parser(policy=policy.default)
                    msg = parser.parse(f)
                    
                    # Test if the parsed message has valid structure
                    if 'From' not in msg and 'To' not in msg and 'Subject' not in msg:
                        raise ValueError("Parsed message lacks basic email headers")
                    
                    with open(output_file, 'w', encoding='utf-8') as out_file:
                        out_file.write(msg.as_string())
                    print(f"Text parsing successful for {msg_file}")
                    return msg
            except Exception as text_error:
                print(f"Text parsing failed: {text_error}")
                
                # Last resort - try to extract email parts
                msg = try_extract_email_parts(msg_file)
                if msg:
                    with open(output_file, 'wb') as out_file:
                        out_file.write(msg.as_bytes())
                    print(f"Alternative parsing successful for {msg_file}")
                    return msg
                else:
                    print(f"All parsing methods failed for {msg_file}")
                    return None
        
    except Exception as e:
        print(f"Error converting {msg_file} to {output_file}: {e}")
        return None

def is_target_email_involved(email_msg, target_email=TARGET_EMAIL):
    """
    Check if the target email address is in From, To, or Cc fields
    """
    # Initialize with empty string if header is missing
    from_field = email_msg.get('From', '')
    to_field = email_msg.get('To', '')
    cc_field = email_msg.get('Cc', '')
    
    # Convert all fields to lowercase for case-insensitive comparison
    target_email = target_email.lower()
    from_field = from_field.lower()
    to_field = to_field.lower()
    cc_field = cc_field.lower()
    
    # Check if target email is in any of the fields
    if target_email in from_field or target_email in to_field or target_email in cc_field:
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Convert Zimbra .msg files to .eml format')
    parser.add_argument('-i', '--input', default=DEFAULT_SOURCE_DIR, 
                       help=f'Input .msg file or directory containing .msg files (default: {DEFAULT_SOURCE_DIR})')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR, 
                       help=f'Output directory for .eml files (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('-t', '--target-email', default=TARGET_EMAIL,
                       help=f'Target email address to filter for (default: {TARGET_EMAIL})')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Process all emails, not just those related to the target email')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Print detailed processing information')
    args = parser.parse_args()
    
    # Check if input is a file or directory
    input_path = Path(args.input)
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = list(input_path.glob('**/*.msg'))  # Also search subdirectories
    else:
        print(f"Error: {args.input} does not exist")
        return 1
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    if not output_path.exists():
        print(f"Creating output directory: {args.output}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Create a specific directory for target emails
    target_dir = output_path / f"{args.target_email.split('@')[0]}_emails"
    if not target_dir.exists() and not args.all:
        print(f"Creating directory for {args.target_email} emails: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    success_count = 0
    target_count = 0
    print(f"Found {len(files)} .msg files to process")
    
    if not args.all:
        print(f"Filtering for emails involving: {args.target_email}")
    
    for msg_file in files:
        try:
            if args.verbose:
                print(f"Processing {msg_file}...")
            else:
                print(f"Processing {msg_file.name}...")
            
            # Generate temporary output filename
            temp_output_file = output_path / f"{msg_file.stem}.eml"
            
            # Convert the file
            parsed_msg = convert_msg_to_eml(str(msg_file), str(temp_output_file))
            
            if parsed_msg:
                success_count += 1
                
                if args.all:
                    # Keep all emails in the main output directory
                    if args.verbose:
                        print(f"Saved to {temp_output_file}")
                    else:
                        print(f"Saved {temp_output_file.name}")
                else:
                    # Check if the email involves our target address
                    if is_target_email_involved(parsed_msg, args.target_email):
                        # Move to target directory
                        target_file = target_dir / f"{msg_file.stem}.eml"
                        shutil.move(str(temp_output_file), str(target_file))
                        if args.verbose:
                            print(f"Target email found! Moved to {target_file}")
                        else:
                            print(f"Target email found! Moved to {target_file.name}")
                        target_count += 1
                    else:
                        # Remove the file as it doesn't match our target
                        os.remove(temp_output_file)
                        print(f"Skipped {msg_file.name} - not related to {args.target_email}")
            
        except Exception as e:
            print(f"Error processing {msg_file}: {e}")
    
    print(f"Conversion complete. {success_count} of {len(files)} files processed successfully.")
    if not args.all:
        print(f"Found {target_count} emails involving {args.target_email}.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())