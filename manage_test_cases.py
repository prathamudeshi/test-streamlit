#!/usr/bin/env python3
"""
Test Case Management Utility
Helps manage test cases in the CSV file
"""

import csv
import sys
import os

def view_test_cases():
    """Display all test cases"""
    try:
        with open("test_cases.csv", "r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"{'#':<3} {'Query':<40} {'Expected':<8} {'Category':<15} {'Description'}")
            print("-" * 90)
            for i, row in enumerate(reader, 1):
                query = row['query'][:37] + "..." if len(row['query']) > 40 else row['query']
                print(f"{i:<3} {query:<40} {row['expected_action']:<8} {row['expected_category']:<15} {row['description']}")
    except FileNotFoundError:
        print("test_cases.csv not found!")

def add_test_case():
    """Add a new test case"""
    print("Enter test case details:")
    query = input("Query: ").strip()
    expected_action = input("Expected action (allow/block/flag): ").strip()
    expected_category = input("Expected category: ").strip()
    description = input("Description: ").strip()
    
    if not all([query, expected_action, expected_category, description]):
        print("All fields are required!")
        return
    
    # Read existing test cases
    test_cases = []
    try:
        with open("test_cases.csv", "r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            test_cases = list(reader)
    except FileNotFoundError:
        pass
    
    # Add new test case
    new_case = {
        'query': query,
        'expected_action': expected_action,
        'expected_category': expected_category,
        'description': description
    }
    test_cases.append(new_case)
    
    # Write back to CSV
    with open("test_cases.csv", "w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['query', 'expected_action', 'expected_category', 'description'])
        writer.writeheader()
        writer.writerows(test_cases)
    
    print(f"Added test case: {query}")

def delete_test_case():
    """Delete a test case by number"""
    view_test_cases()
    try:
        num = int(input("\nEnter test case number to delete: ")) - 1
    except ValueError:
        print("Invalid number!")
        return
    
    # Read existing test cases
    try:
        with open("test_cases.csv", "r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            test_cases = list(reader)
    except FileNotFoundError:
        print("test_cases.csv not found!")
        return
    
    if 0 <= num < len(test_cases):
        deleted = test_cases.pop(num)
        print(f"Deleted: {deleted['query']}")
        
        # Write back to CSV
        with open("test_cases.csv", "w", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['query', 'expected_action', 'expected_category', 'description'])
            writer.writeheader()
            writer.writerows(test_cases)
    else:
        print("Invalid test case number!")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "view":
            view_test_cases()
        elif command == "add":
            add_test_case()
        elif command == "delete":
            delete_test_case()
        else:
            print("Unknown command. Use: view, add, or delete")
    else:
        print("Test Case Management Utility")
        print("Usage:")
        print("  python manage_test_cases.py view    - View all test cases")
        print("  python manage_test_cases.py add     - Add a new test case")
        print("  python manage_test_cases.py delete  - Delete a test case")

if __name__ == "__main__":
    main() 